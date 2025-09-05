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

# Payment integrations
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Tiger Bank Games API",
    description="Gaming that grows your wealth with real payments & token bridges!",
    version="2.0.0"
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

# Initialize Stripe
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
stripe_checkout = None

if STRIPE_API_KEY:
    try:
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url="")
        logger.info("✅ Stripe integration initialized")
    except Exception as e:
        logger.error(f"❌ Stripe initialization failed: {e}")

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

class DepositRequest(BaseModel):
    package_id: str
    origin_url: str

class WithdrawRequest(BaseModel):
    amount: float
    from_account: str  # "savings" or "pools"
    origin_url: str

class PaymentTransaction(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    currency: str
    transaction_type: str  # "deposit" or "withdraw"
    status: str
    session_id: Optional[str]
    created_at: datetime

class BridgeSwapRequest(BaseModel):
    from_wallet: str
    token_in_address: str
    token_in_amount: str
    token_out_address: str
    token_out_min_amount: str
    chain_id: int = 42161  # Arbitrum

# Deposit packages (predefined for security)
DEPOSIT_PACKAGES = {
    "starter": {"amount": 10.0, "bonus_balance": 1000.0, "description": "Starter Package"},
    "high_roller": {"amount": 25.0, "bonus_balance": 2500.0, "description": "High Roller Package"},
    "vip": {"amount": 50.0, "bonus_balance": 5000.0, "description": "VIP Package"}
}

# Mock database (replace with real database in production)
mock_db = {
    "users": {
        "user123": {
            "balance": 1000.0,
            "savings": 250.0,
            "pool_allocation": 250.0,
            "total_losses": 1000.0
        }
    },
    "payment_transactions": []
}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Tiger Bank Games API v2.0",
        "description": "Gaming that grows your wealth with real payments & token bridges!",
        "version": "2.0.0",
        "features": [
            "🎰 Casino Games (Blackjack, Roulette, Slots)",
            "🐷 Smart Loss Allocation (50% savings, 50% pools)",
            "💳 Real Money Deposits (Stripe)",
            "💰 Secure Withdrawals",
            "🌉 Cross-chain Token Bridge",
            "📊 Transaction History"
        ]
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    integrations = {
        "stripe": stripe_checkout is not None,
        "database": True,  # Mock database always available
        "casino_engine": True
    }
    
    return {
        "status": "healthy",
        "service": "tiger-bank-games",
        "integrations": integrations,
        "version": "2.0.0"
    }

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

# === STRIPE PAYMENT ENDPOINTS ===

@app.get("/api/payments/packages")
async def get_deposit_packages():
    """Get available deposit packages"""
    return {"packages": DEPOSIT_PACKAGES}

@app.post("/api/payments/deposit")
async def create_deposit_session(request: DepositRequest):
    """Create Stripe checkout session for deposit"""
    if not stripe_checkout:
        raise HTTPException(status_code=503, detail="Payment service unavailable")
    
    # Validate package
    if request.package_id not in DEPOSIT_PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package selected")
    
    package = DEPOSIT_PACKAGES[request.package_id]
    amount = package["amount"]
    
    # Create success and cancel URLs
    success_url = f"{request.origin_url}/deposit-success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{request.origin_url}/deposit-cancel"
    
    try:
        # Create checkout session
        checkout_request = CheckoutSessionRequest(
            amount=amount,
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "package_id": request.package_id,
                "user_id": "user123",  # In real app, get from auth
                "transaction_type": "deposit"
            }
        )
        
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Create pending transaction record
        transaction = {
            "transaction_id": f"dep_{session.session_id}",
            "user_id": "user123",
            "amount": amount,
            "currency": "usd",
            "transaction_type": "deposit",
            "status": "pending",
            "session_id": session.session_id,
            "created_at": datetime.now(),
            "package_id": request.package_id
        }
        mock_db["payment_transactions"].append(transaction)
        
        return {
            "checkout_url": session.url,
            "session_id": session.session_id,
            "amount": amount,
            "package": package
        }
        
    except Exception as e:
        logger.error(f"Deposit session creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment session")

