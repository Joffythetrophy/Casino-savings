#!/usr/bin/env python3
"""
CRT Balance Investigation - Deep dive into CRT balance discrepancy
Blockchain shows 21M CRT but wallet shows only 2,100 CRT
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://cryptoplay-8.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

async def investigate_crt_balance():
    """Investigate CRT balance discrepancy"""
    async with aiohttp.ClientSession() as session:
        wallet_address = TEST_CREDENTIALS["wallet_address"]
        
        print("🔍 CRT BALANCE INVESTIGATION")
        print("=" * 50)
        
        # 1. Check blockchain CRT balance
        print("\n1. BLOCKCHAIN CRT BALANCE:")
        async with session.get(f"{BACKEND_URL}/wallet/balance/CRT?wallet_address={wallet_address}") as response:
            if response.status == 200:
                data = await response.json()
                if data.get("success"):
                    blockchain_crt = data.get("balance", 0)
                    print(f"   ✅ Blockchain CRT: {blockchain_crt:,.0f} CRT")
                    print(f"   📍 Source: {data.get('source')}")
                    print(f"   🏦 Mint Address: {data.get('mint_address')}")
                else:
                    print(f"   ❌ Error: {data.get('error')}")
            else:
                print(f"   ❌ HTTP {response.status}")
        
        # 2. Check wallet database balance
        print("\n2. WALLET DATABASE BALANCE:")
        async with session.get(f"{BACKEND_URL}/wallet/{wallet_address}") as response:
            if response.status == 200:
                data = await response.json()
                if data.get("success"):
                    wallet = data["wallet"]
                    deposit_crt = wallet.get("deposit_balance", {}).get("CRT", 0)
                    savings_crt = wallet.get("savings_balance", {}).get("CRT", 0)
                    winnings_crt = wallet.get("winnings_balance", {}).get("CRT", 0)
                    gaming_crt = wallet.get("gaming_balance", {}).get("CRT", 0)
                    liquidity_crt = wallet.get("liquidity_pool", {}).get("CRT", 0)
                    
                    total_db_crt = deposit_crt + savings_crt + winnings_crt + gaming_crt
                    
                    print(f"   💰 Deposit Balance: {deposit_crt:,.2f} CRT")
                    print(f"   💎 Savings Balance: {savings_crt:,.2f} CRT")
                    print(f"   🎰 Winnings Balance: {winnings_crt:,.2f} CRT")
                    print(f"   🎮 Gaming Balance: {gaming_crt:,.2f} CRT")
                    print(f"   🌊 Liquidity Pool: {liquidity_crt:,.2f} CRT")
                    print(f"   📊 TOTAL DATABASE: {total_db_crt:,.2f} CRT")
                    print(f"   📝 Balance Source: {wallet.get('balance_source')}")
                    print(f"   📅 Last Update: {wallet.get('last_balance_update')}")
                else:
                    print(f"   ❌ Error: {data}")
            else:
                print(f"   ❌ HTTP {response.status}")
        
        # 3. Check all blockchain balances
        print("\n3. ALL BLOCKCHAIN BALANCES:")
        async with session.get(f"{BACKEND_URL}/blockchain/balances?wallet_address={wallet_address}") as response:
            if response.status == 200:
                data = await response.json()
                if data.get("success"):
                    balances = data.get("balances", {})
                    errors = data.get("errors", {})
                    
                    for currency, balance_info in balances.items():
                        balance = balance_info.get("balance", 0)
                        source = balance_info.get("source", "unknown")
                        print(f"   {currency}: {balance:,.2f} (source: {source})")
                    
                    if errors:
                        print(f"   ❌ Errors: {errors}")
                else:
                    print(f"   ❌ Error: {data}")
            else:
                print(f"   ❌ HTTP {response.status}")
        
        # 4. Check CRT token info
        print("\n4. CRT TOKEN INFO:")
        async with session.get(f"{BACKEND_URL}/crt/info") as response:
            if response.status == 200:
                data = await response.json()
                if data.get("success"):
                    token_info = data.get("token_info", {})
                    mint_address = data.get("mint_address")
                    current_price = data.get("current_price")
                    decimals = data.get("decimals")
                    
                    print(f"   🪙 Mint Address: {mint_address}")
                    print(f"   💲 Current Price: ${current_price}")
                    print(f"   🔢 Decimals: {decimals}")
                    print(f"   📈 Token Info: {token_info}")
                else:
                    print(f"   ❌ Error: {data}")
            else:
                print(f"   ❌ HTTP {response.status}")
        
        # 5. Test CRT conversion to see available amount
        print("\n5. CRT CONVERSION TEST:")
        try:
            # Try to convert 1000 CRT to DOGE to see if it works
            convert_payload = {
                "wallet_address": wallet_address,
                "from_currency": "CRT",
                "to_currency": "DOGE",
                "amount": 1000.0
            }
            
            async with session.post(f"{BACKEND_URL}/wallet/convert", json=convert_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        converted_amount = data.get("converted_amount", 0)
                        rate = data.get("rate", 0)
                        print(f"   ✅ Conversion Test: 1000 CRT → {converted_amount:,.2f} DOGE (rate: {rate})")
                        print(f"   💡 This suggests CRT is available for conversion")
                    else:
                        print(f"   ❌ Conversion Failed: {data.get('message')}")
                        if "insufficient balance" in data.get("message", "").lower():
                            print(f"   🚨 CRITICAL: User cannot convert CRT - insufficient balance!")
                else:
                    print(f"   ❌ HTTP {response.status}")
        except Exception as e:
            print(f"   ❌ Conversion test error: {e}")
        
        # 6. Check conversion rates
        print("\n6. CONVERSION RATES:")
        async with session.get(f"{BACKEND_URL}/conversion/rates") as response:
            if response.status == 200:
                data = await response.json()
                if data.get("success"):
                    rates = data.get("rates", {})
                    crt_rates = {k: v for k, v in rates.items() if "CRT" in k}
                    print(f"   📊 CRT Conversion Rates: {crt_rates}")
                else:
                    print(f"   ❌ Error: {data}")
            else:
                print(f"   ❌ HTTP {response.status}")
        
        print("\n" + "=" * 50)
        print("🎯 INVESTIGATION SUMMARY:")
        print("🔍 The user has 21M CRT on blockchain but only 2,100 CRT in wallet database")
        print("💡 This suggests the wallet balance is not synced with blockchain balance")
        print("🚨 USER CANNOT ACCESS THEIR FULL CRT HOLDINGS!")

if __name__ == "__main__":
    asyncio.run(investigate_crt_balance())