#!/usr/bin/env python3
"""
Balance Deduction Bug Verification Test
Specifically tests the CRITICAL bug where 21M CRT is in liquidity_pool but pool funding only checks deposit/gaming/winnings
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

async def test_balance_bug():
    """Test the specific balance deduction bug"""
    print("🚨 TESTING CRITICAL BALANCE DEDUCTION BUG")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        # 1. Get user balances
        async with session.get(f"{BACKEND_URL}/wallet/{TEST_USER['wallet_address']}") as resp:
            if resp.status == 200:
                result = await resp.json()
                wallet = result.get("wallet", {})
                
                deposit_crt = wallet.get("deposit_balance", {}).get("CRT", 0)
                gaming_crt = wallet.get("gaming_balance", {}).get("CRT", 0)
                winnings_crt = wallet.get("winnings_balance", {}).get("CRT", 0)
                liquidity_crt = wallet.get("liquidity_pool", {}).get("CRT", 0)
                
                print(f"📊 USER CRT BALANCE BREAKDOWN:")
                print(f"   Deposit Balance:    {deposit_crt:,.2f} CRT")
                print(f"   Gaming Balance:     {gaming_crt:,.2f} CRT")
                print(f"   Winnings Balance:   {winnings_crt:,.2f} CRT")
                print(f"   Liquidity Pool:     {liquidity_crt:,.2f} CRT")
                print(f"   TOTAL CRT:          {deposit_crt + gaming_crt + winnings_crt + liquidity_crt:,.2f} CRT")
                
                # Calculate what pool funding system sees
                pool_funding_sees = deposit_crt + gaming_crt + winnings_crt
                print(f"\n🔍 POOL FUNDING SYSTEM CALCULATION:")
                print(f"   Available CRT (deposit + gaming + winnings): {pool_funding_sees:,.2f} CRT")
                print(f"   Missing CRT (in liquidity_pool):            {liquidity_crt:,.2f} CRT")
                
                if liquidity_crt > 20000000 and pool_funding_sees < 1000000:
                    print(f"\n❌ CRITICAL BUG CONFIRMED!")
                    print(f"   • User has {liquidity_crt:,.0f} CRT in liquidity_pool")
                    print(f"   • Pool funding only sees {pool_funding_sees:,.0f} CRT")
                    print(f"   • Bug: Pool funding ignores liquidity_pool balance!")
                    return False
                else:
                    print(f"\n✅ Balance calculation appears correct")
                    return True
            else:
                print(f"❌ Failed to get wallet info: {resp.status}")
                return False

async def test_small_pool_funding():
    """Test small pool funding to confirm the bug"""
    print(f"\n🧪 TESTING SMALL POOL FUNDING ($100)")
    print("="*60)
    
    async with aiohttp.ClientSession() as session:
        # Authenticate first
        login_data = {
            "identifier": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        
        async with session.post(f"{BACKEND_URL}/auth/login", json=login_data) as resp:
            if resp.status == 200:
                result = await resp.json()
                token = result.get("token")
                headers = {"Authorization": f"Bearer {token}"}
                
                # Try small pool funding
                pool_request = {
                    "wallet_address": TEST_USER["wallet_address"],
                    "pool_requests": [
                        {
                            "pool_type": "CRT/USDC",
                            "amount_usd": 100
                        }
                    ]
                }
                
                async with session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                      json=pool_request, headers=headers) as resp:
                    result = await resp.json()
                    
                    if resp.status == 200 and result.get("success"):
                        print(f"✅ Pool funding successful!")
                        return True
                    else:
                        error = result.get("error", "Unknown error")
                        needed = result.get("needed", {})
                        available = result.get("available", {})
                        
                        print(f"❌ Pool funding failed: {error}")
                        print(f"   Needed CRT:    {needed.get('CRT', 0):,.0f}")
                        print(f"   Available CRT: {available.get('CRT', 0):,.0f}")
                        
                        if "insufficient balance" in error.lower() and available.get('CRT', 0) == 0:
                            print(f"\n🚨 BUG CONFIRMED: System shows 0 CRT available despite user having 21M CRT!")
                            return False
                        return False
            else:
                print(f"❌ Authentication failed: {resp.status}")
                return False

async def main():
    """Run balance bug verification tests"""
    print("🚨 CRITICAL BALANCE DEDUCTION BUG VERIFICATION")
    print(f"User: {TEST_USER['username']} ({TEST_USER['wallet_address']})")
    print("="*80)
    
    # Test 1: Check balance breakdown
    balance_ok = await test_balance_bug()
    
    # Test 2: Test pool funding
    funding_ok = await test_small_pool_funding()
    
    print(f"\n{'='*80}")
    print(f"🎯 FINAL ASSESSMENT:")
    
    if not balance_ok and not funding_ok:
        print(f"❌ CRITICAL BUG CONFIRMED!")
        print(f"   • User has 21M CRT in liquidity_pool balance")
        print(f"   • Pool funding system ignores liquidity_pool balance")
        print(f"   • System incorrectly shows 0 CRT available")
        print(f"   • Pool funding fails due to 'insufficient balance'")
        print(f"\n🔧 FIX REQUIRED:")
        print(f"   Update lines 1831-1835 in server.py to include liquidity_pool balance:")
        print(f"   total = (deposit_balance.get(currency, 0) + ")
        print(f"           gaming_balance.get(currency, 0) + ")
        print(f"           winnings_balance.get(currency, 0) +")
        print(f"           liquidity_pool.get(currency, 0))  # ADD THIS LINE")
        return 1
    else:
        print(f"✅ Balance deduction bug appears to be fixed")
        return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)