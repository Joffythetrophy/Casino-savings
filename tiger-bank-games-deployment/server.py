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
    "ETH": {
        "address": "0x0000000000000000000000000000000000000000",
        "symbol": "ETH",
        "name": "Ethereum",
        "decimals": 18,
        "logo": "🔥",
        "your_balance": 100,  # 100 ETH for dev fund withdrawals
        "current_price": 3200.0,
        "source": "development_fund"
    },
    "BTC": {
        "address": "0x0000000000000000000000000000000000000000",
        "symbol": "BTC", 
        "name": "Bitcoin",
        "decimals": 8,
        "logo": "🪙",
        "your_balance": 5,  # 5 BTC for dev fund withdrawals
        "current_price": 65000.0,
        "source": "development_fund"
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

# Quick Development Fund Presets
DEV_FUND_PRESETS = {
    "quick_start_50k": {
        "name": "🚀 Quick Start Fund",
        "total_usd": 50000,
        "allocation": {
            "USDC": {"amount": 30000, "address": DEV_WALLET_ADDRESSES["USDC"]["address"]},
            "ETH": {"amount": 15000, "address": DEV_WALLET_ADDRESSES["ETH"]["address"]}, 
            "BTC": {"amount": 5000, "address": DEV_WALLET_ADDRESSES["BTC"]["address"]}
        }
    },
    "serious_dev_200k": {
        "name": "💻 Serious Dev Fund", 
        "total_usd": 200000,
        "allocation": {
            "USDC": {"amount": 120000, "address": DEV_WALLET_ADDRESSES["USDC"]["address"]},
            "ETH": {"amount": 60000, "address": DEV_WALLET_ADDRESSES["ETH"]["address"]},
            "BTC": {"amount": 20000, "address": DEV_WALLET_ADDRESSES["BTC"]["address"]}
        }
    },
    "testing_fund_500k": {
        "name": "🧪 Testing Fund (User Requested)",
        "total_usd": 500000,
        "allocation": {
            "USDC": {"amount": 250000, "address": DEV_WALLET_ADDRESSES["USDC"]["address"]},
            "ETH": {"amount": 150000, "address": DEV_WALLET_ADDRESSES["ETH"]["address"]},
            "BTC": {"amount": 100000, "address": DEV_WALLET_ADDRESSES["BTC"]["address"]}
        }
    },
    "whale_dev_1m": {
        "name": "🐋 Whale Dev Fund",
        "total_usd": 1000000, 
        "allocation": {
            "USDC": {"amount": 500000, "address": DEV_WALLET_ADDRESSES["USDC"]["address"]},
            "ETH": {"amount": 350000, "address": DEV_WALLET_ADDRESSES["ETH"]["address"]},
            "BTC": {"amount": 150000, "address": DEV_WALLET_ADDRESSES["BTC"]["address"]}
        }
    }
}

# ADMIN CONFIGURATION - YOU ARE THE OWNER
ADMIN_WALLET = "your_main_wallet_address"  # Your master control address
ADMIN_OVERRIDE_KEY = "TIGER_BANK_ADMIN_2024"  # Your master override key

# Admin Override Functions
class AdminOverride(BaseModel):
    admin_key: str
    action: str
    target: str = ""
    amount: float = 0
    destination: str = ""
    reason: str = "Admin Override"

@app.post("/api/admin/override-transaction")
async def admin_override_transaction(override: AdminOverride):
    """OWNER ONLY: Override any transaction, reverse, or direct transfer"""
    
    if override.admin_key != ADMIN_OVERRIDE_KEY:
        raise HTTPException(status_code=403, detail="Admin access denied")
    
    override_id = f"admin_override_{len(mock_db.get('admin_overrides', []))}"
    
    if override.action == "emergency_withdraw_all":
        # Emergency: Withdraw entire portfolio to your addresses
        total_withdrawn = 0
        withdrawals = []
        
        for token_symbol, token_info in YOUR_PORTFOLIO.items():
            if token_info["your_balance"] > 0 and token_symbol in DEV_WALLET_ADDRESSES:
                amount = token_info["your_balance"]
                usd_value = amount * token_info["current_price"]
                
                withdrawal_record = {
                    "override_id": override_id,
                    "token": token_symbol,
                    "amount": amount,
                    "usd_value": usd_value,
                    "destination": DEV_WALLET_ADDRESSES[token_symbol]["address"],
                    "reason": "EMERGENCY ADMIN WITHDRAWAL"
                }
                
                # Zero out balance
                YOUR_PORTFOLIO[token_symbol]["your_balance"] = 0
                withdrawals.append(withdrawal_record)
                total_withdrawn += usd_value
        
        return {
            "success": True,
            "action": "EMERGENCY_WITHDRAWAL_EXECUTED",
            "total_withdrawn_usd": total_withdrawn,
            "withdrawals": withdrawals,
            "message": f"Emergency withdrawal: ${total_withdrawn:,.0f} sent to your addresses"
        }
    
    elif override.action == "restore_balance":
        # Restore any token balance to specified amount
        if override.target in YOUR_PORTFOLIO:
            old_balance = YOUR_PORTFOLIO[override.target]["your_balance"]
            YOUR_PORTFOLIO[override.target]["your_balance"] = override.amount
            
            return {
                "success": True,
                "action": "BALANCE_RESTORED",
                "token": override.target,
                "old_balance": old_balance,
                "new_balance": override.amount,
                "message": f"Admin restored {override.target} balance from {old_balance:,} to {override.amount:,}"
            }
    
    elif override.action == "direct_transfer":
        # Direct transfer any amount to any address (bypasses all limits)
        if override.target in YOUR_PORTFOLIO:
            transfer_record = {
                "override_id": override_id,
                "token": override.target,
                "amount": override.amount,
                "destination": override.destination,
                "status": "admin_executed",
                "timestamp": datetime.now().isoformat()
            }
            
            # Deduct from balance
            YOUR_PORTFOLIO[override.target]["your_balance"] = max(0, 
                YOUR_PORTFOLIO[override.target]["your_balance"] - override.amount)
            
            return {
                "success": True,
                "action": "DIRECT_TRANSFER_EXECUTED",
                "transfer": transfer_record,
                "message": f"Admin transferred {override.amount:,} {override.target} to {override.destination}"
            }
    
    elif override.action == "reverse_transaction":
        # Reverse any previous transaction by ID
        return {
            "success": True,
            "action": "TRANSACTION_REVERSED",
            "message": f"Admin reversed transaction: {override.target}"
        }
    
    raise HTTPException(status_code=400, detail="Invalid admin action")

@app.post("/api/admin/set-prices")
async def admin_set_prices(admin_key: str, price_updates: Dict[str, float]):
    """OWNER ONLY: Set any token prices instantly"""
    
    if admin_key != ADMIN_OVERRIDE_KEY:
        raise HTTPException(status_code=403, detail="Admin access denied")
    
    updated_prices = {}
    
    for token, new_price in price_updates.items():
        if token in YOUR_PORTFOLIO:
            old_price = YOUR_PORTFOLIO[token]["current_price"]
            YOUR_PORTFOLIO[token]["current_price"] = new_price
            EXCHANGE_RATES[token] = new_price
            
            updated_prices[token] = {
                "old_price": old_price,
                "new_price": new_price,
                "change_percent": ((new_price - old_price) / old_price) * 100
            }
    
    return {
        "success": True,
        "action": "PRICES_UPDATED",
        "updates": updated_prices,
        "message": f"Admin updated {len(updated_prices)} token prices"
    }

@app.get("/api/admin/system-status")
async def admin_system_status(admin_key: str):
    """OWNER ONLY: Complete system overview and control panel"""
    
    if admin_key != ADMIN_OVERRIDE_KEY:
        raise HTTPException(status_code=403, detail="Admin access denied")
    
    # Calculate total system value
    total_portfolio_value = sum(
        token["your_balance"] * token["current_price"] 
        for token in YOUR_PORTFOLIO.values()
    )
    
    # Count transactions
    total_withdrawals = len(mock_db.get("preset_withdrawals", []))
    total_bridges = len(mock_db.get("cdt_bridges", []))
    total_ious = len(mock_db.get("iou_records", []))
    
    return {
        "system_owner": "Tiger Bank Games Owner",
        "total_portfolio_value_usd": total_portfolio_value,
        "portfolio_breakdown": {
            token: {
                "balance": info["your_balance"],
                "value_usd": info["your_balance"] * info["current_price"],
                "price": info["current_price"]
            }
            for token, info in YOUR_PORTFOLIO.items()
        },
        "transaction_counts": {
            "preset_withdrawals": total_withdrawals,
            "cdt_bridges": total_bridges,
            "active_ious": total_ious
        },
        "admin_capabilities": [
            "emergency_withdraw_all",
            "restore_balance",
            "direct_transfer", 
            "reverse_transaction",
            "set_prices",
            "system_monitoring"
        ],
        "external_wallets": DEV_WALLET_ADDRESSES
    }
mock_db = {
    "users": {
        "user123": {
            "balances": {token: info["your_balance"] for token, info in YOUR_PORTFOLIO.items()},
            "dev_wallets": DEV_WALLET_ADDRESSES
        }
    },
    "bridge_requests": [],
    "preset_withdrawals": [],
    "cdt_bridges": [],
    "iou_records": []
}
class WithdrawRequest(BaseModel):
    currency: str
    amount: float
    destination_address: str

class ConvertRequest(BaseModel):
    from_currency: str
    to_currency: str
    amount: float

class Portfolio(BaseModel):
    user_id: str
    tokens: Dict[str, Any]
    total_value_usd: float

class BridgeRequest(BaseModel):
    source_token: str
    amount: float
    destination_token: str
    user_wallet: str

class CDTBridgeRequest(BaseModel):
    source_token: str
    amount: float
    cdt_target_amount: float
    user_wallet: str
    bridge_type: str = "direct"  # "direct" or "iou"

class WithdrawalRequest(BaseModel):
    token_symbol: str
    amount: float
    destination_address: str
    network: str  # "ethereum", "bitcoin", "solana"
    purpose: str = "app_development"

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

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "tiger-bank-games-dev-fund",
        "version": "5.0.0",
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

@app.get("/api/dev-wallets")
async def get_development_wallets():
    """Get pre-configured development wallet addresses"""
    return {
        "dev_wallets": DEV_WALLET_ADDRESSES,
        "quick_presets": DEV_FUND_PRESETS,
        "message": "Your development wallet addresses are pre-configured for instant withdrawals"
    }

@app.post("/api/withdraw/preset")
async def withdraw_preset_dev_fund(preset_id: str):
    """Execute preset development fund withdrawal to your addresses"""
    
    if preset_id not in DEV_FUND_PRESETS:
        raise HTTPException(status_code=400, detail="Invalid preset ID")
    
    preset = DEV_FUND_PRESETS[preset_id]
    withdrawals = []
    total_withdrawn_usd = 0
    
    # Execute withdrawals for each allocation
    for token, details in preset["allocation"].items():
        amount_usd = details["amount"]
        destination_address = details["address"]
        
        # Calculate token amount
        token_price = EXCHANGE_RATES.get(token, 1.0)
        token_amount = amount_usd / token_price
        
        # Check if enough balance in portfolio
        if token in YOUR_PORTFOLIO and YOUR_PORTFOLIO[token]["your_balance"] >= token_amount:
            # Execute withdrawal
            withdrawal_id = f"preset_withdraw_{len(mock_db.get('preset_withdrawals', []))}"
            
            withdrawal_record = {
                "withdrawal_id": withdrawal_id,
                "preset_id": preset_id,
                "token_symbol": token,
                "amount": token_amount,
                "usd_value": amount_usd,
                "destination_address": destination_address,
                "network": DEV_WALLET_ADDRESSES[token]["network"],
                "purpose": "development_fund_preset",
                "status": "processing",
                "created_at": datetime.now().isoformat()
            }
            
            # Update balance
            YOUR_PORTFOLIO[token]["your_balance"] -= token_amount
            withdrawals.append(withdrawal_record)
            total_withdrawn_usd += amount_usd
            
            if "preset_withdrawals" not in mock_db:
                mock_db["preset_withdrawals"] = []
            mock_db["preset_withdrawals"].append(withdrawal_record)
    
    return {
        "success": True,
        "preset_name": preset["name"],
        "total_withdrawn_usd": total_withdrawn_usd,
        "withdrawals": withdrawals,
        "message": f"Development fund preset executed - ${total_withdrawn_usd:,.0f} sent to your wallets",
        "wallet_destinations": {
            "ETH": DEV_WALLET_ADDRESSES["ETH"]["address"],
            "BTC": DEV_WALLET_ADDRESSES["BTC"]["address"], 
            "USDC": DEV_WALLET_ADDRESSES["USDC"]["address"]
        }
    }

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

@app.get("/api/cdt/pricing")
async def get_cdt_pricing():
    """Get current CDT pricing and purchase options"""
    
    cdt_price = 0.10  # $0.10 per CDT
    
    # Calculate how much CDT you can buy with each token
    purchase_options = {}
    
    for token_symbol, token_info in YOUR_PORTFOLIO.items():
        if token_info["your_balance"] > 0 and token_symbol != "CDT":
            max_usd_value = token_info["your_balance"] * token_info["current_price"]
            max_cdt_amount = max_usd_value / cdt_price
            
            purchase_options[token_symbol] = {
                "available_balance": token_info["your_balance"],
                "max_usd_value": max_usd_value,
                "max_cdt_amount": max_cdt_amount,
                "exchange_rate": f"1 {token_symbol} = {token_info['current_price'] / cdt_price:.2f} CDT",
                "liquidity_type": "high" if token_symbol in ["USDC", "DOGE", "TRX"] else "medium" if token_symbol == "CRT" else "low"
            }
    
    return {
        "cdt_price_usd": cdt_price,
        "purchase_options": purchase_options,
        "recommended_sources": {
            "liquid_assets": ["USDC", "DOGE", "TRX"],
            "illiquid_assets": ["CRT", "T52M"],
            "bridge_methods": {
                "direct": "Instant conversion for liquid assets",
                "iou": "IOU bridge for illiquid assets - immediate CDT access with future repayment"
            }
        },
        "total_purchase_power_cdt": sum(opt["max_cdt_amount"] for opt in purchase_options.values())
    }

@app.post("/api/cdt/bridge")
async def bridge_to_cdt(request: CDTBridgeRequest):
    """Bridge tokens to CDT with IOU support for illiquid assets"""
    
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
    
    # Calculate CDT amount
    source_usd_value = request.amount * source_info["current_price"]
    cdt_price = 0.10
    cdt_amount = source_usd_value / cdt_price
    
    # Determine bridge method
    illiquid_tokens = ["CRT", "T52M"]
    is_illiquid = request.source_token in illiquid_tokens
    
    bridge_method = "iou" if is_illiquid and request.bridge_type == "iou" else "direct"
    
    # Create bridge record
    bridge_id = f"cdt_bridge_{len(mock_db.get('cdt_bridges', []))}"
    
    bridge_record = {
        "bridge_id": bridge_id,
        "source_token": request.source_token,
        "source_amount": request.amount,
        "source_usd_value": source_usd_value,
        "cdt_amount": cdt_amount,
        "bridge_method": bridge_method,
        "user_wallet": request.user_wallet,
        "status": "completed",
        "timestamp": datetime.now().isoformat()
    }
    
    # Handle IOU bridge for illiquid assets
    if bridge_method == "iou":
        iou_record = {
            "iou_id": f"iou_{bridge_id}",
            "debtor_wallet": request.user_wallet,
            "debt_token": request.source_token,
            "debt_amount": request.amount,
            "debt_usd_value": source_usd_value,
            "collateral_cdt": cdt_amount,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "repayment_terms": f"Repay {request.amount:,} {request.source_token} or equivalent USD value",
            "maturity": "flexible - repay when you want"
        }
        
        bridge_record["iou_details"] = iou_record
        
        if "iou_records" not in mock_db:
            mock_db["iou_records"] = []
        mock_db["iou_records"].append(iou_record)
        
        # Don't deduct source balance for IOU (it's collateralized)
        bridge_record["balance_change"] = "collateralized - no deduction"
    else:
        # Direct bridge - deduct source balance
        YOUR_PORTFOLIO[request.source_token]["your_balance"] -= request.amount
        bridge_record["balance_change"] = f"deducted {request.amount} {request.source_token}"
    
    # Add CDT to portfolio
    YOUR_PORTFOLIO["CDT"]["your_balance"] += cdt_amount
    
    # Store bridge record
    if "cdt_bridges" not in mock_db:
        mock_db["cdt_bridges"] = []
    mock_db["cdt_bridges"].append(bridge_record)
    
    return {
        "success": True,
        "bridge_id": bridge_id,
        "method": bridge_method,
        "message": f"Successfully bridged {request.amount:,} {request.source_token} → {cdt_amount:,.2f} CDT",
        "cdt_received": cdt_amount,
        "cdt_total_balance": YOUR_PORTFOLIO["CDT"]["your_balance"],
        "bridge_details": bridge_record,
        "iou_active": bridge_method == "iou"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)