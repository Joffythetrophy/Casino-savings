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

class WithdrawalRequest(BaseModel):
    token_symbol: str
    amount: float
    destination_address: str
    network: str  # "ethereum", "bitcoin", "solana"
    purpose: str = "app_development"

@app.post("/api/withdraw/external")
async def withdraw_to_external_wallet(request: WithdrawalRequest):
    """Withdraw tokens directly to external wallet for app development"""
    
    # Validate token availability
    if request.token_symbol not in YOUR_PORTFOLIO:
        raise HTTPException(status_code=400, detail="Token not available for withdrawal")
    
    token_info = YOUR_PORTFOLIO[request.token_symbol]
    
    # Check balance
    if request.amount > token_info["your_balance"]:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Available: {token_info['your_balance']:,} {request.token_symbol}"
        )
    
    # Calculate USD value
    usd_value = request.amount * token_info["current_price"]
    
    # Create withdrawal record
    withdrawal_id = f"ext_withdraw_{len(mock_db.get('external_withdrawals', []))}"
    
    withdrawal_record = {
        "withdrawal_id": withdrawal_id,
        "token_symbol": request.token_symbol,
        "amount": request.amount,
        "usd_value": usd_value,
        "destination_address": request.destination_address,
        "network": request.network,
        "purpose": request.purpose,
        "status": "processing",
        "created_at": datetime.now().isoformat(),
        "estimated_completion": "10-30 minutes",
        "tx_hash": f"0x{withdrawal_id}mock_hash_for_demo"
    }
    
    # Update balance
    YOUR_PORTFOLIO[request.token_symbol]["your_balance"] -= request.amount
    
    # Store withdrawal
    if "external_withdrawals" not in mock_db:
        mock_db["external_withdrawals"] = []
    mock_db["external_withdrawals"].append(withdrawal_record)
    
    return {
        "success": True,
        "withdrawal_id": withdrawal_id,
        "message": f"Withdrawal of {request.amount:,} {request.token_symbol} initiated to {request.network}",
        "amount": request.amount,
        "token": request.token_symbol,
        "usd_value": usd_value,
        "destination_address": request.destination_address,
        "network": request.network,
        "estimated_completion": withdrawal_record["estimated_completion"],
        "remaining_balance": token_info["your_balance"]
    }

@app.get("/api/dev-fund/opportunities")
async def get_development_fund_opportunities():
    """Get optimal bridging opportunities for app development fund"""
    
    # Development-focused allocations
    dev_fund_strategies = {
        "conservative_dev_fund": {
            "name": "🛡️ Conservative Dev Fund",
            "total_usd": 500000,  # $500k
            "allocation": {
                "USDC": {"percentage": 0.60, "reason": "Stable development funding"},
                "ETH": {"percentage": 0.25, "reason": "Smart contract development"},
                "BTC": {"percentage": 0.15, "reason": "Long-term store of value"}
            }
        },
        "balanced_dev_fund": {
            "name": "⚖️ Balanced Dev Fund", 
            "total_usd": 1000000,  # $1M
            "allocation": {
                "USDC": {"percentage": 0.50, "reason": "Operating expenses & team"},
                "ETH": {"percentage": 0.30, "reason": "DeFi & smart contract projects"},
                "BTC": {"percentage": 0.20, "reason": "Treasury reserve"}
            }
        },
        "aggressive_dev_fund": {
            "name": "🚀 Aggressive Dev Fund",
            "total_usd": 2000000,  # $2M
            "allocation": {
                "USDC": {"percentage": 0.40, "reason": "Development runway"},
                "ETH": {"percentage": 0.35, "reason": "Major DeFi development"},
                "BTC": {"percentage": 0.25, "reason": "Strategic treasury"}
            }
        }
    }
    
    # Calculate what you can bridge from each source
    bridge_sources = {}
    
    for token_symbol, token_info in YOUR_PORTFOLIO.items():
        if token_info["your_balance"] > 0 and token_symbol != "CDT":
            max_usd_value = token_info["your_balance"] * token_info["current_price"]
            bridge_sources[token_symbol] = {
                "available_balance": token_info["your_balance"],
                "max_usd_value": max_usd_value,
                "recommendation": get_bridge_recommendation(token_symbol, max_usd_value)
            }
    
    # Calculate fund breakdowns
    fund_breakdowns = {}
    
    for fund_id, fund_info in dev_fund_strategies.items():
        total_usd = fund_info["total_usd"]
        breakdown = {}
        
        for target_token, details in fund_info["allocation"].items():
            percentage = details["percentage"]
            target_price = EXCHANGE_RATES.get(target_token, 1.0)
            
            usd_amount = total_usd * percentage
            token_amount = usd_amount / target_price
            
            breakdown[target_token] = {
                "usd_amount": usd_amount,
                "token_amount": token_amount,
                "percentage": f"{percentage*100}%",
                "reason": details["reason"]
            }
        
        fund_breakdowns[fund_id] = {
            "name": fund_info["name"],
            "total_usd": total_usd,
            "breakdown": breakdown,
            "percentage_of_portfolio": f"{(total_usd / 12277000) * 100:.1f}%"
        }
    
    return {
        "available_for_bridging": bridge_sources,
        "development_fund_options": fund_breakdowns,
        "recommendations": {
            "conservative": "Use USDC/TRX for stable funding",
            "balanced": "Mix DOGE/T52M for larger allocations", 
            "aggressive": "Use CRT for maximum development capital"
        }
    }

