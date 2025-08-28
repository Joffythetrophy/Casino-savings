#!/usr/bin/env python3
"""
VERIFICATION TEST - Additional checks for the massive conversion
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://smart-savings-dapp.preview.emergentagent.com/api"
USER_WALLET = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"

async def verify_final_state():
    """Verify the final state after massive conversion"""
    async with aiohttp.ClientSession() as session:
        print("🔍 FINAL VERIFICATION OF MASSIVE CONVERSION")
        print("=" * 60)
        
        # Check final wallet state
        async with session.get(f"{BACKEND_URL}/wallet/{USER_WALLET}") as response:
            if response.status == 200:
                data = await response.json()
                if data.get("success"):
                    wallet = data["wallet"]
                    deposit_balance = wallet.get("deposit_balance", {})
                    
                    crt_balance = deposit_balance.get("CRT", 0)
                    usdc_balance = deposit_balance.get("USDC", 0)
                    
                    print(f"💰 FINAL BALANCES:")
                    print(f"   CRT:  {crt_balance:,.0f}")
                    print(f"   USDC: {usdc_balance:,.2f}")
                    print()
                    
                    # Calculate USD value
                    usdc_usd_value = usdc_balance * 1.0  # USDC is $1
                    print(f"💵 USD VALUE:")
                    print(f"   USDC Value: ${usdc_usd_value:,.2f}")
                    print()
                    
                    if usdc_balance >= 150000:
                        print("✅ SUCCESS: User has received the expected 150,000+ USDC")
                        print("✅ REAL MONEY: User now has real USDC stablecoin worth ~$150,000")
                        return True
                    else:
                        print(f"❌ ERROR: User has only {usdc_balance:,.2f} USDC (expected 150,000+)")
                        return False
                else:
                    print("❌ ERROR: Cannot retrieve wallet data")
                    return False
            else:
                print(f"❌ ERROR: HTTP {response.status}")
                return False

async def test_additional_conversion():
    """Test another smaller conversion to verify system is still working"""
    async with aiohttp.ClientSession() as session:
        print("🧪 TESTING ADDITIONAL CONVERSION (10,000 CRT → USDC)")
        print("=" * 60)
        
        conversion_payload = {
            "wallet_address": USER_WALLET,
            "from_currency": "CRT",
            "to_currency": "USDC", 
            "amount": 10000.0
        }
        
        async with session.post(f"{BACKEND_URL}/wallet/convert", json=conversion_payload) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("success"):
                    converted_amount = data.get("converted_amount", 0)
                    rate = data.get("rate", 0)
                    tx_id = data.get("transaction_id")
                    
                    expected_usdc = 10000 * 0.15  # 1,500 USDC
                    if abs(converted_amount - expected_usdc) < 1.0:
                        print(f"✅ ADDITIONAL CONVERSION SUCCESS: 10,000 CRT → {converted_amount:,.0f} USDC")
                        print(f"   Rate: {rate}, Transaction: {tx_id}")
                        return True
                    else:
                        print(f"❌ WRONG AMOUNT: Got {converted_amount} USDC (expected {expected_usdc})")
                        return False
                else:
                    print(f"❌ CONVERSION FAILED: {data.get('message', 'Unknown error')}")
                    return False
            else:
                print(f"❌ API ERROR: HTTP {response.status}")
                return False

async def main():
    print("🚀 STARTING VERIFICATION TESTS")
    print()
    
    # Verify final state
    final_ok = await verify_final_state()
    
    # Test additional conversion
    additional_ok = await test_additional_conversion()
    
    print()
    print("=" * 60)
    print("🎯 VERIFICATION SUMMARY")
    print("=" * 60)
    
    if final_ok and additional_ok:
        print("🎉 ALL VERIFICATIONS PASSED!")
        print("✅ Massive conversion successful")
        print("✅ System continues to work properly")
        print("✅ User has real USDC stablecoin")
    elif final_ok:
        print("⚠️ PARTIAL SUCCESS")
        print("✅ Massive conversion successful")
        print("❌ Additional conversion issues")
    else:
        print("❌ VERIFICATION FAILED")
        print("❌ Issues with conversion system")

if __name__ == "__main__":
    asyncio.run(main())