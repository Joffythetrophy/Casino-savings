"""
Real Withdrawal Service - Production Ready Cryptocurrency Withdrawals
Integrates with the Node.js blockchain manager for actual cryptocurrency transactions
"""

import subprocess
import json
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RealWithdrawalService:
    def __init__(self):
        self.blockchain_manager_path = "/app/backend/blockchain/real_blockchain_manager.js"
        self.supported_currencies = ["SOL", "USDC", "CRT", "DOGE", "TRX"]
        
    async def execute_real_withdrawal(
        self, 
        currency: str, 
        to_address: str, 
        amount: float,
        user_wallet: str,
        withdrawal_type: str = "external"
    ) -> Dict[str, Any]:
        """Execute real cryptocurrency withdrawal via blockchain"""
        try:
            logger.info(f"🌐 Executing real {currency} withdrawal: {amount} to {to_address}")
            
            # Validate currency support
            if currency.upper() not in self.supported_currencies:
                return {
                    "success": False,
                    "error": f"Currency {currency} not supported for real withdrawals",
                    "supported_currencies": self.supported_currencies
                }
            
            # Validate address format first
            address_validation = await self.validate_address(currency, to_address)
            if not address_validation.get("valid"):
                return {
                    "success": False,
                    "error": f"Invalid {currency} address: {address_validation.get('error')}",
                    "address": to_address
                }
            
            # Execute blockchain transaction
            blockchain_result = await self.call_blockchain_manager(
                "sendCryptocurrency", 
                currency=currency.upper(),
                toAddress=to_address,
                amount=amount
            )
            
            if blockchain_result.get("success"):
                # Transaction successful
                transaction_data = {
                    "success": True,
                    "transaction_hash": blockchain_result.get("signature"),
                    "explorer_url": blockchain_result.get("explorerUrl"),
                    "amount": amount,
                    "currency": currency.upper(),
                    "destination_address": to_address,
                    "network": blockchain_result.get("network"),
                    "user_wallet": user_wallet,
                    "withdrawal_type": withdrawal_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "service": "real_blockchain",
                    "fee_estimate": blockchain_result.get("fee_estimate", 0),
                    "note": blockchain_result.get("note", "")
                }
                
                logger.info(f"✅ Real {currency} withdrawal successful: {blockchain_result.get('signature')}")
                return transaction_data
                
            else:
                error_message = blockchain_result.get("error", "Unknown blockchain error")
                logger.error(f"❌ Real {currency} withdrawal failed: {error_message}")
                return {
                    "success": False,
                    "error": f"Blockchain transaction failed: {error_message}",
                    "currency": currency,
                    "amount": amount
                }
            
        except Exception as e:
            logger.error(f"❌ Real withdrawal service error: {str(e)}")
            return {
                "success": False,
                "error": f"Withdrawal service error: {str(e)}"
            }
    
    async def validate_address(self, currency: str, address: str) -> Dict[str, Any]:
        """Validate cryptocurrency address format"""
        try:
            validation_result = await self.call_blockchain_manager(
                "validateAddress",
                currency=currency.upper(),
                address=address
            )
            return validation_result
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Address validation error: {str(e)}"
            }
    
    async def get_real_balance(self, currency: str, address: str) -> Dict[str, Any]:
        """Get real blockchain balance for address"""
        try:
            balance_result = await self.call_blockchain_manager(
                "getBalance",
                currency=currency.upper(),
                address=address
            )
            return balance_result
            
        except Exception as e:
            return {
                "success": False,
                "balance": 0,
                "error": f"Balance check error: {str(e)}"
            }
    
    async def get_network_fees(self) -> Dict[str, Any]:
        """Get current network fees for all supported currencies"""
        try:
            fees_result = await self.call_blockchain_manager("getNetworkFees")
            return {
                "success": True,
                "fees": fees_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Fee estimation error: {str(e)}"
            }
    
    async def call_blockchain_manager(self, method: str, **kwargs) -> Dict[str, Any]:
        """Call Node.js blockchain manager function"""
        try:
            # Prepare arguments as individual parameters
            args_str = ""
            if kwargs:
                arg_values = []
                for key, value in kwargs.items():
                    if isinstance(value, str):
                        arg_values.append(f'"{value}"')
                    else:
                        arg_values.append(str(value))
                args_str = ", ".join(arg_values)
            
            # Create a more robust Node.js script
            node_script = f"""
            const path = require('path');
            const RealBlockchainManager = require('{self.blockchain_manager_path}');
            
            async function execute() {{
                try {{
                    const manager = new RealBlockchainManager();
                    let result;
                    
                    if ('{method}' === 'sendCryptocurrency' && {len(kwargs)} >= 3) {{
                        result = await manager.{method}({args_str});
                    }} else if ('{method}' === 'validateAddress' && {len(kwargs)} >= 2) {{
                        result = await manager.{method}({args_str});
                    }} else if ('{method}' === 'getBalance' && {len(kwargs)} >= 2) {{
                        result = await manager.{method}({args_str});
                    }} else if ('{method}' === 'getNetworkFees') {{
                        result = await manager.{method}();
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
                    return {"success": False, "error": "Empty response from blockchain manager"}
            else:
                error_msg = stderr.decode() if stderr else f"Process exit code: {process.returncode}"
                return {
                    "success": False,
                    "error": f"Blockchain manager error: {error_msg}"
                }
                
        except Exception as e:
            logger.error(f"Blockchain manager call exception: {str(e)}")
            return {"success": False, "error": f"Call failed: {str(e)}"}
    
    async def test_blockchain_connectivity(self) -> Dict[str, Any]:
        """Test connectivity to all blockchain networks"""
        try:
            logger.info("🧪 Testing blockchain connectivity...")
            
            test_results = {}
            
            # Test each supported currency
            for currency in self.supported_currencies:
                try:
                    # Test with a known address (not sending any funds)
                    test_addresses = {
                        "SOL": "11111111111111111111111111111112",  # System program
                        "USDC": "11111111111111111111111111111112",
                        "CRT": "11111111111111111111111111111112", 
                        "DOGE": "D7LCDsmMATQ5B7UonSZNfnrxCQ2GRTXKNi",  # Example DOGE address
                        "TRX": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"   # USDT contract address
                    }
                    
                    test_address = test_addresses.get(currency)
                    if test_address:
                        # Test address validation
                        validation = await self.validate_address(currency, test_address)
                        test_results[currency] = {
                            "network_accessible": validation.get("valid", False),
                            "validation_working": True,
                            "error": validation.get("error") if not validation.get("valid") else None
                        }
                    else:
                        test_results[currency] = {
                            "network_accessible": False,
                            "validation_working": False,
                            "error": "No test address defined"
                        }
                        
                except Exception as e:
                    test_results[currency] = {
                        "network_accessible": False,
                        "validation_working": False,
                        "error": str(e)
                    }
            
            # Count successful connections
            successful_networks = sum(1 for result in test_results.values() if result["network_accessible"])
            total_networks = len(self.supported_currencies)
            
            return {
                "success": True,
                "connectivity_test": test_results,
                "summary": {
                    "successful_networks": successful_networks,
                    "total_networks": total_networks,
                    "success_rate": f"{(successful_networks/total_networks)*100:.1f}%"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Blockchain connectivity test failed: {str(e)}")
            return {
                "success": False,
                "error": f"Connectivity test failed: {str(e)}"
            }

# Global service instance
real_withdrawal_service = RealWithdrawalService()