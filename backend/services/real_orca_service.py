"""
Real Orca Service - Production Ready Pool Creation
Interfaces with the Node.js Real Orca Manager for actual liquidity pool creation
"""

import asyncio
import json
import logging
import subprocess
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RealOrcaService:
    def __init__(self):
        self.orca_manager_path = "/app/backend/blockchain/real_orca_manager.js"
        
        # Default pool configurations
        self.pool_configs = {
            "CRT/SOL": {
                "initial_crt_amount": 1000000,  # 1M CRT tokens
                "initial_sol_amount": 100,      # 100 SOL (~$10,000)
                "description": "CRT Tiger Token / Solana Native Pool"
            },
            "CRT/USDC": {
                "initial_crt_amount": 1000000,  # 1M CRT tokens  
                "initial_usdc_amount": 10000,   # $10,000 USDC
                "description": "CRT Tiger Token / USD Coin Stable Pool"
            }
        }
    
    async def create_real_crt_sol_pool(self, initial_crt: float = None, initial_sol: float = None) -> Dict[str, Any]:
        """Create actual CRT/SOL liquidity pool on Orca"""
        try:
            logger.info("🌊 Creating REAL CRT/SOL pool on Orca mainnet")
            
            # Use provided amounts or defaults
            crt_amount = initial_crt or self.pool_configs["CRT/SOL"]["initial_crt_amount"]
            sol_amount = initial_sol or self.pool_configs["CRT/SOL"]["initial_sol_amount"]
            
            # Call Node.js Orca manager
            result = await self.call_orca_manager(
                "createCRTSOLPool",
                initialCRTAmount=crt_amount,
                initialSOLAmount=sol_amount
            )
            
            if result.get("success"):
                logger.info(f"✅ Real CRT/SOL pool created: {result.get('pool_address')}")
                
                return {
                    "success": True,
                    "message": "Real CRT/SOL pool created on Orca",
                    "pool": {
                        "pool_pair": "CRT/SOL",
                        "pool_address": result.get("pool_address"),
                        "transaction_hash": result.get("transaction_hash"),
                        "explorer_url": result.get("explorer_url"),
                        "pool_url": result.get("pool_url"),
                        "network": "Solana Mainnet",
                        "dex": "Orca",
                        "initial_liquidity": {
                            "crt_amount": crt_amount,
                            "sol_amount": sol_amount,
                            "total_value_usd": sol_amount * 100  # Assuming $100/SOL
                        },
                        "fee_tier": result.get("fee_tier", 0.003),
                        "created_at": datetime.utcnow().isoformat(),
                        "status": "active"
                    },
                    "real_blockchain": True,
                    "existing": result.get("existing", False)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown pool creation error"),
                    "details": result.get("details")
                }
                
        except Exception as e:
            logger.error(f"❌ Real CRT/SOL pool creation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Pool creation error: {str(e)}"
            }
    
    async def create_real_crt_usdc_pool(self, initial_crt: float = None, initial_usdc: float = None) -> Dict[str, Any]:
        """Create actual CRT/USDC liquidity pool on Orca"""
        try:
            logger.info("💰 Creating REAL CRT/USDC pool on Orca mainnet")
            
            # Use provided amounts or defaults
            crt_amount = initial_crt or self.pool_configs["CRT/USDC"]["initial_crt_amount"]
            usdc_amount = initial_usdc or self.pool_configs["CRT/USDC"]["initial_usdc_amount"]
            
            # Call Node.js Orca manager
            result = await self.call_orca_manager(
                "createCRTUSDCPool", 
                initialCRTAmount=crt_amount,
                initialUSDCAmount=usdc_amount
            )
            
            if result.get("success"):
                logger.info(f"✅ Real CRT/USDC pool created: {result.get('pool_address')}")
                
                return {
                    "success": True,
                    "message": "Real CRT/USDC pool created on Orca",
                    "pool": {
                        "pool_pair": "CRT/USDC",
                        "pool_address": result.get("pool_address"),
                        "transaction_hash": result.get("transaction_hash"),
                        "explorer_url": result.get("explorer_url"),
                        "pool_url": result.get("pool_url"),
                        "network": "Solana Mainnet", 
                        "dex": "Orca",
                        "initial_liquidity": {
                            "crt_amount": crt_amount,
                            "usdc_amount": usdc_amount,
                            "total_value_usd": usdc_amount * 2  # Double for both sides
                        },
                        "fee_tier": result.get("fee_tier", 0.003),
                        "created_at": datetime.utcnow().isoformat(),
                        "status": "active"
                    },
                    "real_blockchain": True,
                    "existing": result.get("existing", False)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown pool creation error"),
                    "details": result.get("details")
                }
                
        except Exception as e:
            logger.error(f"❌ Real CRT/USDC pool creation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Pool creation error: {str(e)}"
            }
    
    async def get_treasury_balances(self) -> Dict[str, Any]:
        """Check treasury balances for pool creation"""
        try:
            result = await self.call_orca_manager("checkTreasuryBalances")
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Balance check failed: {str(e)}"
            }
    
    async def get_pool_info(self, pool_address: str) -> Dict[str, Any]:
        """Get information about an existing pool"""
        try:
            result = await self.call_orca_manager("getPoolInfo", poolAddress=pool_address)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Pool info fetch failed: {str(e)}"
            }
    
    async def add_liquidity(self, pool_address: str, token_a_amount: float, token_b_amount: float) -> Dict[str, Any]:
        """Add liquidity to an existing pool"""
        try:
            result = await self.call_orca_manager(
                "addLiquidity",
                poolAddress=pool_address,
                tokenAAmount=token_a_amount,
                tokenBAmount=token_b_amount
            )
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Add liquidity failed: {str(e)}"
            }
    
    async def get_all_orca_pools(self) -> Dict[str, Any]:
        """Get all available Orca pools"""
        try:
            result = await self.call_orca_manager("getAllOrcaPools")
            return result
        except Exception as e:
            return {
                "success": False,
                "error": f"Pool listing failed: {str(e)}"
            }
    
    async def call_orca_manager(self, method: str, **kwargs) -> Dict[str, Any]:
        """Call Node.js Real Orca Manager function"""
        try:
            # Prepare arguments
            args_str = ""
            if kwargs:
                arg_values = []
                for key, value in kwargs.items():
                    if isinstance(value, str):
                        arg_values.append(f'"{value}"')
                    else:
                        arg_values.append(str(value))
                args_str = ", ".join(arg_values)
            
            # Create Node.js script
            node_script = f"""
            const RealOrcaManager = require('{self.orca_manager_path}');
            
            async function execute() {{
                try {{
                    const manager = new RealOrcaManager();
                    let result;
                    
                    if ('{method}' === 'createCRTSOLPool' && {len(kwargs)} >= 2) {{
                        result = await manager.{method}({args_str});
                    }} else if ('{method}' === 'createCRTUSDCPool' && {len(kwargs)} >= 2) {{
                        result = await manager.{method}({args_str});
                    }} else if ('{method}' === 'getPoolInfo' && {len(kwargs)} >= 1) {{
                        result = await manager.{method}({args_str});
                    }} else if ('{method}' === 'addLiquidity' && {len(kwargs)} >= 3) {{
                        result = await manager.{method}({args_str});
                    }} else if ('{method}' === 'getAllOrcaPools') {{
                        result = await manager.{method}();
                    }} else if ('{method}' === 'checkTreasuryBalances') {{
                        result = await manager.checkTreasuryBalances(manager.treasuryKeypair.publicKey, 1000000, 100);
                    }} else {{
                        result = {{ success: false, error: "Unknown method or invalid parameters" }};
                    }}
                    
                    console.log(JSON.stringify(result));
                }} catch (error) {{
                    const errorResult = {{ 
                        success: false, 
                        error: error.message,
                        stack: error.stack
                    }};
                    console.log(JSON.stringify(errorResult));
                }}
            }}
            
            execute();
            """
            
            # Execute the Node.js script
            process = await asyncio.create_subprocess_exec(
                "node", "-e", node_script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd="/app/backend"
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                stdout_text = stdout.decode().strip()
                if stdout_text:
                    try:
                        result = json.loads(stdout_text)
                        return result
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}, Raw output: {stdout_text}")
                        return {"success": False, "error": f"Invalid JSON: {stdout_text}"}
                else:
                    return {"success": False, "error": "Empty response from Orca manager"}
            else:
                error_msg = stderr.decode() if stderr else f"Process exit code: {process.returncode}"
                return {
                    "success": False,
                    "error": f"Orca manager error: {error_msg}"
                }
                
        except Exception as e:
            logger.error(f"Orca manager call exception: {str(e)}")
            return {"success": False, "error": f"Call failed: {str(e)}"}

# Global service instance
real_orca_service = RealOrcaService()