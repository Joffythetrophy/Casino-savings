import asyncio
import aiohttp
import base58
from typing import Optional, Dict, Any, List
import os
import json
from datetime import datetime, timedelta

class SolanaManager:
    def __init__(self, rpc_url: str = None):
        self.rpc_url = rpc_url or os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        
    async def connect(self):
        """Test connection to Solana network"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getHealth"
                }
                async with session.post(self.rpc_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("result") == "ok":
                            return {"success": True, "network": "Solana Mainnet"}
                    return {"success": False, "error": "Health check failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_balance(self, address: str) -> Dict[str, Any]:
        """Get SOL balance for address"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getBalance",
                    "params": [address]
                }
                async with session.post(self.rpc_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "result" in data:
                            lamports = data["result"]["value"]
                            sol_balance = lamports / 1_000_000_000  # Convert lamports to SOL
                            return {
                                "success": True,
                                "balance": sol_balance,
                                "lamports": lamports,
                                "address": address
                            }
                    return {"success": False, "error": "Failed to get balance"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_token_accounts_by_owner(self, owner: str, mint: str) -> Dict[str, Any]:
        """Get token accounts owned by address for specific mint"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTokenAccountsByOwner",
                    "params": [
                        owner,
                        {"mint": mint},
                        {"encoding": "jsonParsed"}
                    ]
                }
                async with session.post(self.rpc_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {"success": True, "result": data.get("result", {})}
                    return {"success": False, "error": "Failed to get token accounts"}
        except Exception as e:
            return {"success": False, "error": str(e)}

class SPLTokenManager:
    def __init__(self, solana_manager: SolanaManager):
        self.solana = solana_manager
        
    async def get_token_balance(self, wallet_address: str, token_mint: str) -> Dict[str, Any]:
        """Get SPL token balance for a wallet"""
        try:
            # Get token accounts for this wallet and mint
            accounts_result = await self.solana.get_token_accounts_by_owner(wallet_address, token_mint)
            
            if not accounts_result.get("success"):
                return {"balance": "0", "decimals": 9, "ui_amount": 0.0, "error": accounts_result.get("error")}
            
            accounts = accounts_result["result"].get("value", [])
            
            if accounts:
                # Get the first token account (user usually has one per token)
                account_data = accounts[0]["account"]["data"]["parsed"]["info"]
                token_amount = account_data["tokenAmount"]
                
                return {
                    "balance": token_amount["amount"],
                    "decimals": token_amount["decimals"],
                    "ui_amount": float(token_amount["uiAmount"]) if token_amount["uiAmount"] else 0.0,
                    "token_address": accounts[0]["pubkey"]
                }
            else:
                # No token account found, balance is 0
                return {"balance": "0", "decimals": 9, "ui_amount": 0.0}
                
        except Exception as e:
            print(f"Error getting token balance: {e}")
            return {"balance": "0", "decimals": 9, "ui_amount": 0.0, "error": str(e)}

class CRTTokenManager:
    def __init__(self, solana_manager: SolanaManager, spl_manager: SPLTokenManager):
        self.solana = solana_manager
        self.spl = spl_manager
        self.crt_mint = os.getenv("CRT_TOKEN_MINT", "6kx78Yu19PmGjb9YbfP5nRUvFPY4kFcDKKmGpdSpump")
        self.decimals = 6  # CRT token uses 6 decimals
        self.price_cache = {"price": 0.15, "last_update": None}  # Mock price for now
        
    async def get_crt_balance(self, wallet_address: str) -> Dict[str, Any]:
        """Get real CRT token balance for specific wallet"""
        try:
            balance_data = await self.spl.get_token_balance(wallet_address, self.crt_mint)
            
            # Extract balance information
            ui_balance = balance_data.get("ui_amount", 0.0)
            raw_balance = int(balance_data.get("balance", "0"))
            
            # Get current price
            price_info = await self.get_crt_price()
            usd_value = ui_balance * price_info.get("price", 0)
            
            return {
                "success": True,
                "crt_balance": ui_balance,
                "raw_balance": raw_balance,
                "usd_value": usd_value,
                "price_per_token": price_info.get("price", 0),
                "mint_address": self.crt_mint,
                "decimals": self.decimals,
                "last_updated": datetime.utcnow().isoformat(),
                "source": "solana_rpc"
            }
            
        except Exception as e:
            print(f"Error getting CRT balance: {e}")
            return {
                "success": False,
                "crt_balance": 0.0,
                "raw_balance": 0,
                "usd_value": 0.0,
                "price_per_token": 0.15,
                "error": str(e)
            }
    
    async def get_crt_price(self) -> Dict[str, float]:
        """Get CRT token price (mock for now, can be replaced with real price feed)"""
        try:
            # Check cache validity (update every 5 minutes)
            if (self.price_cache.get("last_update") and 
                datetime.utcnow() - self.price_cache["last_update"] < timedelta(minutes=5)):
                return {"price": self.price_cache["price"]}
            
            # For now, return a mock price since CRT might not be on major exchanges
            # In production, you would fetch from Jupiter, Raydium, or other Solana DEX
            price = 0.15  # Mock CRT price in USD
            
            # Update cache
            self.price_cache = {
                "price": price,
                "last_update": datetime.utcnow()
            }
            
            return {"price": price}
            
        except Exception as e:
            print(f"Error fetching CRT price: {e}")
            return {"price": self.price_cache.get("price", 0.15)}

    async def get_token_info(self) -> Dict[str, Any]:
        """Get CRT token information"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getAccountInfo",
                    "params": [
                        self.crt_mint,
                        {"encoding": "jsonParsed"}
                    ]
                }
                async with session.post(self.solana.rpc_url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "result" in data and data["result"]["value"]:
                            mint_data = data["result"]["value"]["data"]["parsed"]["info"]
                            return {
                                "success": True,
                                "mint_address": self.crt_mint,
                                "decimals": mint_data.get("decimals", 9),
                                "supply": int(mint_data.get("supply", 0)) / (10 ** mint_data.get("decimals", 9)),
                                "mint_authority": mint_data.get("mintAuthority"),
                                "freeze_authority": mint_data.get("freezeAuthority"),
                                "is_initialized": mint_data.get("isInitialized", False)
                            }
                    return {"success": False, "error": "Failed to get token info"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def validate_address(self, address: str) -> Dict[str, Any]:
        """Validate Solana address format"""
        try:
            # Basic validation for Solana address (base58 encoded, 32-44 characters)
            if not address or len(address) < 32 or len(address) > 44:
                return {"success": False, "valid": False, "error": "Invalid address length"}
            
            # Try to decode as base58
            try:
                decoded = base58.b58decode(address)
                if len(decoded) == 32:  # Solana public keys are 32 bytes
                    return {"success": True, "valid": True, "address": address}
                else:
                    return {"success": False, "valid": False, "error": "Invalid address format"}
            except:
                return {"success": False, "valid": False, "error": "Invalid base58 encoding"}
                
        except Exception as e:
            return {"success": False, "valid": False, "error": str(e)}

    async def simulate_deposit(self, wallet_address: str, amount: float = 1000000.0) -> Dict[str, Any]:
        """Simulate a CRT deposit for testing purposes"""
        try:
            # This is a mock function for testing
            # In production, this would involve creating and sending a real transaction
            
            # Validate address first
            validation = await self.validate_address(wallet_address)
            if not validation.get("valid"):
                return {"success": False, "error": "Invalid wallet address"}
            
            # Get current balance
            current_balance = await self.get_crt_balance(wallet_address)
            
            return {
                "success": True,
                "message": f"Simulated deposit of {amount:,.0f} CRT to {wallet_address}",
                "deposit_amount": amount,
                "wallet_address": wallet_address,
                "current_balance": current_balance.get("crt_balance", 0.0),
                "estimated_new_balance": current_balance.get("crt_balance", 0.0) + amount,
                "note": "This is a simulation. Real deposits require transaction signing with private keys."
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}