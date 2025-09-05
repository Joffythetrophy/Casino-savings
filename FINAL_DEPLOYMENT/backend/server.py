from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Tiger Bank Games - Final System",
    description="Multi-token casino with your complete converted portfolio!",
    version="4.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# YOUR COMPLETE CONVERTED PORTFOLIO (from your conversion history)
YOUR_PORTFOLIO = {
    "USDC": {
        "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "symbol": "USDC",
        "name": "USD Coin",
        "decimals": 6,
        "logo": "💵",
        "your_balance": 319000,  # 319K USDC (converted)
        "current_price": 1.0,
        "source": "converted_from_previous_portfolio"
    },
    "DOGE": {
        "address": "DogecoinAddressHere1111111111111111111111",
        "symbol": "DOGE",
        "name": "Dogecoin",
        "decimals": 8,
        "logo": "🐕",
        "your_balance": 13000000,  # 13M DOGE (converted)
        "current_price": 0.08,
        "source": "converted_from_previous_portfolio"
    },
    "TRX": {
        "address": "TronAddressHere1111111111111111111111111",
        "symbol": "TRX", 
        "name": "TRON",
        "decimals": 6,
        "logo": "⚡",
        "your_balance": 3900000,  # 3.9M TRX (converted)
        "current_price": 0.12,
        "source": "converted_from_previous_portfolio"
    },
    "CRT": {
        "address": "CRTtoken1111111111111111111111111111111111",
        "symbol": "CRT",
        "name": "Casino Revenue Token",
        "decimals": 9,
        "logo": "💎",
        "your_balance": 21000000,  # 21M CRT (converted)
        "current_price": 0.25,
        "source": "converted_from_previous_portfolio"
    },
    "T52M": {
        "address": "6MPSpfXcbYaZNLczhu53Q9MaqTHPa1B7BRGJSmiU17f4",
        "symbol": "T52M",
        "name": "Tiger Token 52M Supply",
        "decimals": 9,
        "logo": "🔥",
        "your_balance": 52000000,  # 52M T52M (current holding)
        "current_price": 0.10,
        "source": "current_holding"
    },
    "CDT": {
        "address": "3ZP9KAKwJTMbhcbJdiaLvLXAgkmKVoAeNMQ6wNavjupx",
        "symbol": "CDT",
        "name": "Creative Dollar Token",
        "decimals": 9,
        "logo": "🎨",
        "your_balance": 0,  # Target for purchase
        "current_price": 0.10,
        "source": "target_purchase"
    }
}

# Exchange rates
EXCHANGE_RATES = {
    "USDC": 1.0,
    "DOGE": 0.08,
    "TRX": 0.12,
    "CRT": 0.25,
    "T52M": 0.10,
    "CDT": 0.10,
    "SOL": 180.0,
    "BTC": 65000.0,
    "ETH": 3200.0
}

# Pydantic models
class Portfolio(BaseModel):
    user_id: str
    tokens: Dict[str, Any]
    total_value_usd: float

class BridgeRequest(BaseModel):
    source_token: str
    amount: float
    destination_token: str
    user_wallet: str

# Mock database
mock_db = {
    "users": {
        "user123": {
            "balances": {token: info["your_balance"] for token, info in YOUR_PORTFOLIO.items()}
        }
    },
    "bridge_requests": []
}

@app.get("/")
async def root():
    """Root endpoint"""
    total_portfolio_value = sum(
        info["your_balance"] * info["current_price"] 
        for info in YOUR_PORTFOLIO.values()
    )
    
    return {
        "message": "🐅 Tiger Bank Games - Your Complete Portfolio System! 🎮",
        "version": "4.0.0",
        "your_portfolio_value": f"${total_portfolio_value:,.2f}",
        "tokens": list(YOUR_PORTFOLIO.keys()),
        "features": [
            "🎰 Multi-Token Casino Gaming",
            "💰 Complete Converted Portfolio Access",
            "🌉 Bridge Any Token to Any Token", 
            "💸 Real Crypto Withdrawals",
            "🎨 CDT Purchase System",
            "🌈 Diversified Portfolio Builder"
        ]
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "tiger-bank-games-final",
        "version": "4.0.0",
        "portfolio_loaded": len(YOUR_PORTFOLIO) > 0
    }

