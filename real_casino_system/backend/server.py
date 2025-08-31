"""
Real Casino Savings System - Backend API
Built specifically for CRT token integration with Bridge Pool functionality and USDC/CRT conversion
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import uuid

# Import REAL system components - NO SIMULATIONS
from blockchain.real_wallet_manager import real_wallet_manager
from casino.real_casino_engine import real_casino_engine
from savings.real_savings_manager import real_savings_manager
from bridge.crt_bridge_manager import crt_bridge_manager
from conversion.real_usdc_crt_converter import real_usdc_crt_converter
from defi.real_orca_manager import real_orca_manager
from config.blockchain_config import blockchain_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="REAL Blockchain Casino - NO SIMULATIONS",
    description="REAL cryptocurrency casino with REAL CRT token integration, REAL bridge pools, and REAL USDC/CRT conversion via Jupiter aggregator",
    version="2.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# USDC TO CRT CONVERSION ENDPOINTS
# ===============================

@app.post("/api/conversion/usdc-to-crt")
async def convert_usdc_to_crt(request: Dict[str, Any]):
    """Convert USDC to CRT tokens using real DEX swaps"""
    try:
        wallet_address = request.get("wallet_address")
        usdc_amount = request.get("usdc_amount")  # Optional - if not provided, convert ALL
        
        if not wallet_address:
            raise HTTPException(status_code=400, detail="wallet_address is required")
        
        logger.info(f"💱 USDC to CRT conversion request from {wallet_address}")
        
        # Get current USDC balance
        balance_result = await real_usdc_crt_converter.get_current_usdc_balance(wallet_address)
        if not balance_result.get('success'):
            raise HTTPException(status_code=400, detail=f"Could not get USDC balance: {balance_result.get('error')}")
        
        current_usdc = balance_result.get('usdc_balance', 0.0)
        
        if current_usdc <= 0:
            return {
                "success": False,
                "error": "No USDC balance to convert",
                "current_usdc": current_usdc
            }
        
        # Determine amount to convert
        if usdc_amount is None:
            # Convert ALL USDC
            amount_to_convert = current_usdc
            conversion_type = "CONVERT_ALL_USDC"
        else:
            # Convert specified amount
            amount_to_convert = float(usdc_amount)
            conversion_type = "CONVERT_PARTIAL_USDC"
            
            if amount_to_convert > current_usdc:
                raise HTTPException(status_code=400, detail=f"Insufficient USDC: {current_usdc} < {amount_to_convert}")
        
        # Execute conversion
        conversion_result = await real_usdc_crt_converter.convert_all_usdc_to_crt(
            wallet_address, amount_to_convert
        )
        
        if conversion_result.get('success'):
            return {
                "success": True,
                "conversion_result": conversion_result,
                "conversion_type": conversion_type,
                "usdc_converted": amount_to_convert,
                "crt_received": conversion_result.get('crt_received'),
                "wallet_address": wallet_address,
                "real_conversion": True,
                "note": f"✅ REAL USDC to CRT conversion completed: {amount_to_convert} USDC → {conversion_result.get('crt_received', 0):,.0f} CRT"
            }
        else:
            return {
                "success": False,
                "error": conversion_result.get('error', 'Conversion failed'),
                "usdc_amount": amount_to_convert
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ USDC to CRT conversion failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversion/estimate-usdc-to-crt")
async def estimate_usdc_to_crt_conversion(usdc_amount: float):
    """Estimate CRT received for USDC amount"""
    try:
        logger.info(f"💡 Estimating USDC to CRT conversion: {usdc_amount} USDC")
        
        estimation = await real_usdc_crt_converter.estimate_usdc_to_crt_conversion(usdc_amount)
        
        return estimation
        
    except Exception as e:
        logger.error(f"❌ USDC to CRT estimation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversion/current-usdc-balance")
async def get_current_usdc_balance(wallet_address: str):
    """Get current USDC balance for conversion"""
    try:
        logger.info(f"💰 Getting current USDC balance for {wallet_address}")
        
        balance_result = await real_usdc_crt_converter.get_current_usdc_balance(wallet_address)
        
        return balance_result
        
    except Exception as e:
        logger.error(f"❌ Failed to get USDC balance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# CRT TOKEN WALLET ENDPOINTS
# ===============================

@app.get("/api/wallet/crt-balance")
async def get_crt_balance(wallet_address: str):
    """Get REAL CRT token balance from Solana blockchain"""
    try:
        logger.info(f"🔍 Getting REAL CRT balance for {wallet_address}")
        
        balance_result = await real_wallet_manager.get_real_solana_balance(wallet_address)
        
        if balance_result.get('success'):
            balances = balance_result.get('balances', {})
            crt_balance = balances.get('CRT', 0.0)
            
            return {
                "success": True,
                "crt_balance": crt_balance,
                "all_balances": balances,
                "wallet_address": wallet_address,
                "source": "REAL_SOLANA_BLOCKCHAIN",
                "last_updated": datetime.utcnow().isoformat(),
                "note": "✅ REAL CRT balance from Solana blockchain"
            }
        else:
            return {
                "success": False,
                "error": balance_result.get('error', 'Failed to get CRT balance'),
                "crt_balance": 0.0
            }
            
    except Exception as e:
        logger.error(f"❌ Failed to get CRT balance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wallet/all-balances")
async def get_all_balances(wallet_address: str):
    """Get all cryptocurrency balances for wallet"""
    try:
        logger.info(f"🔍 Getting all REAL balances for {wallet_address}")
        
        # Get Solana balances (CRT, SOL, USDC)
        solana_result = await real_wallet_manager.get_real_solana_balance(wallet_address)
        
        # Get Bitcoin balances (if applicable)
        bitcoin_result = await real_wallet_manager.get_real_bitcoin_balance(wallet_address)
        
        combined_balances = {}
        
        if solana_result.get('success'):
            combined_balances.update(solana_result.get('balances', {}))
        
        if bitcoin_result.get('success'):
            combined_balances.update(bitcoin_result.get('balances', {}))
        
        return {
            "success": True,
            "balances": combined_balances,
            "wallet_address": wallet_address,
            "networks": ["solana", "bitcoin"],
            "source": "REAL_BLOCKCHAIN_APIs",
            "last_updated": datetime.utcnow().isoformat(),
            "note": "✅ All balances from REAL blockchain sources"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get all balances: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# CRT BRIDGE POOL ENDPOINTS
# ===============================

@app.post("/api/bridge/create-crt-bridge-pool")
async def create_crt_bridge_pool(request: Dict[str, Any]):
    """Create REAL CRT bridge pool for cross-chain functionality"""
    try:
        wallet_address = request.get("wallet_address")
        bridge_pair = request.get("bridge_pair", "CRT/SOL")  # CRT/SOL, CRT/USDC, CRT/ETH, CRT/BTC
        target_value_usd = float(request.get("target_value_usd", 10000))  # $10K default
        
        if not wallet_address:
            raise HTTPException(status_code=400, detail="wallet_address is required")
        
        logger.info(f"🌉 Creating CRT bridge pool: {bridge_pair} worth ${target_value_usd} for {wallet_address}")
        
        # Estimate requirements
        estimation = await crt_bridge_manager.estimate_bridge_requirements(bridge_pair, target_value_usd)
        if not estimation.get('success'):
            raise HTTPException(status_code=400, detail=estimation.get('error'))
        
        required_crt = estimation['required_crt']
        
        # Verify user has enough CRT balance
        balance_result = await real_wallet_manager.get_real_solana_balance(wallet_address)
        if not balance_result.get('success'):
            raise HTTPException(status_code=400, detail="Could not verify CRT balance")
        
        crt_balance = balance_result.get('balances', {}).get('CRT', 0.0)
        if crt_balance < required_crt:
            raise HTTPException(status_code=400, detail=f"Insufficient CRT balance: {crt_balance:,.0f} < {required_crt:,.0f}")
        
        # Create bridge pool
        bridge_result = await crt_bridge_manager.create_bridge_pool(
            wallet_address=wallet_address,
            bridge_pair=bridge_pair,
            crt_amount=required_crt,
            target_value_usd=target_value_usd
        )
        
        if bridge_result.get('success'):
            return {
                "success": True,
                "bridge_result": bridge_result,
                "bridge_pair": bridge_pair,
                "target_value_usd": target_value_usd,
                "required_crt": required_crt,
                "wallet_address": wallet_address,
                "real_bridge_pool": True,
                "note": f"✅ REAL {bridge_pair} bridge pool created for cross-chain CRT transfers"
            }
        else:
            return {
                "success": False,
                "error": bridge_result.get('error', 'Bridge pool creation failed'),
                "bridge_pair": bridge_pair,
                "target_value_usd": target_value_usd
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CRT bridge pool creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bridge/estimate-requirements")
async def estimate_bridge_requirements(bridge_pair: str, target_value_usd: float):
    """Estimate CRT and other token requirements for bridge pool"""
    try:
        logger.info(f"💡 Estimating bridge requirements: {bridge_pair} worth ${target_value_usd}")
        
        estimation = await crt_bridge_manager.estimate_bridge_requirements(bridge_pair, target_value_usd)
        
        return estimation
        
    except Exception as e:
        logger.error(f"❌ Bridge estimation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bridge/supported-pairs")
async def get_supported_bridge_pairs():
    """Get all supported CRT bridge pairs"""
    try:
        return {
            "success": True,
            "bridge_pairs": crt_bridge_manager.supported_bridge_pairs,
            "note": "All bridge pairs support REAL cross-chain CRT transfers"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get bridge pairs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bridge/crt-summary")
async def get_crt_bridge_summary(wallet_address: str):
    """Get comprehensive CRT bridge pools summary"""
    try:
        logger.info(f"📊 Getting CRT bridge summary for {wallet_address}")
        
        bridge_summary = await crt_bridge_manager.get_bridge_pools_summary(wallet_address)
        
        return {
            "success": True,
            "bridge_summary": bridge_summary,
            "wallet_address": wallet_address,
            "last_updated": datetime.utcnow().isoformat(),
            "note": "CRT bridge pools and cross-chain functionality summary"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get CRT bridge summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# CRT CASINO BETTING ENDPOINTS
# ===============================

@app.post("/api/casino/bet-crt")
async def place_crt_bet(request: Dict[str, Any]):
    """Place REAL CRT token bet in casino games"""
    try:
        wallet_address = request.get("wallet_address")
        game = request.get("game", "slots")
        bet_amount = float(request.get("bet_amount", 0))
        game_params = request.get("game_params", {})
        
        if not wallet_address or bet_amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid wallet address or bet amount")
        
        logger.info(f"🎰 REAL CRT bet: {bet_amount} CRT on {game} by {wallet_address}")
        
        # Verify user has enough CRT balance
        balance_result = await real_wallet_manager.get_real_solana_balance(wallet_address)
        if not balance_result.get('success'):
            raise HTTPException(status_code=400, detail="Could not verify CRT balance")
        
        crt_balance = balance_result.get('balances', {}).get('CRT', 0.0)
        if crt_balance < bet_amount:
            raise HTTPException(status_code=400, detail=f"Insufficient CRT balance: {crt_balance} < {bet_amount}")
        
        # Place real bet
        bet_result = await real_casino_engine.place_real_bet(
            wallet_address=wallet_address,
            game=game,
            bet_amount=bet_amount,
            currency="CRT",
            game_params=game_params
        )
        
        if bet_result.get('success'):
            # If user lost, convert loss to savings
            if not bet_result.get('won'):
                loss_amount = bet_amount
                savings_result = await real_savings_manager.process_gaming_loss(
                    wallet_address=wallet_address,
                    loss_amount=loss_amount,
                    currency="CRT",
                    game_data=bet_result
                )
                bet_result['savings_created'] = savings_result
            
            return {
                "success": True,
                "bet_result": bet_result,
                "game": game,
                "bet_amount": bet_amount,
                "currency": "CRT",
                "wallet_address": wallet_address,
                "real_cryptocurrency_bet": True,
                "note": "✅ REAL CRT token bet with actual payout/loss"
            }
        else:
            return {
                "success": False,
                "error": bet_result.get('error', 'Bet failed'),
                "bet_amount": bet_amount,
                "currency": "CRT"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CRT bet failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/casino/games")
async def get_available_games():
    """Get list of available casino games for CRT betting"""
    try:
        games = {
            "slots": {
                "name": "CRT Slots",
                "description": "Classic slot machine with CRT token betting",
                "min_bet": blockchain_config.CASINO_CONFIG['min_bet_amounts']['CRT'],
                "max_bet": blockchain_config.CASINO_CONFIG['max_bet_amounts']['CRT'],
                "house_edge": blockchain_config.CASINO_CONFIG['house_edge'],
                "max_multiplier": 10.0
            },
            "blackjack": {
                "name": "CRT Blackjack", 
                "description": "Classic blackjack with CRT token stakes",
                "min_bet": blockchain_config.CASINO_CONFIG['min_bet_amounts']['CRT'],
                "max_bet": blockchain_config.CASINO_CONFIG['max_bet_amounts']['CRT'],
                "house_edge": blockchain_config.CASINO_CONFIG['house_edge'],
                "max_multiplier": 2.5
            },
            "roulette": {
                "name": "CRT Roulette",
                "description": "European roulette with CRT token betting",
                "min_bet": blockchain_config.CASINO_CONFIG['min_bet_amounts']['CRT'],
                "max_bet": blockchain_config.CASINO_CONFIG['max_bet_amounts']['CRT'],
                "house_edge": blockchain_config.CASINO_CONFIG['house_edge'],
                "max_multiplier": 36.0
            },
            "dice": {
                "name": "CRT Dice",
                "description": "Provably fair dice with CRT tokens",
                "min_bet": blockchain_config.CASINO_CONFIG['min_bet_amounts']['CRT'],
                "max_bet": blockchain_config.CASINO_CONFIG['max_bet_amounts']['CRT'],
                "house_edge": blockchain_config.CASINO_CONFIG['house_edge'],
                "max_multiplier": 99.0
            }
        }
        
        return {
            "success": True,
            "games": games,
            "currency": "CRT",
            "note": "All games support REAL CRT token betting"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get games: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# CRT SAVINGS SYSTEM ENDPOINTS
# ===============================

@app.post("/api/savings/create-crt-pool")
async def create_crt_savings_pool(request: Dict[str, Any]):
    """Create REAL CRT liquidity pool for savings"""
    try:
        wallet_address = request.get("wallet_address")
        crt_amount = float(request.get("crt_amount", 0))
        pool_type = request.get("pool_type", "CRT/SOL")  # CRT/SOL or CRT/USDC
        
        if not wallet_address or crt_amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid parameters")
        
        logger.info(f"🏊‍♂️ Creating REAL CRT savings pool: {crt_amount} CRT for {pool_type}")
        
        # Verify CRT balance
        balance_result = await real_wallet_manager.get_real_solana_balance(wallet_address)
        if not balance_result.get('success'):
            raise HTTPException(status_code=400, detail="Could not verify CRT balance")
        
        crt_balance = balance_result.get('balances', {}).get('CRT', 0.0)
        if crt_balance < crt_amount:
            raise HTTPException(status_code=400, detail=f"Insufficient CRT balance: {crt_balance} < {crt_amount}")
        
        # Create savings pool
        if pool_type == "CRT/SOL":
            pool_result = await real_savings_manager._create_orca_pool(wallet_address, crt_amount, "CRT")
        elif pool_type == "CRT/USDC":
            pool_result = await real_savings_manager._create_orca_pool(wallet_address, crt_amount, "CRT")
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported pool type: {pool_type}")
        
        if pool_result.get('success'):
            return {
                "success": True,
                "pool_result": pool_result,
                "crt_amount": crt_amount,
                "pool_type": pool_type,
                "wallet_address": wallet_address,
                "real_liquidity_pool": True,
                "note": "✅ REAL CRT liquidity pool created on Orca DEX"
            }
        else:
            return {
                "success": False,
                "error": pool_result.get('error', 'Pool creation failed'),
                "crt_amount": crt_amount,
                "pool_type": pool_type
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CRT pool creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/savings/crt-summary")
async def get_crt_savings_summary(wallet_address: str):
    """Get comprehensive CRT savings summary"""
    try:
        logger.info(f"📊 Getting CRT savings summary for {wallet_address}")
        
        savings_summary = await real_savings_manager.get_savings_summary(wallet_address)
        
        return {
            "success": True,
            "savings_summary": savings_summary,
            "wallet_address": wallet_address,
            "currency_focus": "CRT",
            "last_updated": datetime.utcnow().isoformat(),
            "note": "CRT token savings and investment summary"
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get CRT savings summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# CRT WITHDRAWAL ENDPOINTS
# ===============================

@app.post("/api/wallet/withdraw-crt")
async def withdraw_crt(request: Dict[str, Any]):
    """Execute REAL CRT token withdrawal to external wallet"""
    try:
        from_address = request.get("from_address")
        to_address = request.get("to_address")
        amount = float(request.get("amount", 0))
        
        if not all([from_address, to_address, amount]):
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        logger.info(f"💸 REAL CRT withdrawal: {amount} CRT from {from_address} to {to_address}")
        
        # Verify CRT balance
        balance_result = await real_wallet_manager.get_real_solana_balance(from_address)
        if not balance_result.get('success'):
            raise HTTPException(status_code=400, detail="Could not verify CRT balance")
        
        crt_balance = balance_result.get('balances', {}).get('CRT', 0.0)
        if crt_balance < amount:
            raise HTTPException(status_code=400, detail=f"Insufficient CRT balance: {crt_balance} < {amount}")
        
        # Check withdrawal limits
        daily_limit = blockchain_config.WITHDRAWAL_LIMITS['daily_limits']['CRT']
        min_withdrawal = blockchain_config.WITHDRAWAL_LIMITS['min_withdrawal']['CRT']
        
        if amount > daily_limit:
            raise HTTPException(status_code=400, detail=f"Amount exceeds daily limit: {daily_limit} CRT")
        
        if amount < min_withdrawal:
            raise HTTPException(status_code=400, detail=f"Amount below minimum: {min_withdrawal} CRT")
        
        # Execute real withdrawal
        withdrawal_result = await real_wallet_manager.execute_real_withdrawal(
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            currency="CRT"
        )
        
        if withdrawal_result.get('success'):
            return {
                "success": True,
                "withdrawal_result": withdrawal_result,
                "amount": amount,
                "currency": "CRT",
                "from_address": from_address,
                "to_address": to_address,
                "real_withdrawal": True,
                "note": "✅ REAL CRT token withdrawal to external wallet"
            }
        else:
            return {
                "success": False,
                "error": withdrawal_result.get('error', 'Withdrawal failed'),
                "amount": amount,
                "currency": "CRT"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ CRT withdrawal failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===============================
# SYSTEM STATUS ENDPOINTS
# ===============================

@app.get("/api/system/status")
async def get_system_status():
    """Get real casino savings system status"""
    try:
        return {
            "success": True,
            "system": "Real Casino Savings System with CRT Bridge Pools and USDC Conversion",
            "version": "1.0.0",
            "primary_currency": "CRT",
            "supported_networks": ["Solana", "Ethereum", "Bitcoin", "TRON"],
            "features": {
                "real_cryptocurrency_betting": True,
                "real_blockchain_withdrawals": True,
                "real_dex_pool_creation": True,
                "real_bridge_pools": True,
                "real_usdc_crt_conversion": True,
                "real_balance_checking": True,
                "cross_chain_transfers": True,
                "fake_transactions": False,
                "simulated_balances": False
            },
            "casino_games": ["slots", "blackjack", "roulette", "dice"],
            "savings_strategies": ["dex_pools", "yield_farming", "compound_savings"],
            "bridge_pairs": ["CRT/SOL", "CRT/USDC", "CRT/ETH", "CRT/BTC"],
            "conversion_pairs": ["USDC/CRT"],
            "status": "OPERATIONAL",
            "timestamp": datetime.utcnow().isoformat(),
            "note": "✅ Real cryptocurrency system with bridge pools and USDC conversion - NO SIMULATIONS"
        }
        
    except Exception as e:
        logger.error(f"❌ System status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Real Casino Savings System with CRT Bridge Pools and USDC Conversion API",
        "status": "OPERATIONAL",
        "primary_currency": "CRT",
        "real_cryptocurrency": True,
        "bridge_pools_supported": True,
        "usdc_crt_conversion": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)