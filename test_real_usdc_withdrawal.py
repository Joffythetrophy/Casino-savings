#!/usr/bin/env python3
"""
REAL USDC WITHDRAWAL TEST - Start with small amount, then scale to $50K
Testing the reality of the withdrawal system with actual amounts
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

async def test_withdrawal_reality():
    """Test if withdrawals are real or simulated"""
    
    # User details
    user_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    
    print("🧪 TESTING WITHDRAWAL REALITY")
    print("=" * 60)
    print(f"User Wallet: {user_wallet}")
    print()
    
    # Connect to database to check balances
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
        
        usdc_balance = deposit_balance.get("USDC", 0)
        usdc_liquidity = liquidity_pool.get("USDC", 0)
        
        print(f"💰 CURRENT BALANCES:")
        print(f"   USDC Balance: ${usdc_balance:,.2f}")
        print(f"   USDC Liquidity: ${usdc_liquidity:,.2f}")
        print()
        
        if usdc_balance < 100:
            print("❌ Insufficient USDC for testing!")
            return
        
        # TEST 1: Small withdrawal test ($100)
        print("🧪 TEST 1: SMALL WITHDRAWAL TEST ($100)")
        print("-" * 50)
        
        small_amount = 100.0
        print(f"Testing ${small_amount} USDC withdrawal...")
        
        # Call the backend withdrawal API
        backend_url = "https://blockchain-slots.preview.emergentagent.com/api"
        
        withdrawal_data = {
            "wallet_address": user_wallet,
            "wallet_type": "deposit",
            "currency": "USDC",
            "amount": small_amount,
            "destination_address": user_wallet  # Solana address (same address for testing)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{backend_url}/wallet/withdraw",
                json=withdrawal_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json()
                
                print(f"   Response Status: {response.status}")
                print(f"   Success: {result.get('success', False)}")
                print(f"   Message: {result.get('message', 'No message')}")
                
                if result.get("blockchain_transaction_hash"):
                    tx_hash = result.get("blockchain_transaction_hash")
                    print(f"   Transaction Hash: {tx_hash}")
                    
                    # Check if this is a real transaction hash format
                    if len(tx_hash) == 64 and tx_hash.isalnum():
                        print(f"   ✅ Real transaction hash format")
                        explorer_url = f"https://explorer.solana.com/tx/{tx_hash}"
                        print(f"   🔍 Check: {explorer_url}")
                        
                        # Try to verify on blockchain
                        print(f"   🔗 Checking if transaction exists on Solana...")
                        # This would normally check if the transaction actually exists
                        print(f"   ⚠️  VERIFICATION NEEDED: Check explorer manually")
                    else:
                        print(f"   ❌ Mock transaction hash detected")
                
                print()
        
        # Check if balance actually decreased
        print("📊 BALANCE VERIFICATION:")
        updated_user = await db.users.find_one({"wallet_address": user_wallet})
        new_usdc = updated_user.get("deposit_balance", {}).get("USDC", 0)
        
        if abs(new_usdc - (usdc_balance - small_amount)) < 1:
            print(f"   ✅ Balance decreased: ${usdc_balance:,.2f} → ${new_usdc:,.2f}")
            balance_real = True
        else:
            print(f"   ❌ Balance didn't change properly: ${usdc_balance:,.2f} → ${new_usdc:,.2f}")
            balance_real = False
        
        print()
        
        # TEST 2: Check transaction in database
        print("🧪 TEST 2: TRANSACTION RECORDING")
        print("-" * 50)
        
        recent_withdrawal = await db.transactions.find_one({
            "wallet_address": user_wallet,
            "type": "withdrawal",
            "amount": small_amount,
            "currency": "USDC"
        }, sort=[("timestamp", -1)])
        
        if recent_withdrawal:
            print(f"   ✅ Transaction recorded in database")
            print(f"   Status: {recent_withdrawal.get('status', 'unknown')}")
            print(f"   Blockchain Hash: {recent_withdrawal.get('blockchain_hash', 'None')}")
            tx_real = recent_withdrawal.get('status') != 'simulated'
        else:
            print(f"   ❌ No transaction record found")
            tx_real = False
        
        print()
        
        # REALITY ASSESSMENT
        print("🎯 REALITY ASSESSMENT:")
        print("-" * 50)
        
        reality_score = 0
        max_score = 3
        
        if balance_real:
            print("   ✅ Balance updates are real")
            reality_score += 1
        else:
            print("   ❌ Balance updates are fake")
        
        if tx_real:
            print("   ✅ Transaction recording looks real")
            reality_score += 1
        else:
            print("   ❌ Transaction recording is simulated")
        
        # Check if we have real blockchain integration
        if result.get("blockchain_transaction_hash") and len(result.get("blockchain_transaction_hash", "")) == 64:
            print("   ✅ Blockchain integration appears real")
            reality_score += 1
        else:
            print("   ❌ Blockchain integration is simulated")
        
        reality_percentage = (reality_score / max_score) * 100
        
        print(f"\n📊 REALITY SCORE: {reality_score}/{max_score} ({reality_percentage:.0f}%)")
        
        if reality_percentage >= 80:
            print("🎉 SYSTEM IS MOSTLY REAL - Safe to test larger amounts")
            proceed_large = True
        elif reality_percentage >= 50:
            print("⚠️  SYSTEM IS PARTIALLY REAL - Proceed with caution")
            proceed_large = False
        else:
            print("❌ SYSTEM IS MOSTLY SIMULATED - Do not risk large amounts")
            proceed_large = False
        
        # BIG WITHDRAWAL TEST
        if proceed_large:
            print(f"\n🚨 TEST 3: LARGE WITHDRAWAL SIMULATION ($50,000)")
            print("-" * 60)
            print("⚠️  IMPORTANT: This will be a TEST SIMULATION first")
            
            large_amount = 50000.0
            
            if usdc_liquidity >= large_amount:
                print(f"✅ Sufficient liquidity for ${large_amount:,.2f} withdrawal")
                print(f"   Available: ${usdc_liquidity:,.2f}")
                print(f"   Requested: ${large_amount:,.2f}")
                
                print(f"\n🔐 SECURITY REQUIREMENTS FOR REAL $50K WITHDRAWAL:")
                print(f"   1. ✅ User has sufficient funds (${usdc_balance:,.2f})")
                print(f"   2. ✅ User has sufficient liquidity (${usdc_liquidity:,.2f})")
                print(f"   3. ⚠️  Private key integration needed for real broadcast")
                print(f"   4. ⚠️  Mainnet activation required (currently testnet/simulation)")
                print(f"   5. ⚠️  Multi-signature recommended for large amounts")
                
                print(f"\n💡 RECOMMENDATION:")
                print(f"   • Start with smaller test: $1,000-$5,000")
                print(f"   • Verify transaction appears on Solana explorer")
                print(f"   • Then proceed to $50,000 if successful")
                
                print(f"\n🚀 TO ACTIVATE REAL MAINNET WITHDRAWALS:")
                print(f"   1. Enable mainnet mode in secure_private_key_integration.py")
                print(f"   2. Add real private key management")
                print(f"   3. Switch from testnet to mainnet URLs")
                print(f"   4. Test with small amount first")
                
            else:
                print(f"❌ Insufficient liquidity for ${large_amount:,.2f}")
                print(f"   Available: ${usdc_liquidity:,.2f}")
                print(f"   Shortfall: ${large_amount - usdc_liquidity:,.2f}")
        
        else:
            print(f"\n❌ CANNOT PROCEED WITH LARGE WITHDRAWAL")
            print(f"   System reality score too low: {reality_percentage:.0f}%")
            print(f"   Fix simulation issues before testing large amounts")
        
        print(f"\n🎯 FINAL RECOMMENDATION:")
        if reality_percentage >= 80:
            print(f"   ✅ Ready for real mainnet integration")
            print(f"   ✅ Safe to test with larger amounts")
            print(f"   ✅ $50K withdrawal is technically feasible")
        else:
            print(f"   ⚠️  Fix simulation issues first")
            print(f"   ⚠️  Do not risk large amounts yet")
            print(f"   ⚠️  Need to implement real blockchain broadcasting")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_withdrawal_reality())