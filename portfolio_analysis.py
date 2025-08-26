#!/usr/bin/env python3
"""
Portfolio Analysis for user - Check conversion history, remaining balances, and liquidity status
"""

import os
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.append(str(backend_dir))

# Load environment variables
load_dotenv(backend_dir / '.env')

async def main():
    """Analyze user's complete portfolio and conversion history"""
    
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # User's wallet address
    user_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    
    print(f"📊 PORTFOLIO ANALYSIS for wallet: {user_wallet}")
    print("=" * 80)
    
    try:
        # Find user in database
        user = await db.users.find_one({"wallet_address": user_wallet})
        if not user:
            print("❌ User not found!")
            return
        
        print(f"👤 User: {user.get('username', 'unknown')}")
        print()
        
        # 1. CURRENT PORTFOLIO STATE
        print("💼 CURRENT PORTFOLIO STATE:")
        print("-" * 40)
        
        deposit_balance = user.get("deposit_balance", {})
        winnings_balance = user.get("winnings_balance", {})
        savings_balance = user.get("savings_balance", {})
        liquidity_pool = user.get("liquidity_pool", {})
        
        currencies = ["CRT", "DOGE", "TRX", "USDC"]
        total_value = 0
        
        # Mock prices for calculation
        prices = {"CRT": 0.15, "DOGE": 0.236, "TRX": 0.363, "USDC": 1.0}
        
        print("Currency    | Deposit      | Winnings    | Savings     | Liquidity   | Total       | USD Value")
        print("-" * 100)
        
        for currency in currencies:
            deposit = deposit_balance.get(currency, 0)
            winnings = winnings_balance.get(currency, 0)
            savings = savings_balance.get(currency, 0)
            liquidity = liquidity_pool.get(currency, 0)
            total_currency = deposit + winnings + savings
            usd_value = total_currency * prices.get(currency, 0)
            total_value += usd_value
            
            print(f"{currency:<11} | {deposit:>12,.2f} | {winnings:>11,.2f} | {savings:>11,.2f} | {liquidity:>11,.2f} | {total_currency:>11,.2f} | ${usd_value:>9,.2f}")
        
        print("-" * 100)
        print(f"{'TOTAL USD VALUE':<76} | ${total_value:>11,.2f}")
        print()
        
        # 2. CONVERSION HISTORY
        print("🔄 CONVERSION HISTORY:")
        print("-" * 40)
        
        # Get all conversion transactions
        conversion_cursor = db.transactions.find({
            "wallet_address": user_wallet, 
            "type": {"$regex": "conversion"}
        }).sort("timestamp", -1).limit(20)
        
        conversions = await conversion_cursor.to_list(20)
        
        if conversions:
            print("Date/Time           | From      | To        | Amount     | Converted  | Rate      | Type")
            print("-" * 95)
            
            total_crt_converted = 0
            
            for conv in conversions:
                timestamp = conv.get("timestamp", "Unknown")
                if hasattr(timestamp, 'strftime'):
                    date_str = timestamp.strftime("%Y-%m-%d %H:%M")
                else:
                    date_str = str(timestamp)[:16]
                
                from_curr = conv.get("from_currency", "?")
                to_curr = conv.get("to_currency", "?")
                amount = conv.get("amount", 0)
                converted = conv.get("converted_amount", 0)
                rate = conv.get("rate", 0)
                conv_type = conv.get("conversion_type", conv.get("type", "unknown"))
                
                print(f"{date_str:<19} | {from_curr:<9} | {to_curr:<9} | {amount:>10,.2f} | {converted:>10,.2f} | {rate:>9.4f} | {conv_type}")
                
                # Track CRT conversions
                if from_curr == "CRT":
                    total_crt_converted += amount
            
            print("-" * 95)
            print(f"TOTAL CRT CONVERTED OUT: {total_crt_converted:,.2f} CRT")
            print()
        else:
            print("No conversion history found.")
            print()
        
        # 3. ORIGINAL CRT vs REMAINING
        print("🏦 CRT BALANCE ANALYSIS:")
        print("-" * 40)
        
        current_crt = deposit_balance.get("CRT", 0)
        
        # Try to estimate original CRT (from blockchain we know they had 21M)
        original_crt_estimate = 21000000  # 21 million from blockchain
        
        print(f"Original CRT (estimated):     {original_crt_estimate:>15,.2f}")
        print(f"Current CRT in portfolio:     {current_crt:>15,.2f}")
        print(f"CRT converted to other coins: {total_crt_converted:>15,.2f}")
        print(f"Remaining after conversions:  {current_crt:>15,.2f}")
        
        # Calculate what should be remaining
        expected_remaining = original_crt_estimate - total_crt_converted
        print(f"Expected remaining (calc):    {expected_remaining:>15,.2f}")
        
        if abs(current_crt - expected_remaining) < 100000:  # Within 100K tolerance
            print("✅ CRT balance matches conversion history")
        else:
            print("⚠️  CRT balance doesn't match conversion history - possible database sync issue")
        print()
        
        # 4. LIQUIDITY POOL STATUS
        print("🌊 LIQUIDITY POOL STATUS:")
        print("-" * 40)
        
        total_liquidity_usd = 0
        has_liquidity = False
        
        for currency in currencies:
            liquidity = liquidity_pool.get(currency, 0)
            usd_value = liquidity * prices.get(currency, 0)
            total_liquidity_usd += usd_value
            
            if liquidity > 0:
                has_liquidity = True
                print(f"{currency}: {liquidity:>12,.2f} (${usd_value:>8,.2f})")
        
        if has_liquidity:
            print(f"\nTotal Liquidity: ${total_liquidity_usd:,.2f}")
            print("✅ Liquidity pool has started! You can now withdraw up to your liquidity amounts.")
        else:
            print("❌ No liquidity pool funds yet. Convert currencies to build liquidity for withdrawals.")
        print()
        
        # 5. GAMING/SAVINGS ACTIVITY
        print("🎮 GAMING & SAVINGS ACTIVITY:")
        print("-" * 40)
        
        # Get recent game activity
        game_count = await db.game_bets.count_documents({"wallet_address": user_wallet})
        total_winnings = await db.game_bets.aggregate([
            {"$match": {"wallet_address": user_wallet, "result": "win"}},
            {"$group": {"_id": "$currency", "total": {"$sum": "$payout"}}}
        ]).to_list(10)
        
        total_losses = await db.game_bets.aggregate([
            {"$match": {"wallet_address": user_wallet, "result": "loss"}},
            {"$group": {"_id": "$currency", "total": {"$sum": "$bet_amount"}}}
        ]).to_list(10)
        
        print(f"Total games played: {game_count}")
        
        if total_winnings:
            print("Winnings by currency:")
            for win in total_winnings:
                currency = win["_id"]
                amount = win["total"]
                print(f"  {currency}: {amount:,.2f}")
        
        if total_losses:
            print("Losses (saved) by currency:")
            for loss in total_losses:
                currency = loss["_id"]
                amount = loss["total"]
                print(f"  {currency}: {amount:,.2f}")
        
        print()
        
        # 6. SUMMARY
        print("📋 SUMMARY:")
        print("-" * 40)
        print(f"💰 Total Portfolio Value: ${total_value:,.2f}")
        print(f"🏦 Liquidity Available: ${total_liquidity_usd:,.2f}")
        print(f"🎮 Games Played: {game_count}")
        print(f"🔄 Conversions Made: {len(conversions)}")
        
        if has_liquidity:
            print("✅ You can withdraw funds up to your liquidity amounts")
        else:
            print("ℹ️  Convert more currencies to build withdrawal liquidity")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())