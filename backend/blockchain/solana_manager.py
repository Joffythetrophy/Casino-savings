import asyncio
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.signature import Signature
from solders.transaction import Transaction
from typing import Optional, Dict, Any
import os
import aiohttp
from datetime import datetime, timedelta

class SolanaManager:
    def __init__(self, rpc_url: str = None, ws_url: str = None):
        self.rpc_url = rpc_url or os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        self.ws_url = ws_url or os.getenv("SOLANA_WS_URL", "wss://api.mainnet-beta.solana.com")
        self.client: Optional[AsyncClient] = None
        
    async def connect(self):
        """Initialize connection to Solana network"""
        self.client = AsyncClient(
            endpoint=self.rpc_url,
            commitment=Commitment.Confirmed,
            timeout=30
        )
        try:
            # Test connection
            await self.client.get_health()
            return {"success": True, "network": "Solana"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def disconnect(self):
        """Close Solana connection"""
        if self.client:
            await self.client.close()

class SPLTokenManager:
    def __init__(self, solana_manager: SolanaManager):
        self.solana = solana_manager
        self.crt_mint = Pubkey.from_string("AAHn4ZD9EpkcRDNv8nW2hsNoCW9kSun7qP2bPGFsEcMs")
        
    async def get_token_balance(self, wallet_address: str, token_mint: Optional[str] = None) -> Dict[str, Any]:
        """Get SPL token balance for a wallet"""
        try:
            wallet_pubkey = Pubkey.from_string(wallet_address)
            mint_pubkey = Pubkey.from_string(token_mint) if token_mint else self.crt_mint
            
            # Get token accounts by owner
            response = await self.solana.client.get_token_accounts_by_owner(
                wallet_pubkey,
                {"mint": mint_pubkey}
            )
            
            if response.value:
                for account_info in response.value:
                    # Get account data
                    account_data = account_info.account.data
                    # Parse token account data (simplified)
                    # In production, you would properly parse the account data
                    return {
                        "balance": "0",
                        "decimals": 6,
                        "ui_amount": 0.0,
                        "token_address": str(account_info.pubkey)
                    }
            
            return {"balance": "0", "decimals": 6, "ui_amount": 0.0}
                
        except Exception as e:
            print(f"Error getting token balance: {e}")
            return {"balance": "0", "decimals": 6, "ui_amount": 0.0, "error": str(e)}

class CRTTokenManager:
    def __init__(self, solana_manager: SolanaManager, spl_manager: SPLTokenManager):
        self.solana = solana_manager
        self.spl = spl_manager
        self.crt_mint = "AAHn4ZD9EpkcRDNv8nW2hsNoCW9kSun7qP2bPGFsEcMs"
        self.decimals = 6
        self.price_cache = {"price": 0.005045, "last_update": None}
        
    async def get_crt_balance(self, wallet_address: str) -> Dict[str, Any]:
        """Get CRT token balance for specific wallet"""
        try:
            balance_data = await self.spl.get_token_balance(wallet_address, self.crt_mint)
            
            # Convert to human-readable format
            raw_balance = int(balance_data.get("balance", "0"))
            ui_balance = raw_balance / (10 ** self.decimals)
            
            # Get current price
            price_info = await self.get_crt_price()
            usd_value = ui_balance * price_info.get("price", 0)
            
            return {
                "crt_balance": ui_balance,
                "raw_balance": raw_balance,
                "usd_value": usd_value,
                "price_per_token": price_info.get("price", 0),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting CRT balance: {e}")
            return {
                "crt_balance": 0.0,
                "raw_balance": 0,
                "usd_value": 0.0,
                "price_per_token": 0.005045,
                "error": str(e)
            }
    
    async def get_crt_price(self) -> Dict[str, float]:
        """Fetch current CRT token price from market data"""
        try:
            # Check cache validity (update every 5 minutes)
            if (self.price_cache.get("last_update") and 
                datetime.utcnow() - self.price_cache["last_update"] < timedelta(minutes=5)):
                return {"price": self.price_cache["price"]}
            
            # For demo purposes, return a mock price
            # In production, you would fetch from a real API
            price = 0.005045  # Mock CRT price
            
            # Update cache
            self.price_cache = {
                "price": price,
                "last_update": datetime.utcnow()
            }
            
            return {"price": price}
            
        except Exception as e:
            print(f"Error fetching CRT price: {e}")
            return {"price": self.price_cache.get("price", 0.005045)}