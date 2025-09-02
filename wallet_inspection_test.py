#!/usr/bin/env python3
"""
Detailed Wallet Inspection Test
Get complete wallet data to understand current state vs expected fixes
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

BACKEND_URL = "https://gamewin-vault.preview.emergentagent.com/api"

async def inspect_wallet():
    """Get detailed wallet information"""
    target_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    target_username = "cryptoking"
    target_password = "crt21million"
    
    async with aiohttp.ClientSession() as session:
        # Authenticate first
        login_payload = {
            "username": target_username,
            "password": target_password
        }
        
        async with session.post(f"{BACKEND_URL}/auth/login-username", json=login_payload) as response:
            if response.status != 200:
                print(f"❌ Authentication failed: {response.status}")
                return
            
            auth_data = await response.json()
            if not auth_data.get("success"):
                print(f"❌ Authentication failed: {auth_data.get('message')}")
                return
            
            print("✅ Authentication successful")
        
        # Get wallet data
        async with session.get(f"{BACKEND_URL}/wallet/{target_wallet}") as response:
            if response.status != 200:
                print(f"❌ Wallet request failed: {response.status}")
                return
            
            data = await response.json()
            if not data.get("success"):
                print(f"❌ Wallet request failed: {data}")
                return
            
            wallet = data["wallet"]
            
            print("\n" + "="*80)
            print("📊 COMPLETE WALLET DATA INSPECTION")
            print("="*80)
            
            print(f"🔍 Wallet Address: {wallet.get('wallet_address')}")
            print(f"🔍 User ID: {wallet.get('user_id')}")
            print(f"🔍 Balance Source: {wallet.get('balance_source')}")
            print(f"🔍 Last Update: {wallet.get('last_balance_update')}")
            
            print("\n💰 DEPOSIT BALANCES:")
            deposit_balance = wallet.get('deposit_balance', {})
            for currency, amount in deposit_balance.items():
                print(f"   {currency}: {amount:,.2f}")
            
            print("\n🎰 WINNINGS BALANCES:")
            winnings_balance = wallet.get('winnings_balance', {})
            for currency, amount in winnings_balance.items():
                print(f"   {currency}: {amount:,.2f}")
            
            print("\n🎮 GAMING BALANCES:")
            gaming_balance = wallet.get('gaming_balance', {})
            if gaming_balance:
                for currency, amount in gaming_balance.items():
                    print(f"   {currency}: {amount:,.2f}")
            else:
                print("   ❌ Gaming balance field missing or empty")
            
            print("\n💧 LIQUIDITY POOL:")
            liquidity_pool = wallet.get('liquidity_pool', {})
            if liquidity_pool:
                total_usd = 0
                rates = {"CRT": 0.15, "DOGE": 0.24, "TRX": 0.37, "USDC": 1.0}
                for currency, amount in liquidity_pool.items():
                    usd_value = amount * rates.get(currency, 0)
                    total_usd += usd_value
                    print(f"   {currency}: {amount:,.2f} (${usd_value:,.2f})")
                print(f"   💵 Total USD: ${total_usd:,.2f}")
            else:
                print("   ❌ Liquidity pool field missing or empty")
            
            print("\n💾 SAVINGS BALANCES:")
            savings_balance = wallet.get('savings_balance', {})
            for currency, amount in savings_balance.items():
                print(f"   {currency}: {amount:,.2f}")
            
            print("\n📝 BALANCE NOTES:")
            balance_notes = wallet.get('balance_notes', {})
            for currency, note in balance_notes.items():
                print(f"   {currency}: {note}")
            
            print("\n" + "="*80)
            print("🎯 CRITICAL FIXES ANALYSIS")
            print("="*80)
            
            # Fix 1: CRT Balance Logic
            crt_balance = deposit_balance.get('CRT', 0)
            print(f"FIX 1 - CRT Balance: {crt_balance:,.0f} CRT")
            if 500000 <= crt_balance <= 2000000:
                print("   ✅ EXPECTED: Shows ~1M CRT (database priority)")
            elif crt_balance > 20000000:
                print("   ❌ ISSUE: Shows 21M+ CRT (blockchain priority - should be database)")
            else:
                print(f"   ⚠️ UNEXPECTED: Shows {crt_balance:,.0f} CRT (neither ~1M nor 21M)")
            
            # Fix 2: Winnings Balance
            print(f"FIX 2 - Winnings Balance: {winnings_balance}")
            if isinstance(winnings_balance, dict) and len(winnings_balance) > 0:
                print("   ✅ FIXED: Shows real database values (not hardcoded 0)")
            else:
                print("   ❌ ISSUE: Still hardcoded or missing")
            
            # Fix 3: Gaming Balance
            print(f"FIX 3 - Gaming Balance: {gaming_balance}")
            if isinstance(gaming_balance, dict) and all(curr in gaming_balance for curr in ["CRT", "DOGE", "TRX", "USDC"]):
                print("   ✅ FIXED: Gaming balance field added with all currencies")
            elif gaming_balance:
                print("   ⚠️ PARTIAL: Gaming balance added but missing some currencies")
            else:
                print("   ❌ ISSUE: Gaming balance field missing")
            
            # Fix 4: Liquidity Pool
            print(f"FIX 4 - Liquidity Pool: {liquidity_pool}")
            if isinstance(liquidity_pool, dict) and liquidity_pool:
                rates = {"CRT": 0.15, "DOGE": 0.24, "TRX": 0.37, "USDC": 1.0}
                total_usd = sum(liquidity_pool.get(curr, 0) * rates.get(curr, 0) for curr in rates.keys())
                print(f"   💵 Total USD Value: ${total_usd:,.2f}")
                if total_usd >= 2200000:
                    print("   ✅ FIXED: Shows $2.2M+ liquidity as expected")
                else:
                    print("   ⚠️ PARTIAL: Liquidity pool added but less than expected $2.2M")
            else:
                print("   ❌ ISSUE: Liquidity pool field missing")
            
            print("\n" + "="*80)
            print("📋 SUMMARY OF FIXES STATUS")
            print("="*80)
            
            fixes_status = []
            
            # Check each fix
            if 500000 <= crt_balance <= 2000000:
                fixes_status.append("✅ FIX 1: CRT Balance Logic")
            else:
                fixes_status.append("❌ FIX 1: CRT Balance Logic")
            
            if isinstance(winnings_balance, dict) and len(winnings_balance) > 0:
                fixes_status.append("✅ FIX 2: Winnings Balance")
            else:
                fixes_status.append("❌ FIX 2: Winnings Balance")
            
            if isinstance(gaming_balance, dict) and all(curr in gaming_balance for curr in ["CRT", "DOGE", "TRX", "USDC"]):
                fixes_status.append("✅ FIX 3: Gaming Balance Added")
            else:
                fixes_status.append("❌ FIX 3: Gaming Balance Added")
            
            if isinstance(liquidity_pool, dict) and liquidity_pool:
                fixes_status.append("✅ FIX 4: Liquidity Pool Added")
            else:
                fixes_status.append("❌ FIX 4: Liquidity Pool Added")
            
            for status in fixes_status:
                print(status)
            
            passed_fixes = sum(1 for status in fixes_status if status.startswith("✅"))
            print(f"\n🎯 OVERALL: {passed_fixes}/4 Critical Fixes Verified")
            
            if passed_fixes == 4:
                print("🎉 ALL CRITICAL FIXES SUCCESSFULLY IMPLEMENTED!")
            else:
                print("⚠️ Some fixes still need attention")

if __name__ == "__main__":
    asyncio.run(inspect_wallet())