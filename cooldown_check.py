#!/usr/bin/env python3
"""
Check DOGE deposit cooldown status and timing
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

BACKEND_URL = "https://gamewin-vault.preview.emergentagent.com/api"

async def check_cooldown_details():
    """Check detailed cooldown information"""
    user_doge_address = "DLZccCAopg8SJYdmUWdjEkGq9t7boXMKMe"
    user_casino_account = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    
    async with aiohttp.ClientSession() as session:
        # Try the manual deposit endpoint to get detailed cooldown info
        payload = {
            "wallet_address": user_casino_account,
            "doge_address": user_doge_address
        }
        
        print("🕐 CHECKING DETAILED COOLDOWN STATUS...")
        print(f"📍 DOGE Address: {user_doge_address}")
        print(f"🎰 Casino Account: {user_casino_account}")
        print("=" * 60)
        
        try:
            async with session.post(f"{BACKEND_URL}/deposit/doge/manual", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"📊 Response: {json.dumps(data, indent=2)}")
                    
                    if not data.get("success"):
                        message = data.get("message", "")
                        if "cooldown" in message.lower() or "hour" in message.lower():
                            print(f"⏳ COOLDOWN STATUS: {message}")
                            
                            # Try to extract timing information
                            if "last deposit check" in message:
                                print("🔍 ANALYZING COOLDOWN TIMING...")
                                # The message should contain timestamp info
                                print(f"💡 RECOMMENDATION: User should wait and try again in a few minutes")
                        else:
                            print(f"❌ OTHER ERROR: {message}")
                    else:
                        print(f"🎉 SUCCESS: Deposit processed! {data}")
                else:
                    error_text = await response.text()
                    print(f"❌ API ERROR: HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            print(f"💥 ERROR: {e}")

        # Also check if we can get deposit records from database
        print("\n🔍 CHECKING FOR DEPOSIT RECORDS...")
        try:
            async with session.get(f"{BACKEND_URL}/deposit/check-doge?wallet_address={user_casino_account}&doge_address={user_doge_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"📋 Deposit Check Response: {json.dumps(data, indent=2)}")
                elif response.status == 404:
                    print("📋 Deposit check endpoint not available")
                else:
                    error_text = await response.text()
                    print(f"❌ Deposit Check Error: HTTP {response.status}: {error_text}")
        except Exception as e:
            print(f"💥 Deposit Check Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_cooldown_details())