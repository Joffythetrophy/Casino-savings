#!/usr/bin/env python3
"""
Fix CRT Balance Sync - Import blockchain CRT balance into database
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Import blockchain managers
from blockchain.solana_manager import SolanaManager, CRTTokenManager

# Initialize clients
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# User details
USER_WALLET = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
USERNAME = "cryptoking"

async def fix_crt_balance_sync():
    """
    Fix CRT balance synchronization between blockchain and database
    User has 21M CRT on blockchain but only 2.1K in database
    """
    
    print("🔄 FIXING CRT BALANCE SYNCHRONIZATION...")
    print(f"👤 User: {USERNAME} ({USER_WALLET})")
    
    try:
        # Initialize blockchain managers
        crt_manager = CRTTokenManager()
        
        # Get real CRT balance from blockchain
        print("\n📡 Checking blockchain CRT balance...")
        real_crt_balance = await crt_manager.get_balance(USER_WALLET)
        print(f"   Blockchain CRT: {real_crt_balance:,.2f} CRT")
        
        # Get current database balance
        user = await db.users.find_one({"wallet_address": USER_WALLET})
        if not user:
            print(f"❌ User not found: {USER_WALLET}")
            return False
        
        current_db_crt = 0
        for balance_type in ['deposit_balance', 'winnings_balance', 'savings_balance']:
            if balance_type in user.get('balance', {}):
                current_db_crt += user['balance'][balance_type].get('CRT', 0)
        
        print(f"   Database CRT: {current_db_crt:,.2f} CRT")
        print(f"   Missing CRT: {real_crt_balance - current_db_crt:,.2f} CRT")
        
        if real_crt_balance <= current_db_crt:
            print("✅ CRT balance already synchronized!")
            return True
        
        # Calculate how much CRT to add to deposit balance
        missing_crt = real_crt_balance - current_db_crt
        
        print(f"\n💰 Adding {missing_crt:,.2f} CRT to deposit balance...")
        
        # Get current balance structure
        current_balance = user.get('balance', {
            'deposit_balance': {'CRT': 0, 'DOGE': 0, 'TRX': 0, 'USDC': 0, 'SOL': 0},
            'winnings_balance': {'CRT': 0, 'DOGE': 0, 'TRX': 0, 'USDC': 0, 'SOL': 0},
            'savings_balance': {'CRT': 0, 'DOGE': 0, 'TRX': 0, 'USDC': 0, 'SOL': 0}
        })
        
        # Add missing CRT to deposit balance (main gaming wallet)
        current_deposit_crt = current_balance.get('deposit_balance', {}).get('CRT', 0)
        new_deposit_crt = current_deposit_crt + missing_crt
        
        # Update the balance structure
        if 'deposit_balance' not in current_balance:
            current_balance['deposit_balance'] = {}
        
        current_balance['deposit_balance']['CRT'] = new_deposit_crt
        
        # Update database
        result = await db.users.update_one(
            {"wallet_address": USER_WALLET},
            {
                "$set": {
                    "balance": current_balance,
                    "last_balance_sync": datetime.now(timezone.utc),
                    "crt_balance_sync_timestamp": datetime.now(timezone.utc).isoformat(),
                    "crt_balance_sync_note": f"Synchronized {missing_crt:,.2f} CRT from blockchain"
                }
            }
        )
        
        if result.modified_count > 0:
            print("✅ Database updated successfully!")
            
            # Log the sync transaction
            sync_record = {
                "transaction_id": f"crt_sync_{int(datetime.now().timestamp())}",
                "user_id": user.get('user_id', user['_id']),
                "wallet_address": USER_WALLET,
                "username": user.get('username', 'Unknown'),
                "transaction_type": "crt_balance_sync",
                "source": "solana_blockchain",
                "currency": "CRT",
                "amount_added": missing_crt,
                "blockchain_balance": real_crt_balance,
                "previous_db_balance": current_db_crt,
                "new_db_balance": real_crt_balance,
                "created_at": datetime.now(timezone.utc),
                "status": "completed"
            }
            
            await db.transactions.insert_one(sync_record)
            print("📋 Sync transaction recorded")
            
            print("\n🎉 CRT BALANCE SYNC COMPLETED!")
            print("=" * 50)
            print("📊 FINAL BALANCE STATUS:")
            print(f"   Blockchain CRT: {real_crt_balance:,.2f}")
            print(f"   Database CRT: {real_crt_balance:,.2f}")
            print(f"   Available for gaming: {new_deposit_crt:,.2f}")
            print(f"   Available for conversion: {new_deposit_crt:,.2f}")
            print("✅ User can now access full CRT balance!")
            
            return True
        else:
            print("❌ Failed to update database")
            return False
            
    except Exception as e:
        print(f"❌ Error during CRT balance sync: {e}")
        return False

async def main():
    """Main execution function"""
    success = await fix_crt_balance_sync()
    if success:
        print("\n🎯 Next Steps:")
        print("1. Test CRT conversion with full balance")
        print("2. Test multi-currency gaming")
        print("3. Verify real-time balance updates")
    else:
        print("\n❌ CRT sync failed - please check the logs")

if __name__ == "__main__":
    asyncio.run(main())