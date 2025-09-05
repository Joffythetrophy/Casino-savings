from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv
import logging
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Tiger Bank Games API - Multi Token",
    description="Gaming with multiple Solana tokens that grows your wealth!",
    version="2.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Supported Tokens Configuration
SUPPORTED_TOKENS = {
    "USDC": {
        "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "symbol": "USDC",
        "name": "USD Coin",
        "decimals": 6,
        "logo": "https://cryptologos.cc/logos/usd-coin-usdc-logo.png"
    },
    "TOKEN_A": {
        "address": "3ZP9KAKwJTMbhcbJdiaLvLXAgkmKVoAeNMQ6wNavjupx",
        "symbol": "TKA", 
        "name": "Tiger Token A",
        "decimals": 9,
        "logo": "🐅"
    },
    "TOKEN_B": {
        "address": "6MPSpfXcbYaZNLczhu53Q9MaqTHPa1B7BRGJSmiU17f4",
        "symbol": "TKB",
        "name": "Tiger Token B", 
        "decimals": 9,
        "logo": "🏦"
    },
    "SOL": {
        "address": "So11111111111111111111111111111111111111112",
        "symbol": "SOL",
        "name": "Solana",
        "decimals": 9,
        "logo": "https://cryptologos.cc/logos/solana-sol-logo.png"
    }
}

# Pydantic models
class GameResult(BaseModel):
    game_type: str
    bet_amount: float
    bet_token: str
    result: str
    winnings: float
    winnings_token: str
    balance_after: Dict[str, float]

class MultiTokenBalance(BaseModel):
    user_id: str
    balances: Dict[str, float]  # token_symbol -> balance
    savings: Dict[str, float]   # token_symbol -> savings
    pool_allocation: Dict[str, float]  # token_symbol -> pool_allocation

class TokenSwapRequest(BaseModel):
    from_token: str
    to_token: str
    amount: float
    user_id: str = "user123"

class TokenDepositRequest(BaseModel):
    token_symbol: str
    amount: float
    user_id: str = "user123"

# Mock database with multi-token support
mock_db = {
    "users": {
        "user123": {
            "balances": {
                "USDC": 1000.0,
                "TKA": 5000.0,   # Your first token
                "TKB": 2500.0,   # Your second token
                "SOL": 10.0
            },
            "savings": {
                "USDC": 250.0,
                "TKA": 1250.0,
                "TKB": 625.0,
                "SOL": 2.5
            },
            "pool_allocation": {
                "USDC": 250.0,
                "TKA": 1250.0,
                "TKB": 625.0,
                "SOL": 2.5
            }
        }
    },
    "token_transactions": [],
    "swap_history": []
}

# Token exchange rates (mock - in real app, fetch from DEX)
TOKEN_EXCHANGE_RATES = {
    "USDC": 1.0,      # Base currency
    "TKA": 0.05,      # 1 TKA = $0.05
    "TKB": 0.10,      # 1 TKB = $0.10  
    "SOL": 180.0      # 1 SOL = $180
}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Tiger Bank Games - Multi Token Casino! 🐅",
        "description": "Gaming with multiple Solana tokens that grows your wealth!",
        "version": "2.1.0",
        "supported_tokens": list(SUPPORTED_TOKENS.keys()),
        "features": [
            "🎰 Multi-Token Casino Games",
            "🐷 Smart Loss Allocation (50% savings, 50% pools)",
            "🔄 Token Swapping (TKA ↔ TKB ↔ USDC ↔ SOL)",
            "💰 Multi-Token Balances",
            "📊 Cross-Token Analytics"
        ]
    }

@app.get("/api/tokens")
async def get_supported_tokens():
    """Get all supported tokens"""
    return {
        "tokens": SUPPORTED_TOKENS,
        "exchange_rates": TOKEN_EXCHANGE_RATES
    }

@app.get("/api/user/{user_id}/balance")
async def get_user_balance(user_id: str) -> MultiTokenBalance:
    """Get user multi-token balance"""
    if user_id not in mock_db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = mock_db["users"][user_id]
    return MultiTokenBalance(
        user_id=user_id,
        balances=user_data["balances"],
        savings=user_data["savings"],
        pool_allocation=user_data["pool_allocation"]
    )

