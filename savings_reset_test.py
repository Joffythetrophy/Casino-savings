#!/usr/bin/env python3
"""
URGENT: Savings Reset Test
Testing if we can reset USDC and CRT savings to zero as requested
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://crypto-treasury.preview.emergentagent.com/api"

async def test_savings_reset():
    """Test various approaches to reset savings balances"""
    target_user = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    
    async with aiohttp.ClientSession() as session:
        print(f"🔄 TESTING SAVINGS RESET APPROACHES FOR: {target_user}")
        
        # Approach 1: Check if there's a direct savings reset endpoint
        print("\n1. Testing direct savings reset endpoint...")
        reset_payload = {
            "wallet_address": target_user,
            "reset_savings": True,
            "currencies": ["USDC", "CRT"]
        }
        
        async with session.post(f"{BACKEND_URL}/wallet/reset-savings", json=reset_payload) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Direct reset endpoint works: {data}")
            else:
                print(f"❌ Direct reset endpoint not available: HTTP {response.status}")
        
        # Approach 2: Check if there's a test endpoint for balance manipulation
        print("\n2. Testing test balance manipulation endpoint...")
        test_payload = {
            "wallet_address": target_user,
            "action": "reset_savings",
            "currencies": ["USDC", "CRT"]
        }
        
        async with session.post(f"{BACKEND_URL}/test/reset-savings", json=test_payload) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Test reset endpoint works: {data}")
            else:
                print(f"❌ Test reset endpoint not available: HTTP {response.status}")
        
        # Approach 3: Check if we can use withdrawal to zero out savings
        print("\n3. Testing withdrawal approach to zero out savings...")
        
        # First get current savings
        async with session.get(f"{BACKEND_URL}/wallet/{target_user}") as response:
            if response.status == 200:
                data = await response.json()
                if data.get("success"):
                    wallet = data["wallet"]
                    savings_balance = wallet.get("savings_balance", {})
                    usdc_savings = savings_balance.get("USDC", 0)
                    crt_savings = savings_balance.get("CRT", 0)
                    
                    print(f"Current savings - USDC: {usdc_savings}, CRT: {crt_savings}")
                    
                    # Try to withdraw all USDC savings
                    if usdc_savings > 0:
                        withdraw_payload = {
                            "wallet_address": target_user,
                            "wallet_type": "savings",
                            "currency": "USDC",
                            "amount": usdc_savings
                        }
                        
                        async with session.post(f"{BACKEND_URL}/wallet/withdraw", json=withdraw_payload) as withdraw_response:
                            if withdraw_response.status == 200:
                                withdraw_data = await withdraw_response.json()
                                print(f"✅ USDC savings withdrawal: {withdraw_data}")
                            else:
                                print(f"❌ USDC savings withdrawal failed: HTTP {withdraw_response.status}")
                    
                    # Try to withdraw all CRT savings
                    if crt_savings > 0:
                        withdraw_payload = {
                            "wallet_address": target_user,
                            "wallet_type": "savings",
                            "currency": "CRT",
                            "amount": crt_savings
                        }
                        
                        async with session.post(f"{BACKEND_URL}/wallet/withdraw", json=withdraw_payload) as withdraw_response:
                            if withdraw_response.status == 200:
                                withdraw_data = await withdraw_response.json()
                                print(f"✅ CRT savings withdrawal: {withdraw_data}")
                            else:
                                print(f"❌ CRT savings withdrawal failed: HTTP {withdraw_response.status}")
        
        # Approach 4: Check if there's a savings withdrawal endpoint
        print("\n4. Testing savings withdrawal endpoint...")
        savings_withdraw_payload = {
            "wallet_address": target_user,
            "currency": "USDC",
            "amount": 700.0  # Current USDC savings amount
        }
        
        async with session.post(f"{BACKEND_URL}/savings/withdraw", json=savings_withdraw_payload) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Savings withdrawal endpoint: {data}")
            else:
                print(f"❌ Savings withdrawal endpoint: HTTP {response.status}")
        
        # Approach 5: Check current balance after all attempts
        print("\n5. Final balance check...")
        async with session.get(f"{BACKEND_URL}/wallet/{target_user}") as response:
            if response.status == 200:
                data = await response.json()
                if data.get("success"):
                    wallet = data["wallet"]
                    savings_balance = wallet.get("savings_balance", {})
                    usdc_savings = savings_balance.get("USDC", 0)
                    crt_savings = savings_balance.get("CRT", 0)
                    
                    print(f"📊 Final savings - USDC: {usdc_savings}, CRT: {crt_savings}")
                    
                    if usdc_savings == 0 and crt_savings == 0:
                        print("✅ SUCCESS: Both USDC and CRT savings reset to zero!")
                    else:
                        print("❌ FAILED: Savings still not reset to zero")
                        print("🔧 RECOMMENDATION: Need to implement direct database update for savings reset")

if __name__ == "__main__":
    asyncio.run(test_savings_reset())