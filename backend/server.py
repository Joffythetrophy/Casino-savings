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

# Import blockchain managers
from blockchain.solana_manager import SolanaManager, SPLTokenManager, CRTTokenManager
from blockchain.tron_manager import TronManager, TronTransactionManager
from blockchain.doge_manager import DogeManager, DogeTransactionManager
from auth.wallet_auth import WalletAuthManager, get_authenticated_wallet, ChallengeRequest, VerifyRequest

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

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

# Enhanced wallet management endpoints
@api_router.get("/wallet/{wallet_address}")
async def get_wallet_info(wallet_address: str, wallet_info: Dict = Depends(get_authenticated_wallet)):
    """Get comprehensive wallet information"""
    try:
        if wallet_address != wallet_info["wallet_address"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Get or create wallet record
        wallet_record = await db.user_wallets.find_one({"wallet_address": wallet_address})
        
        if not wallet_record:
            # Create new wallet record
            new_wallet = UserWallet(wallet_address=wallet_address)
            await db.user_wallets.insert_one(new_wallet.dict())
            wallet_record = new_wallet.dict()
        
        return {
            "success": True,
            "wallet": wallet_record
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/wallet/deposit")
async def deposit_funds(request: Dict[str, Any], wallet_info: Dict = Depends(get_authenticated_wallet)):
    """Deposit funds to deposit wallet"""
    try:
        wallet_address = request.get("wallet_address")
        currency = request.get("currency")
        amount = float(request.get("amount", 0))
        
        if wallet_address != wallet_info["wallet_address"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid amount")
        
        # Update wallet record
        await db.user_wallets.update_one(
            {"wallet_address": wallet_address},
            {
                "$inc": {f"deposit_balance.{currency}": amount},
                "$set": {"last_updated": datetime.utcnow()}
            },
            upsert=True
        )
        
        # Record transaction
        transaction_record = {
            "wallet_address": wallet_address,
            "type": "deposit",
            "currency": currency,
            "amount": amount,
            "timestamp": datetime.utcnow(),
            "status": "completed"
        }
        await db.wallet_transactions.insert_one(transaction_record)
        
        return {
            "success": True,
            "message": f"Deposited {amount} {currency}",
            "transaction_id": str(transaction_record["_id"]) if "_id" in transaction_record else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/wallet/withdraw")
async def withdraw_funds(request: Dict[str, Any], wallet_info: Dict = Depends(get_authenticated_wallet)):
    """Withdraw funds from winnings or savings wallet"""
    try:
        wallet_address = request.get("wallet_address")
        wallet_type = request.get("wallet_type")  # "winnings" or "savings"
        currency = request.get("currency")
        amount = float(request.get("amount", 0))
        
        if wallet_address != wallet_info["wallet_address"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid amount")
        
        # Get current wallet
        wallet_record = await db.user_wallets.find_one({"wallet_address": wallet_address})
        if not wallet_record:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        # Check balance
        current_balance = wallet_record.get(f"{wallet_type}_balance", {}).get(currency, 0)
        if current_balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # Update wallet record
        await db.user_wallets.update_one(
            {"wallet_address": wallet_address},
            {
                "$inc": {f"{wallet_type}_balance.{currency}": -amount},
                "$set": {"last_updated": datetime.utcnow()}
            }
        )
        
        # Record transaction
        transaction_record = {
            "wallet_address": wallet_address,
            "type": f"withdraw_{wallet_type}",
            "currency": currency,
            "amount": amount,
            "timestamp": datetime.utcnow(),
            "status": "completed"
        }
        await db.wallet_transactions.insert_one(transaction_record)
        
        return {
            "success": True,
            "message": f"Withdrew {amount} {currency} from {wallet_type}",
            "transaction_id": str(transaction_record["_id"]) if "_id" in transaction_record else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/wallet/convert")
async def convert_crypto(request: Dict[str, Any], wallet_info: Dict = Depends(get_authenticated_wallet)):
    """Convert cryptocurrency within deposit wallet"""
    try:
        wallet_address = request.get("wallet_address")
        from_currency = request.get("from_currency")
        to_currency = request.get("to_currency")
        amount = float(request.get("amount", 0))
        
        if wallet_address != wallet_info["wallet_address"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid amount")
        
        # Mock conversion rates - in production these would be live rates
        conversion_rates = {
            "CRT_DOGE": 21.5, "CRT_TRX": 9.8,
            "DOGE_CRT": 0.047, "DOGE_TRX": 0.456,
            "TRX_CRT": 0.102, "TRX_DOGE": 2.19
        }
        
        rate_key = f"{from_currency}_{to_currency}"
        if rate_key not in conversion_rates:
            raise HTTPException(status_code=400, detail="Conversion not supported")
        
        converted_amount = amount * conversion_rates[rate_key]
        
        # Get current wallet
        wallet_record = await db.user_wallets.find_one({"wallet_address": wallet_address})
        if not wallet_record:
            raise HTTPException(status_code=404, detail="Wallet not found")
        
        # Check balance
        current_balance = wallet_record.get("deposit_balance", {}).get(from_currency, 0)
        if current_balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # Update wallet record
        await db.user_wallets.update_one(
            {"wallet_address": wallet_address},
            {
                "$inc": {
                    f"deposit_balance.{from_currency}": -amount,
                    f"deposit_balance.{to_currency}": converted_amount
                },
                "$set": {"last_updated": datetime.utcnow()}
            }
        )
        
        # Record transaction
        transaction_record = {
            "wallet_address": wallet_address,
            "type": "conversion",
            "from_currency": from_currency,
            "to_currency": to_currency,
            "from_amount": amount,
            "to_amount": converted_amount,
            "rate": conversion_rates[rate_key],
            "timestamp": datetime.utcnow(),
            "status": "completed"
        }
        await db.wallet_transactions.insert_one(transaction_record)
        
        return {
            "success": True,
            "message": f"Converted {amount} {from_currency} to {converted_amount:.4f} {to_currency}",
            "converted_amount": converted_amount,
            "rate": conversion_rates[rate_key]
        }
        
    except Exception as e:
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
        
        # Insert into database
        await db.game_bets.insert_one(bet_record)
        
        # If it's a loss, it automatically becomes savings (no additional record needed)
        savings_contribution = bet.bet_amount if not is_winner else 0
        
        return {
            "success": True,
            "game_id": game_id,
            "bet_amount": bet.bet_amount,
            "currency": bet.currency,
            "result": "win" if is_winner else "loss",
            "payout": payout,
            "savings_contribution": savings_contribution,
            "message": f"Saved {savings_contribution} {bet.currency} to your vault!" if not is_winner else f"Won {payout} {bet.currency}!"
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

# WebSocket endpoint for real-time wallet updates
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
