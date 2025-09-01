
#!/usr/bin/env python3
"""
Balance Checker for CRT Casino System
Check current balances for user cryptoking
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Backend configuration
BACKEND_URL = "https://crypto-treasury.preview.emergentagent.com/api"
TEST_USER = {
    "username": "cryptoking",
    "password": "crt21million",
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

class BalanceChecker:
    def __init__(self):
        self.session = None
        self.auth_token = None
    
    async def setup(self):
        """Initialize session and authenticate"""
        self.session = aiohttp.ClientSession()
        
        # Authenticate user
        login_data = {
            "identifier": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        
        try:
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                result = await response.json()
                
                if result.get("success"):
                    self.auth_token = result.get("token")
                    print(f"✅ Authenticated as: {result.get('username')}")
                    print(f"   Wallet: {result.get('wallet_address')}")
                    return True
                else:
                    print(f"❌ Authentication failed: {result.get('message')}")
                    return False
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    async def check_wallet_balances(self):
        """Get comprehensive wallet balance information"""
        try:
            wallet_address = TEST_USER["wallet_address"]
            
            # Get wallet information
            async with self.session.get(f"{BACKEND_URL}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    result = await response.json()
                    
                    if result.get("success"):
                        wallet = result.get("wallet", {})
                        
                        print(f"\n🏦 WALLET BALANCE SUMMARY")
                        print(f"=" * 60)
                        print(f"User: {wallet.get('user_id', 'N/A')}")
                        print(f"Wallet: {wallet_address}")
                        print(f"Balance Source: {wallet.get('balance_source', 'Unknown')}")
                        print(f"Last Updated: {wallet.get('last_balance_update', 'N/A')}")
                        
                        # Display balances by wallet type
                        balance_types = [
                            ("💳 Deposit Wallet", wallet.get("deposit_balance", {})),
                            ("🏆 Winnings Wallet", wallet.get("winnings_balance", {})),
                            ("🐷 Savings Vault", wallet.get("savings_balance", {})),
                            ("🎮 Gaming Balance", wallet.get("gaming_balance", {})),
                            ("💧 Liquidity Pool", wallet.get("liquidity_pool", {}))
                        ]
                        
                        total_values = {"CRT": 0, "DOGE": 0, "TRX": 0, "USDC": 0, "SOL": 0}
                        
                        for wallet_name, balances in balance_types:
                            print(f"\n{wallet_name}:")
                            if balances:
                                for currency, amount in balances.items():
                                    if amount > 0:
                                        print(f"  {currency}: {amount:,.6f}")
                                        total_values[currency] += amount
                                    else:
                                        print(f"  {currency}: 0.000000")
                            else:
                                print("  No balances")
                        
                        # Total summary
                        print(f"\n💰 TOTAL BALANCES ACROSS ALL WALLETS:")
                        print(f"=" * 40)
                        
                        total_usd_estimate = 0
                        for currency, total_amount in total_values.items():
                            if total_amount > 0:
                                # Rough USD estimates (update with real prices)
                                usd_rate = {
                                    "CRT": 0.15, "DOGE": 0.24, "TRX": 0.36, 
                                    "USDC": 1.0, "SOL": 100.0
                                }.get(currency, 0)
                                
                                usd_value = total_amount * usd_rate
                                total_usd_estimate += usd_value
                                
                                print(f"  {currency}: {total_amount:,.6f} (~${usd_value:,.2f})")
                            else:
                                print(f"  {currency}: 0.000000")
                        
                        print(f"\n🎯 ESTIMATED TOTAL VALUE: ${total_usd_estimate:,.2f}")
                        
                        # Balance notes if available
                        if wallet.get("balance_notes"):
                            print(f"\n📝 Balance Notes:")
                            for currency, note in wallet.get("balance_notes", {}).items():
                                print(f"  {currency}: {note}")
                        
                        return True
                    else:
                        print(f"❌ Failed to get wallet info: {result.get('message')}")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Balance check error: {str(e)}")
            return False
    
    async def check_real_blockchain_balances(self):
        """Check real blockchain balances for comparison"""
        try:
            print(f"\n🔗 REAL BLOCKCHAIN BALANCES:")
            print(f"=" * 40)
            
            wallet_address = TEST_USER["wallet_address"]
            currencies = ["CRT", "DOGE", "TRX", "SOL", "USDC"]
            
            for currency in currencies:
                try:
                    async with self.session.get(
                        f"{BACKEND_URL}/wallet/balance/{currency}?wallet_address={wallet_address}"
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            
                            if result.get("success"):
                                balance = result.get("balance", 0)
                                source = result.get("source", "unknown")
                                
                                print(f"  {currency}: {balance:,.6f} (Source: {source})")
                            else:
                                print(f"  {currency}: Error - {result.get('error', 'Unknown')}")
                        else:
                            print(f"  {currency}: HTTP {response.status}")
                except Exception as e:
                    print(f"  {currency}: Exception - {str(e)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Real blockchain balance check error: {str(e)}")
            return False
    
    async def cleanup(self):
        """Cleanup session"""
        if self.session:
            await self.session.close()

async def main():
    """Main function to check balances"""
    print(f"🎰 CRT Casino Balance Checker")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"User: {TEST_USER['username']}")
    
    checker = BalanceChecker()
    
    try:
        # Setup and authenticate
        if await checker.setup():
            # Check wallet balances
            await checker.check_wallet_balances()
            
            # Check real blockchain balances
            await checker.check_real_blockchain_balances()
            
            print(f"\n✅ Balance check completed successfully!")
        else:
            print(f"❌ Failed to authenticate user")
    
    except Exception as e:
        print(f"❌ Balance checker error: {str(e)}")
    
    finally:
        await checker.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
