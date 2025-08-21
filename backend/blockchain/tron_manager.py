from tronpy import Tron
from typing import Optional, Dict, Any, List
import os
from datetime import datetime

class TronManager:
    def __init__(self, network: str = "mainnet"):
        self.network = network
        try:
            if network == "mainnet":
                self.client = Tron()
            else:
                self.client = Tron(network="shasta")  # Testnet
            self.energy_limit = 100_000_000
        except Exception as e:
            print(f"Error initializing TRON client: {e}")
            self.client = None
        
    async def get_account_info(self, address: str) -> Dict[str, Any]:
        """Get TRON account information"""
        try:
            if not self.client:
                return {"success": False, "error": "TRON client not initialized"}
                
            account = self.client.get_account(address)
            
            # Get TRX balance (in SUN units, 1 TRX = 1,000,000 SUN)
            trx_balance = account.get("balance", 0) / 1_000_000
            
            # Get account resources
            try:
                resources = self.client.get_account_resource(address)
            except:
                resources = {}
            
            return {
                "success": True,
                "address": address,
                "trx_balance": trx_balance,
                "bandwidth": resources.get("NetUsed", 0),
                "energy": resources.get("EnergyUsed", 0),
                "bandwidth_limit": resources.get("NetLimit", 0),
                "energy_limit": resources.get("EnergyLimit", 0)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_transaction_history(self, 
                                    address: str, 
                                    limit: int = 50) -> List[Dict[str, Any]]:
        """Get transaction history for TRON address"""
        try:
            if not self.client:
                return []
                
            # For demo purposes, return empty list
            # In production, you would implement proper transaction fetching
            return []
            
        except Exception as e:
            print(f"Error getting TRON transaction history: {e}")
            return []

class TronTransactionManager:
    def __init__(self, tron_manager: TronManager):
        self.tron = tron_manager
        self.client = tron_manager.client if tron_manager else None
        
    async def get_trx_balance(self, address: str) -> Dict[str, Any]:
        """Get TRX balance for address"""
        if not self.client:
            return {
                "success": False, 
                "error": "TRON client not available",
                "balance": 0.0
            }
        
        try:
            account_info = await self.tron.get_account_info(address)
            return {
                "success": True,
                "balance": account_info.get("trx_balance", 0.0),
                "address": address
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "balance": 0.0
            }