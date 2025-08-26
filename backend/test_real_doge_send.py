#!/usr/bin/env python3
"""
Real DOGE Withdrawal Test Script
Demonstrates how to execute real blockchain transactions with actual private keys

REQUIREMENTS FOR REAL TRANSACTIONS:
1. Funded DOGE wallet with private key
2. BlockCypher API token
3. Destination address (your CoinGate address)

THIS SCRIPT SHOWS THE STRUCTURE - YOU NEED TO PROVIDE REAL CREDENTIALS
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from blockchain.direct_doge_sender import direct_doge_sender
from decimal import Decimal

async def test_real_doge_withdrawal():
    """
    Test real DOGE withdrawal to CoinGate
    
    NOTE: This will only work with real private keys and funding
    """
    
    print("🚀 TESTING REAL DOGE BLOCKCHAIN WITHDRAWAL")
    print("=" * 50)
    
    # Your withdrawal details
    coingate_address = "D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda"
    amount_doge = Decimal("1000")  # 1000 DOGE test
    user_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    
    print(f"💰 Amount: {amount_doge} DOGE")
    print(f"🎯 Destination: {coingate_address}")
    print(f"👤 User: {user_wallet}")
    print()
    
    # Step 1: Validate address
    print("1️⃣ Validating DOGE address...")
    is_valid = direct_doge_sender.validate_doge_address(coingate_address)
    print(f"   ✅ Address valid: {is_valid}")
    
    if not is_valid:
        print("❌ Invalid DOGE address format")
        return
    
    # Step 2: Check configuration
    print("\n2️⃣ Checking configuration...")
    hot_wallet = direct_doge_sender.hot_wallet_address
    has_private_key = bool(direct_doge_sender.hot_wallet_private_key)
    has_blockcypher = bool(direct_doge_sender.blockcypher_token)
    
    print(f"   Hot wallet: {hot_wallet or 'NOT CONFIGURED'}")
    print(f"   Private key: {'CONFIGURED' if has_private_key else 'NOT CONFIGURED'}")
    print(f"   BlockCypher token: {'CONFIGURED' if has_blockcypher else 'NOT CONFIGURED'}")
    
    if not all([hot_wallet, has_private_key, has_blockcypher]):
        print("\n❌ CONFIGURATION INCOMPLETE:")
        print("   To execute REAL transactions, you need:")
        print("   1. DOGE_HOT_WALLET_ADDRESS (funded DOGE address)")
        print("   2. DOGE_HOT_WALLET_PRIVATE_KEY (private key for that address)")  
        print("   3. DOGE_BLOCKCYPHER_TOKEN (BlockCypher API token)")
        print("\n   Set these in /app/backend/.env file")
        return
    
    # Step 3: Check hot wallet balance
    print("\n3️⃣ Checking hot wallet balance...")
    try:
        balance = await direct_doge_sender.get_balance(hot_wallet)
        print(f"   Balance: {balance} DOGE")
        
        if balance < amount_doge + Decimal("1"):  # Include fee
            print(f"❌ Insufficient hot wallet funds: {balance} DOGE < {amount_doge + 1} DOGE needed")
            return
    except Exception as e:
        print(f"   ❌ Balance check failed: {e}")
        return
    
    # Step 4: Execute real withdrawal
    print("\n4️⃣ Executing REAL blockchain withdrawal...")
    print("   ⚠️ This will create an actual DOGE transaction!")
    
    try:
        result = await direct_doge_sender.send_doge(
            destination_address=coingate_address,
            amount_doge=amount_doge,
            user_wallet=user_wallet
        )
        
        if result.get('success'):
            print("\n🎉 REAL WITHDRAWAL SUCCESSFUL!")
            print(f"   ✅ Blockchain Hash: {result.get('blockchain_hash')}")
            print(f"   ✅ Transaction ID: {result.get('txid')}")
            print(f"   ✅ Verification URL: {result.get('verification_url')}")
            print(f"   ✅ From Address: {result.get('from_address')}")
            print(f"   ✅ To Address: {coingate_address}")
            print(f"   ✅ Amount: {amount_doge} DOGE")
            print("\n🏦 CHECK YOUR COINGATE ACCOUNT!")
            
        else:
            print(f"\n❌ Withdrawal failed: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ Withdrawal error: {e}")
    
    print("\n" + "=" * 50)

def show_configuration_requirements():
    """Show what's needed for real transactions"""
    
    print("🔧 REAL DOGE WITHDRAWAL CONFIGURATION")
    print("=" * 50)
    print()
    print("To execute REAL blockchain transactions, you need:")
    print()
    print("1️⃣ FUNDED DOGE WALLET:")
    print("   • Create a DOGE wallet (Dogecoin Core, MultiDoge, etc.)")
    print("   • Fund it with DOGE (buy from exchange, transfer, etc.)")
    print("   • Export the private key")
    print()
    print("2️⃣ BLOCKCYPHER API TOKEN:")
    print("   • Sign up at https://www.blockcypher.com/")
    print("   • Get free API token (3000 requests/hour)")
    print("   • Premium token for more requests")
    print()
    print("3️⃣ ENVIRONMENT CONFIGURATION:")
    print("   Edit /app/backend/.env:")
    print("   DOGE_HOT_WALLET_ADDRESS='your_funded_doge_address'")
    print("   DOGE_HOT_WALLET_PRIVATE_KEY='your_private_key'")
    print("   DOGE_BLOCKCYPHER_TOKEN='your_blockcypher_token'")
    print()
    print("⚠️ SECURITY WARNINGS:")
    print("   • Never share private keys")
    print("   • Use dedicated hot wallet with limited funds")
    print("   • Test with small amounts first")
    print("   • Private keys give full control of funds")
    print()
    print("📋 CURRENT STATUS:")
    
    hot_wallet = os.getenv('DOGE_HOT_WALLET_ADDRESS')
    private_key = os.getenv('DOGE_HOT_WALLET_PRIVATE_KEY') 
    blockcypher = os.getenv('DOGE_BLOCKCYPHER_TOKEN')
    
    print(f"   Hot Wallet: {'✅ SET' if hot_wallet and hot_wallet != 'YOUR_REAL_DOGE_PRIVATE_KEY_HERE' else '❌ NOT SET'}")
    print(f"   Private Key: {'✅ SET' if private_key and private_key != 'YOUR_REAL_DOGE_PRIVATE_KEY_HERE' else '❌ NOT SET'}")
    print(f"   BlockCypher: {'✅ SET' if blockcypher else '❌ NOT SET'}")
    print()

if __name__ == "__main__":
    print("🚀 REAL DOGE BLOCKCHAIN WITHDRAWAL SYSTEM")
    print("=" * 50)
    
    # Show configuration requirements
    show_configuration_requirements()
    
    # Check if properly configured
    hot_wallet = os.getenv('DOGE_HOT_WALLET_ADDRESS')
    private_key = os.getenv('DOGE_HOT_WALLET_PRIVATE_KEY')
    blockcypher = os.getenv('DOGE_BLOCKCYPHER_TOKEN')
    
    if all([hot_wallet, private_key, blockcypher]) and private_key != 'YOUR_REAL_DOGE_PRIVATE_KEY_HERE':
        print("✅ Configuration appears complete. Testing real withdrawal...")
        asyncio.run(test_real_doge_withdrawal())
    else:
        print("❌ Configuration incomplete. Cannot test real withdrawals.")
        print("\nProvide real credentials in .env file to enable blockchain transactions.")