@app.post("/api/payments/withdraw")
async def create_withdraw_session(request: WithdrawRequest):
    """Create withdrawal session"""
    if not stripe_checkout:
        raise HTTPException(status_code=503, detail="Payment service unavailable")
    
    user_data = mock_db["users"]["user123"]
    
    # Validate withdrawal amount and source
    if request.from_account == "savings":
        available = user_data["savings"]
    elif request.from_account == "pools":
        available = user_data["pool_allocation"]
    else:
        raise HTTPException(status_code=400, detail="Invalid account type")
    
    if request.amount > available:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    # Create withdrawal record (in real app, integrate with Stripe Express/Connect)
    transaction = {
        "transaction_id": f"with_{len(mock_db['payment_transactions'])}",
        "user_id": "user123",
        "amount": request.amount,
        "currency": "usd",
        "transaction_type": "withdraw",
        "status": "processing",
        "from_account": request.from_account,
        "created_at": datetime.now()
    }
    mock_db["payment_transactions"].append(transaction)
    
    # Update user balance
    if request.from_account == "savings":
        user_data["savings"] -= request.amount
    else:
        user_data["pool_allocation"] -= request.amount
    
    return {
        "message": "Withdrawal initiated",
        "transaction_id": transaction["transaction_id"],
        "amount": request.amount,
        "from_account": request.from_account,
        "estimated_completion": "2-3 business days"
    }

@app.get("/api/payments/status/{session_id}")
async def get_payment_status(session_id: str):
    """Get payment status"""
    if not stripe_checkout:
        raise HTTPException(status_code=503, detail="Payment service unavailable")
    
    try:
        status_response = await stripe_checkout.get_checkout_status(session_id)
        
        # Find transaction in database
        transaction = None
        for t in mock_db["payment_transactions"]:
            if t.get("session_id") == session_id:
                transaction = t
                break
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Update transaction status if payment completed
        if status_response.payment_status == "paid" and transaction["status"] == "pending":
            transaction["status"] = "completed"
            
            # Add balance if deposit
            if transaction["transaction_type"] == "deposit":
                package_id = transaction.get("package_id")
                if package_id in DEPOSIT_PACKAGES:
                    bonus_balance = DEPOSIT_PACKAGES[package_id]["bonus_balance"]
                    mock_db["users"]["user123"]["balance"] += bonus_balance
        
        return {
            "session_id": session_id,
            "status": status_response.status,
            "payment_status": status_response.payment_status,
            "amount": status_response.amount_total / 100,  # Convert from cents
            "currency": status_response.currency,
            "transaction": transaction
        }
        
    except Exception as e:
        logger.error(f"Payment status check failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to check payment status")

@app.post("/api/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    if not stripe_checkout:
        raise HTTPException(status_code=503, detail="Payment service unavailable")
    
    try:
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Handle webhook events
        if webhook_response.event_type == "checkout.session.completed":
            # Update transaction status
            for transaction in mock_db["payment_transactions"]:
                if transaction.get("session_id") == webhook_response.session_id:
                    transaction["status"] = "completed"
                    break
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Webhook handling failed: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")

# === THIRDWEB BRIDGE ENDPOINTS ===

@app.post("/api/bridge/quote")
async def get_bridge_quote(request: BridgeSwapRequest):
    """Get quote for cross-chain token swap"""
    # This would integrate with thirdweb bridge API
    # For now, return mock quote
    return {
        "quote_id": "quote_123",
        "from_token": request.token_in_address,
        "to_token": request.token_out_address,
        "from_amount": request.token_in_amount,
        "to_amount": request.token_out_min_amount,
        "estimated_gas": "0.002",
        "bridge_fee": "0.1%",
        "estimated_time": "2-5 minutes"
    }

@app.post("/api/bridge/swap")
async def execute_bridge_swap(request: BridgeSwapRequest):
    """Execute cross-chain token swap"""
    # This would integrate with thirdweb bridge API
    # For now, return mock response
    return {
        "swap_id": "swap_123",
        "status": "initiated",
        "transaction_hash": "0x123...",
        "estimated_completion": "2-5 minutes",
        "message": "Swap initiated successfully"
    }

@app.get("/api/transactions/{user_id}")
async def get_user_transactions(user_id: str):
    """Get user transaction history"""
    user_transactions = [
        t for t in mock_db["payment_transactions"] 
        if t["user_id"] == user_id
    ]
    
    return {
        "user_id": user_id,
        "transactions": user_transactions,
        "total_count": len(user_transactions)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)