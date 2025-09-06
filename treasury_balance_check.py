#!/usr/bin/env python3
"""
Treasury Balance Check - Verify user's USDC distribution across wallet types
"""

import asyncio
import aiohttp
import json
import jwt
from datetime import datetime, timedelta

class TreasuryBalanceChecker:
    def __init__(self):
        self.base_url = "https://blockchain-slots.preview.emergentagent.com/api"
        self.session = None
        self.auth_token = None
        
        # Test credentials
        self.test_username = "cryptoking"
        self.test_password = "crt21million"
        self.test_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        
    async def setup_session(self):
        """Setup HTTP session"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def authenticate_user(self):
        """Authenticate user and get JWT token"""
        try:
            login_data = {
                "username": self.test_username,
                "password": self.test_password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        payload = {
                            "wallet_address": data.get("wallet_address"),
                            "network": "multi",
                            "exp": int((datetime.utcnow() + timedelta(hours=24)).timestamp()),
                            "iat": int(datetime.utcnow().timestamp()),
                            "type": "wallet_auth"
                        }
                        
                        jwt_secret = "casino_dapp_secret_2024"
                        self.auth_token = jwt.encode(payload, jwt_secret, algorithm="HS256")
                        return True
                        
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    async def check_balance_distribution(self):
        """Check user's USDC balance across all wallet types"""
        try:
            if not self.auth_token:
                print("❌ No authentication token")
                return
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(f"{self.base_url}/wallet/{self.test_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        wallet_info = data.get("wallet", {})
                        
                        print("💰 USDC Balance Distribution:")
                        print("="*50)
                        
                        # Check all wallet types
                        deposit_usdc = wallet_info.get("deposit_balance", {}).get("USDC", 0)
                        winnings_usdc = wallet_info.get("winnings_balance", {}).get("USDC", 0)
                        savings_usdc = wallet_info.get("savings_balance", {}).get("USDC", 0)
                        gaming_usdc = wallet_info.get("gaming_balance", {}).get("USDC", 0)
                        liquidity_usdc = wallet_info.get("liquidity_pool", {}).get("USDC", 0)
                        
                        total_usdc = deposit_usdc + winnings_usdc + savings_usdc + gaming_usdc + liquidity_usdc
                        
                        print(f"Deposit Balance:    {deposit_usdc:>15,.2f} USDC")
                        print(f"Winnings Balance:   {winnings_usdc:>15,.2f} USDC")
                        print(f"Savings Balance:    {savings_usdc:>15,.2f} USDC")
                        print(f"Gaming Balance:     {gaming_usdc:>15,.2f} USDC")
                        print(f"Liquidity Pool:     {liquidity_usdc:>15,.2f} USDC")
                        print("-" * 50)
                        print(f"Total USDC:         {total_usdc:>15,.2f} USDC")
                        print("="*50)
                        
                        # Show which wallet types have sufficient balance for withdrawals
                        required_amounts = [3160278, 2765243, 1975174]
                        
                        print("\n🏦 Treasury Withdrawal Feasibility:")
                        print("="*50)
                        
                        for i, amount in enumerate(required_amounts, 1):
                            print(f"\nWithdrawal {i}: {amount:,.0f} USDC")
                            print(f"  From Deposit:  {'✅ Sufficient' if deposit_usdc >= amount else '❌ Insufficient'} ({deposit_usdc:,.2f})")
                            print(f"  From Winnings: {'✅ Sufficient' if winnings_usdc >= amount else '❌ Insufficient'} ({winnings_usdc:,.2f})")
                            print(f"  From Savings:  {'✅ Sufficient' if savings_usdc >= amount else '❌ Insufficient'} ({savings_usdc:,.2f})")
                        
                        # Suggest optimal distribution
                        print(f"\n💡 Suggested Balance Redistribution:")
                        print("="*50)
                        
                        if total_usdc >= sum(required_amounts):
                            print("✅ Total USDC is sufficient for all withdrawals")
                            print("📋 Recommended actions:")
                            print("1. Move USDC to appropriate wallet types before withdrawal")
                            print("2. Use deposit balance for largest withdrawal")
                            print("3. Distribute remaining across winnings and savings")
                        else:
                            print("❌ Insufficient total USDC for planned withdrawals")
                            print(f"   Required: {sum(required_amounts):,.0f} USDC")
                            print(f"   Available: {total_usdc:,.2f} USDC")
                            print(f"   Shortfall: {sum(required_amounts) - total_usdc:,.2f} USDC")
                        
                        return {
                            "deposit": deposit_usdc,
                            "winnings": winnings_usdc,
                            "savings": savings_usdc,
                            "gaming": gaming_usdc,
                            "liquidity": liquidity_usdc,
                            "total": total_usdc
                        }
                    else:
                        print(f"❌ Failed to get wallet info: {data.get('message')}")
                else:
                    print(f"❌ HTTP {response.status}")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    async def run_check(self):
        """Run the balance check"""
        print("🔍 TREASURY BALANCE DISTRIBUTION CHECK")
        print("="*60)
        
        await self.setup_session()
        
        try:
            auth_success = await self.authenticate_user()
            
            if auth_success:
                print(f"✅ Authenticated as: {self.test_username}")
                print(f"🔑 Wallet: {self.test_wallet}")
                print()
                
                await self.check_balance_distribution()
            else:
                print("❌ Authentication failed")
        
        finally:
            await self.cleanup_session()

async def main():
    """Main execution"""
    checker = TreasuryBalanceChecker()
    await checker.run_check()

if __name__ == "__main__":
    asyncio.run(main())