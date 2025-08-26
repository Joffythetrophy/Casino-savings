#!/usr/bin/env python3
"""
Recalculate CRT balance based on actual conversion history
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
    """Recalculate user's CRT balance based on conversion history"""
    
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    user_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    
    print("🔢 RECALCULATING CRT BALANCE FROM CONVERSION HISTORY")
    print("=" * 70)
    
    try:
        # Get user
        user = await db.users.find_one({"wallet_address": user_wallet})
        if not user:
            print("❌ User not found!")
            return
        
        # Original CRT balance (from blockchain)
        original_crt = 21000000  # 21 million
        print(f"📊 Starting CRT Balance: {original_crt:,.2f}")
        
        # Get all conversion transactions
        conversions = await db.transactions.find({
            "wallet_address": user_wallet,
            "type": {"$regex": "conversion"},
            "from_currency": "CRT"
        }).sort("timestamp", 1).to_list(100)
        
        print(f"\n🔄 Found {len(conversions)} CRT conversion transactions:")
        print("-" * 70)
        
        total_crt_converted = 0
        
        for i, conv in enumerate(conversions, 1):
            amount = conv.get("amount", 0)
            to_currency = conv.get("to_currency", "?")
            converted_amount = conv.get("converted_amount", 0)
            timestamp = conv.get("timestamp", "Unknown")
            
            if hasattr(timestamp, 'strftime'):
                date_str = timestamp.strftime("%Y-%m-%d %H:%M")
            else:
                date_str = str(timestamp)[:16]
            
            total_crt_converted += amount
            
            print(f"{i:2d}. {date_str} | {amount:>12,.2f} CRT → {converted_amount:>12,.2f} {to_currency}")
        
        print("-" * 70)
        print(f"💸 Total CRT Converted: {total_crt_converted:,.2f}")
        
        # Calculate remaining CRT
        remaining_crt = original_crt - total_crt_converted
        print(f"🏦 Remaining CRT Should Be: {remaining_crt:,.2f}")
        
        # Check current database balance
        current_crt = user.get("deposit_balance", {}).get("CRT", 0)
        print(f"💾 Current Database Shows: {current_crt:,.2f}")
        
        # Check difference
        difference = current_crt - remaining_crt
        print(f"📈 Difference: {difference:,.2f} CRT")
        
        if abs(difference) > 100000:  # More than 100K difference
            print(f"\n⚠️  SIGNIFICANT DISCREPANCY DETECTED!")
            print(f"   Database should show: {remaining_crt:,.2f} CRT")
            print(f"   Database actually shows: {current_crt:,.2f} CRT")
            
            # Fix the balance
            print(f"\n🔧 FIXING CRT BALANCE...")
            await db.users.update_one(
                {"wallet_address": user_wallet},
                {"$set": {"deposit_balance.CRT": remaining_crt}}
            )
            
            print(f"✅ CRT balance updated to: {remaining_crt:,.2f}")
            
            # Verify the fix
            updated_user = await db.users.find_one({"wallet_address": user_wallet})
            new_crt = updated_user.get("deposit_balance", {}).get("CRT", 0)
            
            if abs(new_crt - remaining_crt) < 100:
                print(f"✅ VERIFICATION PASSED: Balance now shows {new_crt:,.2f} CRT")
            else:
                print(f"❌ VERIFICATION FAILED: Balance shows {new_crt:,.2f} CRT")
        else:
            print(f"✅ CRT balance is approximately correct (within 100K tolerance)")
        
        # Show final portfolio impact
        print(f"\n💰 PORTFOLIO IMPACT:")
        crt_usd_value = remaining_crt * 0.15  # CRT price
        print(f"   Corrected CRT Value: ${crt_usd_value:,.2f}")
        print(f"   This should be the CRT amount shown in frontend")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())