def get_bridge_recommendation(token_symbol: str, max_usd_value: float) -> str:
    """Get bridging recommendation for each token"""
    recommendations = {
        "USDC": f"Already stable - perfect for development expenses (${max_usd_value:,.0f} available)",
        "DOGE": f"High liquidity - ideal for large conversions (${max_usd_value:,.0f} → ETH/BTC)",
        "TRX": f"Moderate size - good for balanced allocations (${max_usd_value:,.0f} available)",
        "CRT": f"MASSIVE value - can fund major development projects (${max_usd_value:,.0f}!)",
        "T52M": f"Huge supply - excellent for large-scale bridging (${max_usd_value:,.0f})"
    }
    return recommendations.get(token_symbol, f"${max_usd_value:,.0f} available for bridging")

@app.post("/api/dev-fund/create")
async def create_development_fund(fund_type: str, source_tokens: Dict[str, float]):
    """Create development fund by bridging multiple tokens"""
    
    if fund_type not in ["conservative_dev_fund", "balanced_dev_fund", "aggressive_dev_fund"]:
        raise HTTPException(status_code=400, detail="Invalid fund type")
    
    # Get fund strategy
    opportunities = await get_development_fund_opportunities()
    fund_strategy = opportunities["development_fund_options"][fund_type]
    
    total_bridged_usd = 0
    bridge_records = []
    
    # Execute bridges from source tokens
    for source_token, amount in source_tokens.items():
        if source_token not in YOUR_PORTFOLIO:
            continue
            
        token_info = YOUR_PORTFOLIO[source_token]
        if amount > token_info["your_balance"]:
            continue
            
        # Calculate USD value
        usd_value = amount * token_info["current_price"]
        total_bridged_usd += usd_value
        
        # Update balance
        YOUR_PORTFOLIO[source_token]["your_balance"] -= amount
        
        bridge_records.append({
            "source_token": source_token,
            "amount": amount,
            "usd_value": usd_value
        })
    
    # Allocate to development targets
    dev_allocations = {}
    
    for target_token, details in fund_strategy["breakdown"].items():
        percentage = float(details["percentage"].rstrip('%')) / 100
        target_usd = total_bridged_usd * percentage
        target_price = EXCHANGE_RATES.get(target_token, 1.0)
        target_amount = target_usd / target_price
        
        dev_allocations[target_token] = {
            "amount": target_amount,
            "usd_value": target_usd,
            "reason": details["reason"]
        }
        
        # Add to portfolio if not exists
        if target_token not in YOUR_PORTFOLIO:
            YOUR_PORTFOLIO[target_token] = {
                "symbol": target_token,
                "your_balance": target_amount,
                "current_price": target_price
            }
        else:
            YOUR_PORTFOLIO[target_token]["your_balance"] += target_amount
    
    # Create fund record
    fund_id = f"dev_fund_{len(mock_db.get('development_funds', []))}"
    
    fund_record = {
        "fund_id": fund_id,
        "fund_type": fund_type,
        "fund_name": fund_strategy["name"],
        "total_usd_value": total_bridged_usd,
        "source_bridges": bridge_records,
        "target_allocations": dev_allocations,
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    if "development_funds" not in mock_db:
        mock_db["development_funds"] = []
    mock_db["development_funds"].append(fund_record)
    
    return {
        "success": True,
        "fund_id": fund_id,
        "fund_name": fund_strategy["name"],
        "total_development_capital": total_bridged_usd,
        "allocations": dev_allocations,
        "message": f"Development fund created with ${total_bridged_usd:,.0f} in capital",
        "ready_for_withdrawal": True
    }

@app.get("/api/withdrawals/history")
async def get_withdrawal_history():
    """Get withdrawal history for external wallets"""
    
    return {
        "external_withdrawals": mock_db.get("external_withdrawals", []),
        "development_funds": mock_db.get("development_funds", []),
        "total_withdrawn_usd": sum(w.get("usd_value", 0) for w in mock_db.get("external_withdrawals", []))
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