@app.get("/api/user/{user_id}/portfolio")
async def get_user_portfolio(user_id: str) -> Portfolio:
    """Get complete user portfolio with converted tokens"""
    
    portfolio_breakdown = {}
    total_value = 0
    
    for token_symbol, token_info in YOUR_PORTFOLIO.items():
        balance = token_info["your_balance"]
        price = token_info["current_price"]
        value_usd = balance * price
        total_value += value_usd
        
        portfolio_breakdown[token_symbol] = {
            "symbol": token_symbol,
            "name": token_info["name"],
            "balance": balance,
            "price_usd": price,
            "value_usd": value_usd,
            "logo": token_info["logo"],
            "source": token_info["source"],
            "withdrawable": balance > 0
        }
    
    return Portfolio(
        user_id=user_id,
        tokens=portfolio_breakdown,
        total_value_usd=total_value
    )

@app.get("/api/tokens/summary")
async def get_tokens_summary():
    """Get summary of all your tokens"""
    
    converted_tokens = {}
    current_holdings = {}
    targets = {}
    
    total_converted_value = 0
    total_current_value = 0
    
    for token_symbol, token_info in YOUR_PORTFOLIO.items():
        balance = token_info["your_balance"]
        price = token_info["current_price"]
        value_usd = balance * price
        
        token_data = {
            "symbol": token_symbol,
            "name": token_info["name"],
            "balance": balance,
            "value_usd": value_usd,
            "logo": token_info["logo"]
        }
        
        if token_info["source"] == "converted_from_previous_portfolio":
            converted_tokens[token_symbol] = token_data
            total_converted_value += value_usd
        elif token_info["source"] == "current_holding":
            current_holdings[token_symbol] = token_data
            total_current_value += value_usd
        elif token_info["source"] == "target_purchase":
            targets[token_symbol] = token_data
    
    return {
        "converted_portfolio": {
            "tokens": converted_tokens,
            "total_value_usd": total_converted_value,
            "description": "Your previous conversions: 319K USDC + 13M DOGE + 3.9M TRX + 21M CRT"
        },
        "current_holdings": {
            "tokens": current_holdings,
            "total_value_usd": total_current_value,
            "description": "Your current T52M token holdings"
        },
        "purchase_targets": {
            "tokens": targets,
            "description": "Tokens you want to acquire (CDT)"
        },
        "grand_total_usd": total_converted_value + total_current_value
    }

@app.post("/api/tokens/bridge")
async def bridge_tokens(request: BridgeRequest):
    """Bridge between any of your tokens"""
    
    # Validate source token
    if request.source_token not in YOUR_PORTFOLIO:
        raise HTTPException(status_code=400, detail="Source token not available")
    
    source_info = YOUR_PORTFOLIO[request.source_token]
    
    # Check balance
    if request.amount > source_info["your_balance"]:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Available: {source_info['your_balance']:,} {request.source_token}"
        )
    
    # Calculate conversion
    source_price = source_info["current_price"]
    dest_price = EXCHANGE_RATES.get(request.destination_token, 1.0)
    
    usd_value = request.amount * source_price
    destination_amount = usd_value / dest_price
    
    # Execute bridge (mock)
    bridge_id = f"bridge_{len(mock_db['bridge_requests'])}"
    
    bridge_record = {
        "bridge_id": bridge_id,
        "source_token": request.source_token,
        "source_amount": request.amount,
        "destination_token": request.destination_token,
        "destination_amount": destination_amount,
        "usd_value": usd_value,
        "user_wallet": request.user_wallet,
        "status": "completed",
        "timestamp": datetime.now().isoformat()
    }
    
    # Update balances
    YOUR_PORTFOLIO[request.source_token]["your_balance"] -= request.amount
    
    if request.destination_token in YOUR_PORTFOLIO:
        YOUR_PORTFOLIO[request.destination_token]["your_balance"] += destination_amount
    
    mock_db["bridge_requests"].append(bridge_record)
    
    return {
        "success": True,
        "bridge_id": bridge_id,
        "message": f"Successfully bridged {request.amount:,} {request.source_token} → {destination_amount:,.2f} {request.destination_token}",
        "source_remaining": YOUR_PORTFOLIO[request.source_token]["your_balance"],
        "usd_value": usd_value
    }

@app.get("/api/games")
async def get_games():
    """Get available casino games"""
    return {
        "games": [
            {"id": "blackjack", "name": "🃏 Blackjack", "min_bet": 10, "max_bet": 10000},
            {"id": "roulette", "name": "🎰 Roulette", "min_bet": 5, "max_bet": 5000},
            {"id": "slots", "name": "🎲 Slots", "min_bet": 1, "max_bet": 1000}
        ],
        "supported_tokens": list(YOUR_PORTFOLIO.keys())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)