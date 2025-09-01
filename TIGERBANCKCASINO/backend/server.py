from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Tiger Bank Casino API",
    description="A casino that saves your losses like a piggy bank",
    version="1.0.0"
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

# Pydantic models
class GameResult(BaseModel):
    game_type: str
    bet_amount: float
    result: str
    winnings: float
    balance_after: float

class UserBalance(BaseModel):
    user_id: str
    balance: float
    savings: float
    pool_allocation: float

# Mock database (replace with real database in production)
mock_db = {
    "users": {
        "user123": {
            "balance": 1000.0,
            "savings": 250.0,
            "pool_allocation": 250.0,
            "total_losses": 1000.0
        }
    }
}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Tiger Bank Casino API",
        "description": "A casino that saves your losses like a piggy bank",
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "tiger-bank-casino"}

@app.get("/api/user/{user_id}/balance")
async def get_user_balance(user_id: str) -> UserBalance:
    """Get user balance and savings"""
    if user_id not in mock_db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = mock_db["users"][user_id]
    return UserBalance(
        user_id=user_id,
        balance=user_data["balance"],
        savings=user_data["savings"],
        pool_allocation=user_data["pool_allocation"]
    )

@app.post("/api/game/play")
async def play_game(
    game_type: str,
    bet_amount: float,
    user_id: str = "user123"
) -> GameResult:
    """Play a casino game"""
    if user_id not in mock_db["users"]:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = mock_db["users"][user_id]
    
    if bet_amount > user_data["balance"]:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Simple game logic (50% win chance for demo)
    import random
    win = random.random() > 0.5
    
    if win:
        winnings = bet_amount * 1.8  # 80% profit on win
        user_data["balance"] += winnings - bet_amount
        result = "win"
    else:
        # Loss - smart allocation: 50% savings, 50% pools
        loss_amount = bet_amount
        savings_amount = loss_amount * 0.50    # 50% to personal savings
        pool_amount = loss_amount * 0.50       # 50% to investment pools
        
        user_data["balance"] -= bet_amount
        user_data["savings"] += savings_amount
        user_data["pool_allocation"] += pool_amount
        user_data["total_losses"] += loss_amount
        
        winnings = 0
        result = "loss"
    
    return GameResult(
        game_type=game_type,
        bet_amount=bet_amount,
        result=result,
        winnings=winnings,
        balance_after=user_data["balance"]
    )

@app.get("/api/games")
async def get_available_games():
    """Get list of available games"""
    return {
        "games": [
            {"id": "blackjack", "name": "Blackjack", "min_bet": 10, "max_bet": 1000},
            {"id": "roulette", "name": "Roulette", "min_bet": 5, "max_bet": 500},
            {"id": "slots", "name": "Slots", "min_bet": 1, "max_bet": 100}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)