@app.get("/api/user/{user_id}/portfolio")
async def get_user_portfolio(user_id: str):
    """Get user portfolio value in USD"""
    if user_id not in mock_db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = mock_db["users"][user_id]
    
    # Calculate total portfolio value
    total_balance_usd = 0
    total_savings_usd = 0
    total_pools_usd = 0
    
    portfolio_breakdown = {}
    
    for token, balance in user_data["balances"].items():
        rate = TOKEN_EXCHANGE_RATES.get(token, 0)
        balance_usd = balance * rate
        savings_usd = user_data["savings"].get(token, 0) * rate
        pools_usd = user_data["pool_allocation"].get(token, 0) * rate
        
        total_balance_usd += balance_usd
        total_savings_usd += savings_usd
        total_pools_usd += pools_usd
        
        portfolio_breakdown[token] = {
            "balance": balance,
            "balance_usd": balance_usd,
            "savings": user_data["savings"].get(token, 0),
            "savings_usd": savings_usd,
            "pools": user_data["pool_allocation"].get(token, 0),
            "pools_usd": pools_usd,
            "token_info": SUPPORTED_TOKENS.get(token, {})
        }
    
    return {
        "user_id": user_id,
        "total_value_usd": total_balance_usd + total_savings_usd + total_pools_usd,
        "playing_balance_usd": total_balance_usd,
        "savings_usd": total_savings_usd,
        "pools_usd": total_pools_usd,
        "tokens": portfolio_breakdown
    }

@app.post("/api/game/play")
async def play_game(
    game_type: str,
    bet_amount: float,
    bet_token: str,
    user_id: str = "user123"
) -> GameResult:
    """Play casino game with any supported token"""
    if user_id not in mock_db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    
    if bet_token not in SUPPORTED_TOKENS:
        raise HTTPException(status_code=400, detail="Unsupported token")
    
    user_data = mock_db["users"][user_id]
    
    if bet_amount > user_data["balances"].get(bet_token, 0):
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Simple game logic (50% win chance)
    import random
    win = random.random() > 0.5
    
    if win:
        winnings = bet_amount * 1.8  # 80% profit on win
        user_data["balances"][bet_token] += winnings - bet_amount
        result = "win"
        winnings_token = bet_token
    else:
        # Loss - smart allocation: 50% savings, 50% pools
        loss_amount = bet_amount
        savings_amount = loss_amount * 0.50
        pool_amount = loss_amount * 0.50
        
        user_data["balances"][bet_token] -= bet_amount
        user_data["savings"][bet_token] = user_data["savings"].get(bet_token, 0) + savings_amount
        user_data["pool_allocation"][bet_token] = user_data["pool_allocation"].get(bet_token, 0) + pool_amount
        
        winnings = 0
        result = "loss"
        winnings_token = bet_token
    
    return GameResult(
        game_type=game_type,
        bet_amount=bet_amount,
        bet_token=bet_token,
        result=result,
        winnings=winnings,
        winnings_token=winnings_token,
        balance_after=user_data["balances"]
    )

@app.post("/api/tokens/swap")
async def swap_tokens(request: TokenSwapRequest):
    """Swap between supported tokens"""
    if request.from_token not in SUPPORTED_TOKENS or request.to_token not in SUPPORTED_TOKENS:
        raise HTTPException(status_code=400, detail="Unsupported token pair")
    
    if request.user_id not in mock_db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = mock_db["users"][request.user_id]
    
    # Check balance
    if request.amount > user_data["balances"].get(request.from_token, 0):
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Calculate exchange (using USD as intermediary)
    from_rate = TOKEN_EXCHANGE_RATES[request.from_token]
    to_rate = TOKEN_EXCHANGE_RATES[request.to_token]
    
    usd_value = request.amount * from_rate
    to_amount = usd_value / to_rate
    
    # Apply 0.5% swap fee
    swap_fee = to_amount * 0.005
    final_amount = to_amount - swap_fee
    
    # Execute swap
    user_data["balances"][request.from_token] -= request.amount
    user_data["balances"][request.to_token] = user_data["balances"].get(request.to_token, 0) + final_amount
    
    # Record swap
    swap_record = {
        "swap_id": f"swap_{len(mock_db['swap_history'])}",
        "user_id": request.user_id,
        "from_token": request.from_token,
        "to_token": request.to_token,
        "from_amount": request.amount,
        "to_amount": final_amount,
        "fee": swap_fee,
        "rate": final_amount / request.amount,
        "timestamp": datetime.now()
    }
    mock_db["swap_history"].append(swap_record)
    
    return {
        "swap_id": swap_record["swap_id"],
        "from_token": request.from_token,
        "to_token": request.to_token,
        "from_amount": request.amount,
        "to_amount": final_amount,
        "fee": swap_fee,
        "new_balances": user_data["balances"]
    }

