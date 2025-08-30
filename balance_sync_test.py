#!/usr/bin/env python3
"""
Real Balance Synchronization System Testing
Testing the new /api/wallet/sync-real-balances endpoint for user cryptoking
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = "https://crypto-treasury-app.preview.emergentagent.com/api"
TEST_USER = {
    "username": "cryptoking",
    "password": "crt21million",
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

class BalanceSyncTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def authenticate_user(self):
        """Authenticate user cryptoking"""
        try:
            login_data = {
                "identifier": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                result = await response.json()
                
                if result.get("success"):
                    self.auth_token = result.get("token")
                    print(f"✅ Authentication successful for user: {result.get('username')}")
                    print(f"   Wallet: {result.get('wallet_address')}")
                    return True
                else:
                    print(f"❌ Authentication failed: {result.get('message', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    async def get_user_balances_before_sync(self):
        """Get user balances before synchronization"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            async with self.session.get(
                f"{BACKEND_URL}/wallet/{TEST_USER['wallet_address']}", 
                headers=headers
            ) as response:
                result = await response.json()
                
                if result.get("success"):
                    wallet_data = result.get("wallet", {})
                    print(f"\n📊 BALANCES BEFORE SYNC:")
                    print(f"   Deposit Balance: {wallet_data.get('deposit_balance', {})}")
                    print(f"   Winnings Balance: {wallet_data.get('winnings_balance', {})}")
                    print(f"   Savings Balance: {wallet_data.get('savings_balance', {})}")
                    print(f"   Balance Source: {wallet_data.get('balance_source', 'unknown')}")
                    
                    return {
                        "success": True,
                        "balances": wallet_data,
                        "source": wallet_data.get('balance_source', 'unknown')
                    }
                else:
                    print(f"❌ Failed to get balances: {result.get('message', 'Unknown error')}")
                    return {"success": False, "error": result.get('message')}
                    
        except Exception as e:
            print(f"❌ Error getting balances: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_balance_sync_endpoint(self):
        """Test the /api/wallet/sync-real-balances endpoint"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            sync_data = {
                "wallet_address": TEST_USER["wallet_address"]
            }
            
            print(f"\n🔄 TESTING BALANCE SYNCHRONIZATION...")
            print(f"   Endpoint: {BACKEND_URL}/wallet/sync-real-balances")
            print(f"   Wallet: {TEST_USER['wallet_address']}")
            
            async with self.session.post(
                f"{BACKEND_URL}/wallet/sync-real-balances", 
                json=sync_data,
                headers=headers
            ) as response:
                result = await response.json()
                
                print(f"\n📋 SYNC RESPONSE:")
                print(f"   Status Code: {response.status}")
                print(f"   Success: {result.get('success', False)}")
                print(f"   Message: {result.get('message', 'No message')}")
                
                if result.get("success"):
                    print(f"   Synchronized Balances: {result.get('synchronized_balances', {})}")
                    print(f"   Blockchain Balances: {result.get('blockchain_balances', {})}")
                    print(f"   Balance Source: {result.get('balance_source', 'unknown')}")
                    print(f"   Sync Timestamp: {result.get('sync_timestamp', 'unknown')}")
                    
                    # Verify balance source is correct
                    if result.get('balance_source') == "REAL_BLOCKCHAIN_SYNCHRONIZED":
                        print(f"✅ Balance source correctly set to 'REAL_BLOCKCHAIN_SYNCHRONIZED'")
                        self.test_results.append(("Balance Source Verification", True, "Correctly set to REAL_BLOCKCHAIN_SYNCHRONIZED"))
                    else:
                        print(f"❌ Balance source incorrect: {result.get('balance_source')}")
                        self.test_results.append(("Balance Source Verification", False, f"Expected REAL_BLOCKCHAIN_SYNCHRONIZED, got {result.get('balance_source')}"))
                    
                    return {
                        "success": True,
                        "sync_result": result,
                        "blockchain_balances": result.get('blockchain_balances', {}),
                        "balance_source": result.get('balance_source')
                    }
                else:
                    error_msg = result.get('message', 'Unknown sync error')
                    print(f"❌ Sync failed: {error_msg}")
                    self.test_results.append(("Balance Sync Execution", False, error_msg))
                    return {"success": False, "error": error_msg}
                    
        except Exception as e:
            print(f"❌ Sync endpoint error: {str(e)}")
            self.test_results.append(("Balance Sync Execution", False, str(e)))
            return {"success": False, "error": str(e)}
    
    async def get_user_balances_after_sync(self):
        """Get user balances after synchronization"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            async with self.session.get(
                f"{BACKEND_URL}/wallet/{TEST_USER['wallet_address']}", 
                headers=headers
            ) as response:
                result = await response.json()
                
                if result.get("success"):
                    wallet_data = result.get("wallet", {})
                    print(f"\n📊 BALANCES AFTER SYNC:")
                    print(f"   Deposit Balance: {wallet_data.get('deposit_balance', {})}")
                    print(f"   Winnings Balance: {wallet_data.get('winnings_balance', {})}")
                    print(f"   Savings Balance: {wallet_data.get('savings_balance', {})}")
                    print(f"   Balance Source: {wallet_data.get('balance_source', 'unknown')}")
                    print(f"   Last Blockchain Sync: {wallet_data.get('last_blockchain_sync', 'never')}")
                    
                    return {
                        "success": True,
                        "balances": wallet_data,
                        "source": wallet_data.get('balance_source', 'unknown')
                    }
                else:
                    print(f"❌ Failed to get post-sync balances: {result.get('message', 'Unknown error')}")
                    return {"success": False, "error": result.get('message')}
                    
        except Exception as e:
            print(f"❌ Error getting post-sync balances: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_blockchain_integration(self):
        """Test blockchain integration endpoints"""
        try:
            print(f"\n🔗 TESTING BLOCKCHAIN INTEGRATION...")
            
            # Test individual currency balance endpoints
            currencies = ["CRT", "USDC", "SOL"]
            blockchain_results = {}
            
            for currency in currencies:
                try:
                    async with self.session.get(
                        f"{BACKEND_URL}/wallet/balance/{currency}?wallet_address={TEST_USER['wallet_address']}"
                    ) as response:
                        result = await response.json()
                        
                        blockchain_results[currency] = result
                        print(f"   {currency} Balance: {result.get('balance', 0)} (Source: {result.get('source', 'unknown')})")
                        
                        if result.get("success") and result.get("source") in ["solana_rpc", "solana_blockchain"]:
                            self.test_results.append((f"{currency} Blockchain Integration", True, f"Successfully connected to {result.get('source')}"))
                        else:
                            self.test_results.append((f"{currency} Blockchain Integration", False, f"Failed or wrong source: {result.get('source')}"))
                            
                except Exception as e:
                    print(f"   ❌ {currency} balance error: {str(e)}")
                    blockchain_results[currency] = {"success": False, "error": str(e)}
                    self.test_results.append((f"{currency} Blockchain Integration", False, str(e)))
            
            return blockchain_results
            
        except Exception as e:
            print(f"❌ Blockchain integration test error: {str(e)}")
            return {}
    
    async def test_data_integrity(self, before_balances, after_balances):
        """Test that gaming/winnings balances are preserved during sync"""
        try:
            print(f"\n🔒 TESTING DATA INTEGRITY...")
            
            if not before_balances.get("success") or not after_balances.get("success"):
                print(f"❌ Cannot test data integrity - missing balance data")
                self.test_results.append(("Data Integrity", False, "Missing balance data"))
                return False
            
            before_data = before_balances.get("balances", {})
            after_data = after_balances.get("balances", {})
            
            # Check winnings balance preservation
            before_winnings = before_data.get("winnings_balance", {})
            after_winnings = after_data.get("winnings_balance", {})
            
            winnings_preserved = True
            for currency in before_winnings:
                if before_winnings.get(currency, 0) != after_winnings.get(currency, 0):
                    print(f"❌ Winnings balance changed for {currency}: {before_winnings.get(currency)} → {after_winnings.get(currency)}")
                    winnings_preserved = False
            
            # Check savings balance preservation
            before_savings = before_data.get("savings_balance", {})
            after_savings = after_data.get("savings_balance", {})
            
            savings_preserved = True
            for currency in before_savings:
                if before_savings.get(currency, 0) != after_savings.get(currency, 0):
                    print(f"❌ Savings balance changed for {currency}: {before_savings.get(currency)} → {after_savings.get(currency)}")
                    savings_preserved = False
            
            if winnings_preserved and savings_preserved:
                print(f"✅ Gaming/winnings balances preserved during sync")
                self.test_results.append(("Data Integrity", True, "Gaming/winnings balances preserved"))
                return True
            else:
                print(f"❌ Some balances were not preserved during sync")
                self.test_results.append(("Data Integrity", False, "Some balances changed during sync"))
                return False
                
        except Exception as e:
            print(f"❌ Data integrity test error: {str(e)}")
            self.test_results.append(("Data Integrity", False, str(e)))
            return False
    
    async def test_error_handling(self):
        """Test error handling with invalid data"""
        try:
            print(f"\n⚠️ TESTING ERROR HANDLING...")
            
            # Test with invalid wallet address
            invalid_sync_data = {
                "wallet_address": "InvalidWalletAddress123"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/wallet/sync-real-balances", 
                json=invalid_sync_data
            ) as response:
                result = await response.json()
                
                if response.status >= 400 and not result.get("success"):
                    print(f"✅ Properly handles invalid wallet address (Status: {response.status})")
                    self.test_results.append(("Error Handling - Invalid Wallet", True, f"Properly rejected with status {response.status}"))
                else:
                    print(f"❌ Should reject invalid wallet address")
                    self.test_results.append(("Error Handling - Invalid Wallet", False, "Did not reject invalid wallet"))
            
            # Test with missing wallet address
            empty_sync_data = {}
            
            async with self.session.post(
                f"{BACKEND_URL}/wallet/sync-real-balances", 
                json=empty_sync_data
            ) as response:
                result = await response.json()
                
                if response.status >= 400 and not result.get("success"):
                    print(f"✅ Properly handles missing wallet address (Status: {response.status})")
                    self.test_results.append(("Error Handling - Missing Wallet", True, f"Properly rejected with status {response.status}"))
                else:
                    print(f"❌ Should reject missing wallet address")
                    self.test_results.append(("Error Handling - Missing Wallet", False, "Did not reject missing wallet"))
            
            return True
            
        except Exception as e:
            print(f"❌ Error handling test error: {str(e)}")
            self.test_results.append(("Error Handling", False, str(e)))
            return False
    
    async def run_comprehensive_test(self):
        """Run comprehensive balance synchronization test"""
        print(f"🚀 STARTING REAL BALANCE SYNCHRONIZATION TESTING")
        print(f"=" * 60)
        print(f"Target User: {TEST_USER['username']}")
        print(f"Wallet Address: {TEST_USER['wallet_address']}")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"=" * 60)
        
        try:
            await self.setup_session()
            
            # Step 1: Authenticate user
            print(f"\n1️⃣ AUTHENTICATING USER...")
            auth_success = await self.authenticate_user()
            if not auth_success:
                self.test_results.append(("User Authentication", False, "Failed to authenticate cryptoking"))
                return
            else:
                self.test_results.append(("User Authentication", True, "Successfully authenticated cryptoking"))
            
            # Step 2: Get balances before sync
            print(f"\n2️⃣ GETTING BALANCES BEFORE SYNC...")
            before_balances = await self.get_user_balances_before_sync()
            
            # Step 3: Test blockchain integration
            print(f"\n3️⃣ TESTING BLOCKCHAIN INTEGRATION...")
            blockchain_results = await self.test_blockchain_integration()
            
            # Step 4: Execute balance synchronization
            print(f"\n4️⃣ EXECUTING BALANCE SYNCHRONIZATION...")
            sync_result = await self.test_balance_sync_endpoint()
            
            if sync_result.get("success"):
                self.test_results.append(("Balance Sync Execution", True, "Successfully executed balance sync"))
            else:
                self.test_results.append(("Balance Sync Execution", False, sync_result.get("error", "Unknown sync error")))
            
            # Step 5: Get balances after sync
            print(f"\n5️⃣ GETTING BALANCES AFTER SYNC...")
            after_balances = await self.get_user_balances_after_sync()
            
            # Step 6: Test data integrity
            print(f"\n6️⃣ TESTING DATA INTEGRITY...")
            await self.test_data_integrity(before_balances, after_balances)
            
            # Step 7: Test error handling
            print(f"\n7️⃣ TESTING ERROR HANDLING...")
            await self.test_error_handling()
            
            # Final results
            await self.print_final_results()
            
        except Exception as e:
            print(f"❌ Test execution error: {str(e)}")
            self.test_results.append(("Test Execution", False, str(e)))
        
        finally:
            await self.cleanup_session()
    
    async def print_final_results(self):
        """Print comprehensive test results"""
        print(f"\n" + "=" * 60)
        print(f"🎯 FINAL TEST RESULTS")
        print(f"=" * 60)
        
        passed_tests = 0
        total_tests = len(self.test_results)
        
        for test_name, success, details in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}")
            if not success or details:
                print(f"     Details: {details}")
            if success:
                passed_tests += 1
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        # Critical assessment
        critical_tests = [
            "User Authentication",
            "Balance Sync Execution", 
            "Balance Source Verification",
            "Data Integrity"
        ]
        
        critical_passed = sum(1 for test_name, success, _ in self.test_results 
                            if test_name in critical_tests and success)
        critical_total = len([t for t, _, _ in self.test_results if t in critical_tests])
        
        print(f"\n🎯 CRITICAL TESTS:")
        print(f"   Critical Passed: {critical_passed}/{critical_total}")
        
        if critical_passed == critical_total:
            print(f"✅ ALL CRITICAL TESTS PASSED - Balance sync system is working!")
        else:
            print(f"❌ CRITICAL TESTS FAILED - Balance sync system needs fixes!")
        
        print(f"=" * 60)

async def main():
    """Main test execution"""
    tester = BalanceSyncTester()
    await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())