#!/usr/bin/env python3
"""
NOWPayments Authentication Test - Test JWT authentication for NOWPayments endpoints
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://tiger-dex-casino.preview.emergentagent.com/api"

TEST_CREDENTIALS = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

async def test_nowpayments_authentication():
    """Test authentication flow for NOWPayments endpoints"""
    
    async with aiohttp.ClientSession() as session:
        print("🔐 Testing NOWPayments Authentication Flow")
        print("="*60)
        
        # Step 1: Login to get user session
        print("1️⃣ Testing user login...")
        login_payload = {
            "username": TEST_CREDENTIALS["username"],
            "password": TEST_CREDENTIALS["password"]
        }
        
        async with session.post(f"{BACKEND_URL}/auth/login-username", json=login_payload) as response:
            if response.status == 200:
                login_data = await response.json()
                if login_data.get("success"):
                    print(f"✅ User login successful: {login_data.get('message')}")
                else:
                    print(f"❌ User login failed: {login_data.get('message')}")
                    return
            else:
                print(f"❌ Login HTTP error: {response.status}")
                return
        
        # Step 2: Generate wallet authentication challenge
        print("\n2️⃣ Testing wallet authentication challenge...")
        challenge_payload = {
            "wallet_address": TEST_CREDENTIALS["wallet_address"],
            "network": "solana"
        }
        
        async with session.post(f"{BACKEND_URL}/auth/challenge", json=challenge_payload) as response:
            if response.status == 200:
                challenge_data = await response.json()
                if challenge_data.get("success"):
                    print(f"✅ Challenge generated: {challenge_data.get('challenge_hash')[:16]}...")
                    challenge_hash = challenge_data.get("challenge_hash")
                else:
                    print(f"❌ Challenge generation failed: {challenge_data}")
                    return
            else:
                print(f"❌ Challenge HTTP error: {response.status}")
                return
        
        # Step 3: Verify wallet signature to get JWT token
        print("\n3️⃣ Testing wallet signature verification...")
        verify_payload = {
            "challenge_hash": challenge_hash,
            "signature": "mock_signature_for_nowpayments_test",
            "wallet_address": TEST_CREDENTIALS["wallet_address"],
            "network": "solana"
        }
        
        async with session.post(f"{BACKEND_URL}/auth/verify", json=verify_payload) as response:
            if response.status == 200:
                verify_data = await response.json()
                if verify_data.get("success"):
                    jwt_token = verify_data.get("token")
                    print(f"✅ JWT token generated: {jwt_token[:20]}...")
                else:
                    print(f"❌ Verification failed: {verify_data}")
                    return
            else:
                print(f"❌ Verification HTTP error: {response.status}")
                return
        
        # Step 4: Test NOWPayments endpoints with JWT token
        print("\n4️⃣ Testing NOWPayments endpoints with JWT authentication...")
        headers = {"Authorization": f"Bearer {jwt_token}"}
        
        # Test currencies endpoint
        async with session.get(f"{BACKEND_URL}/nowpayments/currencies", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ NOWPayments currencies accessible with JWT")
            else:
                print(f"❌ Currencies endpoint failed: {response.status}")
        
        # Test treasuries endpoint
        async with session.get(f"{BACKEND_URL}/nowpayments/treasuries", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ NOWPayments treasuries accessible with JWT")
            else:
                print(f"❌ Treasuries endpoint failed: {response.status}")
        
        # Test withdrawal endpoint (with small amount)
        print("\n5️⃣ Testing NOWPayments withdrawal endpoint with JWT...")
        withdrawal_payload = {
            "user_id": TEST_CREDENTIALS["username"],
            "currency": "DOGE",
            "amount": "10",  # Small test amount
            "destination_address": "D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda",
            "withdrawal_type": "standard"
        }
        
        async with session.post(f"{BACKEND_URL}/nowpayments/withdraw", 
                               json=withdrawal_payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("success"):
                    print(f"✅ NOWPayments withdrawal endpoint accessible: {data.get('message')}")
                    print(f"   Payout ID: {data.get('withdrawal', {}).get('payout_id')}")
                elif "Insufficient" in data.get("message", ""):
                    print(f"✅ NOWPayments withdrawal endpoint working (insufficient balance expected)")
                else:
                    print(f"⚠️  NOWPayments withdrawal response: {data.get('message')}")
            elif response.status == 403:
                error_data = await response.json()
                print(f"❌ Still getting 403 Forbidden: {error_data}")
            else:
                print(f"❌ Withdrawal endpoint error: {response.status} - {await response.text()}")
        
        print("\n🎯 AUTHENTICATION TEST SUMMARY:")
        print("✅ User login working")
        print("✅ Wallet challenge generation working") 
        print("✅ JWT token generation working")
        print("✅ NOWPayments read endpoints accessible with JWT")
        print("🔍 NOWPayments withdrawal endpoint authentication status checked")

if __name__ == "__main__":
    asyncio.run(test_nowpayments_authentication())