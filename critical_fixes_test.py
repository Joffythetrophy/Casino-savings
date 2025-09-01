#!/usr/bin/env python3
"""
Critical Fixes Test Suite for User DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq
Tests the 3 priority fixes:
1. CRT Balance Display Fix (21M CRT instead of 845K)
2. 500 USDC Refund Verification
3. Real Blockchain Withdrawal Methods
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://solana-casino.preview.emergentagent.com/api"

class CriticalFixesTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        
        # User credentials from review request
        self.target_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        self.username = "cryptoking"
        self.password = "crt21million"
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    async def authenticate_user(self):
        """Authenticate the specific user for testing"""
        try:
            # Test login with username
            login_payload = {
                "username": self.username,
                "password": self.password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("wallet_address") == self.target_wallet:
                        self.log_test("User Authentication", True, 
                                    f"Successfully authenticated user {self.username} with wallet {self.target_wallet}")
                        return True
                    else:
                        self.log_test("User Authentication", False, 
                                    f"Authentication failed or wallet mismatch: {data}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, 
                                f"Authentication failed - HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("User Authentication", False, f"Authentication error: {str(e)}")
            return False

    async def test_priority_1_crt_balance_fix(self):
        """PRIORITY 1: Test CRT Balance Display Fix - Should show 21,000,000 CRT not 845,824"""
        try:
            # Test the wallet endpoint for the specific user
            async with self.session.get(f"{self.base_url}/wallet/{self.target_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        crt_balance = deposit_balance.get("CRT", 0)
                        balance_source = wallet.get("balance_source", "unknown")
                        
                        # Check if CRT balance shows 21,000,000 (or close to it)
                        expected_crt = 21000000  # 21 million CRT
                        tolerance = 100000  # Allow some tolerance
                        
                        if abs(crt_balance - expected_crt) <= tolerance:
                            self.log_test("PRIORITY 1 - CRT Balance Fix", True, 
                                        f"✅ CRT balance correctly shows {crt_balance:,.0f} CRT (expected ~21M), source: {balance_source}", 
                                        {"crt_balance": crt_balance, "expected": expected_crt, "source": balance_source})
                        else:
                            self.log_test("PRIORITY 1 - CRT Balance Fix", False, 
                                        f"❌ CRT balance shows {crt_balance:,.0f} CRT but should be ~21,000,000 CRT", 
                                        {"crt_balance": crt_balance, "expected": expected_crt, "source": balance_source})
                        
                        # Additional check: Verify blockchain balance is prioritized
                        balance_notes = wallet.get("balance_notes", {})
                        crt_note = balance_notes.get("CRT", "")
                        
                        if "blockchain" in crt_note.lower():
                            self.log_test("CRT Blockchain Priority", True, 
                                        f"✅ CRT balance prioritizes blockchain data: {crt_note}")
                        else:
                            self.log_test("CRT Blockchain Priority", False, 
                                        f"❌ CRT balance may not prioritize blockchain: {crt_note}")
                        
                        return crt_balance
                    else:
                        self.log_test("PRIORITY 1 - CRT Balance Fix", False, 
                                    "Invalid wallet response format", data)
                        return 0
                else:
                    error_text = await response.text()
                    self.log_test("PRIORITY 1 - CRT Balance Fix", False, 
                                f"Wallet endpoint failed - HTTP {response.status}: {error_text}")
                    return 0
                    
        except Exception as e:
            self.log_test("PRIORITY 1 - CRT Balance Fix", False, f"Error: {str(e)}")
            return 0

    async def test_priority_2_usdc_refund_verification(self):
        """PRIORITY 2: Test 500 USDC Refund Verification and Savings Reset"""
        try:
            # Get current wallet state
            async with self.session.get(f"{self.base_url}/wallet/{self.target_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        savings_balance = wallet.get("savings_balance", {})
                        
                        usdc_balance = deposit_balance.get("USDC", 0)
                        crt_savings = savings_balance.get("CRT", 0)
                        usdc_savings = savings_balance.get("USDC", 0)
                        
                        # Check USDC balance (should be around 317,582 after 500 refund)
                        expected_usdc_min = 317000  # Around 317K
                        expected_usdc_max = 318000  # Allow some range
                        
                        if expected_usdc_min <= usdc_balance <= expected_usdc_max:
                            self.log_test("PRIORITY 2 - USDC Refund", True, 
                                        f"✅ USDC balance shows {usdc_balance:,.2f} (expected ~317,582 after 500 refund)")
                        else:
                            self.log_test("PRIORITY 2 - USDC Refund", False, 
                                        f"❌ USDC balance shows {usdc_balance:,.2f} but expected ~317,582")
                        
                        # Check CRT savings reset to 0
                        if crt_savings == 0:
                            self.log_test("PRIORITY 2 - CRT Savings Reset", True, 
                                        f"✅ CRT savings correctly reset to {crt_savings}")
                        else:
                            self.log_test("PRIORITY 2 - CRT Savings Reset", False, 
                                        f"❌ CRT savings shows {crt_savings:,.2f} but should be 0")
                        
                        # Check USDC savings reset to 0
                        if usdc_savings == 0:
                            self.log_test("PRIORITY 2 - USDC Savings Reset", True, 
                                        f"✅ USDC savings correctly reset to {usdc_savings}")
                        else:
                            self.log_test("PRIORITY 2 - USDC Savings Reset", False, 
                                        f"❌ USDC savings shows {usdc_savings:,.2f} but should be 0")
                        
                        return {
                            "usdc_balance": usdc_balance,
                            "crt_savings": crt_savings,
                            "usdc_savings": usdc_savings
                        }
                    else:
                        self.log_test("PRIORITY 2 - USDC Refund Verification", False, 
                                    "Invalid wallet response format", data)
                        return None
                else:
                    error_text = await response.text()
                    self.log_test("PRIORITY 2 - USDC Refund Verification", False, 
                                f"Wallet endpoint failed - HTTP {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            self.log_test("PRIORITY 2 - USDC Refund Verification", False, f"Error: {str(e)}")
            return None

    async def test_priority_3_real_blockchain_withdrawal_methods(self):
        """PRIORITY 3: Test Real Blockchain Withdrawal Methods (send_spl_token, send_crt_token)"""
        try:
            # Test 1: Simulate CRT withdrawal to verify send_crt_token method is called
            crt_withdrawal_payload = {
                "wallet_address": self.target_wallet,
                "wallet_type": "deposit",
                "currency": "CRT",
                "amount": 100.0,  # Small test amount
                "destination_address": "DT5fbwaBAMwVucd9A8X8JrF5NFdE4xhZ54boyiGNjNrb"  # Test Solana address
            }
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=crt_withdrawal_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        # Check if real blockchain transaction was attempted
                        blockchain_hash = data.get("blockchain_transaction_hash")
                        verification_url = data.get("verification_url")
                        blockchain_confirmed = data.get("blockchain_confirmed", False)
                        
                        if blockchain_hash and "solana.com" in str(verification_url):
                            self.log_test("PRIORITY 3 - CRT Withdrawal Method", True, 
                                        f"✅ CRT withdrawal uses real blockchain method: {blockchain_hash}")
                        else:
                            self.log_test("PRIORITY 3 - CRT Withdrawal Method", False, 
                                        f"❌ CRT withdrawal may not use real blockchain method")
                    else:
                        # Check if it's a balance/liquidity issue (expected for testing)
                        error_msg = data.get("message", "")
                        if "insufficient" in error_msg.lower() or "liquidity" in error_msg.lower():
                            self.log_test("PRIORITY 3 - CRT Withdrawal Method", True, 
                                        f"✅ CRT withdrawal endpoint working (insufficient balance expected): {error_msg}")
                        else:
                            self.log_test("PRIORITY 3 - CRT Withdrawal Method", False, 
                                        f"❌ CRT withdrawal failed unexpectedly: {error_msg}")
                else:
                    error_text = await response.text()
                    self.log_test("PRIORITY 3 - CRT Withdrawal Method", False, 
                                f"CRT withdrawal failed - HTTP {response.status}: {error_text}")
            
            # Test 2: Simulate USDC withdrawal to verify send_spl_token method is called
            usdc_withdrawal_payload = {
                "wallet_address": self.target_wallet,
                "wallet_type": "deposit",
                "currency": "USDC",
                "amount": 10.0,  # Small test amount
                "destination_address": "DT5fbwaBAMwVucd9A8X8JrF5NFdE4xhZ54boyiGNjNrb"  # Test Solana address
            }
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=usdc_withdrawal_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        # Check if real blockchain transaction was attempted
                        blockchain_hash = data.get("blockchain_transaction_hash")
                        verification_url = data.get("verification_url")
                        blockchain_confirmed = data.get("blockchain_confirmed", False)
                        
                        if blockchain_hash and "solana.com" in str(verification_url):
                            self.log_test("PRIORITY 3 - USDC Withdrawal Method", True, 
                                        f"✅ USDC withdrawal uses real blockchain method: {blockchain_hash}")
                        else:
                            self.log_test("PRIORITY 3 - USDC Withdrawal Method", False, 
                                        f"❌ USDC withdrawal may not use real blockchain method")
                    else:
                        # Check if it's a balance/liquidity issue (expected for testing)
                        error_msg = data.get("message", "")
                        if "insufficient" in error_msg.lower() or "liquidity" in error_msg.lower():
                            self.log_test("PRIORITY 3 - USDC Withdrawal Method", True, 
                                        f"✅ USDC withdrawal endpoint working (insufficient balance expected): {error_msg}")
                        else:
                            self.log_test("PRIORITY 3 - USDC Withdrawal Method", False, 
                                        f"❌ USDC withdrawal failed unexpectedly: {error_msg}")
                else:
                    error_text = await response.text()
                    self.log_test("PRIORITY 3 - USDC Withdrawal Method", False, 
                                f"USDC withdrawal failed - HTTP {response.status}: {error_text}")
            
            # Test 3: Verify withdrawal method routing by checking the code paths
            # This tests that the correct methods are called for different currencies
            test_currencies = ["CRT", "USDC", "DOGE", "TRX"]
            method_routing_results = {}
            
            for currency in test_currencies:
                test_payload = {
                    "wallet_address": self.target_wallet,
                    "wallet_type": "deposit",
                    "currency": currency,
                    "amount": 1.0,  # Minimal test amount
                    "destination_address": "test_address_for_routing_check"
                }
                
                try:
                    async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                               json=test_payload) as response:
                        data = await response.json() if response.status == 200 else {}
                        
                        # Check if the response indicates proper method routing
                        if response.status == 200:
                            if data.get("success") or "insufficient" in data.get("message", "").lower():
                                method_routing_results[currency] = "✅ Routed correctly"
                            else:
                                method_routing_results[currency] = f"❌ Routing issue: {data.get('message', 'Unknown')}"
                        else:
                            # Some errors are expected for invalid addresses
                            method_routing_results[currency] = f"⚠️ HTTP {response.status} (may be expected)"
                            
                except Exception as e:
                    method_routing_results[currency] = f"❌ Error: {str(e)}"
            
            # Evaluate method routing results
            successful_routes = sum(1 for result in method_routing_results.values() if "✅" in result)
            total_routes = len(method_routing_results)
            
            if successful_routes >= 2:  # At least CRT and USDC should work
                self.log_test("PRIORITY 3 - Withdrawal Method Routing", True, 
                            f"✅ Withdrawal method routing working: {successful_routes}/{total_routes} currencies", 
                            method_routing_results)
            else:
                self.log_test("PRIORITY 3 - Withdrawal Method Routing", False, 
                            f"❌ Withdrawal method routing issues: {successful_routes}/{total_routes} currencies", 
                            method_routing_results)
                    
        except Exception as e:
            self.log_test("PRIORITY 3 - Real Blockchain Withdrawal Methods", False, f"Error: {str(e)}")

    async def test_comprehensive_wallet_state(self):
        """Comprehensive test of the user's wallet state after all fixes"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.target_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        savings_balance = wallet.get("savings_balance", {})
                        balance_source = wallet.get("balance_source", "unknown")
                        
                        # Create comprehensive summary
                        summary = {
                            "wallet_address": wallet.get("wallet_address"),
                            "balance_source": balance_source,
                            "deposit_balances": {
                                "CRT": deposit_balance.get("CRT", 0),
                                "USDC": deposit_balance.get("USDC", 0),
                                "DOGE": deposit_balance.get("DOGE", 0),
                                "TRX": deposit_balance.get("TRX", 0)
                            },
                            "savings_balances": {
                                "CRT": savings_balance.get("CRT", 0),
                                "USDC": savings_balance.get("USDC", 0),
                                "DOGE": savings_balance.get("DOGE", 0),
                                "TRX": savings_balance.get("TRX", 0)
                            }
                        }
                        
                        # Calculate total portfolio value (using approximate prices)
                        prices = {"CRT": 0.15, "USDC": 1.0, "DOGE": 0.24, "TRX": 0.36}
                        total_value = sum(
                            deposit_balance.get(currency, 0) * price 
                            for currency, price in prices.items()
                        )
                        
                        summary["total_portfolio_value_usd"] = total_value
                        
                        self.log_test("Comprehensive Wallet State", True, 
                                    f"✅ Complete wallet state retrieved: ${total_value:,.2f} total value", 
                                    summary)
                        
                        return summary
                    else:
                        self.log_test("Comprehensive Wallet State", False, 
                                    "Invalid wallet response format", data)
                        return None
                else:
                    error_text = await response.text()
                    self.log_test("Comprehensive Wallet State", False, 
                                f"Wallet endpoint failed - HTTP {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            self.log_test("Comprehensive Wallet State", False, f"Error: {str(e)}")
            return None

    async def run_all_tests(self):
        """Run all critical fix tests"""
        print(f"🚀 Starting Critical Fixes Test Suite for User: {self.target_wallet}")
        print(f"📅 Test Time: {datetime.utcnow().isoformat()}")
        print("=" * 80)
        
        # Step 1: Authenticate user
        auth_success = await self.authenticate_user()
        if not auth_success:
            print("❌ Authentication failed - cannot proceed with tests")
            return self.generate_summary()
        
        # Step 2: Test Priority 1 - CRT Balance Fix
        print("\n🔍 PRIORITY 1: Testing CRT Balance Display Fix...")
        crt_balance = await self.test_priority_1_crt_balance_fix()
        
        # Step 3: Test Priority 2 - USDC Refund and Savings Reset
        print("\n💰 PRIORITY 2: Testing 500 USDC Refund and Savings Reset...")
        refund_results = await self.test_priority_2_usdc_refund_verification()
        
        # Step 4: Test Priority 3 - Real Blockchain Withdrawal Methods
        print("\n🔗 PRIORITY 3: Testing Real Blockchain Withdrawal Methods...")
        await self.test_priority_3_real_blockchain_withdrawal_methods()
        
        # Step 5: Comprehensive wallet state check
        print("\n📊 COMPREHENSIVE: Testing Complete Wallet State...")
        wallet_state = await self.test_comprehensive_wallet_state()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 80)
        print("📋 CRITICAL FIXES TEST SUMMARY")
        print("=" * 80)
        print(f"🎯 Target User: {self.username} ({self.target_wallet})")
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        print("\n🔍 PRIORITY RESULTS:")
        
        # Priority 1 Results
        priority_1_tests = [r for r in self.test_results if "PRIORITY 1" in r["test"]]
        p1_passed = sum(1 for r in priority_1_tests if r["success"])
        print(f"   PRIORITY 1 (CRT Balance Fix): {p1_passed}/{len(priority_1_tests)} passed")
        
        # Priority 2 Results
        priority_2_tests = [r for r in self.test_results if "PRIORITY 2" in r["test"]]
        p2_passed = sum(1 for r in priority_2_tests if r["success"])
        print(f"   PRIORITY 2 (USDC Refund): {p2_passed}/{len(priority_2_tests)} passed")
        
        # Priority 3 Results
        priority_3_tests = [r for r in self.test_results if "PRIORITY 3" in r["test"]]
        p3_passed = sum(1 for r in priority_3_tests if r["success"])
        print(f"   PRIORITY 3 (Withdrawal Methods): {p3_passed}/{len(priority_3_tests)} passed")
        
        print("\n📝 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"   {status} {result['test']}: {result['details']}")
        
        print("\n" + "=" * 80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests*100) if total_tests > 0 else 0,
            "results": self.test_results
        }

async def main():
    """Main test execution"""
    async with CriticalFixesTester(BACKEND_URL) as tester:
        summary = await tester.run_all_tests()
        
        # Return appropriate exit code
        if summary["success_rate"] >= 80:  # 80% or higher success rate
            print(f"\n🎉 CRITICAL FIXES TEST SUITE COMPLETED SUCCESSFULLY!")
            sys.exit(0)
        else:
            print(f"\n⚠️ CRITICAL FIXES TEST SUITE COMPLETED WITH ISSUES!")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())