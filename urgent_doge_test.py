#!/usr/bin/env python3
"""
URGENT: DOGE Deposit Confirmation Status Check for Real User
"""

import asyncio
import aiohttp
import json
from datetime import datetime

# Backend URL
BACKEND_URL = "https://winsaver.preview.emergentagent.com/api"

async def check_doge_deposit_status():
    """Check DOGE deposit confirmation status for the specific user"""
    
    # User's specific details from review request
    user_doge_address = "DLZccCAopg8SJYdmUWdjEkGq9t7boXMKMe"
    user_casino_account = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    expected_amount = 30.0
    
    print("🚨 URGENT: DOGE Deposit Confirmation Status Check")
    print("=" * 60)
    print(f"👤 User Casino Account: {user_casino_account}")
    print(f"🏷️ DOGE Deposit Address: {user_doge_address}")
    print(f"💰 Expected Amount: {expected_amount} DOGE")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Current DOGE Balance Status Check
        print(f"\n🔍 1. Checking current DOGE balance status...")
        try:
            async with session.get(f"{BACKEND_URL}/wallet/balance/DOGE?wallet_address={user_doge_address}") as response:
                print(f"   Response Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Response Data: {json.dumps(data, indent=2)}")
                    
                    if data.get("success"):
                        balance = data.get("balance", 0)
                        unconfirmed = data.get("unconfirmed", 0)
                        total = data.get("total", 0)
                        source = data.get("source", "unknown")
                        
                        print(f"   ✅ DOGE Balance Check Results:")
                        print(f"      - Confirmed Balance: {balance} DOGE")
                        print(f"      - Unconfirmed Balance: {unconfirmed} DOGE")
                        print(f"      - Total Balance: {total} DOGE")
                        print(f"      - Source: {source}")
                        
                        if total >= expected_amount:
                            if balance >= expected_amount:
                                print(f"   🎉 STATUS: CONFIRMED - {expected_amount} DOGE is CONFIRMED!")
                            else:
                                print(f"   ⏳ STATUS: UNCONFIRMED - {expected_amount} DOGE detected but waiting for confirmations")
                        else:
                            print(f"   ❌ STATUS: NOT FOUND - Expected {expected_amount} DOGE not detected")
                    else:
                        error_msg = data.get("error", "Unknown error")
                        print(f"   ❌ DOGE balance check failed: {error_msg}")
                else:
                    error_text = await response.text()
                    print(f"   ❌ HTTP {response.status}: {error_text}")
        except Exception as e:
            print(f"   ❌ Error checking DOGE balance: {str(e)}")
        
        # Test 2: Manual Deposit Re-Check
        print(f"\n🔄 2. Testing manual deposit re-check...")
        try:
            manual_deposit_payload = {
                "doge_address": user_doge_address,
                "wallet_address": user_casino_account
            }
            
            async with session.post(f"{BACKEND_URL}/deposit/doge/manual", 
                                   json=manual_deposit_payload) as response:
                print(f"   Response Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Response Data: {json.dumps(data, indent=2)}")
                    
                    if data.get("success"):
                        credited_amount = data.get("credited_amount", 0)
                        transaction_id = data.get("transaction_id", "N/A")
                        print(f"   ✅ MANUAL DEPOSIT SUCCESSFUL!")
                        print(f"      - Credited Amount: {credited_amount} DOGE")
                        print(f"      - Transaction ID: {transaction_id}")
                    else:
                        reason = data.get("message", "Unknown reason")
                        print(f"   ⏳ Manual deposit not processed yet: {reason}")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Manual deposit check failed - HTTP {response.status}: {error_text}")
        except Exception as e:
            print(f"   ❌ Error with manual deposit check: {str(e)}")
        
        # Test 3: Casino Account Balance Check
        print(f"\n💰 3. Checking casino account balance...")
        try:
            async with session.get(f"{BACKEND_URL}/wallet/{user_casino_account}") as response:
                print(f"   Response Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Response Data: {json.dumps(data, indent=2)}")
                    
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        doge_deposit_balance = wallet.get("deposit_balance", {}).get("DOGE", 0)
                        doge_winnings_balance = wallet.get("winnings_balance", {}).get("DOGE", 0)
                        total_doge_in_casino = doge_deposit_balance + doge_winnings_balance
                        
                        print(f"   💰 Casino DOGE Balance:")
                        print(f"      - Deposit Balance: {doge_deposit_balance} DOGE")
                        print(f"      - Winnings Balance: {doge_winnings_balance} DOGE")
                        print(f"      - Total in Casino: {total_doge_in_casino} DOGE")
                        
                        if total_doge_in_casino >= expected_amount:
                            print(f"   ✅ DOGE CREDITED TO CASINO ACCOUNT!")
                        else:
                            print(f"   ⏳ DOGE not yet credited to casino account")
                    else:
                        print(f"   ❌ Could not retrieve casino account balance: {data.get('message', 'Unknown error')}")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Casino account check failed - HTTP {response.status}: {error_text}")
        except Exception as e:
            print(f"   ❌ Error checking casino account: {str(e)}")
        
        # Test 4: DOGE Deposit Address Verification
        print(f"\n🏷️ 4. Verifying DOGE deposit address...")
        try:
            async with session.get(f"{BACKEND_URL}/deposit/doge-address/{user_casino_account}") as response:
                print(f"   Response Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Response Data: {json.dumps(data, indent=2)}")
                    
                    if data.get("success"):
                        generated_address = data.get("doge_address", "N/A")
                        network = data.get("network", "N/A")
                        min_deposit = data.get("min_deposit", "N/A")
                        
                        print(f"   🏷️ DOGE Address Info:")
                        print(f"      - Generated Address: {generated_address}")
                        print(f"      - User's Address: {user_doge_address}")
                        print(f"      - Network: {network}")
                        print(f"      - Min Deposit: {min_deposit}")
                        
                        if generated_address == user_doge_address:
                            print(f"   ✅ ADDRESS MATCH CONFIRMED!")
                        else:
                            print(f"   ℹ️ Different address generated (user used different address)")
                    else:
                        print(f"   ❌ Could not generate DOGE address: {data.get('message', 'Unknown error')}")
                else:
                    error_text = await response.text()
                    print(f"   ❌ DOGE address generation failed - HTTP {response.status}: {error_text}")
        except Exception as e:
            print(f"   ❌ Error verifying DOGE address: {str(e)}")
    
    print(f"\n🎯 FINAL STATUS SUMMARY:")
    print("=" * 50)
    print(f"⏰ Check completed at: {datetime.utcnow().isoformat()}")
    print("📊 Review the detailed results above for current DOGE deposit status!")

if __name__ == "__main__":
    asyncio.run(check_doge_deposit_status())