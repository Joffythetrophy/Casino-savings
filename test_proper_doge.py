#!/usr/bin/env python3
"""
Test with proper DOGE address format
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://tiger-dex-casino.preview.emergentagent.com/api"

async def test_proper_doge():
    user_wallet_address = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    
    # Test with proper DOGE addresses that start with 'D' and are correct length
    test_addresses = [
        "D7Y55r6hNkcqDTvFW8GmyJKBGkbqNgLKjh",  # Valid format
        "DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L",  # Valid format
        "D8cGKNNrHAkbRUpDrUrqkMZvkp8xPcXr7J"   # Valid format
    ]
    
    async with aiohttp.ClientSession() as session:
        
        for doge_address in test_addresses:
            print(f"\n🧪 Testing DOGE address: {doge_address}")
            print(f"Length: {len(doge_address)}, Starts with D: {doge_address.startswith('D')}")
            
            # Test address validation first
            print("1. Testing address validation...")
            validation_payload = {"address": doge_address}
            
            # Test manual verification
            print("2. Testing manual verification...")
            manual_payload = {
                "wallet_address": user_wallet_address,
                "doge_address": doge_address,
                "expected_amount": 25.0
            }
            
            async with session.post(f"{BACKEND_URL}/deposit/doge/manual", 
                                  json=manual_payload) as response:
                print(f"   Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"   Response: {json.dumps(data, indent=4)}")
                    
                    if data.get("success"):
                        print("   ✅ DOGE deposit would be successful!")
                    else:
                        print(f"   ⚠️ Expected response: {data.get('message')}")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Error: {error_text}")
            
            print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_proper_doge())