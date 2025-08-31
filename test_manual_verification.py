#!/usr/bin/env python3
"""
Test Manual DOGE Verification System
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://crypto-treasury.preview.emergentagent.com/api"

async def test_manual_verification():
    user_wallet_address = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    
    print("🔍 TESTING MANUAL DOGE VERIFICATION SYSTEM")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Test with a valid DOGE address
        valid_doge_address = "DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L"
        
        print(f"User's Solana Wallet: {user_wallet_address}")
        print(f"Test DOGE Address: {valid_doge_address}")
        print()
        
        manual_payload = {
            "wallet_address": user_wallet_address,
            "doge_address": valid_doge_address,
            "expected_amount": 50.0
        }
        
        print("📤 Sending manual verification request...")
        print(f"Payload: {json.dumps(manual_payload, indent=2)}")
        print()
        
        async with session.post(f"{BACKEND_URL}/deposit/doge/manual", 
                              json=manual_payload) as response:
            print(f"Response Status: {response.status}")
            
            if response.status == 200:
                data = await response.json()
                print("✅ Manual verification system response:")
                print(json.dumps(data, indent=2))
                
                if data.get("success"):
                    print("\n🎉 DOGE deposit would be credited!")
                    print(f"Amount: {data.get('amount', 0)} DOGE")
                    print(f"Transaction ID: {data.get('transaction_id', 'N/A')}")
                else:
                    print(f"\n⚠️ Expected response: {data.get('message', 'No message')}")
                    
            else:
                error_text = await response.text()
                print(f"❌ Error response: {error_text}")

if __name__ == "__main__":
    asyncio.run(test_manual_verification())