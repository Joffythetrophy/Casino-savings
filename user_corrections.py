#!/usr/bin/env python3
"""
Script to fix user's immediate concerns:
1. Refund 500 USDC balance
2. Reset USDC and CRT saved amounts
3. Check CRT balance display issue
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

# Import blockchain managers
from blockchain.solana_manager import SolanaManager, SPLTokenManager, CRTTokenManager

async def main():
    """Fix user's immediate concerns"""
    
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    # User's wallet address (from test results)
    user_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    
    print(f"🔧 FIXING USER CONCERNS for wallet: {user_wallet}")
    
    try:
        # Find user in database
        user = await db.users.find_one({"wallet_address": user_wallet})
        if not user:
            print("❌ User not found!")
            return
        
        print(f"✅ Found user: {user.get('username', 'unknown')}")
        
        # 1. REFUND 500 USDC - Add to deposit balance
        current_usdc = user.get("deposit_balance", {}).get("USDC", 0)
        new_usdc = current_usdc + 500
        
        print(f"💰 USDC REFUND: {current_usdc} → {new_usdc} (+500 USDC)")
        
        # 2. RESET SAVED AMOUNTS - Set CRT and USDC savings to 0
        current_crt_savings = user.get("savings_balance", {}).get("CRT", 0)
        current_usdc_savings = user.get("savings_balance", {}).get("USDC", 0)
        
        print(f"🔄 RESET CRT SAVINGS: {current_crt_savings} → 0")
        print(f"🔄 RESET USDC SAVINGS: {current_usdc_savings} → 0")
        
        # Apply database updates
        await db.users.update_one(
            {"wallet_address": user_wallet},
            {"$set": {
                "deposit_balance.USDC": new_usdc,
                "savings_balance.CRT": 0,
                "savings_balance.USDC": 0
            }}
        )
        
        print("✅ Database updates applied!")
        
        # 3. INVESTIGATE CRT BALANCE DISPLAY ISSUE
        print("\n🔍 INVESTIGATING CRT BALANCE DISPLAY ISSUE...")
        
        # Initialize blockchain managers
        solana_manager = SolanaManager()
        spl_manager = SPLTokenManager(solana_manager)
        crt_manager = CRTTokenManager(solana_manager, spl_manager)
        
        # Check real CRT balance from blockchain
        print(f"📡 Checking real CRT balance for {user_wallet}...")
        crt_balance_result = await crt_manager.get_crt_balance(user_wallet)
        
        if crt_balance_result.get("success"):
            real_crt_balance = crt_balance_result.get("crt_balance", 0)
            raw_balance = crt_balance_result.get("raw_balance", 0)
            decimals = crt_balance_result.get("decimals", 6)
            
            print(f"🟨 REAL CRT BALANCE: {real_crt_balance:,.2f} CRT")
            print(f"🔢 RAW BALANCE: {raw_balance}")
            print(f"📏 DECIMALS: {decimals}")
            print(f"💲 USD VALUE: ${crt_balance_result.get('usd_value', 0):,.2f}")
            print(f"🏦 MINT ADDRESS: {crt_balance_result.get('mint_address')}")
            
            # Check if this matches expected 18 million
            if real_crt_balance < 1000000:  # Less than 1M, might be decimal issue
                print(f"⚠️  POTENTIAL ISSUE: Balance shows {real_crt_balance:,.2f} but user expects 18,000,000")
                print(f"🔍 Raw balance calculation: {raw_balance} / 10^{decimals} = {raw_balance / (10**decimals):,.2f}")
        else:
            print(f"❌ Failed to get CRT balance: {crt_balance_result.get('error')}")
        
        # Get database balance for comparison
        db_crt_balance = user.get("deposit_balance", {}).get("CRT", 0)
        print(f"💾 DATABASE CRT BALANCE: {db_crt_balance:,.2f} CRT")
        
        # Final verification - check updated user data
        print("\n✅ FINAL VERIFICATION:")
        updated_user = await db.users.find_one({"wallet_address": user_wallet})
        final_usdc = updated_user.get("deposit_balance", {}).get("USDC", 0)
        final_crt_savings = updated_user.get("savings_balance", {}).get("CRT", 0)
        final_usdc_savings = updated_user.get("savings_balance", {}).get("USDC", 0)
        
        print(f"💰 USDC Balance: {final_usdc} (should be original + 500)")
        print(f"💾 CRT Savings: {final_crt_savings} (should be 0)")
        print(f"💾 USDC Savings: {final_usdc_savings} (should be 0)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())