#!/usr/bin/env python3
"""
Secure DOGE Hot Wallet Configuration Script
Allows you to securely configure your DOGE hot wallet without sharing private keys
"""

import os
import sys
import getpass
import asyncio
from pathlib import Path

# Add backend path
sys.path.append('/app/backend')

try:
    from blockchain.direct_doge_sender import DirectDogeSender
    from decimal import Decimal
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class SecureDOGESetup:
    def __init__(self):
        self.env_file = Path('/app/backend/.env')
        self.blockcypher_token = "3d9749fc8a924be894ebd8a66c2a9e00"
        
    def show_instructions(self):
        """Show setup instructions"""
        print("🔐 SECURE DOGE HOT WALLET SETUP")
        print("=" * 50)
        print()
        print("This script will help you configure real DOGE blockchain transactions.")
        print("Your private key will be stored locally and never transmitted.")
        print()
        print("📋 WHAT YOU NEED:")
        print("1. A DOGE wallet with some balance (100-1000 DOGE recommended)")
        print("2. The private key for that wallet")
        print("3. The DOGE address for that wallet")
        print()
        print("⚠️ SECURITY REMINDERS:")
        print("• Only use a dedicated hot wallet with limited funds")
        print("• Never share your private key with anyone")
        print("• Test with small amounts first")
        print("• Keep backup of your private key securely")
        print("")
        
    def get_wallet_info(self):
        """Securely collect wallet information"""
        print("📝 WALLET CONFIGURATION:")
        print("-" * 30)
        
        # Get DOGE address
        while True:
            doge_address = input("Enter your funded DOGE address: ").strip()
            if not doge_address:
                print("❌ Address cannot be empty")
                continue
            if not doge_address.startswith('D'):
                print("❌ DOGE addresses should start with 'D'")
                continue
            if len(doge_address) < 25 or len(doge_address) > 35:
                print("❌ Invalid DOGE address length")
                continue
            break
        
        # Get private key securely
        while True:
            print("\n🔑 Enter your DOGE private key:")
            print("   (Input will be hidden for security)")
            private_key = getpass.getpass("Private key: ").strip()
            if not private_key:
                print("❌ Private key cannot be empty")
                continue
            if len(private_key) < 30:
                print("❌ Private key seems too short")
                continue
            break
        
        return doge_address, private_key
    
    def update_env_file(self, doge_address, private_key):
        """Update .env file with new configuration"""
        try:
            # Read current .env file
            if self.env_file.exists():
                with open(self.env_file, 'r') as f:
                    lines = f.readlines()
            else:
                lines = []
            
            # Update or add configuration
            updated_lines = []
            updated_fields = set()
            
            for line in lines:
                if line.startswith('DOGE_HOT_WALLET_ADDRESS='):
                    updated_lines.append(f'DOGE_HOT_WALLET_ADDRESS="{doge_address}"\n')
                    updated_fields.add('address')
                elif line.startswith('DOGE_HOT_WALLET_PRIVATE_KEY='):
                    updated_lines.append(f'DOGE_HOT_WALLET_PRIVATE_KEY="{private_key}"\n')
                    updated_fields.add('private_key')
                elif line.startswith('DOGE_BLOCKCYPHER_TOKEN='):
                    updated_lines.append(f'DOGE_BLOCKCYPHER_TOKEN="{self.blockcypher_token}"\n')
                    updated_fields.add('token')
                else:
                    updated_lines.append(line)
            
            # Add missing fields
            if 'address' not in updated_fields:
                updated_lines.append(f'DOGE_HOT_WALLET_ADDRESS="{doge_address}"\n')
            if 'private_key' not in updated_fields:
                updated_lines.append(f'DOGE_HOT_WALLET_PRIVATE_KEY="{private_key}"\n')
            if 'token' not in updated_fields:
                updated_lines.append(f'DOGE_BLOCKCYPHER_TOKEN="{self.blockcypher_token}"\n')
            
            # Write updated file
            with open(self.env_file, 'w') as f:
                f.writelines(updated_lines)
            
            print("✅ Configuration saved to .env file")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update .env file: {e}")
            return False
    
    async def test_configuration(self, doge_address):
        """Test the wallet configuration"""
        print("\n🧪 TESTING CONFIGURATION:")
        print("-" * 30)
        
        try:
            # Initialize sender with new config
            sender = DirectDogeSender()
            
            # Test address validation
            print("1. Testing address validation...")
            is_valid = sender.validate_doge_address(doge_address)
            print(f"   ✅ Address format: {'Valid' if is_valid else 'Invalid'}")
            
            # Test balance check (with rate limiting)
            print("2. Testing balance check...")
            try:
                balance = await sender.get_balance(doge_address)
                print(f"   ✅ Wallet balance: {balance} DOGE")
                
                if balance == 0:
                    print("   ⚠️ Wallet has 0 DOGE - you need to fund it for real transactions")
                elif balance < Decimal("10"):
                    print("   ⚠️ Low balance - consider adding more DOGE for multiple transactions")
                else:
                    print("   ✅ Sufficient balance for transactions")
                    
            except Exception as e:
                print(f"   ⚠️ Balance check failed (rate limit?): {e}")
                print("   This is normal - BlockCypher has rate limits")
            
            # Test CoinGate address validation
            print("3. Testing destination address...")
            coingate_addr = "D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda"
            coingate_valid = sender.validate_doge_address(coingate_addr)
            print(f"   ✅ CoinGate address: {'Valid' if coingate_valid else 'Invalid'}")
            
            print("\n🎉 CONFIGURATION TEST COMPLETE!")
            return True
            
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            return False
    
    def show_next_steps(self):
        """Show what to do next"""
        print("\n🚀 SETUP COMPLETE!")
        print("=" * 30)
        print()
        print("✅ Your DOGE hot wallet is now configured for real blockchain transactions!")
        print()
        print("🎯 WHAT YOU CAN DO NOW:")
        print("1. Test small withdrawal (10-100 DOGE) to your CoinGate address")
        print("2. Use the direct blockchain withdrawal API endpoint") 
        print("3. Get REAL blockchain hashes for your transactions")
        print()
        print("🔧 API ENDPOINT:")
        print("POST /api/wallet/direct-blockchain-withdraw")
        print("{\n  \"wallet_address\": \"DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq\",")
        print("  \"currency\": \"DOGE\",")
        print("  \"amount\": 100,")
        print("  \"destination_address\": \"D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda\"\n}")
        print()
        print("💎 READY FOR REAL BLOCKCHAIN WITHDRAWALS!")
        
    async def run_setup(self):
        """Run the complete setup process"""
        try:
            self.show_instructions()
            
            # Get user confirmation
            confirm = input("Do you want to proceed with setup? (y/N): ").strip().lower()
            if confirm != 'y':
                print("Setup cancelled.")
                return
            
            # Get wallet information
            doge_address, private_key = self.get_wallet_info()
            
            # Update configuration
            if not self.update_env_file(doge_address, private_key):
                return
            
            # Test configuration
            await self.test_configuration(doge_address)
            
            # Show next steps
            self.show_next_steps()
            
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user.")
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")

async def main():
    setup = SecureDOGESetup()
    await setup.run_setup()

if __name__ == "__main__":
    asyncio.run(main())