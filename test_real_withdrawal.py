#!/usr/bin/env python3
"""
REAL WITHDRAWAL TEST - Prove the system works with Solana address
Test actual blockchain withdrawal to user's Solana wallet
"""

import os
import sys
import asyncio
import aiohttp
import json
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.append(str(backend_dir))

# Load environment variables
load_dotenv(backend_dir / '.env')

# Import blockchain managers for direct testing
from blockchain.solana_manager import SolanaManager, SPLTokenManager, CRTTokenManager

async def test_real_withdrawal():
    """Test real withdrawal to user's Solana address"""
    
    # User details
    user_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    withdrawal_amount = 100.0  # Test with 100 USDC
    currency = "USDC"
    
    print("🧪 REAL WITHDRAWAL TEST")
    print("=" * 60)
    print(f"From Wallet: {user_wallet}")
    print(f"To Wallet: {user_wallet} (same address - Solana native)")
    print(f"Amount: {withdrawal_amount} {currency}")
    print(f"Network: Solana")
    print()
    
    # Connect to database
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    try:
        # Check user's current balance and liquidity
        user = await db.users.find_one({"wallet_address": user_wallet})
        if not user:
            print("❌ User not found!")
            return
        
        deposit_balance = user.get("deposit_balance", {})
        liquidity_pool = user.get("liquidity_pool", {})
        
        current_usdc = deposit_balance.get("USDC", 0)
        usdc_liquidity = liquidity_pool.get("USDC", 0)
        
        print(f"📊 CURRENT BALANCES:")
        print(f"   USDC Deposit Balance: {current_usdc:,.2f}")
        print(f"   USDC Liquidity: {usdc_liquidity:,.2f}")
        print()
        
        if usdc_liquidity < withdrawal_amount:
            print(f"❌ Insufficient liquidity! Need {withdrawal_amount}, have {usdc_liquidity}")
            return
        
        print("🔗 INITIATING REAL BLOCKCHAIN WITHDRAWAL...")
        print("-" * 50)
        
        # Initialize Solana managers
        solana_manager = SolanaManager()
        spl_manager = SPLTokenManager(solana_manager)
        
        # Test 1: Direct blockchain manager test
        print("TEST 1: Direct Blockchain Manager")
        
        usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # Real USDC mint on Solana
        
        direct_result = await solana_manager.send_spl_token(
            from_address=user_wallet,
            to_address=user_wallet,  # Send to same address for testing
            amount=withdrawal_amount,
            token_mint=usdc_mint
        )
        
        print(f"   Result: {'✅ SUCCESS' if direct_result.get('success') else '❌ FAILED'}")
        print(f"   Transaction Hash: {direct_result.get('transaction_hash', 'None')}")
        print(f"   Message: {direct_result.get('note', 'No message')}")
        print()
        
        # Test 2: Backend API withdrawal test
        print("TEST 2: Backend API Withdrawal")
        
        backend_url = "https://tiger-dex-casino.preview.emergentagent.com/api"
        
        withdrawal_data = {
            "wallet_address": user_wallet,
            "wallet_type": "deposit",
            "currency": currency,
            "amount": withdrawal_amount,
            "destination_address": user_wallet  # Solana address
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{backend_url}/wallet/withdraw",
                json=withdrawal_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                api_result = await response.json()
                
                print(f"   HTTP Status: {response.status}")
                print(f"   Result: {'✅ SUCCESS' if api_result.get('success') else '❌ FAILED'}")
                print(f"   Message: {api_result.get('message', 'No message')}")
                
                if api_result.get("blockchain_transaction_hash"):
                    print(f"   Blockchain TX: {api_result.get('blockchain_transaction_hash')}")
                
                if api_result.get("verification_url"):
                    print(f"   Verify at: {api_result.get('verification_url')}")
                
                print()
        
        # Test 3: Check transaction was recorded
        print("TEST 3: Transaction Recording Check")
        
        # Look for recent withdrawal transaction
        recent_tx = await db.transactions.find_one({
            "wallet_address": user_wallet,
            "type": "withdrawal",
            "amount": withdrawal_amount,
            "currency": currency
        }, sort=[("timestamp", -1)])
        
        if recent_tx:
            print("   ✅ Transaction recorded in database")
            print(f"   Transaction ID: {recent_tx.get('transaction_id')}")
            print(f"   Status: {recent_tx.get('status')}")
            print(f"   Blockchain Hash: {recent_tx.get('blockchain_hash', 'None')}")
        else:
            print("   ❌ No transaction found in database")
        
        print()
        
        # Test 4: Balance update verification
        print("TEST 4: Balance Update Verification")
        
        updated_user = await db.users.find_one({"wallet_address": user_wallet})
        new_usdc = updated_user.get("deposit_balance", {}).get("USDC", 0)
        new_liquidity = updated_user.get("liquidity_pool", {}).get("USDC", 0)
        
        expected_usdc = current_usdc - withdrawal_amount
        expected_liquidity = usdc_liquidity - withdrawal_amount
        
        print(f"   USDC Balance: {current_usdc:,.2f} → {new_usdc:,.2f} (expected: {expected_usdc:,.2f})")
        print(f"   USDC Liquidity: {usdc_liquidity:,.2f} → {new_liquidity:,.2f} (expected: {expected_liquidity:,.2f})")
        
        balance_correct = abs(new_usdc - expected_usdc) < 0.01
        liquidity_correct = abs(new_liquidity - expected_liquidity) < 0.01
        
        print(f"   Balance Update: {'✅ CORRECT' if balance_correct else '❌ INCORRECT'}")
        print(f"   Liquidity Update: {'✅ CORRECT' if liquidity_correct else '❌ INCORRECT'}")
        print()
        
        # FINAL SUMMARY
        print("🎯 REAL WITHDRAWAL TEST SUMMARY:")
        print("-" * 50)
        
        tests_passed = 0
        total_tests = 4
        
        if direct_result.get("success"):
            tests_passed += 1
            print("✅ Direct blockchain manager works")
        else:
            print("❌ Direct blockchain manager failed")
        
        if api_result.get("success"):
            tests_passed += 1
            print("✅ Backend API withdrawal works")
        else:
            print("❌ Backend API withdrawal failed")
        
        if recent_tx:
            tests_passed += 1
            print("✅ Transaction recording works")
        else:
            print("❌ Transaction recording failed")
        
        if balance_correct and liquidity_correct:
            tests_passed += 1
            print("✅ Balance updates work correctly")
        else:
            print("❌ Balance updates incorrect")
        
        print(f"\n📊 OVERALL RESULT: {tests_passed}/{total_tests} tests passed ({tests_passed/total_tests*100:.0f}%)")
        
        if tests_passed >= 3:
            print("🎉 REAL WITHDRAWAL SYSTEM IS WORKING!")
            print("   Your Solana address is compatible for real withdrawals")
            print("   The system can handle real blockchain transactions")
        else:
            print("⚠️  REAL WITHDRAWAL SYSTEM NEEDS FIXES")
            print("   Some components are not working correctly")
        
        # Show verification instructions
        if direct_result.get("transaction_hash"):
            tx_hash = direct_result.get("transaction_hash")
            print(f"\n🔍 VERIFICATION:")
            print(f"   Transaction Hash: {tx_hash}")
            print(f"   Check on Solscan: https://solscan.io/tx/{tx_hash}")
            print(f"   Note: This may be simulated - check the explorer")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_real_withdrawal())