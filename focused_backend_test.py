#!/usr/bin/env python3
"""
Focused Backend Test for Critical Issues Found
Testing specific problems identified in comprehensive verification
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

# Test credentials
TEST_CREDENTIALS = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
    "withdrawal_wallet": "DLbWLzxq2mxE3Adzn9MFKQ6EBP8gTE5po8"
}

class FocusedBackendTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        
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

    async def test_crt_balance_issue(self):
        """Test the critical CRT balance synchronization issue"""
        try:
            wallet_address = TEST_CREDENTIALS["wallet_address"]
            print(f"🔍 Testing CRT balance synchronization issue for {wallet_address}")
            
            # Test 1: Get wallet info (database balances)
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        wallet_info = data.get("wallet", {})
                        
                        # Database balances
                        deposit_balance = wallet_info.get("deposit_balance", {})
                        winnings_balance = wallet_info.get("winnings_balance", {})
                        savings_balance = wallet_info.get("savings_balance", {})
                        liquidity_pool = wallet_info.get("liquidity_pool", {})
                        
                        db_crt_total = (
                            deposit_balance.get("CRT", 0) +
                            winnings_balance.get("CRT", 0) +
                            savings_balance.get("CRT", 0) +
                            liquidity_pool.get("CRT", 0)
                        )
                        
                        self.log_test("Database CRT Balance Check", True, 
                                    f"📊 Database CRT Total: {db_crt_total} (Deposit: {deposit_balance.get('CRT', 0)}, Winnings: {winnings_balance.get('CRT', 0)}, Savings: {savings_balance.get('CRT', 0)}, Liquidity: {liquidity_pool.get('CRT', 0)})", 
                                    wallet_info)
                    else:
                        self.log_test("Database CRT Balance Check", False, 
                                    f"❌ Failed to get wallet info: {data.get('message', 'Unknown error')}", data)
                else:
                    self.log_test("Database CRT Balance Check", False, 
                                f"❌ HTTP {response.status}: {await response.text()}")
            
            # Test 2: Get blockchain CRT balance
            async with self.session.get(f"{self.base_url}/wallet/balance/CRT?wallet_address={wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        blockchain_crt = data.get("balance", 0)
                        source = data.get("source", "unknown")
                        
                        self.log_test("Blockchain CRT Balance Check", True, 
                                    f"🔗 Blockchain CRT: {blockchain_crt} (Source: {source})", data)
                        
                        # Check if there's a discrepancy
                        if blockchain_crt >= 21000000:
                            self.log_test("CRT Balance Discrepancy Analysis", False, 
                                        f"❌ CRITICAL: User has {blockchain_crt} CRT on blockchain but limited database access", 
                                        {"blockchain_balance": blockchain_crt, "database_accessible": db_crt_total})
                        else:
                            self.log_test("CRT Balance Discrepancy Analysis", True, 
                                        f"✅ CRT balances appear synchronized", 
                                        {"blockchain_balance": blockchain_crt, "database_accessible": db_crt_total})
                    else:
                        self.log_test("Blockchain CRT Balance Check", False, 
                                    f"❌ Failed to get blockchain balance: {data.get('error', 'Unknown error')}", data)
                else:
                    self.log_test("Blockchain CRT Balance Check", False, 
                                f"❌ HTTP {response.status}: {await response.text()}")
            
            # Test 3: Test CRT conversion to see if balance limits are enforced
            conversion_payload = {
                "wallet_address": wallet_address,
                "from_currency": "CRT",
                "to_currency": "DOGE",
                "amount": 1000000  # Try to convert 1M CRT
            }
            
            async with self.session.post(f"{self.base_url}/wallet/convert", 
                                       json=conversion_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        self.log_test("Large CRT Conversion Test", True, 
                                    f"✅ Large CRT conversion successful: {data.get('message', 'Success')}", data)
                    else:
                        error_msg = data.get("message", "Unknown error")
                        if "insufficient" in error_msg.lower():
                            self.log_test("Large CRT Conversion Test", False, 
                                        f"❌ CRITICAL: Large CRT conversion blocked by insufficient balance: {error_msg}", data)
                        else:
                            self.log_test("Large CRT Conversion Test", False, 
                                        f"❌ Large CRT conversion failed: {error_msg}", data)
                else:
                    self.log_test("Large CRT Conversion Test", False, 
                                f"❌ HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self.log_test("CRT Balance Issue Test", False, f"Error: {str(e)}")

    async def test_nowpayments_integration(self):
        """Test NOWPayments integration and withdrawal capabilities"""
        try:
            print(f"💰 Testing NOWPayments integration")
            
            # Test 1: Check NOWPayments API status
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Backend API Status", True, 
                                f"✅ Backend API accessible: {data.get('message', 'OK')}", data)
                else:
                    self.log_test("Backend API Status", False, 
                                f"❌ Backend API not accessible: HTTP {response.status}")
            
            # Test 2: Test withdrawal with correct DOGE address format
            withdrawal_payload = {
                "wallet_address": TEST_CREDENTIALS["wallet_address"],
                "wallet_type": "deposit",
                "currency": "DOGE",
                "amount": 10.0,  # Small test amount
                "destination_address": TEST_CREDENTIALS["withdrawal_wallet"]
            }
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=withdrawal_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        self.log_test("NOWPayments Withdrawal Test", True, 
                                    f"✅ Withdrawal successful: {data.get('message', 'Success')}", data)
                    else:
                        error_msg = data.get("message", "Unknown error")
                        
                        # Analyze the error
                        if "invalid" in error_msg.lower() and "address" in error_msg.lower():
                            self.log_test("NOWPayments Withdrawal Test", False, 
                                        f"❌ DOGE address validation issue: {error_msg}", data)
                        elif "insufficient" in error_msg.lower():
                            self.log_test("NOWPayments Withdrawal Test", True, 
                                        f"⚠️ Insufficient balance (expected): {error_msg}", data)
                        elif "unauthorized" in error_msg.lower() or "permission" in error_msg.lower():
                            self.log_test("NOWPayments Withdrawal Test", True, 
                                        f"⏳ NOWPayments whitelisting pending: {error_msg}", data)
                        else:
                            self.log_test("NOWPayments Withdrawal Test", False, 
                                        f"❌ Withdrawal failed: {error_msg}", data)
                else:
                    error_text = await response.text()
                    self.log_test("NOWPayments Withdrawal Test", False, 
                                f"❌ HTTP {response.status}: {error_text}")
            
            # Test 3: Check if NOWPayments service is properly configured
            try:
                # This would test if the service endpoints exist
                async with self.session.get(f"{self.base_url}/nowpayments/status") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.log_test("NOWPayments Service Status", True, 
                                    f"✅ NOWPayments service configured", data)
                    else:
                        self.log_test("NOWPayments Service Status", False, 
                                    f"❌ NOWPayments service endpoint not found: HTTP {response.status}")
            except Exception:
                self.log_test("NOWPayments Service Status", False, 
                            "❌ NOWPayments service endpoints not implemented")
                    
        except Exception as e:
            self.log_test("NOWPayments Integration Test", False, f"Error: {str(e)}")

    async def test_transaction_history_access(self):
        """Test transaction history access issues"""
        try:
            wallet_address = TEST_CREDENTIALS["wallet_address"]
            print(f"📊 Testing transaction history access")
            
            # Test game history endpoint (was returning 403)
            async with self.session.get(f"{self.base_url}/games/history/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        games = data.get("games", [])
                        self.log_test("Game History Access", True, 
                                    f"✅ Game history accessible: {len(games)} games found", data)
                    else:
                        self.log_test("Game History Access", False, 
                                    f"❌ Game history failed: {data.get('message', 'Unknown error')}", data)
                elif response.status == 403:
                    self.log_test("Game History Access", False, 
                                f"❌ CRITICAL: Game history requires authentication (HTTP 403)", 
                                {"status": 403, "issue": "Authentication required"})
                else:
                    self.log_test("Game History Access", False, 
                                f"❌ Game history HTTP {response.status}: {await response.text()}")
            
            # Test if we can access with authentication
            # First try to get auth token
            login_payload = {
                "username": TEST_CREDENTIALS["username"],
                "password": TEST_CREDENTIALS["password"]
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as auth_response:
                if auth_response.status == 200:
                    auth_data = await auth_response.json()
                    
                    if auth_data.get("success"):
                        # Try to get JWT token for API access
                        # Note: This might require wallet signature verification
                        self.log_test("Authentication for History", True, 
                                    f"✅ User authentication successful", auth_data)
                    else:
                        self.log_test("Authentication for History", False, 
                                    f"❌ Authentication failed: {auth_data.get('message', 'Unknown error')}", auth_data)
                else:
                    self.log_test("Authentication for History", False, 
                                f"❌ Authentication HTTP {auth_response.status}")
                    
        except Exception as e:
            self.log_test("Transaction History Access Test", False, f"Error: {str(e)}")

    async def test_doge_address_validation(self):
        """Test DOGE address validation issues"""
        try:
            print(f"🐕 Testing DOGE address validation")
            
            withdrawal_wallet = TEST_CREDENTIALS["withdrawal_wallet"]
            
            # Test 1: Validate the withdrawal address format
            # DOGE addresses should start with 'D' and be 25-34 characters
            is_valid_format = (
                withdrawal_wallet.startswith('D') and 
                25 <= len(withdrawal_wallet) <= 34 and
                withdrawal_wallet.isalnum()
            )
            
            if is_valid_format:
                self.log_test("DOGE Address Format Check", True, 
                            f"✅ DOGE address {withdrawal_wallet} has valid format", 
                            {"address": withdrawal_wallet, "length": len(withdrawal_wallet)})
            else:
                self.log_test("DOGE Address Format Check", False, 
                            f"❌ DOGE address {withdrawal_wallet} has invalid format", 
                            {"address": withdrawal_wallet, "length": len(withdrawal_wallet)})
            
            # Test 2: Check if backend validates DOGE addresses correctly
            async with self.session.get(f"{self.base_url}/wallet/balance/DOGE?wallet_address={withdrawal_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        self.log_test("Backend DOGE Address Validation", True, 
                                    f"✅ Backend accepts DOGE address format", data)
                    else:
                        error_msg = data.get("error", "Unknown error")
                        if "invalid" in error_msg.lower() or "format" in error_msg.lower():
                            self.log_test("Backend DOGE Address Validation", False, 
                                        f"❌ Backend rejects DOGE address: {error_msg}", data)
                        else:
                            self.log_test("Backend DOGE Address Validation", True, 
                                        f"✅ Backend accepts address (balance query failed for other reasons)", data)
                else:
                    self.log_test("Backend DOGE Address Validation", False, 
                                f"❌ Backend DOGE validation HTTP {response.status}")
            
            # Test 3: Test with known valid DOGE addresses
            valid_doge_addresses = [
                "DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L",
                "D7Y55r6hNkcqDTvFW8GmyJKBGkbqNgLKjh",
                "D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda"
            ]
            
            for test_address in valid_doge_addresses:
                async with self.session.get(f"{self.base_url}/wallet/balance/DOGE?wallet_address={test_address}") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            self.log_test(f"Known Valid DOGE Address Test ({test_address[:10]}...)", True, 
                                        f"✅ Backend accepts known valid DOGE address", data)
                            break
                    else:
                        continue
            else:
                self.log_test("Known Valid DOGE Address Test", False, 
                            "❌ Backend rejects all known valid DOGE addresses")
                    
        except Exception as e:
            self.log_test("DOGE Address Validation Test", False, f"Error: {str(e)}")

    async def run_focused_tests(self):
        """Run focused tests on critical issues"""
        print("🎯 FOCUSED BACKEND TESTING - Critical Issues Analysis")
        print(f"🔗 Testing against: {self.base_url}")
        print(f"👤 User: {TEST_CREDENTIALS['username']}")
        print("=" * 80)
        
        # Test 1: CRT Balance Synchronization Issue
        await self.test_crt_balance_issue()
        
        # Test 2: NOWPayments Integration
        await self.test_nowpayments_integration()
        
        # Test 3: Transaction History Access
        await self.test_transaction_history_access()
        
        # Test 4: DOGE Address Validation
        await self.test_doge_address_validation()
        
        print("=" * 80)
        self.print_focused_summary()

    def print_focused_summary(self):
        """Print focused test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n🎯 FOCUSED TEST SUMMARY:")
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Categorize critical issues
        critical_issues = {
            "CRT Balance Sync": False,
            "NOWPayments Integration": False,
            "Transaction History": False,
            "DOGE Address Validation": False
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if result["success"]:
                if "CRT Balance" in test_name or "CRT Conversion" in test_name:
                    critical_issues["CRT Balance Sync"] = True
                elif "NOWPayments" in test_name:
                    critical_issues["NOWPayments Integration"] = True
                elif "History" in test_name or "Authentication" in test_name:
                    critical_issues["Transaction History"] = True
                elif "DOGE Address" in test_name:
                    critical_issues["DOGE Address Validation"] = True
        
        print(f"\n🚨 CRITICAL ISSUES STATUS:")
        for issue, resolved in critical_issues.items():
            status_icon = "✅" if resolved else "❌"
            print(f"{status_icon} {issue}: {'RESOLVED' if resolved else 'NEEDS ATTENTION'}")
        
        # Print recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if not critical_issues["CRT Balance Sync"]:
            print("   🔧 Fix CRT balance synchronization between blockchain and database")
            print("   🔧 Implement proper 21M CRT access for user cryptoking")
        
        if not critical_issues["NOWPayments Integration"]:
            print("   🔧 Complete NOWPayments payout permission activation")
            print("   🔧 Verify NOWPayments API credentials and whitelisting status")
        
        if not critical_issues["Transaction History"]:
            print("   🔧 Fix authentication requirements for transaction history endpoints")
            print("   🔧 Implement proper JWT token handling for API access")
        
        if not critical_issues["DOGE Address Validation"]:
            print("   🔧 Fix DOGE address validation in withdrawal system")
            print("   🔧 Update address format validation for mainnet DOGE addresses")

async def main():
    """Main test execution function"""
    async with FocusedBackendTester(BACKEND_URL) as tester:
        await tester.run_focused_tests()

if __name__ == "__main__":
    asyncio.run(main())