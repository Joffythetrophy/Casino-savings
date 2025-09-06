#!/usr/bin/env python3
"""
URGENT: CRT Savings Reduction Test
Attempting to reduce CRT savings as much as possible through multiple withdrawals
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://blockchain-slots.preview.emergentagent.com/api"

async def reduce_crt_savings():
    """Attempt to reduce CRT savings through multiple maximum withdrawals"""
    target_user = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    
    async with aiohttp.ClientSession() as session:
        print(f"🔄 ATTEMPTING TO REDUCE CRT SAVINGS FOR: {target_user}")
        
        for attempt in range(5):  # Try up to 5 withdrawal attempts
            print(f"\n--- ATTEMPT {attempt + 1} ---")
            
            # Get current savings and liquidity
            async with session.get(f"{BACKEND_URL}/wallet/{target_user}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        wallet = data["wallet"]
                        savings_balance = wallet.get("savings_balance", {})
                        crt_savings = savings_balance.get("CRT", 0)
                        
                        print(f"Current CRT savings: {crt_savings:,.0f}")
                        
                        if crt_savings <= 0:
                            print("✅ CRT savings already at zero!")
                            break
                        
                        # Try to withdraw maximum allowed amount
                        # First, let's test what the maximum withdrawal is
                        test_withdraw_payload = {
                            "wallet_address": target_user,
                            "wallet_type": "savings",
                            "currency": "CRT",
                            "amount": crt_savings  # Try to withdraw all
                        }
                        
                        async with session.post(f"{BACKEND_URL}/wallet/withdraw", json=test_withdraw_payload) as withdraw_response:
                            if withdraw_response.status == 200:
                                withdraw_data = await withdraw_response.json()
                                
                                if withdraw_data.get("success"):
                                    new_balance = withdraw_data.get("new_balance", crt_savings)
                                    withdrawn_amount = crt_savings - new_balance
                                    print(f"✅ Successfully withdrew {withdrawn_amount:,.0f} CRT")
                                    print(f"📊 New CRT savings balance: {new_balance:,.0f}")
                                    
                                    if new_balance <= 0:
                                        print("🎉 CRT savings successfully reset to zero!")
                                        break
                                else:
                                    # Check if it's a liquidity limit
                                    message = withdraw_data.get("message", "")
                                    max_withdrawal = withdraw_data.get("max_withdrawal", 0)
                                    
                                    if "liquidity" in message.lower() and max_withdrawal > 0:
                                        print(f"⚠️ Liquidity limited. Max withdrawal: {max_withdrawal:,.0f} CRT")
                                        
                                        # Try to withdraw the maximum allowed
                                        max_withdraw_payload = {
                                            "wallet_address": target_user,
                                            "wallet_type": "savings",
                                            "currency": "CRT",
                                            "amount": max_withdrawal
                                        }
                                        
                                        async with session.post(f"{BACKEND_URL}/wallet/withdraw", json=max_withdraw_payload) as max_response:
                                            if max_response.status == 200:
                                                max_data = await max_response.json()
                                                if max_data.get("success"):
                                                    print(f"✅ Withdrew maximum allowed: {max_withdrawal:,.0f} CRT")
                                                else:
                                                    print(f"❌ Failed to withdraw max amount: {max_data.get('message')}")
                                                    break
                                            else:
                                                print(f"❌ Max withdrawal failed: HTTP {max_response.status}")
                                                break
                                    else:
                                        print(f"❌ Withdrawal failed: {message}")
                                        break
                            else:
                                print(f"❌ Withdrawal request failed: HTTP {withdraw_response.status}")
                                break
                    else:
                        print("❌ Failed to get wallet info")
                        break
                else:
                    print(f"❌ Failed to get wallet info: HTTP {response.status}")
                    break
            
            # Small delay between attempts
            await asyncio.sleep(1)
        
        # Final status check
        print(f"\n--- FINAL STATUS ---")
        async with session.get(f"{BACKEND_URL}/wallet/{target_user}") as response:
            if response.status == 200:
                data = await response.json()
                if data.get("success"):
                    wallet = data["wallet"]
                    savings_balance = wallet.get("savings_balance", {})
                    usdc_savings = savings_balance.get("USDC", 0)
                    crt_savings = savings_balance.get("CRT", 0)
                    
                    print(f"📊 Final savings status:")
                    print(f"   USDC: {usdc_savings:,.2f} {'✅ RESET' if usdc_savings == 0 else '❌ NOT RESET'}")
                    print(f"   CRT: {crt_savings:,.0f} {'✅ RESET' if crt_savings == 0 else '❌ NOT RESET'}")
                    
                    if usdc_savings == 0 and crt_savings == 0:
                        print("🎉 SUCCESS: Both USDC and CRT savings successfully reset to zero!")
                    elif usdc_savings == 0:
                        print("⚠️ PARTIAL SUCCESS: USDC reset, but CRT savings still remain")
                        print(f"💡 RECOMMENDATION: CRT savings reduced from ~21M to {crt_savings:,.0f}")
                    else:
                        print("❌ FAILED: Savings reset incomplete")

if __name__ == "__main__":
    asyncio.run(reduce_crt_savings())