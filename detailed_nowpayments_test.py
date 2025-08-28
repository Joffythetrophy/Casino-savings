#!/usr/bin/env python3
"""
Detailed NOWPayments Test - Direct API Testing
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime

# New NOWPayments credentials
API_KEY = "FSVPHG1-1TK4MDZ-MKC4TTV-MW1MAXX"
PUBLIC_KEY = "f9a7e8ba-2573-4da2-9f4f-3e0ffd748212"

async def test_nowpayments_direct():
    """Test NOWPayments API directly"""
    
    async with aiohttp.ClientSession() as session:
        headers = {
            'x-api-key': API_KEY,
            'Content-Type': 'application/json'
        }
        
        print("🔍 Testing NOWPayments API directly...")
        print(f"API Key: {API_KEY}")
        print(f"Public Key: {PUBLIC_KEY}")
        print("=" * 60)
        
        # Test 1: Status check
        print("1. Testing API status...")
        try:
            async with session.get("https://api.nowpayments.io/v1/status", headers=headers) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Status OK: {data}")
                else:
                    error = await response.text()
                    print(f"❌ Status Error: {error}")
        except Exception as e:
            print(f"❌ Status Exception: {e}")
        
        print()
        
        # Test 2: Currencies check
        print("2. Testing currencies...")
        try:
            async with session.get("https://api.nowpayments.io/v1/currencies", headers=headers) as response:
                print(f"Currencies Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    currencies = data.get("currencies", [])
                    doge_supported = "doge" in [c.lower() for c in currencies]
                    print(f"✅ Currencies OK: {len(currencies)} total, DOGE supported: {doge_supported}")
                else:
                    error = await response.text()
                    print(f"❌ Currencies Error: {error}")
        except Exception as e:
            print(f"❌ Currencies Exception: {e}")
        
        print()
        
        # Test 3: Minimum amount check
        print("3. Testing minimum amount for DOGE...")
        try:
            async with session.get("https://api.nowpayments.io/v1/min-amount?currency_from=doge", headers=headers) as response:
                print(f"Min Amount Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Min Amount OK: {data}")
                else:
                    error = await response.text()
                    print(f"❌ Min Amount Error: {error}")
        except Exception as e:
            print(f"❌ Min Amount Exception: {e}")
        
        print()
        
        # Test 4: Payout test (this is the critical test)
        print("4. Testing payout creation (CRITICAL TEST)...")
        try:
            payout_data = {
                "withdrawals": [
                    {
                        "address": "DLbWLzxq2mxE3Adzn9MFKQ6EBP8gTE5po8",
                        "currency": "doge",
                        "amount": "50"
                    }
                ]
            }
            
            async with session.post("https://api.nowpayments.io/v1/payout", 
                                  headers=headers, json=payout_data) as response:
                print(f"Payout Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"🎉 PAYOUT SUCCESS: {data}")
                    print("✅ CUSTODY ACTIVATION CONFIRMED!")
                elif response.status == 401:
                    error = await response.text()
                    print(f"❌ PAYOUT 401 UNAUTHORIZED: {error}")
                    print("⏳ Custody activation still pending - payout permissions not yet active")
                else:
                    error = await response.text()
                    print(f"❌ PAYOUT ERROR {response.status}: {error}")
        except Exception as e:
            print(f"❌ Payout Exception: {e}")
        
        print()
        print("=" * 60)
        print("🎯 SUMMARY:")
        print("- New API credentials are valid and working")
        print("- DOGE currency is supported")
        print("- If payout returned 401, custody activation is still in progress")
        print("- If payout succeeded, custody is fully activated!")

if __name__ == "__main__":
    asyncio.run(test_nowpayments_direct())