@app.get("/api/tokens/rates")
async def get_exchange_rates():
    """Get current token exchange rates"""
    return {
        "base_currency": "USDC",
        "rates": TOKEN_EXCHANGE_RATES,
        "last_updated": datetime.now()
    }

@app.post("/api/tokens/deposit")
async def deposit_tokens(request: TokenDepositRequest):
    """Simulate token deposit (in real app, would verify blockchain transaction)"""
    if request.token_symbol not in SUPPORTED_TOKENS:
        raise HTTPException(status_code=400, detail="Unsupported token")
    
    if request.user_id not in mock_db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = mock_db["users"][request.user_id]
    
    # Add to balance
    user_data["balances"][request.token_symbol] = user_data["balances"].get(request.token_symbol, 0) + request.amount
    
    # Record transaction
    transaction = {
        "tx_id": f"dep_{len(mock_db['token_transactions'])}",
        "user_id": request.user_id,
        "token": request.token_symbol,
        "amount": request.amount,
        "type": "deposit",
        "timestamp": datetime.now()
    }
    mock_db["token_transactions"].append(transaction)
    
    return {
        "message": f"Deposited {request.amount} {request.token_symbol}",
        "new_balance": user_data["balances"][request.token_symbol],
        "transaction_id": transaction["tx_id"]
    }

@app.get("/api/games")
async def get_available_games():
    """Get available games with token support info"""
    return {
        "games": [
            {
                "id": "blackjack", 
                "name": "🃏 Blackjack", 
                "min_bet": {"USDC": 10, "TKA": 200, "TKB": 100, "SOL": 0.05},
                "max_bet": {"USDC": 1000, "TKA": 20000, "TKB": 10000, "SOL": 5},
                "supported_tokens": ["USDC", "TKA", "TKB", "SOL"]
            },
            {
                "id": "roulette", 
                "name": "🎰 Roulette", 
                "min_bet": {"USDC": 5, "TKA": 100, "TKB": 50, "SOL": 0.03},
                "max_bet": {"USDC": 500, "TKA": 10000, "TKB": 5000, "SOL": 2.5},
                "supported_tokens": ["USDC", "TKA", "TKB", "SOL"]
            },
            {
                "id": "slots", 
                "name": "🎲 Slots", 
                "min_bet": {"USDC": 1, "TKA": 20, "TKB": 10, "SOL": 0.01},
                "max_bet": {"USDC": 100, "TKA": 2000, "TKB": 1000, "SOL": 0.5},
                "supported_tokens": ["USDC", "TKA", "TKB", "SOL"]
            }
        ]
    }

@app.get("/api/user/{user_id}/transactions")
async def get_user_transactions(user_id: str):
    """Get user transaction history"""
    user_transactions = [
        t for t in mock_db["token_transactions"] 
        if t["user_id"] == user_id
    ]
    
    user_swaps = [
        s for s in mock_db["swap_history"]
        if s["user_id"] == user_id
    ]
    
    return {
        "user_id": user_id,
        "transactions": user_transactions,
        "swaps": user_swaps,
        "total_transactions": len(user_transactions),
        "total_swaps": len(user_swaps)
    }

@app.get("/api/leaderboard")
async def get_leaderboard():
    """Get casino leaderboard by portfolio value"""
    leaderboard = []
    
    for user_id, user_data in mock_db["users"].items():
        total_value = 0
        for token, balance in user_data["balances"].items():
            rate = TOKEN_EXCHANGE_RATES.get(token, 0)
            total_value += balance * rate
            total_value += user_data["savings"].get(token, 0) * rate
            total_value += user_data["pool_allocation"].get(token, 0) * rate
        
        leaderboard.append({
            "user_id": user_id,
            "total_value_usd": total_value,
            "favorite_token": max(user_data["balances"], key=user_data["balances"].get)
        })
    
    leaderboard.sort(key=lambda x: x["total_value_usd"], reverse=True)
    
    return {
        "leaderboard": leaderboard,
        "last_updated": datetime.now()
    }

@app.get("/api/health")
async def health_check():
    """Health check with token support status"""
    return {
        "status": "healthy",
        "service": "tiger-bank-games-multi-token",
        "version": "2.1.0",
        "supported_tokens": len(SUPPORTED_TOKENS),
        "active_users": len(mock_db["users"]),
        "total_transactions": len(mock_db["token_transactions"]),
        "total_swaps": len(mock_db["swap_history"])
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)