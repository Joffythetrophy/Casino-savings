"""
Real Blockchain Service - Executes actual cryptocurrency transactions
This replaces the fake transaction system with real blockchain operations
"""

import asyncio
import subprocess
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from config.hot_wallet_config import hot_wallet_config

logger = logging.getLogger(__name__)

class RealBlockchainService:
    """Service for executing real blockchain transactions"""
    
    def __init__(self):
        self.config = hot_wallet_config
        self.transaction_log = []
    
    async def execute_real_withdrawal(
        self, 
        from_address: str, 
        to_address: str, 
        amount: float, 
        currency: str
    ) -> Dict[str, Any]:
        """Execute real blockchain withdrawal transaction"""
        
        try:
            # Validate configuration
            validation = self.config.validate_private_keys()
            if not validation['valid']:
                return {
                    "success": False,
                    "error": f"Hot wallet not configured: {validation['message']}",
                    "requires_setup": True
                }
            
            # Validate transaction limits
            if not self._validate_transaction_limits(amount, currency):
                return {
                    "success": False,
                    "error": f"Transaction exceeds limits: {amount} {currency}",
                    "max_allowed": self.config.max_transaction_amount.get(currency, 0)
                }
            
            # Execute blockchain transaction based on currency
            if currency in ['USDC', 'CRT', 'SOL']:
                return await self._execute_solana_transaction(to_address, amount, currency)
            elif currency == 'DOGE':
                return await self._execute_doge_transaction(to_address, amount)
            elif currency == 'TRX':
                return await self._execute_tron_transaction(to_address, amount)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported currency for real transactions: {currency}"
                }
        
        except Exception as e:
            logger.error(f"Real blockchain transaction failed: {str(e)}")
            return {
                "success": False,
                "error": f"Blockchain transaction error: {str(e)}"
            }
    
    async def _execute_solana_transaction(self, to_address: str, amount: float, currency: str) -> Dict[str, Any]:
        """Execute REAL Solana blockchain transaction using real_solana_manager"""
        
        try:
            # Import the real solana manager
            from blockchain.solana_real_manager import real_solana_manager
            
            # Execute REAL blockchain transaction based on currency
            if currency == 'SOL':
                result = await real_solana_manager.send_real_sol(to_address, amount)
            elif currency == 'USDC':
                result = await real_solana_manager.send_real_usdc(to_address, amount)
            elif currency == 'CRT':
                result = await real_solana_manager.send_real_crt(to_address, amount)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported Solana token: {currency}"
                }
            
            if result.get("success"):
                # Log successful REAL transaction
                self._log_transaction(to_address, amount, currency, result.get("transaction_hash"))
                
                return {
                    "success": True,
                    "transaction_hash": result.get("transaction_hash"),
                    "blockchain": "Solana",
                    "explorer_url": result.get("explorer_url"),
                    "amount": amount,
                    "currency": currency,
                    "timestamp": datetime.utcnow().isoformat(),
                    "real_transaction": True,
                    "note": "✅ GENUINE Solana blockchain transaction - NOT simulated"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Solana transaction failed")
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Solana transaction exception: {str(e)}"
            }
    
    async def _execute_doge_transaction(self, to_address: str, amount: float) -> Dict[str, Any]:
        """Execute real Dogecoin blockchain transaction"""
        
        try:
            # Call the real DOGE manager
            command = [
                'node', '-e', f'''
                const RealDogeManager = require('./blockchain/real_doge_manager.js');
                const manager = new RealDogeManager();
                
                manager.sendDoge({{
                    toAddress: "{to_address}",
                    amount: {amount},
                    fromPrivateKey: process.env.DOGE_HOT_WALLET_PRIVATE_KEY
                }}).then(result => {{
                    console.log(JSON.stringify(result));
                }}).catch(err => {{
                    console.log(JSON.stringify({{success: false, error: err.message}}));
                }});
                '''
            ]
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/app/backend"
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                result = json.loads(stdout.decode())
                
                if result.get("success"):
                    self._log_transaction(to_address, amount, "DOGE", result.get("transaction_hash"))
                    
                    return {
                        "success": True,
                        "transaction_hash": result.get("transaction_hash"),
                        "blockchain": "Dogecoin",
                        "explorer_url": f"https://dogechain.info/tx/{result.get('transaction_hash')}",
                        "amount": amount,
                        "currency": "DOGE",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get("error", "DOGE transaction failed")
                    }
            else:
                error_msg = stderr.decode() if stderr else "Process failed"
                return {
                    "success": False,
                    "error": f"DOGE execution error: {error_msg}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"DOGE transaction exception: {str(e)}"
            }
    
    async def _execute_tron_transaction(self, to_address: str, amount: float) -> Dict[str, Any]:
        """Execute real TRON blockchain transaction"""
        
        # Similar structure to above methods
        return {
            "success": False,
            "error": "TRON real transactions not implemented yet - requires TronWeb integration"
        }
    
    def _validate_transaction_limits(self, amount: float, currency: str) -> bool:
        """Validate transaction against security limits"""
        max_amount = self.config.max_transaction_amount.get(currency, 0)
        return amount <= max_amount
    
    def _log_transaction(self, to_address: str, amount: float, currency: str, tx_hash: str):
        """Log successful transaction"""
        self.transaction_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "to_address": to_address,
            "amount": amount,
            "currency": currency,
            "transaction_hash": tx_hash,
            "status": "completed"
        })
    
    async def setup_crt_funded_hot_wallet(self, user_wallet_address: str, crt_amount: float) -> Dict[str, Any]:
        """Set up hot wallet using user's CRT tokens as funding"""
        
        try:
            # Validate user has sufficient CRT
            import asyncio
            from motor.motor_asyncio import AsyncIOMotorClient
            import os
            
            mongo_url = os.environ['MONGO_URL']
            client = AsyncIOMotorClient(mongo_url)
            db = client[os.environ['DB_NAME']]
            
            user = await db.users.find_one({"wallet_address": user_wallet_address})
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Calculate total CRT available
            total_crt = 0
            for balance_type in ['deposit_balance', 'winnings_balance', 'gaming_balance', 'savings_balance']:
                total_crt += user.get(balance_type, {}).get('CRT', 0)
            
            if total_crt < crt_amount:
                return {
                    "success": False,
                    "error": f"Insufficient CRT. Available: {total_crt}, Requested: {crt_amount}"
                }
            
            # Create hot wallet using CRT as collateral
            # Since CRT is on Solana, we can use the CRT mint address as the base
            hot_wallet_setup = {
                "funding_source": "CRT_TOKENS",
                "crt_collateral": crt_amount,
                "usd_value": crt_amount * 0.01,  # CRT at $0.01
                "wallet_currencies": {
                    "CRT": crt_amount,
                    "USDC_equivalent": crt_amount * 0.01,  # Convert CRT to USDC equivalent
                    "SOL_equivalent": (crt_amount * 0.01) / 100  # Convert to SOL equivalent at $100/SOL
                },
                "status": "CRT_FUNDED_READY"
            }
            
            # Allocate CRT from user balances to hot wallet
            crt_allocated = 0
            balance_updates = {}
            
            # Allocate from deposit first
            deposit_crt = user.get('deposit_balance', {}).get('CRT', 0)
            if deposit_crt > 0 and crt_allocated < crt_amount:
                take_from_deposit = min(deposit_crt, crt_amount - crt_allocated)
                balance_updates['deposit_balance.CRT'] = deposit_crt - take_from_deposit
                crt_allocated += take_from_deposit
            
            # Allocate from gaming if needed
            if crt_allocated < crt_amount:
                gaming_crt = user.get('gaming_balance', {}).get('CRT', 0)
                if gaming_crt > 0:
                    take_from_gaming = min(gaming_crt, crt_amount - crt_allocated)
                    balance_updates['gaming_balance.CRT'] = gaming_crt - take_from_gaming
                    crt_allocated += take_from_gaming
            
            # Update user balances (move CRT to hot wallet)
            if balance_updates:
                await db.users.update_one(
                    {"wallet_address": user_wallet_address},
                    {"$set": balance_updates}
                )
            
            # Create hot wallet record
            hot_wallet_record = {
                "wallet_id": f"hot_wallet_{user_wallet_address[:8]}",
                "funded_by": user_wallet_address,
                "funding_source": "CRT_TOKENS", 
                "crt_balance": crt_allocated,
                "equivalent_values": {
                    "USDC": crt_allocated * 0.01,
                    "SOL": (crt_allocated * 0.01) / 100,
                    "BTC": (crt_allocated * 0.01) / 50000  # Rough BTC equivalent
                },
                "created_at": datetime.utcnow(),
                "status": "ACTIVE",
                "transaction_limits": {
                    "max_per_tx": min(100000, crt_allocated * 0.1),  # 10% of funding or $100K max
                    "daily_limit": min(1000000, crt_allocated * 0.5)  # 50% of funding or $1M max
                }
            }
            
            await db.hot_wallets.insert_one(hot_wallet_record)
            
            return {
                "success": True,
                "message": f"Hot wallet funded with {crt_allocated:,.0f} CRT tokens",
                "hot_wallet": hot_wallet_setup,
                "funding_summary": {
                    "crt_allocated": crt_allocated,
                    "usd_equivalent": crt_allocated * 0.01,
                    "transaction_capacity": f"${min(100000, crt_allocated * 0.1):,.0f} per transaction",
                    "daily_capacity": f"${min(1000000, crt_allocated * 0.5):,.0f} per day"
                },
                "status": "HOT_WALLET_ACTIVE"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Hot wallet setup failed: {str(e)}"
            }
    
    async def execute_crt_funded_transfer(
        self, 
        from_address: str, 
        to_address: str, 
        amount: float, 
        currency: str
    ) -> Dict[str, Any]:
        """Execute transfer using CRT-funded hot wallet system"""
        
        try:
            # Check if hot wallet exists and has sufficient CRT funding
            import asyncio
            from motor.motor_asyncio import AsyncIOMotorClient
            import os
            
            mongo_url = os.environ['MONGO_URL']
            client = AsyncIOMotorClient(mongo_url)
            db = client[os.environ['DB_NAME']]
            
            hot_wallet = await db.hot_wallets.find_one({"funded_by": from_address})
            
            if not hot_wallet:
                return {
                    "success": False,
                    "error": "No CRT-funded hot wallet found"
                }
            
            if hot_wallet.get('status') != 'ACTIVE':
                return {
                    "success": False,
                    "error": "CRT hot wallet not active"
                }
            
            # Calculate equivalent values
            if currency == 'CRT':
                required_crt = amount
            elif currency == 'USDC':
                required_crt = amount / 0.01  # Convert USDC to CRT at $0.01 rate
            elif currency == 'SOL':
                required_crt = amount * 100 / 0.01  # SOL at ~$100, CRT at $0.01
            else:
                return {
                    "success": False,
                    "error": f"Currency {currency} not supported by CRT hot wallet"
                }
            
            # Check funding capacity
            available_crt = hot_wallet.get('crt_balance', 0)
            if required_crt > available_crt:
                return {
                    "success": False,
                    "error": f"Insufficient CRT funding. Need {required_crt:,.0f}, have {available_crt:,.0f}"
                }
            
            # Since CRT is a REAL Solana SPL token, use the real solana manager
            from blockchain.solana_real_manager import real_solana_manager
            
            # Execute REAL CRT transfer 
            result = await real_solana_manager.send_real_crt(to_address, required_crt)
            
            if not result.get("success"):
                return result
            
            transaction_hash = result.get("transaction_hash")
            
            # Update hot wallet balance
            new_crt_balance = available_crt - required_crt
            await db.hot_wallets.update_one(
                {"funded_by": from_address},
                {
                    "$set": {"crt_balance": new_crt_balance},
                    "$push": {
                        "transaction_history": {
                            "timestamp": datetime.utcnow(),
                            "to_address": to_address,
                            "amount": amount,
                            "currency": currency,
                            "crt_cost": required_crt,
                            "transaction_hash": transaction_hash,
                            "status": "completed"
                        }
                    }
                }
            )
            
            # Log the transfer
            self._log_transaction(to_address, amount, currency, transaction_hash)
            
            return {
                "success": True,
                "transaction_hash": transaction_hash,
                "blockchain": "Solana (CRT-funded)",
                "explorer_url": result.get("explorer_url"),
                "amount": amount,
                "currency": currency,
                "funding_source": "CRT_TOKENS",
                "crt_cost": required_crt,
                "remaining_crt_balance": new_crt_balance,
                "timestamp": datetime.utcnow().isoformat(),
                "real_transaction": True,
                "note": f"✅ REAL transfer funded by {required_crt:,.0f} CRT tokens from hot wallet"
            }
            
        except Exception as e:
            logger.error(f"CRT-funded transfer failed: {str(e)}")
            return {
                "success": False,
                "error": f"CRT-funded transfer error: {str(e)}"
            }

    async def execute_direct_crt_transfer(
        self, 
        from_address: str, 
        to_address: str, 
        amount: float, 
        currency: str
    ) -> Dict[str, Any]:
        """Direct transfer using CRT tokens from user balance (no hot wallet needed)"""
        
        try:
            # Connect to database to get user's actual CRT balances
            import asyncio
            from motor.motor_asyncio import AsyncIOMotorClient
            import os
            
            mongo_url = os.environ['MONGO_URL']
            client = AsyncIOMotorClient(mongo_url)
            db = client[os.environ['DB_NAME']]
            
            user = await db.users.find_one({"wallet_address": from_address})
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Calculate total available CRT across all balance types
            total_crt = 0
            crt_sources = {}
            for balance_type in ['deposit_balance', 'winnings_balance', 'gaming_balance', 'savings_balance']:
                crt_amount = user.get(balance_type, {}).get('CRT', 0)
                if crt_amount > 0:
                    crt_sources[balance_type] = crt_amount
                    total_crt += crt_amount
            
            # Calculate CRT cost for the transfer
            if currency == 'CRT':
                required_crt = amount
            elif currency == 'USDC':
                required_crt = amount / 0.01  # $1 USDC = 100 CRT at $0.01 rate
            elif currency == 'SOL':
                required_crt = amount * 100 / 0.01  # 1 SOL = ~$100, so 10,000 CRT
            else:
                return {"success": False, "error": f"Currency {currency} not supported"}
            
            if total_crt < required_crt:
                return {
                    "success": False,
                    "error": f"Insufficient CRT. Need {required_crt:,.0f}, have {total_crt:,.0f}"
                }
            
            # Deduct CRT from user balances (prioritize deposit first)
            remaining_to_deduct = required_crt
            balance_updates = {}
            
            for balance_type in ['deposit_balance', 'gaming_balance', 'winnings_balance', 'savings_balance']:
                if remaining_to_deduct <= 0:
                    break
                
                available = crt_sources.get(balance_type, 0)
                if available > 0:
                    deduct_amount = min(available, remaining_to_deduct)
                    new_balance = available - deduct_amount
                    balance_updates[f"{balance_type}.CRT"] = new_balance
                    remaining_to_deduct -= deduct_amount
            
            # Update user balances
            if balance_updates:
                await db.users.update_one(
                    {"wallet_address": from_address},
                    {"$set": balance_updates}
                )
            
            # Use real solana manager for CRT transfers
            from blockchain.solana_real_manager import real_solana_manager
            
            # Execute REAL CRT transfer
            result = await real_solana_manager.send_real_crt(to_address, required_crt)
            
            if not result.get("success"):
                return result
            
            transaction_hash = result.get("transaction_hash")
            
            # Log the transaction  
            self._log_transaction(to_address, amount, currency, transaction_hash)
            
            return {
                "success": True,
                "transaction_hash": transaction_hash,
                "blockchain": "Solana (Direct CRT)",
                "explorer_url": f"https://explorer.solana.com/tx/{transaction_hash}",
                "amount": amount,
                "currency": currency,
                "funding_source": "DIRECT_CRT_BALANCE",
                "crt_cost": required_crt,
                "remaining_crt_total": total_crt - required_crt,
                "timestamp": datetime.utcnow().isoformat(),
                "note": f"✅ Transfer funded directly by {required_crt:,.0f} CRT tokens from user balance"
            }
            
        except Exception as e:
            logger.error(f"Direct CRT transfer failed: {str(e)}")
            return {
                "success": False,
                "error": f"Direct CRT transfer error: {str(e)}"
            }

# Global service instance
real_blockchain_service = RealBlockchainService()