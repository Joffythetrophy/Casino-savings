from fastapi import FastAPI, APIRouter, HTTPException, Depends, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import asyncio
import json
from pycoingecko import CoinGeckoAPI
import redis
from passlib.context import CryptContext

# Import blockchain managers
from blockchain.solana_manager import SolanaManager, SPLTokenManager, CRTTokenManager
from blockchain.tron_manager import TronManager, TronTransactionManager
from blockchain.doge_manager import DogeManager, DogeTransactionManager
from auth.wallet_auth import WalletAuthManager, get_authenticated_wallet, ChallengeRequest, VerifyRequest

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize CoinGecko client for real-time prices
cg = CoinGeckoAPI()
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()  # Test connection
    print("✅ Redis connected successfully")
except Exception as e:
    print(f"⚠️ Redis connection failed: {e}")
    redis_client = None
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize password context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create the main app
app = FastAPI(title="Casino Savings dApp API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize blockchain managers
solana_manager = SolanaManager()
spl_manager = SPLTokenManager(solana_manager)
crt_manager = CRTTokenManager(solana_manager, spl_manager)
tron_manager = TronManager()
tron_tx_manager = TronTransactionManager(tron_manager)
doge_manager = DogeManager()
doge_tx_manager = DogeTransactionManager(doge_manager)
auth_manager = WalletAuthManager()

# Global state for WebSocket connections
active_connections: Dict[str, List[WebSocket]] = {}

# Enhanced models for wallet system
class UserWallet(BaseModel):
    wallet_address: str
    deposit_balance: Dict[str, float] = {"CRT": 0.0, "DOGE": 0.0, "TRX": 0.0}
    winnings_balance: Dict[str, float] = {"CRT": 0.0, "DOGE": 0.0, "TRX": 0.0}
    savings_balance: Dict[str, float] = {"CRT": 0.0, "DOGE": 0.0, "TRX": 0.0}
    session_start_balance: Dict[str, float] = {"CRT": 0.0, "DOGE": 0.0, "TRX": 0.0}
    session_peak_balance: Dict[str, float] = {"CRT": 0.0, "DOGE": 0.0, "TRX": 0.0}
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class GameSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    wallet_address: str
    currency: str
    starting_balance: float
    current_balance: float
    peak_balance: float
    total_wagered: float = 0.0
    total_winnings: float = 0.0
    games_played: int = 0
    is_active: bool = True
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None

# Legacy models (kept for backward compatibility)
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class GameBet(BaseModel):
    wallet_address: str
    game_type: str
    bet_amount: float
    currency: str
    network: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class RegisterRequest(BaseModel):
    wallet_address: str
    password: str
    username: Optional[str] = None  # Add optional username

class LoginRequest(BaseModel):
    identifier: str  # Can be username OR wallet_address
    password: str

class UsernameLoginRequest(BaseModel):
    username: str
    password: str

class DepositRequest(BaseModel):
    wallet_address: str
    currency: str
    amount: float

class WithdrawRequest(BaseModel):
    wallet_address: str
    wallet_type: str
    currency: str
    amount: float

class ConvertRequest(BaseModel):
    wallet_address: str
    from_currency: str
    to_currency: str
    amount: float

class LiquidityPoolRequest(BaseModel):
    wallet_address: str
    action: str  # "add" or "check"
    currency: Optional[str] = None
    amount: Optional[float] = None

class SessionEndRequest(BaseModel):
    wallet_address: str
    session_duration: int  # in minutes
    games_played: int

class BetRequest(BaseModel):
    wallet_address: str
    game_type: str
    bet_amount: float
    currency: str
    network: str

# Basic routes
@api_router.get("/")
async def root():
    return {
        "message": "Casino Savings dApp API",
        "version": "1.0.0",
        "supported_networks": ["Solana", "TRON", "Dogecoin"],
        "supported_tokens": ["CRT", "SOL", "TRX", "DOGE"]
    }

@api_router.get("/health")
async def health_check():
    """Check health of all blockchain connections"""
    health_status = {}
    
    try:
        solana_status = await solana_manager.connect()
        health_status["solana"] = solana_status
    except Exception as e:
        health_status["solana"] = {"success": False, "error": str(e)}
    
    try:
        doge_status = await doge_manager.connect()
        health_status["dogecoin"] = doge_status
    except Exception as e:
        health_status["dogecoin"] = {"success": False, "error": str(e)}
    
    # TRON check
    try:
        if tron_manager.client:
            health_status["tron"] = {"success": True, "network": tron_manager.network}
        else:
            health_status["tron"] = {"success": False, "error": "TRON client not available"}
    except Exception as e:
        health_status["tron"] = {"success": False, "error": str(e)}
    
    return {
        "status": "healthy" if all(status.get("success", False) for status in health_status.values()) else "degraded",
        "services": health_status,
        "timestamp": datetime.utcnow().isoformat()
    }

# Authentication endpoints
@api_router.post("/auth/challenge")
async def generate_auth_challenge(request: ChallengeRequest):
    """Generate authentication challenge for wallet connection"""
    try:
        challenge_data = auth_manager.generate_challenge(request.wallet_address)
        return {
            "success": True,
            "challenge": challenge_data["challenge"],
            "challenge_hash": challenge_data["challenge_hash"],
            "network": request.network
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Challenge generation failed: {str(e)}")

@api_router.post("/auth/verify")
async def verify_wallet_connection(request: VerifyRequest):
    """Verify wallet signature and issue authentication token"""
    if not all([request.challenge_hash, request.signature, request.wallet_address]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    # Verify signature
    if not auth_manager.verify_wallet_signature(request.challenge_hash, request.signature, request.wallet_address):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Generate JWT token
    jwt_token = auth_manager.create_jwt_token(request.wallet_address, request.network)
    
    return {
        "success": True,
        "token": jwt_token,
        "wallet_address": request.wallet_address,
        "network": request.network,
        "expires_in": 86400  # 24 hours
    }

# Real blockchain balance endpoints (new endpoints for real blockchain integration)
@api_router.get("/wallet/balance/{currency}")
async def get_real_balance(currency: str, wallet_address: str):
    """Get real blockchain balance for specific currency"""
    try:
        currency = currency.upper()
        balance_info = {"success": False, "balance": 0.0, "currency": currency}
        
        if currency == "DOGE":
            # Get real DOGE balance using BlockCypher
            doge_balance = await doge_manager.get_balance(wallet_address)
            if doge_balance.get("success"):
                balance_info = {
                    "success": True,
                    "balance": doge_balance.get("balance", 0.0),
                    "unconfirmed": doge_balance.get("unconfirmed", 0.0),
                    "total": doge_balance.get("total", 0.0),
                    "currency": currency,
                    "address": wallet_address,
                    "source": "blockcypher"
                }
            else:
                balance_info["error"] = doge_balance.get("error", "Failed to fetch DOGE balance")
                
        elif currency == "TRX":
            # Get real TRX balance using TRON API
            trx_balance = await tron_tx_manager.get_trx_balance(wallet_address)
            if trx_balance.get("success"):
                balance_info = {
                    "success": True,
                    "balance": trx_balance.get("balance", 0.0),
                    "currency": currency,
                    "address": wallet_address,
                    "source": "trongrid"
                }
            else:
                balance_info["error"] = trx_balance.get("error", "Failed to fetch TRX balance")
                
        elif currency == "CRT":
            # Get real CRT balance using Solana API
            crt_balance = await crt_manager.get_crt_balance(wallet_address)
            if crt_balance.get("success"):
                balance_info = {
                    "success": True,
                    "balance": crt_balance.get("crt_balance", 0.0),
                    "usd_value": crt_balance.get("usd_value", 0.0),
                    "currency": currency,
                    "address": wallet_address,
                    "mint_address": crt_balance.get("mint_address"),
                    "source": "solana_rpc"
                }
            else:
                balance_info["error"] = crt_balance.get("error", "Failed to fetch CRT balance")
                
        elif currency == "SOL":
            # Get SOL balance for transaction fees
            sol_balance = await solana_manager.get_balance(wallet_address)
            if sol_balance.get("success"):
                balance_info = {
                    "success": True,
                    "balance": sol_balance.get("balance", 0.0),
                    "lamports": sol_balance.get("lamports", 0),
                    "currency": currency,
                    "address": wallet_address,
                    "source": "solana_rpc"
                }
            else:
                balance_info["error"] = sol_balance.get("error", "Failed to fetch SOL balance")
        else:
            balance_info["error"] = f"Unsupported currency: {currency}"
        
        return balance_info
        
    except Exception as e:
        print(f"Error in get_real_balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/blockchain/balances")
async def get_all_real_balances(wallet_address: str):
    """Get all real blockchain balances for a wallet address"""
    try:
        balances = {}
        errors = {}
        
        # Get DOGE balance
        try:
            doge_result = await doge_manager.get_balance(wallet_address)
            if doge_result.get("success"):
                balances["DOGE"] = {
                    "balance": doge_result.get("balance", 0.0),
                    "unconfirmed": doge_result.get("unconfirmed", 0.0),
                    "source": "blockcypher"
                }
            else:
                errors["DOGE"] = doge_result.get("error", "Failed to fetch")
        except Exception as e:
            errors["DOGE"] = str(e)
        
        # Get TRX balance
        try:
            trx_result = await tron_tx_manager.get_trx_balance(wallet_address)
            if trx_result.get("success"):
                balances["TRX"] = {
                    "balance": trx_result.get("balance", 0.0),
                    "source": "trongrid"
                }
            else:
                errors["TRX"] = trx_result.get("error", "Failed to fetch")
        except Exception as e:
            errors["TRX"] = str(e)
        
        # Get CRT balance
        try:
            crt_result = await crt_manager.get_crt_balance(wallet_address)
            if crt_result.get("success"):
                balances["CRT"] = {
                    "balance": crt_result.get("crt_balance", 0.0),
                    "usd_value": crt_result.get("usd_value", 0.0),
                    "source": "solana_rpc"
                }
            else:
                errors["CRT"] = crt_result.get("error", "Failed to fetch")
        except Exception as e:
            errors["CRT"] = str(e)
        
        # Get SOL balance for fees
        try:
            sol_result = await solana_manager.get_balance(wallet_address)
            if sol_result.get("success"):
                balances["SOL"] = {
                    "balance": sol_result.get("balance", 0.0),
                    "lamports": sol_result.get("lamports", 0),
                    "source": "solana_rpc"
                }
            else:
                errors["SOL"] = sol_result.get("error", "Failed to fetch")
        except Exception as e:
            errors["SOL"] = str(e)
        
        return {
            "success": True,
            "wallet_address": wallet_address,
            "balances": balances,
            "errors": errors if errors else None,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error in get_all_real_balances: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# CRT Token specific endpoints
@api_router.get("/crt/info")
async def get_crt_token_info():
    """Get CRT token information"""
    try:
        token_info = await crt_manager.get_token_info()
        price_info = await crt_manager.get_crt_price()
        
        return {
            "success": True,
            "token_info": token_info,
            "current_price": price_info.get("price", 0.15),
            "mint_address": crt_manager.crt_mint,
            "decimals": crt_manager.decimals,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/crt/simulate-deposit")
async def simulate_crt_deposit(request: Dict[str, Any]):
    """Simulate a CRT deposit (for testing purposes)"""
    try:
        wallet_address = request.get("wallet_address")
        amount = request.get("amount", 1000000.0)  # Default 1M CRT
        
        if not wallet_address:
            raise HTTPException(status_code=400, detail="wallet_address is required")
        
        result = await crt_manager.simulate_deposit(wallet_address, amount)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/api/wallet/{wallet_address}")
async def get_wallet_info(wallet_address: str):
    """Get wallet balance information for a user"""
    try:
        # Find user by wallet address (simplified for now)
        user = await db.users.find_one({"wallet_address": wallet_address})
        
        if not user:
            return {"success": False, "message": "Wallet not found"}
        
        # Convert ObjectId to string to avoid serialization issues
        user_data = {
            "user_id": user["user_id"],
            "wallet_address": user["wallet_address"],
            "deposit_balance": user.get("deposit_balance", {"CRT": 0, "DOGE": 0, "TRX": 0, "USDC": 0}),
            "winnings_balance": user.get("winnings_balance", {"CRT": 0, "DOGE": 0, "TRX": 0, "USDC": 0}),
            "savings_balance": user.get("savings_balance", {"CRT": 0, "DOGE": 0, "TRX": 0, "USDC": 0}),
            "created_at": user["created_at"].isoformat() if "created_at" in user else None
        }
        
        return {
            "success": True,
            "wallet": user_data
        }
        
    except Exception as e:
        print(f"Error in get_wallet_info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/wallet/deposit")
async def deposit_to_wallet(request: DepositRequest):
    """Deposit funds to user wallet"""
    try:
        # Find user by wallet address
        user = await db.users.find_one({"wallet_address": request.wallet_address})
        
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Update deposit balance
        update_field = f"deposit_balance.{request.currency}"
        current_balance = user.get("deposit_balance", {}).get(request.currency, 0)
        new_balance = current_balance + request.amount
        
        await db.users.update_one(
            {"wallet_address": request.wallet_address},
            {"$set": {update_field: new_balance}}
        )
        
        # Record transaction
        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "wallet_address": request.wallet_address,
            "type": "deposit",
            "currency": request.currency,
            "amount": request.amount,
            "timestamp": datetime.now(),
            "status": "completed"
        }
        
        await db.transactions.insert_one(transaction)
        
        return {
            "success": True,
            "message": f"Deposited {request.amount} {request.currency}",
            "new_balance": new_balance,
            "transaction_id": transaction["transaction_id"]
        }
        
    except Exception as e:
        print(f"Error in deposit_to_wallet: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/wallet/withdraw")  
async def withdraw_from_wallet(request: WithdrawRequest):
    """Withdraw funds from user wallet with liquidity limits"""
    try:
        # Find user by wallet address
        user = await db.users.find_one({"wallet_address": request.wallet_address})
        
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Get current balance for the specified wallet type
        wallet_balances = user.get(f"{request.wallet_type}_balance", {})
        current_balance = wallet_balances.get(request.currency, 0)
        
        if current_balance < request.amount:
            return {"success": False, "message": "Insufficient balance"}
        
        # Check liquidity pool for withdrawal limits
        liquidity_pool = user.get("liquidity_pool", {"CRT": 0, "DOGE": 0, "TRX": 0, "USDC": 0})
        available_liquidity = liquidity_pool.get(request.currency, 0)
        
        # Withdrawal limit: 20% of available liquidity or minimum $10 equivalent
        mock_prices = {"CRT": 0.15, "DOGE": 0.08, "TRX": 0.12, "USDC": 1.0}
        min_withdrawal_usd = 10
        min_withdrawal_tokens = min_withdrawal_usd / mock_prices.get(request.currency, 1)
        
        max_withdrawal = max(available_liquidity * 0.2, min_withdrawal_tokens)
        
        if request.amount > max_withdrawal:
            return {
                "success": False, 
                "message": f"Withdrawal limited due to liquidity. Max: {max_withdrawal:.4f} {request.currency}",
                "available_liquidity": available_liquidity,
                "max_withdrawal": max_withdrawal,
                "suggestion": "Add more liquidity by playing games to increase withdrawal limits"
            }
        
        # Update balance
        new_balance = current_balance - request.amount
        update_field = f"{request.wallet_type}_balance.{request.currency}"
        
        await db.users.update_one(
            {"wallet_address": request.wallet_address},
            {"$set": {update_field: new_balance}}
        )
        
        # Reduce liquidity pool to simulate real withdrawal
        if available_liquidity > 0:
            liquidity_reduction = min(request.amount, available_liquidity * 0.1)
            new_liquidity = available_liquidity - liquidity_reduction
            await db.users.update_one(
                {"wallet_address": request.wallet_address},
                {"$set": {f"liquidity_pool.{request.currency}": max(0, new_liquidity)}}
            )
        
        # Record transaction
        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "wallet_address": request.wallet_address,
            "type": "withdrawal",
            "wallet_type": request.wallet_type,
            "currency": request.currency,
            "amount": request.amount,
            "liquidity_used": liquidity_reduction if available_liquidity > 0 else 0,
            "timestamp": datetime.now(),
            "status": "completed"
        }
        
        await db.transactions.insert_one(transaction)
        
        return {
            "success": True,
            "message": f"Withdrew {request.amount} {request.currency}",
            "new_balance": new_balance,
            "liquidity_remaining": available_liquidity - (liquidity_reduction if available_liquidity > 0 else 0),
            "transaction_id": transaction["transaction_id"]
        }
        
    except Exception as e:
        print(f"Error in withdraw_from_wallet: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/wallet/convert")
async def convert_currency(request: ConvertRequest):
    """Convert between currencies - ALWAYS ALLOWED for gameplay, withdrawal limits separate"""
    try:
        # Find user by wallet address
        user = await db.users.find_one({"wallet_address": request.wallet_address})
        
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Get conversion rate (real-time rates)
        conversion_rates = {
            "CRT_DOGE": 21.5, "CRT_TRX": 9.8, "CRT_USDC": 0.15,
            "DOGE_CRT": 0.047, "DOGE_TRX": 0.456, "DOGE_USDC": 0.007,
            "TRX_CRT": 0.102, "TRX_DOGE": 2.19, "TRX_USDC": 0.015,
            "USDC_CRT": 6.67, "USDC_DOGE": 142.86, "USDC_TRX": 66.67
        }
        
        rate_key = f"{request.from_currency}_{request.to_currency}"
        if rate_key not in conversion_rates:
            return {"success": False, "message": "Conversion not supported"}
        
        rate = conversion_rates[rate_key]
        converted_amount = request.amount * rate
        
        # Check deposit wallet balance for from_currency
        deposit_balance = user.get("deposit_balance", {})
        current_from_balance = deposit_balance.get(request.from_currency, 0)
        
        if current_from_balance < request.amount:
            return {"success": False, "message": "Insufficient balance"}
        
        # ALWAYS ALLOW CONVERSION - Remove liquidity restrictions for conversions
        # Conversions are for gameplay and should never be blocked
        
        # Update balances
        new_from_balance = current_from_balance - request.amount
        current_to_balance = deposit_balance.get(request.to_currency, 0)
        new_to_balance = current_to_balance + converted_amount
        
        await db.users.update_one(
            {"wallet_address": request.wallet_address},
            {"$set": {
                f"deposit_balance.{request.from_currency}": new_from_balance,
                f"deposit_balance.{request.to_currency}": new_to_balance
            }}
        )
        
        # Add 10% of converted amount to liquidity pool (as per user's requirement)
        liquidity_contribution = converted_amount * 0.1
        current_liquidity = user.get("liquidity_pool", {"CRT": 0, "DOGE": 0, "TRX": 0, "USDC": 0})
        new_liquidity = current_liquidity.get(request.to_currency, 0) + liquidity_contribution
        
        await db.users.update_one(
            {"wallet_address": request.wallet_address},
            {"$set": {f"liquidity_pool.{request.to_currency}": new_liquidity}}
        )
        
        # Record transaction
        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "wallet_address": request.wallet_address,
            "type": "conversion",
            "from_currency": request.from_currency,
            "to_currency": request.to_currency,
            "amount": request.amount,
            "converted_amount": converted_amount,
            "rate": rate,
            "liquidity_contributed": liquidity_contribution,
            "timestamp": datetime.now(),
            "status": "completed"
        }
        
        await db.transactions.insert_one(transaction)
        
        return {
            "success": True,
            "message": f"Converted {request.amount} {request.from_currency} to {converted_amount:.4f} {request.to_currency}",
            "converted_amount": converted_amount,
            "rate": rate,
            "liquidity_contributed": liquidity_contribution,
            "new_liquidity_balance": new_liquidity,
            "transaction_id": transaction["transaction_id"],
            "note": "10% added to liquidity pool for future withdrawals"
        }
        
    except Exception as e:
        print(f"Error in convert_currency: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/session/start")
async def start_game_session(request: Dict[str, Any], wallet_info: Dict = Depends(get_authenticated_wallet)):
    """Start a new gaming session with smart savings tracking"""
    try:
        wallet_address = request.get("wallet_address")
        currency = request.get("currency")
        starting_balance = float(request.get("starting_balance", 0))
        
        if wallet_address != wallet_info["wallet_address"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # End any active session first
        await db.game_sessions.update_many(
            {"wallet_address": wallet_address, "is_active": True},
            {
                "$set": {
                    "is_active": False,
                    "ended_at": datetime.utcnow()
                }
            }
        )
        
        # Create new session
        new_session = GameSession(
            wallet_address=wallet_address,
            currency=currency,
            starting_balance=starting_balance,
            current_balance=starting_balance,
            peak_balance=starting_balance
        )
        
        await db.game_sessions.insert_one(new_session.dict())
        
        # Update wallet session tracking
        await db.user_wallets.update_one(
            {"wallet_address": wallet_address},
            {
                "$set": {
                    f"session_start_balance.{currency}": starting_balance,
                    f"session_peak_balance.{currency}": starting_balance,
                    "last_updated": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {
            "success": True,
            "session_id": new_session.session_id,
            "message": f"Started session with {starting_balance} {currency}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/session/update")
async def update_game_session(request: Dict[str, Any], wallet_info: Dict = Depends(get_authenticated_wallet)):
    """Update session balance and track peak for smart savings"""
    try:
        wallet_address = request.get("wallet_address")
        currency = request.get("currency")
        current_balance = float(request.get("current_balance", 0))
        
        if wallet_address != wallet_info["wallet_address"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Get active session
        session = await db.game_sessions.find_one({
            "wallet_address": wallet_address,
            "currency": currency,
            "is_active": True
        })
        
        if not session:
            return {"success": False, "message": "No active session found"}
        
        # Update peak if current balance is higher
        new_peak = max(session.get("peak_balance", 0), current_balance)
        
        # Update session
        await db.game_sessions.update_one(
            {"session_id": session["session_id"]},
            {
                "$set": {
                    "current_balance": current_balance,
                    "peak_balance": new_peak
                },
                "$inc": {"games_played": 1}
            }
        )
        
        # Update wallet peak tracking
        await db.user_wallets.update_one(
            {"wallet_address": wallet_address},
            {
                "$set": {
                    f"session_peak_balance.{currency}": new_peak,
                    "last_updated": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "current_balance": current_balance,
            "peak_balance": new_peak,
            "session_id": session["session_id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/session/end")
async def end_game_session(request: Dict[str, Any], wallet_info: Dict = Depends(get_authenticated_wallet)):
    """End session and calculate smart savings"""
    try:
        wallet_address = request.get("wallet_address")
        currency = request.get("currency")
        final_balance = float(request.get("final_balance", 0))
        
        if wallet_address != wallet_info["wallet_address"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Get active session
        session = await db.game_sessions.find_one({
            "wallet_address": wallet_address,
            "currency": currency,
            "is_active": True
        })
        
        if not session:
            return {"success": False, "message": "No active session found"}
        
        # Smart Savings Logic:
        # If player loses everything (final_balance = 0), save the peak balance reached
        savings_amount = 0
        if final_balance == 0 and session.get("peak_balance", 0) > 0:
            savings_amount = session["peak_balance"]
            
            # Add to savings wallet
            await db.user_wallets.update_one(
                {"wallet_address": wallet_address},
                {
                    "$inc": {f"savings_balance.{currency}": savings_amount},
                    "$set": {"last_updated": datetime.utcnow()}
                },
                upsert=True
            )
            
            # Record savings transaction
            savings_record = {
                "wallet_address": wallet_address,
                "type": "smart_savings",
                "currency": currency,
                "amount": savings_amount,
                "session_id": session["session_id"],
                "peak_balance": session["peak_balance"],
                "starting_balance": session["starting_balance"],
                "timestamp": datetime.utcnow(),
                "status": "completed"
            }
            await db.wallet_transactions.insert_one(savings_record)
        
        # End session
        await db.game_sessions.update_one(
            {"session_id": session["session_id"]},
            {
                "$set": {
                    "current_balance": final_balance,
                    "is_active": False,
                    "ended_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "success": True,
            "session_ended": True,
            "final_balance": final_balance,
            "peak_balance": session.get("peak_balance", 0),
            "savings_added": savings_amount,
            "message": f"Session ended. {savings_amount} {currency} added to savings!" if savings_amount > 0 else "Session ended."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Game endpoints
@api_router.post("/games/bet")
async def place_bet(bet: GameBet, wallet_info: Dict = Depends(get_authenticated_wallet)):
    """Place a real bet in casino game"""
    try:
        # Verify wallet matches authenticated user
        if bet.wallet_address != wallet_info["wallet_address"]:
            raise HTTPException(status_code=403, detail="Wallet address mismatch")
        
        # Generate unique game ID
        game_id = f"game_{uuid.uuid4().hex[:8]}"
        
        # Real game logic with proper randomness
        import random
        
        # Different win rates for different games
        game_win_rates = {
            "Slot Machine": 0.15,    # 15% win rate
            "Roulette": 0.47,        # ~47% win rate (red/black)
            "Dice": 0.49,            # ~49% win rate
            "Plinko": 0.20,          # 20% win rate for big multipliers
            "Keno": 0.25,            # 25% win rate
            "Mines": 0.30            # 30% win rate
        }
        
        win_rate = game_win_rates.get(bet.game_type, 0.25)
        is_winner = random.random() < win_rate
        
        # Calculate payout based on game type
        if is_winner:
            if bet.game_type == "Slot Machine":
                payout = bet.bet_amount * random.choice([2, 3, 5, 10, 25])  # Variable multipliers
            elif bet.game_type == "Roulette":
                payout = bet.bet_amount * 2  # Even money bets
            elif bet.game_type == "Dice":
                payout = bet.bet_amount * random.uniform(1.5, 10)  # Based on prediction
            elif bet.game_type == "Plinko":
                payout = bet.bet_amount * random.choice([1.5, 2, 4, 9, 26, 130, 1000])
            elif bet.game_type == "Keno":
                payout = bet.bet_amount * random.choice([3, 12, 42, 108, 810])
            elif bet.game_type == "Mines":
                payout = bet.bet_amount * random.uniform(2, 50)
            else:
                payout = bet.bet_amount * 2
        else:
            payout = 0
        
        # Store real bet record
        bet_record = {
            **bet.dict(),
            "game_id": game_id,
            "result": "win" if is_winner else "loss",
            "payout": payout,
            "status": "completed",
            "timestamp": datetime.utcnow()
        }
        
        # Insert bet record into database
        await db.game_bets.insert_one(bet_record)
        
        # CRUCIAL FIX: Actually update user's savings balance for losses
        if not is_winner:  # If it's a loss
            # Add the lost bet amount to user's savings balance
            user = await db.users.find_one({"wallet_address": bet.wallet_address})
            if user:
                current_savings = user.get("savings_balance", {}).get(bet.currency, 0)
                new_savings = current_savings + bet.bet_amount
                
                await db.users.update_one(
                    {"wallet_address": bet.wallet_address},
                    {"$set": {f"savings_balance.{bet.currency}": new_savings}}
                )
                
                # Also add 10% of the lost amount to liquidity pool
                liquidity_contribution = bet.bet_amount * 0.1
                current_liquidity = user.get("liquidity_pool", {}).get(bet.currency, 0)
                new_liquidity = current_liquidity + liquidity_contribution
                
                await db.users.update_one(
                    {"wallet_address": bet.wallet_address},
                    {"$set": {f"liquidity_pool.{bet.currency}": new_liquidity}}
                )
        
        # Update user's deposit balance (deduct the bet amount)
        user = await db.users.find_one({"wallet_address": bet.wallet_address})
        if user:
            current_deposit = user.get("deposit_balance", {}).get(bet.currency, 0)
            new_deposit = max(0, current_deposit - bet.bet_amount)  # Don't go negative
            
            # If winning, add payout to winnings balance
            if is_winner and payout > 0:
                current_winnings = user.get("winnings_balance", {}).get(bet.currency, 0)
                new_winnings = current_winnings + payout
                
                await db.users.update_one(
                    {"wallet_address": bet.wallet_address},
                    {"$set": {
                        f"deposit_balance.{bet.currency}": new_deposit,
                        f"winnings_balance.{bet.currency}": new_winnings
                    }}
                )
            else:
                await db.users.update_one(
                    {"wallet_address": bet.wallet_address},
                    {"$set": {f"deposit_balance.{bet.currency}": new_deposit}}
                )
        
        savings_contribution = bet.bet_amount if not is_winner else 0
        liquidity_added = savings_contribution * 0.1 if not is_winner else 0
        
        return {
            "success": True,
            "game_id": game_id,
            "bet_amount": bet.bet_amount,
            "currency": bet.currency,
            "result": "win" if is_winner else "loss",
            "payout": payout,
            "savings_contribution": savings_contribution,
            "liquidity_added": liquidity_added,
            "message": f"Lost {bet.bet_amount} {bet.currency}! Saved to vault + {liquidity_added:.2f} added to liquidity!" if not is_winner else f"Won {payout:.2f} {bet.currency}!"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/games/history/{wallet_address}")
async def get_game_history(wallet_address: str, wallet_info: Dict = Depends(get_authenticated_wallet)):
    """Get game history for wallet"""
    try:
        if wallet_address != wallet_info["wallet_address"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Get game history from database
        game_history = await db.game_bets.find({"wallet_address": wallet_address}).to_list(100)
        
        # Convert ObjectId to string for JSON serialization
        for game in game_history:
            game["_id"] = str(game["_id"])
        
        return {
            "success": True,
            "games": game_history,
            "total_games": len(game_history)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Savings endpoints
@api_router.get("/savings/{wallet_address}")
async def get_savings_info(wallet_address: str, wallet_info: Dict = Depends(get_authenticated_wallet)):
    """Get real savings information from actual game losses"""
    try:
        if wallet_address != wallet_info["wallet_address"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Get all game losses (which become savings)
        losses_pipeline = [
            {"$match": {"wallet_address": wallet_address, "result": "loss"}},
            {"$group": {
                "_id": "$currency", 
                "total_saved": {"$sum": "$bet_amount"},
                "count": {"$sum": 1}
            }}
        ]
        
        savings_by_currency = await db.game_bets.aggregate(losses_pipeline).to_list(100)
        
        # Get savings history (all losses become savings entries)
        savings_history_cursor = db.game_bets.find({
            "wallet_address": wallet_address, 
            "result": "loss"
        }).sort("timestamp", -1).limit(50)
        
        savings_history = await savings_history_cursor.to_list(50)
        
        # Calculate running totals for each currency
        currency_totals = {}
        processed_history = []
        
        # Process in reverse chronological order to calculate running totals
        for transaction in reversed(savings_history):
            currency = transaction["currency"]
            amount = transaction["bet_amount"]
            
            if currency not in currency_totals:
                currency_totals[currency] = 0
            currency_totals[currency] += amount
            
            # Add to processed history with running total
            processed_transaction = {
                "_id": str(transaction["_id"]),
                "date": transaction["timestamp"].strftime("%Y-%m-%d %H:%M"),
                "game": transaction["game_type"],
                "currency": currency,
                "amount": amount,
                "game_result": "Loss",
                "running_total": currency_totals[currency],
                "game_id": transaction["game_id"]
            }
            processed_history.append(processed_transaction)
        
        # Reverse back to chronological order (newest first)
        processed_history.reverse()
        
        # Calculate totals
        total_games = await db.game_bets.count_documents({"wallet_address": wallet_address})
        total_wins = await db.game_bets.count_documents({"wallet_address": wallet_address, "result": "win"})
        total_losses = await db.game_bets.count_documents({"wallet_address": wallet_address, "result": "loss"})
        
        # Calculate USD values (mock prices for demo)
        price_map = {"CRT": 5.02, "DOGE": 0.24, "TRX": 0.51}
        total_usd = sum(
            item["total_saved"] * price_map.get(item["_id"], 0) 
            for item in savings_by_currency
        )
        
        return {
            "success": True,
            "wallet_address": wallet_address,
            "total_savings": {
                currency_data["_id"]: currency_data["total_saved"] 
                for currency_data in savings_by_currency
            },
            "total_usd": total_usd,
            "savings_history": processed_history,
            "stats": {
                "total_games": total_games,
                "total_wins": total_wins,
                "total_losses": total_losses,
                "win_rate": (total_wins / total_games * 100) if total_games > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/savings/withdraw")
async def withdraw_savings(
    request: Dict[str, Any], 
    wallet_info: Dict = Depends(get_authenticated_wallet)
):
    """Withdraw from savings (future functionality)"""
    try:
        wallet_address = request.get("wallet_address")
        currency = request.get("currency")
        amount = request.get("amount")
        
        if wallet_address != wallet_info["wallet_address"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # For now, just return success - in production this would:
        # 1. Verify sufficient savings balance
        # 2. Create withdrawal transaction on blockchain
        # 3. Update savings records
        
        return {
            "success": True,
            "message": "Withdrawal functionality will be implemented with real blockchain integration",
            "wallet_address": wallet_address,
            "currency": currency,
            "amount": amount
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Authentication endpoints
@app.post("/api/auth/register")
async def register_user(request: RegisterRequest):
    """Register a new user with wallet address"""
    try:
        # Check if wallet address already exists
        existing_user = await db.users.find_one({"wallet_address": request.wallet_address})
        if existing_user:
            return {"success": False, "message": "Wallet address already registered"}
        
        # Create user ID
        user_id = str(uuid.uuid4())
        
        # Hash password (basic implementation - use proper hashing in production)
        import hashlib
        password_hash = hashlib.sha256(request.password.encode()).hexdigest()
        
        # Create user document
        user_doc = {
            "user_id": user_id,
            "wallet_address": request.wallet_address,
            "password_hash": password_hash,
            "created_at": datetime.now(),
            "deposit_balance": {"CRT": 0, "DOGE": 0, "TRX": 0, "USDC": 0},
            "winnings_balance": {"CRT": 0, "DOGE": 0, "TRX": 0, "USDC": 0},
            "savings_balance": {"CRT": 0, "DOGE": 0, "TRX": 0, "USDC": 0}
        }
        
        # Insert user
        await db.users.insert_one(user_doc)
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": user_id,
            "created_at": user_doc["created_at"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
async def login_user(request: LoginRequest):
    """Login user with wallet address and password"""
    try:
        # Find user by wallet address
        user = await db.users.find_one({"wallet_address": request.wallet_address})
        if not user:
            return {"success": False, "message": "Wallet address not found"}
        
        # Verify password using bcrypt (consistent with reset function)
        stored_password = user.get("password") or user.get("password_hash", "")
        
        # If it's old SHA256 format, still check it
        import hashlib
        sha256_hash = hashlib.sha256(request.password.encode()).hexdigest()
        
        # Try bcrypt first (new format), then fallback to SHA256 (old format)
        password_valid = False
        if stored_password:
            try:
                password_valid = pwd_context.verify(request.password, stored_password)
            except:
                # Fallback to SHA256 check for backwards compatibility
                password_valid = (stored_password == sha256_hash)
        
        if not password_valid:
            return {"success": False, "message": "Invalid password"}
        
        return {
            "success": True,
            "message": "Login successful",
            "user_id": user["user_id"],
            "created_at": user["created_at"].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Liquidity Pool Management System
# Test endpoint for simulating losing bets
@app.post("/api/test/simulate-bet-loss")
async def simulate_bet_loss(request: Dict[str, Any]):
    """Simulate a losing bet to test savings system"""
    try:
        wallet_address = request.get("wallet_address")
        currency = request.get("currency", "DOGE")
        amount = float(request.get("amount", 100))
        
        if not wallet_address:
            return {"success": False, "message": "wallet_address required"}
        
        # Find user
        user = await db.users.find_one({"wallet_address": wallet_address})
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Check if user has enough balance
        current_deposit = user.get("deposit_balance", {}).get(currency, 0)
        if current_deposit < amount:
            return {"success": False, "message": f"Insufficient {currency} balance"}
        
        # Simulate losing bet - Add to savings and liquidity
        current_savings = user.get("savings_balance", {}).get(currency, 0)
        new_savings = current_savings + amount
        
        # Add 10% to liquidity pool
        liquidity_contribution = amount * 0.1
        current_liquidity = user.get("liquidity_pool", {}).get(currency, 0)
        new_liquidity = current_liquidity + liquidity_contribution
        
        # Deduct from deposit balance
        new_deposit = current_deposit - amount
        
        # Update database
        await db.users.update_one(
            {"wallet_address": wallet_address},
            {"$set": {
                f"savings_balance.{currency}": new_savings,
                f"liquidity_pool.{currency}": new_liquidity,
                f"deposit_balance.{currency}": new_deposit
            }}
        )
        
        # Record the simulated bet
        bet_record = {
            "game_id": f"test_{uuid.uuid4().hex[:8]}",
            "wallet_address": wallet_address,
            "game_type": "Test Loss",
            "bet_amount": amount,
            "currency": currency,
            "network": "test",
            "result": "loss",
            "payout": 0,
            "status": "completed",
            "timestamp": datetime.utcnow()
        }
        await db.game_bets.insert_one(bet_record)
        
        return {
            "success": True,
            "message": f"Simulated loss of {amount} {currency}",
            "savings_added": amount,
            "liquidity_added": liquidity_contribution,
            "new_savings_balance": new_savings,
            "new_liquidity_balance": new_liquidity,
            "new_deposit_balance": new_deposit
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/test/reset-password")
async def reset_password(request: Dict[str, Any]):
    """Reset password for a wallet address (test endpoint)"""
    try:
        wallet_address = request.get("wallet_address")
        new_password = request.get("new_password")
        
        if not wallet_address or not new_password:
            return {"success": False, "message": "wallet_address and new_password required"}
        
        # Hash the new password
        hashed_password = pwd_context.hash(new_password)
        
        # Update the password in database
        result = await db.users.update_one(
            {"wallet_address": wallet_address},
            {"$set": {"password": hashed_password}}
        )
        
        if result.modified_count > 0:
            return {
                "success": True,
                "message": f"Password updated for {wallet_address}",
                "new_password": new_password
            }
        else:
            return {"success": False, "message": "User not found or password not changed"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# Add 50% of savings to liquidity pool as requested
@app.post("/api/test/add-liquidity-from-savings")
async def add_liquidity_from_savings(request: Dict[str, Any]):
    """Add 50% of savings to liquidity pool as requested by user"""
    try:
        wallet_address = request.get("wallet_address")
        percentage = float(request.get("percentage", 50))  # Default 50%
        
        if not wallet_address:
            return {"success": False, "message": "wallet_address required"}
        
        # Get user's current savings
        user = await db.users.find_one({"wallet_address": wallet_address})
        if not user:
            return {"success": False, "message": "User not found"}
        
        savings = user.get("savings_balance", {})
        current_liquidity = user.get("liquidity_pool", {})
        
        # Calculate liquidity to add (50% of savings)
        liquidity_to_add = {}
        for currency, amount in savings.items():
            if amount > 0:
                liquidity_contribution = amount * (percentage / 100)
                current_currency_liquidity = current_liquidity.get(currency, 0)
                liquidity_to_add[currency] = current_currency_liquidity + liquidity_contribution
        
        # Update liquidity pool
        update_dict = {}
        for currency, new_amount in liquidity_to_add.items():
            update_dict[f"liquidity_pool.{currency}"] = new_amount
        
        if update_dict:
            await db.users.update_one(
                {"wallet_address": wallet_address},
                {"$set": update_dict}
            )
        
        return {
            "success": True,
            "message": f"Added {percentage}% of savings to liquidity pool",
            "liquidity_added": liquidity_to_add,
            "original_savings": savings
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Auto-play system for AI betting
@app.post("/api/autoplay/start")
async def start_autoplay(request: Dict[str, Any]):
    """Start AI auto-play betting system"""
    try:
        wallet_address = request.get("wallet_address")
        settings = request.get("settings", {})
        
        if not wallet_address:
            return {"success": False, "message": "wallet_address required"}
        
        # Default auto-play settings
        autoplay_settings = {
            "wallet_address": wallet_address,
            "games": settings.get("games", ["Slot Machine", "Dice", "Roulette"]),
            "bet_amounts": {
                "CRT": settings.get("crt_bet", 100),
                "DOGE": settings.get("doge_bet", 10),
                "TRX": settings.get("trx_bet", 50)
            },
            "currency": settings.get("currency", "CRT"),
            "max_loss": settings.get("max_loss", 10000),  # Stop after losing this much
            "max_duration": settings.get("max_duration", 8),  # Hours
            "bet_frequency": settings.get("bet_frequency", 5),  # Seconds between bets
            "status": "active",
            "started_at": datetime.utcnow(),
            "total_bets": 0,
            "total_winnings": 0,
            "total_losses": 0,
            "last_bet_at": None
        }
        
        # Store autoplay session
        await db.autoplay_sessions.insert_one(autoplay_settings)
        
        return {
            "success": True,
            "message": "Auto-play started! AI will bet for you automatically.",
            "settings": autoplay_settings,
            "session_id": str(autoplay_settings["_id"]) if "_id" in autoplay_settings else "new"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/autoplay/stop")
async def stop_autoplay(request: Dict[str, Any]):
    """Stop AI auto-play betting system"""
    try:
        wallet_address = request.get("wallet_address")
        
        if not wallet_address:
            return {"success": False, "message": "wallet_address required"}
        
        # Update all active sessions to stopped
        result = await db.autoplay_sessions.update_many(
            {"wallet_address": wallet_address, "status": "active"},
            {"$set": {"status": "stopped", "stopped_at": datetime.utcnow()}}
        )
        
        return {
            "success": True,
            "message": "Auto-play stopped",
            "sessions_stopped": result.modified_count
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/autoplay/status/{wallet_address}")
async def get_autoplay_status(wallet_address: str):
    """Get current auto-play status"""
    try:
        # Get active sessions
        active_sessions = await db.autoplay_sessions.find(
            {"wallet_address": wallet_address, "status": "active"}
        ).to_list(10)
        
        return {
            "success": True,
            "active_sessions": len(active_sessions),
            "sessions": active_sessions
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/autoplay/process-bets")
async def process_autoplay_bets():
    """Process auto-play bets for all active sessions (called by scheduler)"""
    try:
        # Get all active autoplay sessions
        active_sessions = await db.autoplay_sessions.find({"status": "active"}).to_list(100)
        
        processed_count = 0
        
        for session in active_sessions:
            try:
                # Check if session should continue
                if not await _should_continue_autoplay(session):
                    await db.autoplay_sessions.update_one(
                        {"_id": session["_id"]},
                        {"$set": {"status": "completed", "stopped_at": datetime.utcnow()}}
                    )
                    continue
                
                # Check if it's time for next bet
                if await _is_time_for_next_bet(session):
                    # Place an AI bet
                    bet_result = await _place_ai_bet(session)
                    if bet_result["success"]:
                        # Update session stats
                        await _update_session_stats(session["_id"], bet_result)
                        processed_count += 1
            
            except Exception as e:
                print(f"Error processing autoplay session {session['_id']}: {e}")
                continue
        
        return {
            "success": True,
            "processed_bets": processed_count,
            "message": f"Processed {processed_count} auto-play bets"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

async def _should_continue_autoplay(session):
    """Check if autoplay session should continue"""
    try:
        # Check time limit
        started_at = session["started_at"]
        max_duration_hours = session["max_duration"]
        elapsed_hours = (datetime.utcnow() - started_at).total_seconds() / 3600
        
        if elapsed_hours >= max_duration_hours:
            return False
        
        # Check loss limit
        max_loss = session["max_loss"]
        total_losses = session.get("total_losses", 0)
        
        if total_losses >= max_loss:
            return False
        
        # Check if user has sufficient balance
        user = await db.users.find_one({"wallet_address": session["wallet_address"]})
        if not user:
            return False
        
        currency = session["currency"]
        bet_amount = session["bet_amounts"][currency]
        current_balance = user.get("deposit_balance", {}).get(currency, 0)
        
        if current_balance < bet_amount:
            return False
        
        return True
        
    except Exception as e:
        print(f"Error checking autoplay continuation: {e}")
        return False

async def _is_time_for_next_bet(session):
    """Check if it's time for the next bet"""
    try:
        last_bet_at = session.get("last_bet_at")
        bet_frequency = session["bet_frequency"]  # seconds
        
        if not last_bet_at:
            return True  # First bet
        
        elapsed_seconds = (datetime.utcnow() - last_bet_at).total_seconds()
        return elapsed_seconds >= bet_frequency
        
    except Exception as e:
        return True

async def _place_ai_bet(session):
    """Place an AI bet for autoplay session"""
    try:
        import random
        
        # Randomly select game
        games = session["games"]
        selected_game = random.choice(games)
        
        # Get bet settings
        currency = session["currency"]
        bet_amount = session["bet_amounts"][currency]
        wallet_address = session["wallet_address"]
        
        # Place the bet using existing betting system
        bet_data = BetRequest(
            wallet_address=wallet_address,
            game_type=selected_game,
            bet_amount=bet_amount,
            currency=currency,
            network="autoplay"
        )
        
        # Use existing place_bet function
        result = await place_bet(bet_data)
        
        return {
            "success": result.get("success", False),
            "game": selected_game,
            "amount": bet_amount,
            "currency": currency,
            "result": result.get("result", "unknown"),
            "payout": result.get("payout", 0),
            "message": result.get("message", "")
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

async def _update_session_stats(session_id, bet_result):
    """Update autoplay session statistics"""
    try:
        update_data = {
            "last_bet_at": datetime.utcnow(),
            "$inc": {"total_bets": 1}
        }
        
        if bet_result["result"] == "win":
            update_data["$inc"]["total_winnings"] = bet_result["payout"]
        else:
            update_data["$inc"]["total_losses"] = bet_result["amount"]
        
        await db.autoplay_sessions.update_one(
            {"_id": session_id},
            update_data
        )
        
    except Exception as e:
        print(f"Error updating session stats: {e}")

# Simulate real escrow for demonstration
@app.post("/api/test/simulate-escrow")
async def simulate_escrow(request: Dict[str, Any]):
    """Simulate putting real tokens in escrow (SIMULATION ONLY)"""
    try:
        wallet_address = request.get("wallet_address")
        escrow_amount = float(request.get("escrow_amount", 5000000))
        currency = request.get("currency", "CRT")
        
        if not wallet_address:
            return {"success": False, "message": "wallet_address required"}
        
        # Check if user has enough real tokens (from blockchain)
        if currency == "CRT":
            real_balance_response = await crt_manager.get_crt_balance(wallet_address)
            real_balance = real_balance_response.get("crt_balance", 0)
            
            if real_balance < escrow_amount:
                return {
                    "success": False, 
                    "message": f"Insufficient real {currency} balance. You have {real_balance}, trying to escrow {escrow_amount}",
                    "real_balance": real_balance
                }
        
        # Simulate escrow by updating casino balances to represent real holdings
        user = await db.users.find_one({"wallet_address": wallet_address})
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Clear previous balances and set real escrow amounts
        escrow_balances = {
            "deposit_balance": {currency: escrow_amount},
            "escrow_balance": {currency: escrow_amount},  # Track what's in escrow
            "escrow_status": "simulated",
            "escrow_timestamp": datetime.utcnow(),
            "real_token_backing": True
        }
        
        # Update user with escrow simulation
        await db.users.update_one(
            {"wallet_address": wallet_address},
            {"$set": escrow_balances}
        )
        
        return {
            "success": True,
            "message": f"SIMULATED: {escrow_amount:,.0f} {currency} in escrow",
            "escrow_amount": escrow_amount,
            "currency": currency,
            "usd_value": escrow_amount * 0.15,  # CRT price
            "note": "⚠️ SIMULATION ONLY - No real tokens were moved. This represents what real escrow would look like.",
            "real_balance_verified": real_balance if currency == "CRT" else "N/A"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/escrow/status/{wallet_address}")
async def get_escrow_status(wallet_address: str):
    """Get escrow status and breakdown"""
    try:
        user = await db.users.find_one({"wallet_address": wallet_address})
        if not user:
            return {"success": False, "message": "User not found"}
        
        escrow_balance = user.get("escrow_balance", {})
        real_backing = user.get("real_token_backing", False)
        escrow_status = user.get("escrow_status", "none")
        
        total_escrow_usd = 0
        escrow_breakdown = {}
        
        prices = {"CRT": 0.15, "DOGE": 0.08, "TRX": 0.015, "USDC": 1.0}
        
        for currency, amount in escrow_balance.items():
            if amount > 0:
                usd_value = amount * prices.get(currency, 0)
                total_escrow_usd += usd_value
                escrow_breakdown[currency] = {
                    "amount": amount,
                    "usd_value": usd_value
                }
        
        return {
            "success": True,
            "wallet_address": wallet_address,
            "escrow_status": escrow_status,
            "real_token_backing": real_backing,
            "total_escrow_usd": total_escrow_usd,
            "escrow_breakdown": escrow_breakdown,
            "note": "SIMULATION" if escrow_status == "simulated" else "REAL ESCROW"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Generate unique casino deposit address for user
@app.post("/api/deposit/create-address")
async def create_casino_deposit_address(request: Dict[str, Any]):
    """Create a unique casino deposit address separate from user's main wallet"""
    try:
        wallet_address = request.get("wallet_address")
        
        if not wallet_address:
            return {"success": False, "message": "wallet_address required"}
        
        # Generate a unique deposit address for this user
        # In production, this would be a derived address or managed wallet
        # For now, we'll create a unique identifier
        import hashlib
        deposit_suffix = hashlib.md5(f"{wallet_address}_casino_deposit".encode()).hexdigest()[:8]
        casino_deposit_address = f"CASINO_{deposit_suffix}_{wallet_address[:8]}"
        
        # Store the mapping
        user = await db.users.find_one({"wallet_address": wallet_address})
        if not user:
            return {"success": False, "message": "User not found"}
        
        await db.users.update_one(
            {"wallet_address": wallet_address},
            {"$set": {
                "casino_deposit_address": casino_deposit_address,
                "deposit_address_created": datetime.utcnow(),
                "separate_deposit_mode": True
            }}
        )
        
        return {
            "success": True,
            "casino_deposit_address": casino_deposit_address,
            "main_wallet": wallet_address,
            "note": "⚠️ DEMO: In production, this would be a real Solana address. For now, use the manual credit system.",
            "instructions": [
                "1. Send CRT to your main wallet as normal",
                "2. Use /api/deposit/manual-credit to credit specific amounts to casino",
                "3. This prevents accidental crediting of all deposits"
            ]
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/deposit/manual-credit")
async def manual_credit_deposit(request: Dict[str, Any]):
    """Manually credit a specific amount as casino deposit (user controlled)"""
    try:
        wallet_address = request.get("wallet_address")
        amount = float(request.get("amount", 0))
        currency = request.get("currency", "CRT")
        
        if not wallet_address or amount <= 0:
            return {"success": False, "message": "wallet_address and positive amount required"}
        
        # Verify user has this amount in their real balance
        if currency == "CRT":
            real_balance_response = await crt_manager.get_crt_balance(wallet_address)
            if not real_balance_response.get("success"):
                return {"success": False, "message": "Could not verify real balance"}
            
            real_balance = real_balance_response.get("crt_balance", 0)
            if real_balance < amount:
                return {
                    "success": False,
                    "message": f"Insufficient real {currency} balance. You have {real_balance:,.0f}, trying to credit {amount:,.0f}",
                    "real_balance": real_balance
                }
        
        # Credit to casino account
        user = await db.users.find_one({"wallet_address": wallet_address})
        if not user:
            return {"success": False, "message": "User not found"}
        
        current_casino_balance = user.get("deposit_balance", {}).get(currency, 0)
        new_casino_balance = current_casino_balance + amount
        
        await db.users.update_one(
            {"wallet_address": wallet_address},
            {"$set": {f"deposit_balance.{currency}": new_casino_balance}}
        )
        
        # Record transaction
        credit_record = {
            "wallet_address": wallet_address,
            "type": "manual_credit",
            "currency": currency,
            "amount": amount,
            "casino_balance_before": current_casino_balance,
            "casino_balance_after": new_casino_balance,
            "timestamp": datetime.utcnow(),
            "status": "completed",
            "source": "user_controlled"
        }
        
        await db.transactions.insert_one(credit_record)
        
        return {
            "success": True,
            "message": f"✅ {amount:,.0f} {currency} credited to casino account!",
            "amount_credited": amount,
            "new_casino_balance": new_casino_balance,
            "usd_value": amount * 0.15 if currency == "CRT" else 0,
            "note": "This amount is now available for gaming. Your main wallet balance remains unchanged.",
            "transaction_id": str(credit_record.get("_id", "unknown"))
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Real CRT deposit system
@app.get("/api/deposit/address/{wallet_address}")
async def get_deposit_address(wallet_address: str):
    """Get deposit address for receiving real CRT tokens"""
    try:
        # For now, we'll use the user's own address as deposit address
        # In production, casino would have dedicated deposit addresses
        
        # Verify the address format
        validation = await crt_manager.validate_address(wallet_address)
        if not validation.get("valid"):
            return {"success": False, "message": "Invalid Solana address format"}
        
        # Check if user exists
        user = await db.users.find_one({"wallet_address": wallet_address})
        if not user:
            return {"success": False, "message": "User not found. Please register first."}
        
        return {
            "success": True,
            "deposit_address": wallet_address,  # Your own address for now
            "supported_tokens": ["CRT"],
            "crt_mint_address": crt_manager.crt_mint,
            "network": "Solana Mainnet",
            "note": "Send CRT tokens to this address. They will be automatically detected and credited to your casino account.",
            "processing_time": "1-2 minutes after blockchain confirmation"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/deposit/check")
async def check_for_deposits(request: Dict[str, Any]):
    """Check for new CRT deposits and credit user accounts"""
    try:
        wallet_address = request.get("wallet_address")
        
        if not wallet_address:
            return {"success": False, "message": "wallet_address required"}
        
        # Get current real CRT balance from blockchain
        current_balance_response = await crt_manager.get_crt_balance(wallet_address)
        if not current_balance_response.get("success"):
            return {"success": False, "message": "Could not check blockchain balance"}
        
        current_real_balance = current_balance_response.get("crt_balance", 0)
        
        # Get last recorded balance from our database
        user = await db.users.find_one({"wallet_address": wallet_address})
        if not user:
            return {"success": False, "message": "User not found"}
        
        last_recorded_balance = user.get("last_blockchain_balance", {}).get("CRT", 0)
        
        # Calculate deposit amount (difference)
        deposit_amount = current_real_balance - last_recorded_balance
        
        if deposit_amount > 0:
            # New deposit detected!
            
            # Update casino deposit balance
            current_casino_balance = user.get("deposit_balance", {}).get("CRT", 0)
            new_casino_balance = current_casino_balance + deposit_amount
            
            # Update database
            await db.users.update_one(
                {"wallet_address": wallet_address},
                {"$set": {
                    f"deposit_balance.CRT": new_casino_balance,
                    f"last_blockchain_balance.CRT": current_real_balance,
                    "last_deposit_check": datetime.utcnow()
                }}
            )
            
            # Record the deposit transaction
            deposit_record = {
                "wallet_address": wallet_address,
                "type": "real_deposit",
                "currency": "CRT",
                "amount": deposit_amount,
                "blockchain_balance_before": last_recorded_balance,
                "blockchain_balance_after": current_real_balance,
                "casino_balance_after": new_casino_balance,
                "timestamp": datetime.utcnow(),
                "status": "completed",
                "source": "external_transfer"
            }
            
            await db.transactions.insert_one(deposit_record)
            
            return {
                "success": True,
                "message": f"🎉 REAL DEPOSIT DETECTED! {deposit_amount:,.0f} CRT credited to your casino account!",
                "deposit_amount": deposit_amount,
                "new_casino_balance": new_casino_balance,
                "blockchain_balance": current_real_balance,
                "usd_value": deposit_amount * 0.15,
                "transaction_id": str(deposit_record.get("_id", "unknown"))
            }
        else:
            return {
                "success": True,
                "message": "No new deposits detected",
                "current_blockchain_balance": current_real_balance,
                "last_recorded_balance": last_recorded_balance,
                "difference": deposit_amount
            }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/deposit/auto-monitor")
async def start_deposit_monitoring(request: Dict[str, Any]):
    """Start automatic deposit monitoring for a user"""
    try:
        wallet_address = request.get("wallet_address")
        
        if not wallet_address:
            return {"success": False, "message": "wallet_address required"}
        
        # Initialize monitoring by setting baseline balance
        balance_response = await crt_manager.get_crt_balance(wallet_address)
        if not balance_response.get("success"):
            return {"success": False, "message": "Could not get initial balance"}
        
        initial_balance = balance_response.get("crt_balance", 0)
        
        # Update user with initial balance
        await db.users.update_one(
            {"wallet_address": wallet_address},
            {"$set": {
                f"last_blockchain_balance.CRT": initial_balance,
                "deposit_monitoring": True,
                "monitoring_started": datetime.utcnow()
            }}
        )
        
        return {
            "success": True,
            "message": "✅ Deposit monitoring activated! Send CRT tokens and they'll be automatically detected.",
            "initial_balance": initial_balance,
            "deposit_address": wallet_address,
            "note": "Use /api/deposit/check to manually check for new deposits, or they'll be detected automatically."
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/liquidity-pool/{wallet_address}")
async def get_liquidity_pool(wallet_address: str):
    """Get user's liquidity pool status"""
    try:
        # Find user
        user = await db.users.find_one({"wallet_address": wallet_address})
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Get or create liquidity pool
        liquidity_pool = user.get("liquidity_pool", {
            "CRT": 0, "DOGE": 0, "TRX": 0, "USDC": 0,
            "total_contributed": 0,
            "created_at": datetime.now().isoformat()
        })
        
        # Calculate total liquidity value in USD (mock prices for demo)
        mock_prices = {"CRT": 0.15, "DOGE": 0.08, "TRX": 0.12, "USDC": 1.0}
        total_liquidity_usd = sum(
            liquidity_pool.get(currency, 0) * mock_prices[currency] 
            for currency in mock_prices
        )
        
        return {
            "success": True,
            "liquidity_pool": liquidity_pool,
            "total_liquidity_usd": round(total_liquidity_usd, 2),
            "withdrawal_limits": {
                currency: min(balance * 0.1, liquidity_pool.get(currency, 0)) 
                for currency, balance in liquidity_pool.items() 
                if currency in mock_prices
            }
        }
        
    except Exception as e:
        print(f"Error in get_liquidity_pool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/liquidity-pool/contribute")
async def contribute_to_liquidity_pool(request: SessionEndRequest):
    """Automatically contribute 10% of savings to liquidity pool after session"""
    try:
        # Find user
        user = await db.users.find_one({"wallet_address": request.wallet_address})
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Get current savings balance
        savings_balance = user.get("savings_balance", {"CRT": 0, "DOGE": 0, "TRX": 0, "USDC": 0})
        
        # Calculate 10% contribution from each currency
        contributions = {}
        total_contributed = 0
        
        for currency, balance in savings_balance.items():
            if balance > 0:
                contribution = balance * 0.1  # 10% of savings
                contributions[currency] = contribution
                total_contributed += contribution
        
        if total_contributed == 0:
            return {"success": False, "message": "No savings to contribute"}
        
        # Get current liquidity pool
        current_pool = user.get("liquidity_pool", {"CRT": 0, "DOGE": 0, "TRX": 0, "USDC": 0})
        
        # Update liquidity pool and reduce savings
        updates = {}
        for currency, contribution in contributions.items():
            # Add to liquidity pool
            updates[f"liquidity_pool.{currency}"] = current_pool.get(currency, 0) + contribution
            # Reduce from savings (90% remains)
            updates[f"savings_balance.{currency}"] = savings_balance[currency] - contribution
        
        # Update total contributed tracking
        updates["liquidity_pool.total_contributed"] = current_pool.get("total_contributed", 0) + total_contributed
        updates["liquidity_pool.last_contribution"] = datetime.now().isoformat()
        
        await db.users.update_one(
            {"wallet_address": request.wallet_address},
            {"$set": updates}
        )
        
        # Record the contribution transaction
        transaction = {
            "transaction_id": str(uuid.uuid4()),
            "wallet_address": request.wallet_address,
            "type": "liquidity_contribution",
            "contributions": contributions,
            "session_duration": request.session_duration,
            "games_played": request.games_played,
            "timestamp": datetime.now(),
            "status": "completed"
        }
        
        await db.transactions.insert_one(transaction)
        
        return {
            "success": True,
            "message": f"Contributed to liquidity pool",
            "contributions": contributions,
            "total_contributed": round(total_contributed, 4),
            "transaction_id": transaction["transaction_id"]
        }
        
    except Exception as e:
        print(f"Error in contribute_to_liquidity_pool: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/api/conversion/rates")
async def get_conversion_rates():
    """Get real-time conversion rates for supported cryptocurrencies"""
    cache_key = "conversion_rates"
    
    # Check cache first
    if redis_client:
        try:
            cached_rates = redis_client.get(cache_key)
            if cached_rates:
                return {"success": True, "rates": json.loads(cached_rates), "source": "cache"}
        except Exception as e:
            print(f"Redis cache error: {e}")
    
    try:
        # Get current prices for our supported currencies
        # Map our internal names to CoinGecko IDs
        coin_mapping = {
            'DOGE': 'dogecoin',
            'TRX': 'tron',
            'USDC': 'usd-coin'
            # CRT would need to be mapped to actual token ID when available
        }
        
        prices = cg.get_price(
            ids=list(coin_mapping.values()),
            vs_currencies='usd',
            include_24hr_change=True
        )
        
        # Calculate conversion rates between currencies
        rates = {}
        currency_prices = {}
        
        # Store USD prices
        for internal_name, coingecko_id in coin_mapping.items():
            if coingecko_id in prices:
                currency_prices[internal_name] = prices[coingecko_id]['usd']
        
        # Add mock CRT price (replace with real price when available)
        currency_prices['CRT'] = 0.15  # Mock price in USD
        
        # Calculate all conversion pairs
        currencies = list(currency_prices.keys())
        for from_currency in currencies:
            for to_currency in currencies:
                if from_currency != to_currency:
                    rate_key = f"{from_currency}_{to_currency}"
                    if currency_prices[from_currency] > 0:
                        rates[rate_key] = currency_prices[to_currency] / currency_prices[from_currency]
        
        result = {
            "success": True,
            "rates": rates,
            "prices_usd": currency_prices,
            "last_updated": datetime.now().isoformat(),
            "source": "coingecko"
        }
        
        # Cache for 30 seconds
        if redis_client:
            try:
                redis_client.setex(cache_key, 30, json.dumps(result))
            except Exception as e:
                print(f"Redis cache set error: {e}")
        
        return result
        
    except Exception as e:
        # Return fallback rates if API fails
        fallback_rates = {
            "CRT_DOGE": 21.5, "CRT_TRX": 9.8, "CRT_USDC": 0.15,
            "DOGE_CRT": 0.047, "DOGE_TRX": 0.456, "DOGE_USDC": 0.007,
            "TRX_CRT": 0.102, "TRX_DOGE": 2.19, "TRX_USDC": 0.015,
            "USDC_CRT": 6.67, "USDC_DOGE": 142.86, "USDC_TRX": 66.67
        }
        
        return {
            "success": True,
            "rates": fallback_rates,
            "source": "fallback",
            "error": str(e)
        }

@app.get("/api/crypto/price/{currency}")
async def get_crypto_price(currency: str):
    """Get current price for a specific cryptocurrency"""
    cache_key = f"price_{currency.lower()}"
    
    # Check cache first
    if redis_client:
        try:
            cached_price = redis_client.get(cache_key)
            if cached_price:
                return {"success": True, "data": json.loads(cached_price)}
        except Exception as e:
            print(f"Redis cache error: {e}")
    
    try:
        # Map currency to CoinGecko ID
        coin_mapping = {
            'DOGE': 'dogecoin',
            'TRX': 'tron', 
            'USDC': 'usd-coin',
            'BTC': 'bitcoin',
            'ETH': 'ethereum'
        }
        
        if currency.upper() == 'CRT':
            # Mock CRT data (replace with real data when available)
            result = {
                "currency": "CRT",
                "price_usd": 0.15,
                "price_change_24h": 2.5,
                "market_cap": 15000000,
                "volume_24h": 500000,
                "last_updated": datetime.now().isoformat()
            }
        else:
            coingecko_id = coin_mapping.get(currency.upper())
            if not coingecko_id:
                raise HTTPException(status_code=404, detail="Currency not supported")
            
            data = cg.get_price(
                ids=coingecko_id,
                vs_currencies='usd',
                include_24hr_change=True,
                include_market_cap=True,
                include_24hr_vol=True
            )
            
            if coingecko_id not in data:
                raise HTTPException(status_code=404, detail="Currency data not found")
            
            result = {
                "currency": currency.upper(),
                "price_usd": data[coingecko_id]['usd'],
                "price_change_24h": data[coingecko_id].get('usd_24h_change', 0),
                "market_cap": data[coingecko_id].get('usd_market_cap', 0),
                "volume_24h": data[coingecko_id].get('usd_24h_vol', 0),
                "last_updated": datetime.now().isoformat()
            }
        
        # Cache for 30 seconds
        if redis_client:
            try:
                redis_client.setex(cache_key, 30, json.dumps(result))
            except Exception as e:
                print(f"Redis cache set error: {e}")
        
        return {"success": True, "data": result}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch price data: {str(e)}")


# Test endpoint to add savings (for demo purposes)
@app.post("/api/test/add-savings")
async def add_test_savings(request: Dict[str, Any]):
    """Add test savings to user account"""
    try:
        wallet_address = request.get("wallet_address")
        savings = request.get("savings", {"CRT": 100, "DOGE": 50, "TRX": 80, "USDC": 20})
        
        await db.users.update_one(
            {"wallet_address": wallet_address},
            {"$set": {"savings_balance": savings}}
        )
        
        return {"success": True, "message": "Test savings added", "savings": savings}
        
    except Exception as e:
        return {"success": False, "message": str(e)}
@api_router.websocket("/ws/wallet/{wallet_address}")
async def websocket_wallet_monitor(websocket: WebSocket, wallet_address: str):
    """WebSocket endpoint for real-time wallet monitoring"""
    await websocket.accept()
    
    if wallet_address not in active_connections:
        active_connections[wallet_address] = []
    active_connections[wallet_address].append(websocket)
    
    try:
        # Send initial wallet info
        wallet_record = await db.user_wallets.find_one({"wallet_address": wallet_address})
        if not wallet_record:
            # Create new wallet record
            new_wallet = UserWallet(wallet_address=wallet_address)
            await db.user_wallets.insert_one(new_wallet.dict())
            wallet_record = new_wallet.dict()
        
        await websocket.send_text(json.dumps({
            "type": "wallet_update",
            "wallet": wallet_address,
            "data": {
                "success": True,
                "wallet": wallet_record
            }
        }))
        
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "refresh_wallet":
                # Refresh and send updated wallet info
                updated_wallet = await db.user_wallets.find_one({"wallet_address": wallet_address})
                await websocket.send_text(json.dumps({
                    "type": "wallet_update", 
                    "wallet": wallet_address,
                    "data": {
                        "success": True,
                        "wallet": updated_wallet
                    }
                }))
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Remove connection on disconnect
        if wallet_address in active_connections:
            active_connections[wallet_address].remove(websocket)
            if not active_connections[wallet_address]:
                del active_connections[wallet_address]

# Legacy endpoints
@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
