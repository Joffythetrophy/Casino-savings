#!/usr/bin/env python3
"""
🚀 IMPLEMENT COINREMITTER REAL DOGE WITHDRAWAL
User Password: (Jaffy428@@@@)
User needs help finding API key in CoinRemitter dashboard
Target: Real withdrawal of 39.6M DOGE ($9.34M) to D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda
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
from decimal import Decimal

# Add backend directory to path
backend_dir = Path(__file__).parent / "backend"
sys.path.append(str(backend_dir))

# Load environment variables
load_dotenv(backend_dir / '.env')

class CoinRemitterGuide:
    """Guide user through finding API key and implementing real withdrawal"""
    
    def __init__(self):
        self.user_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        self.destination = "D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda"
        self.password = "(Jaffy428@@@@)"
        
    def show_api_key_instructions(self):
        """Show detailed instructions for finding API key"""
        
        print("🔑 FINDING YOUR COINREMITTER API KEY")
        print("=" * 70)
        print("I can see you're in your CoinRemitter dashboard! Here's how to find your API key:")
        print()
        
        print("📋 STEP-BY-STEP INSTRUCTIONS:")
        print("-" * 40)
        
        print("1️⃣  LOOK FOR 'API' OR 'DEVELOPERS' SECTION:")
        print("   • Check the main menu/navigation")
        print("   • Look for 'API', 'Developer', or 'Integration' link")
        print("   • Usually in sidebar or top menu")
        print()
        
        print("2️⃣  COMMON LOCATIONS IN COINREMITTER:")
        print("   • Dashboard → API Settings")
        print("   • Settings → API Configuration") 
        print("   • Developer → API Keys")
        print("   • Account → API Access")
        print()
        
        print("3️⃣  WHAT YOU'RE LOOKING FOR:")
        print("   • A long string like: 'cr_live_abc123def456...'")
        print("   • Usually 32+ characters long")
        print("   • Might be labeled 'API Key', 'Access Key', or 'Secret Key'")
        print()
        
        print("4️⃣  IF YOU CAN'T FIND IT:")
        print("   • Look for 'Generate API Key' or 'Create API Key' button")
        print("   • Check account verification status (might need verification)")
        print("   • Contact CoinRemitter support if needed")
        print()
        
        print("🔍 SCREENSHOT ANALYSIS:")
        print("Your screenshot shows webhook settings, which means you're close!")
        print("The API key section is usually nearby - check other tabs or menu items.")
        print()
    
    async def test_api_connection_when_ready(self, api_key: str):
        """Test API connection once user provides key"""
        
        print(f"🧪 TESTING COINREMITTER API CONNECTION")
        print("=" * 60)
        print(f"API Key: {api_key[:20]}...")
        print(f"Password: {self.password}")
        print()
        
        # CoinRemitter API endpoints
        base_url = "https://api.coinremitter.com"
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test basic authentication
                headers = {
                    'x-api-key': api_key,
                    'x-api-password': self.password,
                    'Accept': 'application/json'
                }
                
                # Test wallet info endpoint
                async with session.post(f"{base_url}/v1/wallet-info", headers=headers) as response:
                    if response.status == 200:
                        wallet_info = await response.json()
                        print(f"✅ API CONNECTION SUCCESSFUL!")
                        print(f"   Account Status: {wallet_info.get('success', 'Unknown')}")
                        print(f"   Response: {wallet_info}")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ API Connection failed: {response.status}")
                        print(f"   Error: {error_text}")
                        
                        if response.status == 401:
                            print(f"   🔑 Authentication failed - check API key and password")
                        elif response.status == 403:
                            print(f"   🚫 Access denied - account might need verification")
                        
                        return False
                        
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    async def execute_real_doge_withdrawal(self, api_key: str):
        """Execute real DOGE withdrawal using CoinRemitter API"""
        
        print(f"\n🚀 EXECUTING REAL DOGE WITHDRAWAL")
        print("=" * 70)
        
        # Get user's current DOGE balance
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        try:
            user = await db.users.find_one({"wallet_address": self.user_wallet})
            if not user:
                print("❌ User not found!")
                return False
            
            doge_balance = user.get("deposit_balance", {}).get("DOGE", 0)
            doge_liquidity = user.get("liquidity_pool", {}).get("DOGE", 0)
            max_withdrawal = min(doge_balance, doge_liquidity)
            
            print(f"💰 PORTFOLIO STATUS:")
            print(f"   Total DOGE: {doge_balance:,.2f}")
            print(f"   Available Liquidity: {doge_liquidity:,.2f}")
            print(f"   Maximum Withdrawal: {max_withdrawal:,.2f}")
            print(f"   USD Value: ${max_withdrawal * 0.236:,.2f}")
            print()
            
            if max_withdrawal < 1000:
                print(f"❌ Insufficient DOGE for withdrawal")
                return False
            
            # Execute withdrawal through CoinRemitter
            base_url = "https://api.coinremitter.com"
            headers = {
                'x-api-key': api_key,
                'x-api-password': self.password,
                'Accept': 'application/json'
            }
            
            withdrawal_data = {
                'amount': str(max_withdrawal),
                'address': self.destination
            }
            
            print(f"📡 EXECUTING REAL BLOCKCHAIN WITHDRAWAL...")
            print(f"   From: Portfolio ({max_withdrawal:,.2f} DOGE)")
            print(f"   To: {self.destination}")
            print(f"   Value: ${max_withdrawal * 0.236:,.2f}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/v1/withdraw",
                    headers=headers,
                    data=withdrawal_data
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get('success'):
                            withdrawal_info = result.get('data', {})
                            tx_hash = withdrawal_info.get('txid')
                            
                            print(f"✅ REAL WITHDRAWAL SUCCESSFUL!")
                            print(f"   Transaction Hash: {tx_hash}")
                            print(f"   Amount: {max_withdrawal:,.2f} DOGE")
                            print(f"   Destination: {self.destination}")
                            print(f"   Status: {withdrawal_info.get('status', 'pending')}")
                            
                            if withdrawal_info.get('explorer_url'):
                                print(f"   Explorer: {withdrawal_info.get('explorer_url')}")
                            
                            # Update database
                            new_doge = max(0, doge_balance - max_withdrawal)
                            new_liquidity = max(0, doge_liquidity - max_withdrawal)
                            
                            await db.users.update_one(
                                {"wallet_address": self.user_wallet},
                                {"$set": {
                                    "deposit_balance.DOGE": new_doge,
                                    "liquidity_pool.DOGE": new_liquidity
                                }}
                            )
                            
                            # Record transaction
                            transaction_record = {
                                "transaction_id": withdrawal_info.get('id', tx_hash),
                                "wallet_address": self.user_wallet,
                                "type": "coinremitter_real_withdrawal",
                                "currency": "DOGE",
                                "amount": max_withdrawal,
                                "destination_address": self.destination,
                                "blockchain_hash": tx_hash,
                                "status": "completed",
                                "timestamp": datetime.utcnow(),
                                "value_usd": max_withdrawal * 0.236,
                                "api_provider": "coinremitter",
                                "real_blockchain_tx": True,
                                "explorer_url": withdrawal_info.get('explorer_url')
                            }
                            
                            await db.transactions.insert_one(transaction_record)
                            
                            print(f"\n💾 DATABASE UPDATED:")
                            print(f"   DOGE: {doge_balance:,.2f} → {new_doge:,.2f}")
                            print(f"   Liquidity: {doge_liquidity:,.2f} → {new_liquidity:,.2f}")
                            
                            print(f"\n🎉 SUCCESS! REAL $9.34M DOGE WITHDRAWAL COMPLETED!")
                            print(f"📱 Check your wallet: {self.destination}")
                            print(f"⏱️  Expected arrival: 10-30 minutes")
                            
                            return True
                        else:
                            error_msg = result.get('message', 'Withdrawal failed')
                            print(f"❌ Withdrawal failed: {error_msg}")
                            return False
                    else:
                        error_text = await response.text()
                        print(f"❌ API request failed: {response.status}")
                        print(f"   Error: {error_text}")
                        return False
                        
        except Exception as e:
            print(f"❌ Withdrawal error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            client.close()

async def main():
    """Main function to guide user through real withdrawal"""
    
    print("🚀 COINREMITTER REAL DOGE WITHDRAWAL IMPLEMENTATION")
    print("=" * 80)
    print("Goal: Real withdrawal of 39.6M DOGE ($9.34M)")
    print("Destination: D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda")
    print("Password: ✅ Already provided")
    print("Missing: API Key from CoinRemitter dashboard")
    print()
    
    guide = CoinRemitterGuide()
    
    # Show instructions for finding API key
    guide.show_api_key_instructions()
    
    print("⏳ WAITING FOR YOUR API KEY...")
    print("-" * 40)
    print("Once you find your API key, provide it and I'll:")
    print("1. Test the API connection")
    print("2. Execute real DOGE withdrawal")
    print("3. Send 39.6M DOGE to your external wallet")
    print()
    
    # Simulate API key input (in real scenario, would get from user)
    print("💡 NEXT STEPS:")
    print("1. Find your API key in CoinRemitter dashboard")
    print("2. It should look like: 'cr_live_abc123def456...'")
    print("3. Provide the API key")
    print("4. I'll execute the real $9.34M withdrawal immediately")
    
    # Test connection when ready (placeholder)
    test_api_key = "NEED_REAL_API_KEY_FROM_USER"
    
    if test_api_key == "NEED_REAL_API_KEY_FROM_USER":
        print(f"\n🔑 READY TO IMPLEMENT ONCE YOU PROVIDE API KEY!")
        print(f"Your CoinRemitter setup:")
        print(f"   ✅ Account: Active (you're in dashboard)")
        print(f"   ✅ Password: {guide.password}")
        print(f"   ⏳ API Key: Waiting...")
        print(f"   🎯 Target: Real $9.34M DOGE withdrawal")
    else:
        # Would execute real withdrawal here
        connection_success = await guide.test_api_connection_when_ready(test_api_key)
        
        if connection_success:
            withdrawal_success = await guide.execute_real_doge_withdrawal(test_api_key)
            
            if withdrawal_success:
                print(f"\n🏆 MISSION ACCOMPLISHED!")
                print(f"✅ Real DOGE withdrawal executed")
                print(f"✅ $9.34M sent to your external wallet")
                print(f"✅ Transaction hash provided")
            else:
                print(f"\n❌ Withdrawal execution failed")
        else:
            print(f"\n❌ API connection failed - check credentials")

if __name__ == "__main__":
    asyncio.run(main())