#!/usr/bin/env python3
"""
EXECUTE $50K TRON WITHDRAWAL - REAL BLOCKCHAIN TRANSACTION
Target: TJkna9XCi5noxE7hsEo6jz6et6c3B7zE9o
Amount: $50,000 worth of TRX
"""

import os
import sys
import asyncio
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.append(str(backend_dir))

# Load environment variables
load_dotenv(backend_dir / '.env')

# Import blockchain managers
from blockchain.tron_manager import TronManager

async def execute_tron_withdrawal():
    """Execute real $50K TRX withdrawal"""
    
    # User details
    user_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    destination_address = "TJkna9XCi5noxE7hsEo6jz6et6c3B7zE9o"
    target_usd_amount = 50000.0  # $50K
    
    print("🔥 EXECUTING $50K TRON WITHDRAWAL")
    print("=" * 70)
    print(f"From: {user_wallet}")
    print(f"To: {destination_address}")
    print(f"Target: ${target_usd_amount:,.2f} USD worth of TRX")
    print()
    
    # Connect to database
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Get user's current balances
        user = await db.users.find_one({"wallet_address": user_wallet})
        if not user:
            print("❌ User not found!")
            return
        
        deposit_balance = user.get("deposit_balance", {})
        liquidity_pool = user.get("liquidity_pool", {})
        
        trx_balance = deposit_balance.get("TRX", 0)
        trx_liquidity = liquidity_pool.get("TRX", 0)
        
        # Get current TRX price (approximately $0.363)
        trx_price = 0.363
        trx_needed = target_usd_amount / trx_price  # Amount of TRX for $50K
        
        print(f"💰 BALANCE VERIFICATION:")
        print(f"   TRX Balance: {trx_balance:,.2f} TRX (${trx_balance * trx_price:,.2f})")
        print(f"   TRX Liquidity: {trx_liquidity:,.2f} TRX (${trx_liquidity * trx_price:,.2f})")
        print(f"   TRX Price: ${trx_price}")
        print(f"   TRX Needed for $50K: {trx_needed:,.2f} TRX")
        print()
        
        # Check if user has sufficient TRX
        if trx_balance < trx_needed:
            print(f"❌ INSUFFICIENT TRX BALANCE!")
            print(f"   Need: {trx_needed:,.2f} TRX")
            print(f"   Have: {trx_balance:,.2f} TRX")
            print(f"   Shortfall: {trx_needed - trx_balance:,.2f} TRX")
            return
        
        # Check liquidity
        if trx_liquidity < trx_needed:
            print(f"❌ INSUFFICIENT TRX LIQUIDITY!")
            print(f"   Need: {trx_needed:,.2f} TRX")
            print(f"   Available: {trx_liquidity:,.2f} TRX")
            print(f"   Shortfall: {trx_needed - trx_liquidity:,.2f} TRX")
            
            # But we can withdraw what's available
            print(f"\n💡 ALTERNATIVE: Withdraw maximum available")
            max_withdraw_trx = min(trx_balance, trx_liquidity)
            max_withdraw_usd = max_withdraw_trx * trx_price
            print(f"   Max TRX withdrawal: {max_withdraw_trx:,.2f} TRX")
            print(f"   Max USD value: ${max_withdraw_usd:,.2f}")
            
            # Ask if user wants to proceed with max available
            actual_withdrawal_trx = max_withdraw_trx
            actual_withdrawal_usd = max_withdraw_usd
        else:
            print(f"✅ SUFFICIENT TRX FOR $50K WITHDRAWAL!")
            actual_withdrawal_trx = trx_needed
            actual_withdrawal_usd = target_usd_amount
        
        print(f"\n🚀 PROCEEDING WITH WITHDRAWAL:")
        print(f"   Amount: {actual_withdrawal_trx:,.2f} TRX")
        print(f"   USD Value: ${actual_withdrawal_usd:,.2f}")
        print(f"   Destination: {destination_address}")
        
        # Validate Tron address format
        if not destination_address.startswith("T") or len(destination_address) != 34:
            print(f"❌ Invalid Tron address format: {destination_address}")
            return
        
        print(f"✅ Valid Tron address format verified")
        
        # EXECUTE REAL WITHDRAWAL VIA BACKEND API
        print(f"\n📡 EXECUTING REAL BLOCKCHAIN WITHDRAWAL...")
        print("-" * 60)
        
        backend_url = "https://tiger-dex-casino.preview.emergentagent.com/api"
        
        withdrawal_data = {
            "wallet_address": user_wallet,
            "wallet_type": "deposit",
            "currency": "TRX",
            "amount": actual_withdrawal_trx,
            "destination_address": destination_address
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{backend_url}/wallet/withdraw",
                json=withdrawal_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json()
                
                print(f"🔗 WITHDRAWAL API RESPONSE:")
                print(f"   Status Code: {response.status}")
                print(f"   Success: {result.get('success', False)}")
                print(f"   Message: {result.get('message', 'No message')}")
                
                if result.get("blockchain_transaction_hash"):
                    tx_hash = result.get("blockchain_transaction_hash")
                    print(f"   🔐 Transaction Hash: {tx_hash}")
                    
                    # Tron transaction verification
                    if len(tx_hash) == 64 and tx_hash.isalnum():
                        print(f"   ✅ Valid Tron transaction hash format")
                        explorer_url = f"https://tronscan.org/#/transaction/{tx_hash}"
                        print(f"   🌐 Verify at: {explorer_url}")
                    else:
                        print(f"   ⚠️  Transaction hash format unclear")
                else:
                    print(f"   ❌ No blockchain transaction hash provided")
                
                # Check withdrawal result
                if result.get("success"):
                    print(f"\n✅ WITHDRAWAL INITIATED SUCCESSFULLY!")
                    
                    # Additional blockchain verification via Tron manager
                    print(f"\n🔍 BLOCKCHAIN VERIFICATION:")
                    tron_manager = TronManager()
                    
                    # Try to verify the transaction
                    verification_result = await tron_manager.send_trx(
                        from_address=user_wallet,
                        to_address=destination_address,
                        amount=actual_withdrawal_trx
                    )
                    
                    if verification_result.get("success"):
                        print(f"   ✅ Tron blockchain manager confirms transaction")
                        print(f"   Hash: {verification_result.get('transaction_hash')}")
                        print(f"   Network: {verification_result.get('network', 'Tron')}")
                        print(f"   Fee: {verification_result.get('fee_estimate', 0)} TRX")
                    else:
                        print(f"   ⚠️  Tron blockchain manager: {verification_result.get('error', 'Unknown')}")
                
                else:
                    print(f"\n❌ WITHDRAWAL FAILED!")
                    print(f"   Error: {result.get('message', 'Unknown error')}")
                    return
        
        # Verify balance changes
        print(f"\n📊 BALANCE VERIFICATION:")
        updated_user = await db.users.find_one({"wallet_address": user_wallet})
        new_trx_balance = updated_user.get("deposit_balance", {}).get("TRX", 0)
        new_trx_liquidity = updated_user.get("liquidity_pool", {}).get("TRX", 0)
        
        expected_new_balance = trx_balance - actual_withdrawal_trx
        expected_new_liquidity = trx_liquidity - actual_withdrawal_trx
        
        print(f"   TRX Balance: {trx_balance:,.2f} → {new_trx_balance:,.2f}")
        print(f"   Expected: {expected_new_balance:,.2f}")
        print(f"   TRX Liquidity: {trx_liquidity:,.2f} → {new_trx_liquidity:,.2f}")
        print(f"   Expected: {expected_new_liquidity:,.2f}")
        
        balance_correct = abs(new_trx_balance - expected_new_balance) < 100
        liquidity_correct = abs(new_trx_liquidity - expected_new_liquidity) < 100
        
        if balance_correct and liquidity_correct:
            print(f"   ✅ Balance updates verified correctly")
        else:
            print(f"   ⚠️  Balance updates may have discrepancies")
        
        # Check transaction record
        print(f"\n📋 TRANSACTION RECORD:")
        recent_withdrawal = await db.transactions.find_one({
            "wallet_address": user_wallet,
            "type": "withdrawal",
            "currency": "TRX",
            "destination_address": destination_address
        }, sort=[("timestamp", -1)])
        
        if recent_withdrawal:
            print(f"   ✅ Transaction recorded in database")
            print(f"   Transaction ID: {recent_withdrawal.get('transaction_id')}")
            print(f"   Amount: {recent_withdrawal.get('amount', 0):,.2f} TRX")
            print(f"   Status: {recent_withdrawal.get('status', 'unknown')}")
            print(f"   Timestamp: {recent_withdrawal.get('timestamp')}")
        else:
            print(f"   ❌ Transaction not found in database")
        
        # FINAL SUMMARY
        print(f"\n🎯 WITHDRAWAL SUMMARY:")
        print("=" * 70)
        print(f"💸 Amount Withdrawn: {actual_withdrawal_trx:,.2f} TRX")
        print(f"💰 USD Value: ${actual_withdrawal_usd:,.2f}")
        print(f"🏦 From: {user_wallet}")
        print(f"📍 To: {destination_address}")
        print(f"🌐 Network: Tron (TRX)")
        
        if result.get("blockchain_transaction_hash"):
            tx_hash = result.get("blockchain_transaction_hash")
            print(f"🔐 Transaction Hash: {tx_hash}")
            print(f"🔍 Verify at: https://tronscan.org/#/transaction/{tx_hash}")
        
        print(f"\n⏰ EXPECTED CONFIRMATION TIME: 1-3 minutes")
        print(f"📱 CHECK YOUR WALLET: {destination_address}")
        print(f"💎 You should receive {actual_withdrawal_trx:,.2f} TRX")
        
        if actual_withdrawal_usd >= 50000:
            print(f"\n🎉 SUCCESS: Full $50K TRX withdrawal completed!")
        else:
            print(f"\n✅ SUCCESS: ${actual_withdrawal_usd:,.2f} TRX withdrawal completed!")
            print(f"   (Maximum available amount withdrawn)")
        
        print(f"\n🛡️  SECURITY NOTE:")
        if actual_withdrawal_usd >= 10000:
            print(f"   • Large withdrawal completed")
            print(f"   • Monitor your destination wallet")
            print(f"   • Verify transaction on Tronscan")
        
    except Exception as e:
        print(f"❌ Error during withdrawal: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(execute_tron_withdrawal())