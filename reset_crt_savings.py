#!/usr/bin/env python3
"""
Direct database update to reset CRT savings balance to 0 for user DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq
This is a critical correction as requested by the user.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

async def reset_crt_savings():
    """Reset CRT savings balance to 0 for the specific user"""
    
    # Connect to MongoDB
    mongo_url = "mongodb://localhost:27017"
    client = AsyncIOMotorClient(mongo_url)
    db = client["test_database"]
    
    target_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    
    try:
        # Find the user
        user = await db.users.find_one({"wallet_address": target_wallet})
        if not user:
            print(f"❌ User not found: {target_wallet}")
            return False
        
        print(f"✅ User found: {user.get('username', 'unknown')} ({target_wallet})")
        
        # Get current savings balance
        current_savings = user.get("savings_balance", {})
        current_crt_savings = current_savings.get("CRT", 0)
        
        print(f"📊 Current CRT savings: {current_crt_savings}")
        
        if current_crt_savings == 0:
            print(f"✅ CRT savings already reset to 0")
            return True
        
        # Reset CRT savings to 0
        result = await db.users.update_one(
            {"wallet_address": target_wallet},
            {"$set": {"savings_balance.CRT": 0.0}}
        )
        
        if result.modified_count > 0:
            print(f"✅ CRT savings reset successfully: {current_crt_savings} → 0.0")
            
            # Verify the update
            updated_user = await db.users.find_one({"wallet_address": target_wallet})
            updated_crt_savings = updated_user.get("savings_balance", {}).get("CRT", 0)
            
            if updated_crt_savings == 0:
                print(f"✅ Verification successful: CRT savings = {updated_crt_savings}")
                
                # Record the correction in a log
                correction_record = {
                    "wallet_address": target_wallet,
                    "correction_type": "reset_crt_savings",
                    "old_value": current_crt_savings,
                    "new_value": 0.0,
                    "reason": "User requested reset of saved amounts",
                    "timestamp": datetime.utcnow(),
                    "status": "completed"
                }
                
                await db.user_corrections.insert_one(correction_record)
                print(f"✅ Correction logged in database")
                
                return True
            else:
                print(f"❌ Verification failed: CRT savings = {updated_crt_savings}")
                return False
        else:
            print(f"❌ Database update failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        client.close()

async def main():
    """Main execution"""
    print("🚨 URGENT: Resetting CRT savings balance to 0")
    print("=" * 60)
    
    success = await reset_crt_savings()
    
    if success:
        print("\n✅ CRT SAVINGS RESET COMPLETED SUCCESSFULLY!")
        print("User's CRT saved amounts have been reset to 0 as requested.")
    else:
        print("\n❌ CRT SAVINGS RESET FAILED!")
        print("Manual intervention may be required.")

if __name__ == "__main__":
    asyncio.run(main())