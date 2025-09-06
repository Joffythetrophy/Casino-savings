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
    title="Tiger Bank Games - Development Fund System",
    description="Multi-token casino with development fund withdrawals and CDT bridge!",
    version="5.0.0"
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

# Your Development Wallet Addresses
DEV_WALLET_ADDRESSES = {
    "ETH": {
        "address": "0xaA94Fe949f6734e228c13C9Fc25D1eBCd994bffD",
        "network": "ethereum",
        "label": "Your ETH Development Wallet"
    },
    "BTC": {
        "address": "bc1qv489kvy26f4y87murvs39xfq7jv06m4gkth578a5zcw6h6ud038sr99trc",
        "network": "bitcoin", 
        "label": "Your BTC Development Wallet"
    },
    "USDC": {
        "address": "0xaA94Fe949f6734e228c13C9Fc25D1eBCd994bffD",
        "network": "ethereum",
        "label": "Your USDC Development Wallet (Ethereum)"
    }
}

# Request models
class WithdrawRequest(BaseModel):
    currency: str
    amount: float
    destination_address: str

class ConvertRequest(BaseModel):
    from_currency: str
    to_currency: str
    amount: float

# Basic endpoints
@app.get("/")
async def root():
    return {
        "message": "Tiger Bank Games - Development Fund System",
        "version": "5.0.0",
        "portfolio_value_usd": sum([
            token["your_balance"] * token["current_price"] 
            for token in YOUR_PORTFOLIO.values()
        ]),
        "total_tokens": len(YOUR_PORTFOLIO),
        "status": "active"
    }

@app.get("/api/portfolio")
async def get_portfolio():
    """Get your complete converted portfolio"""
    total_value = sum([
        token["your_balance"] * token["current_price"] 
        for token in YOUR_PORTFOLIO.values()
    ])
    
    return {
        "success": True,
        "portfolio": YOUR_PORTFOLIO,
        "summary": {
            "total_value_usd": total_value,
            "total_tokens": len(YOUR_PORTFOLIO),
            "conversion_complete": True,
            "ready_for_development": True
        }
    }

@app.get("/api/balances")
async def get_balances():
    """Get all token balances"""
    balances = {}
    for symbol, token in YOUR_PORTFOLIO.items():
        balances[symbol] = {
            "balance": token["your_balance"],
            "usd_value": token["your_balance"] * token["current_price"],
            "price": token["current_price"],
            "logo": token["logo"]
        }
    
    return {
        "success": True,
        "balances": balances,
        "last_updated": datetime.utcnow().isoformat()
    }

@app.post("/api/withdraw")
async def withdraw_to_development(request: WithdrawRequest):
    """Withdraw funds to development wallets"""
    try:
        currency = request.currency.upper()
        
        if currency not in YOUR_PORTFOLIO:
            raise HTTPException(status_code=400, detail=f"Currency {currency} not supported")
        
        token_info = YOUR_PORTFOLIO[currency]
        available_balance = token_info["your_balance"]
        
        if request.amount > available_balance:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient balance. Available: {available_balance} {currency}"
            )
        
        # Simulate withdrawal (in real implementation, this would interact with blockchain)
        YOUR_PORTFOLIO[currency]["your_balance"] -= request.amount
        
        # Get appropriate development wallet
        dev_wallet = None
        if currency in ["USDC", "ETH"]:
            dev_wallet = DEV_WALLET_ADDRESSES["ETH"]["address"]
        elif currency == "BTC":
            dev_wallet = DEV_WALLET_ADDRESSES["BTC"]["address"]
        else:
            dev_wallet = request.destination_address
        
        return {
            "success": True,
            "message": f"Withdrew {request.amount} {currency} to development wallet",
            "transaction": {
                "currency": currency,
                "amount": request.amount,
                "destination": dev_wallet,
                "remaining_balance": YOUR_PORTFOLIO[currency]["your_balance"],
                "timestamp": datetime.utcnow().isoformat(),
                "status": "completed"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/convert")
async def convert_currency(request: ConvertRequest):
    """Convert between currencies"""
    try:
        from_currency = request.from_currency.upper()
        to_currency = request.to_currency.upper()
        
        if from_currency not in YOUR_PORTFOLIO:
            raise HTTPException(status_code=400, detail=f"Source currency {from_currency} not supported")
        
        if to_currency not in YOUR_PORTFOLIO:
            raise HTTPException(status_code=400, detail=f"Target currency {to_currency} not supported")
        
        from_token = YOUR_PORTFOLIO[from_currency]
        to_token = YOUR_PORTFOLIO[to_currency]
        
        if request.amount > from_token["your_balance"]:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Available: {from_token['your_balance']} {from_currency}"
            )
        
        # Calculate conversion
        from_usd_value = request.amount * from_token["current_price"]
        to_amount = from_usd_value / to_token["current_price"]
        
        # Execute conversion
        YOUR_PORTFOLIO[from_currency]["your_balance"] -= request.amount
        YOUR_PORTFOLIO[to_currency]["your_balance"] += to_amount
        
        return {
            "success": True,
            "message": f"Converted {request.amount} {from_currency} to {to_amount:.8f} {to_currency}",
            "conversion": {
                "from_currency": from_currency,
                "to_currency": to_currency,
                "from_amount": request.amount,
                "to_amount": to_amount,
                "rate": to_amount / request.amount,
                "usd_value": from_usd_value,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/development-wallets")
async def get_development_wallets():
    """Get development wallet addresses"""
    return {
        "success": True,
        "wallets": DEV_WALLET_ADDRESSES,
        "note": "These are your development fund withdrawal addresses"
    }

@app.get("/api/cdt-bridge")
async def cdt_bridge_info():
    """Get CDT bridge information"""
    cdt_info = YOUR_PORTFOLIO["CDT"]
    
    return {
        "success": True,
        "cdt_bridge": {
            "token_address": cdt_info["address"],
            "current_balance": cdt_info["your_balance"],
            "target_purchase": "Available for purchase",
            "bridge_ready": True,
            "purchase_options": {
                "min_purchase": 1000,
                "max_purchase": 1000000,
                "current_price": cdt_info["current_price"]
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)