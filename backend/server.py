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

# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class UserBalance(BaseModel):
    wallet_address: str
    network: str
    currency: str
    balance: float
    usd_value: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)

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

# Balance endpoints
@api_router.get("/balance/{wallet_address}")
async def get_multi_chain_balance(wallet_address: str, wallet_info: Dict = Depends(get_authenticated_wallet)):
    """Get balance across all supported networks"""
    balances = {}
    
    # Get CRT balance (Solana)
    try:
        crt_balance = await crt_manager.get_crt_balance(wallet_address)
        balances["CRT"] = crt_balance
    except Exception as e:
        balances["CRT"] = {"error": str(e), "balance": 0.0}
    
    # Get DOGE balance
    try:
        doge_balance = await doge_manager.get_balance(wallet_address)
        balances["DOGE"] = doge_balance
    except Exception as e:
        balances["DOGE"] = {"error": str(e), "balance": 0.0}
    
    # Get TRX balance
    try:
        trx_balance = await tron_tx_manager.get_trx_balance(wallet_address)
        balances["TRX"] = trx_balance
    except Exception as e:
        balances["TRX"] = {"error": str(e), "balance": 0.0}
    
    return {
        "wallet_address": wallet_address,
        "balances": balances,
        "last_updated": datetime.utcnow().isoformat()
    }

@api_router.get("/balance/crt/{wallet_address}")
async def get_crt_balance(wallet_address: str):
    """Get CRT token balance"""
    try:
        balance = await crt_manager.get_crt_balance(wallet_address)
        return {"success": True, "data": balance}
    except Exception as e:
        return {"success": False, "error": str(e)}

@api_router.get("/balance/doge/{wallet_address}")
async def get_doge_balance(wallet_address: str):
    """Get DOGE balance"""
    try:
        balance = await doge_manager.get_balance(wallet_address)
        return {"success": True, "data": balance}
    except Exception as e:
        return {"success": False, "error": str(e)}

@api_router.get("/balance/trx/{wallet_address}")
async def get_trx_balance(wallet_address: str):
    """Get TRX balance"""
    try:
        balance = await tron_tx_manager.get_trx_balance(wallet_address)
        return {"success": True, "data": balance}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Game endpoints
@api_router.post("/games/bet")
async def place_bet(bet: GameBet, wallet_info: Dict = Depends(get_authenticated_wallet)):
    """Place a bet in casino game"""
    try:
        # Verify wallet matches authenticated user
        if bet.wallet_address != wallet_info["wallet_address"]:
            raise HTTPException(status_code=403, detail="Wallet address mismatch")
        
        # For demo purposes, we'll simulate bet processing
        game_id = f"game_{uuid.uuid4().hex[:8]}"
        
        # In production, you would:
        # 1. Deduct bet amount from player's balance
        # 2. Process the game logic
        # 3. Determine win/loss
        # 4. Update balances accordingly
        
        # Mock game result
        import random
        is_winner = random.choice([True, False])
        payout = bet.bet_amount * 2 if is_winner else 0
        
        # Store bet in database
        bet_record = {
            **bet.dict(),
            "game_id": game_id,
            "result": "win" if is_winner else "loss",
            "payout": payout,
            "status": "completed"
        }
        await db.game_bets.insert_one(bet_record)
        
        return {
            "success": True,
            "game_id": game_id,
            "bet_amount": bet.bet_amount,
            "currency": bet.currency,
            "result": "win" if is_winner else "loss",
            "payout": payout,
            "savings_contribution": bet.bet_amount if not is_winner else 0  # Loss goes to savings
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
    """Get savings information"""
    try:
        if wallet_address != wallet_info["wallet_address"]:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Calculate total savings from game losses
        pipeline = [
            {"$match": {"wallet_address": wallet_address, "result": "loss"}},
            {"$group": {"_id": "$currency", "total_saved": {"$sum": "$bet_amount"}}}
        ]
        
        savings_by_currency = await db.game_bets.aggregate(pipeline).to_list(100)
        
        total_games = await db.game_bets.count_documents({"wallet_address": wallet_address})
        total_wins = await db.game_bets.count_documents({"wallet_address": wallet_address, "result": "win"})
        total_losses = await db.game_bets.count_documents({"wallet_address": wallet_address, "result": "loss"})
        
        return {
            "success": True,
            "wallet_address": wallet_address,
            "savings_by_currency": savings_by_currency,
            "stats": {
                "total_games": total_games,
                "total_wins": total_wins,
                "total_losses": total_losses,
                "win_rate": (total_wins / total_games * 100) if total_games > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time balance updates
@api_router.websocket("/ws/balance/{wallet_address}")
async def websocket_balance_monitor(websocket: WebSocket, wallet_address: str):
    """WebSocket endpoint for real-time balance monitoring"""
    await websocket.accept()
    
    if wallet_address not in active_connections:
        active_connections[wallet_address] = []
    active_connections[wallet_address].append(websocket)
    
    try:
        # Send initial balance
        balance_data = await get_multi_chain_balance(wallet_address, {"wallet_address": wallet_address})
        await websocket.send_text(json.dumps({
            "type": "balance_update",
            "wallet": wallet_address,
            "data": balance_data
        }))
        
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "refresh_balance":
                # Refresh and send updated balance
                updated_balance = await get_multi_chain_balance(wallet_address, {"wallet_address": wallet_address})
                await websocket.send_text(json.dumps({
                    "type": "balance_update", 
                    "wallet": wallet_address,
                    "data": updated_balance
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
