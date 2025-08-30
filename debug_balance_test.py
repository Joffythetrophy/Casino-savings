#!/usr/bin/env python3
"""
Debug Balance Test - Investigate CRT balance availability issue
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

# Test Configuration
BACKEND_URL = "https://crypto-treasury-app.preview.emergentagent.com/api"
TEST_USER = {
    "username": "cryptoking",
    "password": "crt21million",
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

async def debug_balance_issue():
    """Debug why CRT balance shows as 0 in pool funding"""
    
    async with aiohttp.ClientSession() as session:
        # 1. Authenticate
        print("🔐 Authenticating user...")
        login_data = {
            "identifier": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        
        async with session.post(f"{BACKEND_URL}/auth/login", json=login_data) as resp:
            if resp.status == 200:
                result = await resp.json()
                if result.get("success"):
                    auth_token = result.get("token")
                    print(f"✅ Authentication successful")
                else:
                    print(f"❌ Login failed: {result}")
                    return
            else:
                print(f"❌ HTTP {resp.status}")
                return
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # 2. Get detailed wallet info
        print(f"\n💰 Getting wallet balances...")
        async with session.get(f"{BACKEND_URL}/wallet/{TEST_USER['wallet_address']}") as resp:
            if resp.status == 200:
                result = await resp.json()
                if result.get("success"):
                    wallet = result.get("wallet", {})
                    
                    print(f"📊 Balance Breakdown:")
                    print(f"   Deposit Balance: {wallet.get('deposit_balance', {})}")
                    print(f"   Gaming Balance: {wallet.get('gaming_balance', {})}")
                    print(f"   Winnings Balance: {wallet.get('winnings_balance', {})}")
                    print(f"   Savings Balance: {wallet.get('savings_balance', {})}")
                    print(f"   Liquidity Pool: {wallet.get('liquidity_pool', {})}")
                    
                    # Calculate what the endpoint should see
                    deposit = wallet.get("deposit_balance", {})
                    gaming = wallet.get("gaming_balance", {})
                    winnings = wallet.get("winnings_balance", {})
                    
                    calculated_available = {}
                    for currency in ["CRT", "USDC", "SOL"]:
                        total = (deposit.get(currency, 0) + 
                                gaming.get(currency, 0) + 
                                winnings.get(currency, 0))
                        calculated_available[currency] = total
                    
                    print(f"\n🧮 Calculated Available (deposit + gaming + winnings):")
                    print(f"   {calculated_available}")
                    
                    # Calculate true total including all balance types
                    savings = wallet.get("savings_balance", {})
                    liquidity = wallet.get("liquidity_pool", {})
                    
                    true_total = {}
                    for currency in ["CRT", "USDC", "SOL"]:
                        total = (deposit.get(currency, 0) + 
                                gaming.get(currency, 0) + 
                                winnings.get(currency, 0) +
                                savings.get(currency, 0) +
                                liquidity.get(currency, 0))
                        true_total[currency] = total
                    
                    print(f"\n💎 True Total (all balance types):")
                    print(f"   {true_total}")
                    
                else:
                    print(f"❌ Failed to get wallet: {result}")
                    return
            else:
                print(f"❌ HTTP {resp.status}")
                return
        
        # 3. Test pool funding with minimal amount to see exact error
        print(f"\n🌊 Testing pool funding with minimal amount...")
        pool_data = {
            "wallet_address": TEST_USER["wallet_address"],
            "pool_requests": [
                {
                    "pool_type": "CRT/USDC",
                    "amount_usd": 10,  # Just $10 to test
                    "description": "Debug Test Pool"
                }
            ]
        }
        
        async with session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                               json=pool_data, headers=headers) as resp:
            result = await resp.json()
            
            print(f"📋 Pool Funding Response:")
            print(f"   Status: {resp.status}")
            print(f"   Response: {json.dumps(result, indent=2)}")
            
            if not result.get("success"):
                needed = result.get("needed", {})
                available = result.get("available", {})
                
                print(f"\n🔍 Balance Analysis:")
                print(f"   Needed CRT: {needed.get('CRT', 0):,.0f}")
                print(f"   Available CRT: {available.get('CRT', 0):,.0f}")
                print(f"   Needed USDC: {needed.get('USDC', 0):,.0f}")
                print(f"   Available USDC: {available.get('USDC', 0):,.0f}")
                
                # Check if the issue is balance calculation or balance deduction logic
                if available.get('CRT', 0) == 0 and calculated_available.get('CRT', 0) > 0:
                    print(f"\n🚨 ISSUE IDENTIFIED: Endpoint not seeing CRT balance correctly!")
                    print(f"   Expected CRT: {calculated_available.get('CRT', 0):,.0f}")
                    print(f"   Endpoint sees: {available.get('CRT', 0):,.0f}")
                elif available.get('CRT', 0) > 0:
                    print(f"\n✅ Balance calculation working, issue is elsewhere")
        
        # 4. Test if we can manually transfer CRT to gaming balance
        print(f"\n🔄 Testing internal wallet transfer to move CRT to gaming balance...")
        
        # Check if internal transfer endpoint exists
        transfer_data = {
            "wallet_address": TEST_USER["wallet_address"],
            "from_wallet": "deposit",
            "to_wallet": "gaming", 
            "currency": "CRT",
            "amount": 1000000  # 1M CRT
        }
        
        async with session.post(f"{BACKEND_URL}/wallet/transfer", 
                               json=transfer_data, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"✅ Internal transfer successful: {result}")
                
                # Now test pool funding again
                print(f"\n🌊 Re-testing pool funding after CRT transfer...")
                async with session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=pool_data, headers=headers) as resp2:
                    result2 = await resp2.json()
                    print(f"📋 Pool Funding After Transfer:")
                    print(f"   Status: {resp2.status}")
                    print(f"   Response: {json.dumps(result2, indent=2)}")
                    
            else:
                result = await resp.json()
                print(f"❌ Internal transfer failed: {result}")

if __name__ == "__main__":
    asyncio.run(debug_balance_issue())