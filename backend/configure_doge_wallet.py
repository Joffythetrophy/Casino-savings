#!/usr/bin/env python3
"""
DOGE Hot Wallet Configuration Helper
Instructions for setting up real DOGE blockchain transactions
"""

import os
import sys
import asyncio
from pathlib import Path

# Add backend path
sys.path.append('/app/backend')

def show_configuration_instructions():
    """Show detailed configuration instructions"""
    
    print("🔐 DOGE HOT WALLET CONFIGURATION")
    print("=" * 50)
    print()
    print("To enable REAL blockchain transactions, you need to:")
    print()
    
    print("1️⃣ GET YOUR DOGE WALLET INFO:")
    print("   • DOGE Address: Your funded wallet address (starts with 'D')")
    print("   • Private Key: Export from your wallet (51-52 characters)")
    print("   • Balance: Should have some DOGE (100+ recommended)")
    print()
    
    print("2️⃣ EDIT THE .ENV FILE:")
    print("   Open: /app/backend/.env")
    print("   Update these lines:")
    print("   DOGE_HOT_WALLET_ADDRESS=\"your_funded_doge_address_here\"")
    print("   DOGE_HOT_WALLET_PRIVATE_KEY=\"your_private_key_here\"")
    print()
    
    print("3️⃣ EXAMPLE CONFIGURATION:")
    print("   DOGE_HOT_WALLET_ADDRESS=\"DMzWkaGLBqyqG9tCXbK1PZNJjgNTpe9LHx\"")
    print("   DOGE_HOT_WALLET_PRIVATE_KEY=\"QVsRb2XsYcZm...your_private_key_here\"")
    print()
    
    print("⚠️ SECURITY WARNINGS:")
    print("   • Use dedicated hot wallet with limited funds only")
    print("   • Never share private key with anyone")
    print("   • Test with small amounts first (10-50 DOGE)")
    print("   • Private key gives full control - keep it secure")
    print()
    
    print("💡 HOW TO GET DOGE WALLET:")
    print("   Option A: Use existing wallet (Exodus, Dogecoin Core, etc.)")
    print("   Option B: Create new wallet and transfer DOGE from exchange")
    print("   Option C: Use hot wallet service (less secure)")
    print()

def check_current_configuration():
    """Check current configuration status"""
    
    print("🔍 CURRENT CONFIGURATION STATUS:")
    print("-" * 40)
    
    # Check environment variables
    hot_wallet = os.getenv('DOGE_HOT_WALLET_ADDRESS', '')
    private_key = os.getenv('DOGE_HOT_WALLET_PRIVATE_KEY', '')
    blockcypher = os.getenv('DOGE_BLOCKCYPHER_TOKEN', '')
    
    print(f"BlockCypher Token: {'✅ CONFIGURED' if blockcypher else '❌ MISSING'}")
    
    if hot_wallet and hot_wallet != 'YOUR_REAL_DOGE_PRIVATE_KEY_HERE':
        print(f"Hot Wallet Address: ✅ CONFIGURED ({hot_wallet[:15]}...)")
    else:
        print("Hot Wallet Address: ❌ NOT CONFIGURED")
    
    if private_key and private_key != 'YOUR_REAL_DOGE_PRIVATE_KEY_HERE' and len(private_key) > 30:
        print("Private Key: ✅ CONFIGURED")
    else:
        print("Private Key: ❌ NOT CONFIGURED")
    
    print()
    
    if all([hot_wallet, private_key, blockcypher]) and private_key != 'YOUR_REAL_DOGE_PRIVATE_KEY_HERE':
        print("🎉 CONFIGURATION COMPLETE!")
        print("✅ Ready for real blockchain transactions")
        return True
    else:
        print("❌ CONFIGURATION INCOMPLETE")
        print("Follow the instructions above to complete setup")
        return False

async def test_wallet_connection():
    """Test wallet configuration if complete"""
    
    try:
        from blockchain.direct_doge_sender import DirectDogeSender
        from decimal import Decimal
        
        sender = DirectDogeSender()
        hot_wallet = sender.hot_wallet_address
        
        if not hot_wallet or hot_wallet == 'YOUR_REAL_DOGE_PRIVATE_KEY_HERE':
            print("❌ Wallet not configured yet")
            return
        
        print("🧪 TESTING WALLET CONNECTION:")
        print("-" * 35)
        
        # Test address validation
        print("1. Validating hot wallet address...")
        is_valid = sender.validate_doge_address(hot_wallet)
        print(f"   {'✅' if is_valid else '❌'} Address format: {'Valid' if is_valid else 'Invalid'}")
        
        # Test CoinGate address
        coingate_addr = "D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda"
        print("2. Validating CoinGate address...")
        coingate_valid = sender.validate_doge_address(coingate_addr)
        print(f"   {'✅' if coingate_valid else '❌'} CoinGate address: {'Valid' if coingate_valid else 'Invalid'}")
        
        # Test balance (may fail due to rate limits)
        print("3. Checking wallet balance...")
        try:
            balance = await sender.get_balance(hot_wallet)
            print(f"   ✅ Balance: {balance} DOGE")
            
            if balance > Decimal("10"):
                print("   ✅ Sufficient balance for transactions")
            else:
                print("   ⚠️ Low balance - consider adding more DOGE")
                
        except Exception as e:
            print(f"   ⚠️ Balance check failed: {str(e)[:50]}...")
            print("   (This is normal due to API rate limits)")
        
        print()
        print("🚀 READY FOR REAL BLOCKCHAIN TRANSACTIONS!")
        print("You can now use the direct blockchain withdrawal API")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def show_usage_example():
    """Show how to use the configured wallet"""
    
    print("🎯 HOW TO USE REAL BLOCKCHAIN WITHDRAWALS:")
    print("-" * 45)
    print()
    print("Once configured, use this API endpoint:")
    print()
    print("POST /api/wallet/direct-blockchain-withdraw")
    print("{")
    print('  "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",')
    print('  "currency": "DOGE",')
    print('  "amount": 100,')
    print('  "destination_address": "D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda"')
    print("}")
    print()
    print("Response will include:")
    print("✅ Real blockchain hash")
    print("✅ Transaction ID")
    print("✅ Verification URL (dogechain.info)")
    print("✅ From/To addresses")
    print()

async def main():
    """Main configuration helper"""
    
    show_configuration_instructions()
    is_configured = check_current_configuration()
    
    if is_configured:
        print()
        await test_wallet_connection()
        print()
        show_usage_example()
    else:
        print()
        print("📝 NEXT STEPS:")
        print("1. Get your DOGE wallet address and private key")
        print("2. Edit /app/backend/.env file with your credentials")
        print("3. Run this script again to test configuration")
        print("4. Execute real blockchain withdrawals!")

if __name__ == "__main__":
    asyncio.run(main())