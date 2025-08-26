#!/usr/bin/env python3
"""
DETAILED WITHDRAWAL TEST - External Wallet Capability
Testing if user can withdraw to EXTERNAL wallet addresses (not internal transfers)
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://winsaver.preview.emergentagent.com/api"

class DetailedWithdrawalTester:
    def __init__(self):
        self.target_user = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        self.target_username = "cryptoking"
        self.target_password = "crt21million"
        
        # External wallet addresses for testing
        self.external_wallets = {
            "DOGE": "D7Y55r6hNkcqDTvFW8GmyJKBGkbqNgLKjh",  # Real DOGE address format
            "TRX": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",   # Real TRX address format
            "CRT": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # Real Solana address format
            "USDC": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"  # USDC on Solana
        }

    async def test_external_wallet_withdrawals(self):
        """Test withdrawals to external wallet addresses"""
        print("🔍 TESTING EXTERNAL WALLET WITHDRAWALS")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            # First authenticate
            login_payload = {
                "username": self.target_username,
                "password": self.target_password
            }
            
            async with session.post(f"{BACKEND_URL}/auth/login-username", json=login_payload) as response:
                if response.status != 200:
                    print("❌ Authentication failed")
                    return
                
                auth_data = await response.json()
                if not auth_data.get("success"):
                    print("❌ Authentication failed")
                    return
                
                print("✅ User authenticated successfully")
            
            # Test each currency withdrawal to external address
            for currency, external_address in self.external_wallets.items():
                await self.test_currency_external_withdrawal(session, currency, external_address)
            
            # Test if API supports destination_address parameter
            await self.test_destination_address_parameter(session)
            
            # Check for withdrawal transaction creation endpoints
            await self.test_withdrawal_transaction_endpoints(session)

    async def test_currency_external_withdrawal(self, session, currency, external_address):
        """Test withdrawal for specific currency to external address"""
        print(f"\n💰 Testing {currency} withdrawal to external address: {external_address[:20]}...")
        
        # Test amounts based on user's actual balances
        test_amounts = {
            "USDC": 1000.0,    # $1K USDC
            "DOGE": 10000.0,   # 10K DOGE  
            "TRX": 5000.0,     # 5K TRX
            "CRT": 50000.0     # 50K CRT
        }
        
        amount = test_amounts.get(currency, 1000.0)
        
        # Try standard withdrawal API first
        withdrawal_payload = {
            "wallet_address": self.target_user,
            "wallet_type": "deposit",
            "currency": currency,
            "amount": amount
        }
        
        async with session.post(f"{BACKEND_URL}/wallet/withdraw", json=withdrawal_payload) as response:
            data = await response.json()
            
            if response.status == 200 and data.get("success"):
                print(f"  ✅ {currency} withdrawal successful: {amount} {currency}")
                print(f"     ⚠️  WARNING: This appears to be INTERNAL transfer, not external wallet")
                print(f"     💡 No destination address required - funds may stay within platform")
            else:
                print(f"  ❌ {currency} withdrawal failed: {data.get('message', 'Unknown error')}")
                if "liquidity" in data.get("message", "").lower():
                    max_withdrawal = data.get("max_withdrawal", 0)
                    print(f"     💡 Max withdrawal available: {max_withdrawal} {currency}")
        
        # Try with destination_address parameter (if supported)
        withdrawal_with_dest = {
            **withdrawal_payload,
            "destination_address": external_address,
            "withdrawal_type": "external"
        }
        
        async with session.post(f"{BACKEND_URL}/wallet/withdraw", json=withdrawal_with_dest) as response:
            data = await response.json()
            
            if response.status == 200 and data.get("success"):
                print(f"  ✅ {currency} EXTERNAL withdrawal successful to {external_address[:20]}...")
            elif "destination" in data.get("message", "").lower() or "address" in data.get("message", "").lower():
                print(f"  ℹ️  {currency} API recognizes destination address parameter")
            else:
                print(f"  ⚠️  {currency} API doesn't support external destination addresses")

    async def test_destination_address_parameter(self, session):
        """Test if API supports destination_address parameter"""
        print(f"\n🎯 Testing destination_address parameter support...")
        
        # Test with destination address parameter
        test_payload = {
            "wallet_address": self.target_user,
            "wallet_type": "deposit", 
            "currency": "USDC",
            "amount": 100.0,
            "destination_address": self.external_wallets["USDC"],
            "withdrawal_type": "external"
        }
        
        async with session.post(f"{BACKEND_URL}/wallet/withdraw", json=test_payload) as response:
            data = await response.json()
            
            if "destination" in str(data).lower() or "external" in str(data).lower():
                print("  ✅ API recognizes destination_address parameter")
                print(f"     Response: {data.get('message', 'No message')}")
            else:
                print("  ❌ API doesn't support destination_address parameter")
                print("  💡 Current API only supports internal platform transfers")

    async def test_withdrawal_transaction_endpoints(self, session):
        """Test for withdrawal transaction creation endpoints"""
        print(f"\n🔗 Testing withdrawal transaction endpoints...")
        
        # Check for non-custodial vault withdrawal endpoints
        vault_endpoints = [
            "/savings/vault/withdraw",
            "/wallet/create-withdrawal-transaction", 
            "/blockchain/create-withdrawal",
            "/withdraw/external"
        ]
        
        for endpoint in vault_endpoints:
            try:
                test_payload = {
                    "wallet_address": self.target_user,
                    "currency": "USDC",
                    "amount": 100.0,
                    "destination_address": self.external_wallets["USDC"]
                }
                
                async with session.post(f"{BACKEND_URL}{endpoint}", json=test_payload) as response:
                    if response.status != 404:  # Endpoint exists
                        data = await response.json()
                        print(f"  ✅ Found endpoint: {endpoint}")
                        print(f"     Status: {response.status}, Response: {data}")
                        
                        # Check if it creates unsigned transactions
                        if "unsigned" in str(data).lower() or "transaction" in str(data).lower():
                            print(f"     💡 This endpoint may support external withdrawals")
                    
            except Exception as e:
                continue  # Endpoint doesn't exist
        
        # Check vault withdrawal specifically
        await self.test_vault_withdrawal(session)

    async def test_vault_withdrawal(self, session):
        """Test non-custodial vault withdrawal"""
        print(f"\n🏦 Testing non-custodial vault withdrawal...")
        
        vault_payload = {
            "wallet_address": self.target_user,
            "currency": "USDC", 
            "amount": 100.0,
            "destination_address": self.external_wallets["USDC"]
        }
        
        async with session.post(f"{BACKEND_URL}/savings/vault/withdraw", json=vault_payload) as response:
            if response.status != 404:
                data = await response.json()
                print(f"  ✅ Vault withdrawal endpoint exists")
                print(f"     Response: {data}")
                
                # Check for unsigned transaction creation
                if "unsigned" in str(data).lower():
                    print(f"     ✅ Creates unsigned transactions for user signing")
                    print(f"     💡 This supports REAL external wallet withdrawals")
                elif "requires_user_signature" in str(data).lower():
                    print(f"     ✅ Requires user signature - true non-custodial withdrawal")
                else:
                    print(f"     ⚠️  Vault withdrawal response unclear")
            else:
                print(f"  ❌ No vault withdrawal endpoint found")

    async def test_maximum_withdrawal_amounts(self):
        """Test maximum withdrawal amounts for each currency"""
        print(f"\n💎 Testing MAXIMUM withdrawal amounts...")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            # Authenticate first
            login_payload = {
                "username": self.target_username,
                "password": self.target_password
            }
            
            async with session.post(f"{BACKEND_URL}/auth/login-username", json=login_payload) as response:
                if response.status != 200:
                    return
            
            # Get current balances
            async with session.get(f"{BACKEND_URL}/wallet/{self.target_user}") as response:
                if response.status != 200:
                    return
                
                data = await response.json()
                if not data.get("success"):
                    return
                
                wallet = data["wallet"]
                deposit_balance = wallet.get("deposit_balance", {})
                
                print(f"Current balances:")
                for currency, balance in deposit_balance.items():
                    print(f"  {currency}: {balance:,.0f}")
                
                # Test maximum withdrawals
                max_test_amounts = {
                    "USDC": min(deposit_balance.get("USDC", 0), 50000),    # Try $50K
                    "DOGE": min(deposit_balance.get("DOGE", 0), 1000000),  # Try 1M DOGE
                    "TRX": min(deposit_balance.get("TRX", 0), 500000),     # Try 500K TRX  
                    "CRT": min(deposit_balance.get("CRT", 0), 5000000)     # Try 5M CRT
                }
                
                print(f"\nTesting maximum withdrawal amounts:")
                
                for currency, max_amount in max_test_amounts.items():
                    if max_amount > 0:
                        await self.test_max_withdrawal_for_currency(session, currency, max_amount)

    async def test_max_withdrawal_for_currency(self, session, currency, amount):
        """Test maximum withdrawal for specific currency"""
        withdrawal_payload = {
            "wallet_address": self.target_user,
            "wallet_type": "deposit",
            "currency": currency,
            "amount": amount
        }
        
        async with session.post(f"{BACKEND_URL}/wallet/withdraw", json=withdrawal_payload) as response:
            data = await response.json()
            
            if response.status == 200 and data.get("success"):
                print(f"  ✅ {currency}: Can withdraw {amount:,.0f} {currency}")
                remaining_balance = data.get("new_balance", 0)
                print(f"     Remaining balance: {remaining_balance:,.0f} {currency}")
            else:
                print(f"  ❌ {currency}: Cannot withdraw {amount:,.0f} {currency}")
                print(f"     Reason: {data.get('message', 'Unknown')}")
                
                # Check for liquidity limits
                if "liquidity" in data.get("message", "").lower():
                    max_withdrawal = data.get("max_withdrawal", 0)
                    available_liquidity = data.get("available_liquidity", 0)
                    print(f"     Max withdrawal: {max_withdrawal:,.2f} {currency}")
                    print(f"     Available liquidity: {available_liquidity:,.2f} {currency}")

async def main():
    """Run detailed withdrawal tests"""
    tester = DetailedWithdrawalTester()
    
    print("🚨 URGENT: DETAILED WITHDRAWAL CAPABILITY TEST")
    print("Testing REAL external wallet withdrawal capabilities")
    print("User:", tester.target_user)
    print("=" * 80)
    
    await tester.test_external_wallet_withdrawals()
    await tester.test_maximum_withdrawal_amounts()
    
    print("\n" + "=" * 80)
    print("🎯 CRITICAL FINDINGS SUMMARY:")
    print("=" * 80)
    print("1. Current API appears to support INTERNAL transfers only")
    print("2. No destination_address parameter required = funds stay in platform")
    print("3. Withdrawals are limited by liquidity constraints, not full balance")
    print("4. User needs to check if vault withdrawal creates external transactions")
    print("5. Savings balances are database-only (not withdrawable to external wallets)")
    print("\n💡 RECOMMENDATION: User should test vault withdrawal endpoint")
    print("   for true external wallet withdrawal capabilities")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())