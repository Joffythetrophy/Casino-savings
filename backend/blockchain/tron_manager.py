import aiohttp
import asyncio
from typing import Optional, Dict, Any, List
import os
from datetime import datetime

class TronManager:
    def __init__(self, api_key: Optional[str] = None, network: str = "mainnet"):
        self.api_key = api_key or os.getenv("TRON_API_KEY")
        self.network = network
        
        if network == "mainnet":
            self.base_url = "https://api.trongrid.io"
            self.api_url = "https://api.tronstack.io"
        else:
            self.base_url = "https://api.shasta.trongrid.io"
            self.api_url = "https://api.shasta.tronstack.io"
        
        self.headers = {
            "TRON-PRO-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
    async def get_account_info(self, address: str) -> Dict[str, Any]:
        """Get real TRON account information using TronGrid API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/v1/accounts/{address}"
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        account_data = data.get("data", [])
                        
                        if account_data:
                            account = account_data[0]
                            # Get TRX balance (in SUN units, 1 TRX = 1,000,000 SUN)
                            trx_balance = account.get("balance", 0) / 1_000_000
                            
                            return {
                                "success": True,
                                "address": address,
                                "trx_balance": trx_balance,
                                "create_time": account.get("create_time", 0),
                                "latest_operation_time": account.get("latest_operation_time", 0),
                                "account_resource": account.get("account_resource", {}),
                                "source": "trongrid"
                            }
                        else:
                            # Account not found, return 0 balance
                            return {
                                "success": True,
                                "address": address,
                                "trx_balance": 0.0,
                                "create_time": 0,
                                "latest_operation_time": 0,
                                "account_resource": {},
                                "source": "trongrid"
                            }
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"API Error {response.status}: {error_text}"}
                        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_transaction_history(self, 
                                    address: str, 
                                    limit: int = 50,
                                    only_confirmed: bool = True) -> List[Dict[str, Any]]:
        """Get real transaction history for TRON address"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "limit": limit,
                    "only_confirmed": str(only_confirmed).lower()
                }
                
                url = f"{self.base_url}/v1/accounts/{address}/transactions"
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        transactions = []
                        
                        for tx in data.get("data", []):
                            # Parse transaction details
                            tx_info = {
                                "txid": tx.get("txID"),
                                "block_number": tx.get("blockNumber", 0),
                                "block_timestamp": tx.get("block_timestamp", 0),
                                "energy_usage": tx.get("energy_usage", 0),
                                "energy_fee": tx.get("energy_fee", 0),
                                "net_usage": tx.get("net_usage", 0),
                                "net_fee": tx.get("net_fee", 0),
                                "confirmed": tx.get("confirmed", False)
                            }
                            
                            # Extract contract info
                            raw_data = tx.get("raw_data", {})
                            contracts = raw_data.get("contract", [])
                            
                            if contracts:
                                contract = contracts[0]
                                contract_type = contract.get("type")
                                parameter = contract.get("parameter", {}).get("value", {})
                                
                                if contract_type == "TransferContract":
                                    tx_info.update({
                                        "type": "transfer",
                                        "from_address": parameter.get("owner_address"),
                                        "to_address": parameter.get("to_address"),
                                        "amount": parameter.get("amount", 0) / 1_000_000  # Convert to TRX
                                    })
                            
                            transactions.append(tx_info)
                        
                        return transactions[:limit]
                    else:
                        return []
                        
        except Exception as e:
            print(f"Error getting TRON transaction history: {e}")
            return []

    async def get_account_resources(self, address: str) -> Dict[str, Any]:
        """Get account resources (bandwidth, energy)"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/wallet/getaccountresource"
                data = {"address": address}
                
                async with session.post(url, json=data, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "bandwidth_limit": result.get("NetLimit", 0),
                            "bandwidth_used": result.get("NetUsed", 0),
                            "energy_limit": result.get("EnergyLimit", 0),
                            "energy_used": result.get("EnergyUsed", 0),
                            "tron_power_limit": result.get("TronPowerLimit", 0),
                            "tron_power_used": result.get("TronPowerUsed", 0)
                        }
                    else:
                        return {"success": False, "error": f"Failed to get resources"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def validate_address(self, address: str) -> Dict[str, Any]:
        """Validate TRON address"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/wallet/validateaddress"
                data = {"address": address}
                
                async with session.post(url, json=data, headers=self.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "valid": result.get("result", False),
                            "address": address
                        }
                    else:
                        return {"success": False, "valid": False, "error": "Validation failed"}
        except Exception as e:
            return {"success": False, "valid": False, "error": str(e)}

class TronTransactionManager:
    def __init__(self, tron_manager: TronManager):
        self.tron = tron_manager
        
    async def get_trx_balance(self, address: str) -> Dict[str, Any]:
        """Get real TRX balance for address"""
        try:
            account_info = await self.tron.get_account_info(address)
            if account_info.get("success"):
                return {
                    "success": True,
                    "balance": account_info.get("trx_balance", 0.0),
                    "address": address,
                    "source": "trongrid_api"
                }
            else:
                return {
                    "success": False,
                    "error": account_info.get("error", "Failed to get balance"),
                    "balance": 0.0
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "balance": 0.0
            }

    async def estimate_energy(self, from_address: str, to_address: str, amount: float) -> Dict[str, Any]:
        """Estimate energy required for transaction"""
        try:
            # Convert TRX to SUN
            amount_sun = int(amount * 1_000_000)
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.tron.base_url}/wallet/triggerconstantcontract"
                data = {
                    "owner_address": from_address,
                    "contract_address": to_address,
                    "function_selector": "transfer(address,uint256)",
                    "parameter": f"{to_address.replace('0x', '').zfill(64)}{hex(amount_sun)[2:].zfill(64)}"
                }
                
                async with session.post(url, json=data, headers=self.tron.headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "energy_required": result.get("energy_used", 0),
                            "energy_penalty": result.get("energy_penalty", 0)
                        }
                    else:
                        return {"success": False, "error": "Energy estimation failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_transaction(self, from_address: str, to_address: str, amount: float) -> Dict[str, Any]:
        """Create TRX transfer transaction"""
        try:
            # Validate addresses
            from_valid = await self.tron.validate_address(from_address)
            to_valid = await self.tron.validate_address(to_address)
            
            if not from_valid.get("valid") or not to_valid.get("valid"):
                return {"success": False, "error": "Invalid address provided"}
            
            # Check balance
            balance_info = await self.get_trx_balance(from_address)
            if not balance_info["success"] or balance_info["balance"] < amount:
                return {"success": False, "error": "Insufficient TRX balance"}
            
            # Convert TRX to SUN
            amount_sun = int(amount * 1_000_000)
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.tron.base_url}/wallet/createtransaction"
                data = {
                    "to_address": to_address,
                    "owner_address": from_address,
                    "amount": amount_sun
                }
                
                async with session.post(url, json=data, headers=self.tron.headers) as response:
                    if response.status == 200:
                        transaction = await response.json()
                        return {
                            "success": True,
                            "transaction": transaction,
                            "amount": amount,
                            "from_address": from_address,
                            "to_address": to_address
                        }
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"Transaction creation failed: {error_text}"}
                        
        except Exception as e:
            return {"success": False, "error": str(e)}