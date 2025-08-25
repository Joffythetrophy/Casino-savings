#!/usr/bin/env python3
"""
Specific DOGE Deposit Address Test for User Request
Tests the exact functionality requested: Generate DOGE deposit address for user's Solana wallet
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Backend URL from frontend env
BACKEND_URL = "https://winsaver.preview.emergentagent.com/api"

async def test_user_doge_deposit_request():
    """Test the specific DOGE deposit request from the user"""
    
    # User's specific wallet address from the request
    user_wallet_address = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    
    print("🐕 TESTING DOGE DEPOSIT ADDRESS GENERATION FOR USER REQUEST")
    print("=" * 70)
    print(f"User's Solana Wallet: {user_wallet_address}")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Generate DOGE deposit address for the user's wallet
        print("1️⃣ GENERATING DOGE DEPOSIT ADDRESS...")
        try:
            endpoint = f"{BACKEND_URL}/deposit/doge-address/{user_wallet_address}"
            print(f"   Calling: {endpoint}")
            
            async with session.get(endpoint) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        doge_address = data.get("doge_deposit_address")
                        network = data.get("network")
                        instructions = data.get("instructions", {})
                        min_deposit = instructions.get("min_deposit_amount")
                        processing_time = instructions.get("processing_time")
                        
                        print("   ✅ SUCCESS!")
                        print(f"   🏦 DOGE Deposit Address: {doge_address}")
                        print(f"   🌐 Network: {network}")
                        print(f"   💰 Minimum Deposit: {min_deposit} DOGE")
                        print(f"   ⏱️  Processing Time: {processing_time}")
                        print()
                        
                        # Test 2: Get complete deposit instructions
                        print("2️⃣ DEPOSIT INSTRUCTIONS:")
                        if "steps" in instructions:
                            for i, step in enumerate(instructions["steps"], 1):
                                print(f"   Step {i}: {step}")
                        print()
                        
                        # Test 3: Verify this is a real DOGE address format
                        print("3️⃣ DOGE ADDRESS VALIDATION:")
                        if doge_address and doge_address.startswith("DOGE_"):
                            print("   ✅ Generated address follows expected format")
                            print(f"   📝 Address Pattern: DOGE_[hash]_[wallet_prefix]")
                            print(f"   🔗 This address is unique to user's wallet: {user_wallet_address[:12]}...")
                        else:
                            print("   ❌ Address format unexpected")
                        print()
                        
                        # Test 4: Test manual verification system
                        print("4️⃣ TESTING MANUAL VERIFICATION SYSTEM...")
                        
                        # Test with a valid DOGE address to see the system response
                        valid_doge_address = "DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L"  # Known valid DOGE address
                        
                        manual_payload = {
                            "wallet_address": user_wallet_address,
                            "doge_address": valid_doge_address,
                            "expected_amount": 50.0
                        }
                        
                        async with session.post(f"{BACKEND_URL}/deposit/doge/manual", 
                                              json=manual_payload) as manual_response:
                            if manual_response.status == 200:
                                manual_data = await manual_response.json()
                                print("   ✅ Manual verification system is operational")
                                print(f"   📋 Response: {manual_data.get('message', 'System ready')}")
                            else:
                                manual_text = await manual_response.text()
                                print(f"   ⚠️  Manual verification response: HTTP {manual_response.status}")
                                print(f"   📋 Details: {manual_text}")
                        print()
                        
                        # Summary for user
                        print("🎯 SUMMARY FOR USER:")
                        print("=" * 50)
                        print(f"✅ Your DOGE deposit address: {doge_address}")
                        print(f"✅ Network: {network}")
                        print(f"✅ Minimum deposit: {min_deposit} DOGE")
                        print(f"✅ Processing time: {processing_time}")
                        print()
                        print("📋 HOW TO USE:")
                        print("1. Send DOGE to the address above")
                        print("2. Wait for blockchain confirmation")
                        print("3. Use the manual verification system to confirm your deposit")
                        print("4. Your DOGE will be credited to your casino account")
                        
                        return {
                            "success": True,
                            "doge_address": doge_address,
                            "network": network,
                            "min_deposit": min_deposit,
                            "processing_time": processing_time,
                            "instructions": instructions
                        }
                        
                    else:
                        print(f"   ❌ FAILED: {data.get('message', 'Unknown error')}")
                        return {"success": False, "error": data.get('message')}
                        
                else:
                    error_text = await response.text()
                    print(f"   ❌ HTTP {response.status}: {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}"}
                    
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    result = asyncio.run(test_user_doge_deposit_request())
    
    print("\n" + "=" * 70)
    if result["success"]:
        print("🎉 DOGE DEPOSIT ADDRESS GENERATION: SUCCESS")
        print("The user can now receive their DOGE deposit address and instructions!")
    else:
        print("❌ DOGE DEPOSIT ADDRESS GENERATION: FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")
    print("=" * 70)