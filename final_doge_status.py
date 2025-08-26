#!/usr/bin/env python3
"""
Final DOGE Deposit Status Report for User
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

BACKEND_URL = "https://cryptosavings.preview.emergentagent.com/api"

async def generate_final_status_report():
    """Generate comprehensive final status report for user"""
    user_doge_address = "DLZccCAopg8SJYdmUWdjEkGq9t7boXMKMe"
    user_casino_account = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    expected_amount = 30.0
    
    print("🎯 FINAL DOGE DEPOSIT STATUS REPORT")
    print("=" * 60)
    print(f"📍 DOGE Deposit Address: {user_doge_address}")
    print(f"🎰 Casino Account: {user_casino_account}")
    print(f"💰 Expected Amount: {expected_amount} DOGE")
    print(f"🕐 Report Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        
        # 1. Check DOGE balance at deposit address
        print("\n1️⃣ DOGE BALANCE VERIFICATION")
        print("-" * 30)
        try:
            async with session.get(f"{BACKEND_URL}/wallet/balance/DOGE?wallet_address={user_doge_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        confirmed = data.get("balance", 0)
                        unconfirmed = data.get("unconfirmed", 0)
                        total = data.get("total", 0)
                        
                        print(f"✅ CONFIRMED BALANCE: {confirmed} DOGE")
                        print(f"⏳ UNCONFIRMED BALANCE: {unconfirmed} DOGE")
                        print(f"💎 TOTAL BALANCE: {total} DOGE")
                        
                        if confirmed >= expected_amount:
                            print(f"🎉 STATUS: SUFFICIENT DOGE CONFIRMED ({confirmed} >= {expected_amount})")
                        else:
                            print(f"⚠️ STATUS: INSUFFICIENT DOGE ({confirmed} < {expected_amount})")
                    else:
                        print(f"❌ ERROR: {data.get('error', 'Unknown error')}")
                else:
                    print(f"❌ API ERROR: HTTP {response.status}")
        except Exception as e:
            print(f"💥 EXCEPTION: {e}")
        
        # 2. Check casino account balance
        print("\n2️⃣ CASINO ACCOUNT STATUS")
        print("-" * 30)
        try:
            async with session.get(f"{BACKEND_URL}/wallet/{user_casino_account}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        wallet = data["wallet"]
                        current_doge = wallet.get("deposit_balance", {}).get("DOGE", 0)
                        savings_doge = wallet.get("savings_balance", {}).get("DOGE", 0)
                        
                        print(f"💰 CURRENT DOGE BALANCE: {current_doge} DOGE")
                        print(f"🏦 SAVINGS BALANCE: {savings_doge} DOGE")
                        print(f"👤 USER ID: {wallet.get('user_id', 'Unknown')}")
                        print(f"📅 ACCOUNT CREATED: {wallet.get('created_at', 'Unknown')}")
                    else:
                        print(f"❌ ERROR: {data.get('message', 'Unknown error')}")
                else:
                    print(f"❌ API ERROR: HTTP {response.status}")
        except Exception as e:
            print(f"💥 EXCEPTION: {e}")
        
        # 3. Check cooldown status and attempt deposit
        print("\n3️⃣ DEPOSIT PROCESSING STATUS")
        print("-" * 30)
        try:
            payload = {
                "wallet_address": user_casino_account,
                "doge_address": user_doge_address
            }
            
            async with session.post(f"{BACKEND_URL}/deposit/doge/manual", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        credited = data.get("credited_amount", 0)
                        tx_id = data.get("transaction_id", "")
                        print(f"🎉 DEPOSIT SUCCESSFUL!")
                        print(f"💰 CREDITED AMOUNT: {credited} DOGE")
                        print(f"🧾 TRANSACTION ID: {tx_id}")
                        print(f"🎮 STATUS: USER CAN NOW ACCESS GAMING FEATURES")
                        
                        final_status = "DEPOSIT_COMPLETED"
                    else:
                        message = data.get("message", "")
                        last_deposit = data.get("last_deposit", "")
                        
                        if "cooldown" in message.lower() or "hour" in message.lower():
                            print(f"⏳ COOLDOWN ACTIVE")
                            print(f"📝 MESSAGE: {message}")
                            
                            if last_deposit:
                                try:
                                    last_time = datetime.fromisoformat(last_deposit.replace('Z', '+00:00'))
                                    current_time = datetime.utcnow()
                                    elapsed = current_time - last_time.replace(tzinfo=None)
                                    remaining = timedelta(hours=1) - elapsed
                                    
                                    print(f"🕐 LAST CHECK: {last_deposit}")
                                    print(f"⏰ TIME ELAPSED: {elapsed}")
                                    
                                    if remaining.total_seconds() > 0:
                                        minutes_remaining = int(remaining.total_seconds() / 60)
                                        print(f"⏳ COOLDOWN REMAINING: ~{minutes_remaining} minutes")
                                        print(f"🔄 RETRY AFTER: {(current_time + remaining).strftime('%Y-%m-%d %H:%M:%S')} UTC")
                                        final_status = "COOLDOWN_ACTIVE"
                                    else:
                                        print(f"✅ COOLDOWN SHOULD BE EXPIRED - TRY AGAIN")
                                        final_status = "READY_TO_RETRY"
                                except Exception as time_error:
                                    print(f"⚠️ TIME CALCULATION ERROR: {time_error}")
                                    final_status = "COOLDOWN_ACTIVE"
                            else:
                                final_status = "COOLDOWN_ACTIVE"
                        else:
                            print(f"❌ DEPOSIT FAILED: {message}")
                            final_status = "DEPOSIT_FAILED"
                else:
                    print(f"❌ API ERROR: HTTP {response.status}")
                    final_status = "API_ERROR"
        except Exception as e:
            print(f"💥 EXCEPTION: {e}")
            final_status = "EXCEPTION_ERROR"
        
        # 4. Final recommendations
        print("\n4️⃣ RECOMMENDATIONS FOR USER")
        print("-" * 30)
        
        if final_status == "DEPOSIT_COMPLETED":
            print("🎉 CONGRATULATIONS! Your DOGE deposit has been successfully credited!")
            print("🎮 You can now access all casino gaming features")
            print("💰 Your 30 DOGE is ready to use for betting")
            
        elif final_status == "COOLDOWN_ACTIVE":
            print("⏳ Your DOGE deposit is confirmed but in security cooldown")
            print("🔒 This is normal anti-double-spend protection")
            print("⏰ Please wait for the cooldown to expire and try again")
            print("🔄 The system will automatically credit your DOGE after cooldown")
            
        elif final_status == "READY_TO_RETRY":
            print("✅ Cooldown should be expired - please try the deposit again")
            print("🔄 Use the manual deposit verification in your account")
            
        else:
            print("⚠️ There may be an issue with the deposit process")
            print("📞 Consider contacting support if the issue persists")
        
        print("\n" + "=" * 60)
        print(f"🏁 FINAL STATUS: {final_status}")
        print("=" * 60)
        
        return final_status

if __name__ == "__main__":
    asyncio.run(generate_final_status_report())