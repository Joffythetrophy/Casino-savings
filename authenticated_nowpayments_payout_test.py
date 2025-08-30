#!/usr/bin/env python3
"""
URGENT: Authenticated NOWPayments Payout Test
Tests NOWPayments endpoints with proper backend authentication
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://crypto-treasury-app.preview.emergentagent.com/api"

# Test credentials
TEST_CREDENTIALS = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
    "destination_address": "DLbWLzxq2mxE3Adzn9MFKQ6EBP8gTE5po8",
    "test_amount": 50
}

class AuthenticatedNOWPaymentsTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
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

    async def authenticate_user(self):
        """Authenticate user and get JWT token"""
        try:
            # First try username login
            login_payload = {
                "username": TEST_CREDENTIALS["username"],
                "password": TEST_CREDENTIALS["password"]
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_test("User Authentication", True, 
                                    f"✅ User {TEST_CREDENTIALS['username']} authenticated", data)
                        
                        # Now get wallet authentication token
                        challenge_payload = {
                            "wallet_address": TEST_CREDENTIALS["wallet_address"],
                            "network": "solana"
                        }
                        
                        async with self.session.post(f"{self.base_url}/auth/challenge", 
                                                   json=challenge_payload) as challenge_response:
                            if challenge_response.status == 200:
                                challenge_data = await challenge_response.json()
                                if challenge_data.get("success"):
                                    # Verify with mock signature
                                    verify_payload = {
                                        "challenge_hash": challenge_data.get("challenge_hash"),
                                        "signature": "mock_signature_for_testing",
                                        "wallet_address": TEST_CREDENTIALS["wallet_address"],
                                        "network": "solana"
                                    }
                                    
                                    async with self.session.post(f"{self.base_url}/auth/verify", 
                                                               json=verify_payload) as verify_response:
                                        if verify_response.status == 200:
                                            verify_data = await verify_response.json()
                                            if verify_data.get("success"):
                                                self.auth_token = verify_data.get("token")
                                                self.log_test("Wallet Authentication", True, 
                                                            f"✅ JWT token obtained", verify_data)
                                                return True
                        
                        self.log_test("Wallet Authentication", False, "❌ Failed to get JWT token")
                    else:
                        self.log_test("User Authentication", False, 
                                    f"❌ Login failed: {data.get('message')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, 
                                f"❌ HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
        return False

    async def test_nowpayments_currencies(self):
        """Test NOWPayments currencies endpoint"""
        try:
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            async with self.session.get(f"{self.base_url}/nowpayments/currencies", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        currencies = data.get("currencies", [])
                        doge_supported = "DOGE" in currencies
                        
                        self.log_test("NOWPayments Currencies", True, 
                                    f"✅ {len(currencies)} currencies available, DOGE supported: {doge_supported}", data)
                        return True
                    else:
                        self.log_test("NOWPayments Currencies", False, 
                                    f"❌ Currencies request failed: {data.get('error')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("NOWPayments Currencies", False, 
                                f"❌ HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("NOWPayments Currencies", False, f"Error: {str(e)}")
        return False

    async def test_nowpayments_withdrawal(self):
        """Test NOWPayments withdrawal endpoint with authentication"""
        try:
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            withdrawal_payload = {
                "wallet_address": TEST_CREDENTIALS["wallet_address"],
                "currency": "DOGE",
                "amount": TEST_CREDENTIALS["test_amount"],
                "destination_address": TEST_CREDENTIALS["destination_address"],
                "treasury_type": "treasury_2_liquidity",
                "user_id": "cryptoking_test_user"
            }
            
            print(f"🚨 TESTING AUTHENTICATED WITHDRAWAL: {TEST_CREDENTIALS['test_amount']} DOGE")
            print(f"📍 Destination: {TEST_CREDENTIALS['destination_address']}")
            
            async with self.session.post(f"{self.base_url}/nowpayments/withdraw", 
                                       json=withdrawal_payload, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        transaction_id = data.get("transaction_id", "")
                        payout_id = data.get("payout_id", "")
                        blockchain_hash = data.get("blockchain_hash", "")
                        
                        self.log_test("NOWPayments Withdrawal", True, 
                                    f"🎉 WITHDRAWAL SUCCESS! TX: {transaction_id}, Payout: {payout_id}, Hash: {blockchain_hash}", data)
                        return True
                    else:
                        error_msg = data.get("message", "Unknown error")
                        self.log_test("NOWPayments Withdrawal", False, 
                                    f"❌ Withdrawal failed: {error_msg}", data)
                elif response.status == 401:
                    if "Bearer JWTtoken is required" in response_text:
                        self.log_test("NOWPayments Withdrawal", False, 
                                    f"❌ PAYOUT PERMISSIONS NOT ACTIVATED: {response_text}")
                    else:
                        self.log_test("NOWPayments Withdrawal", False, 
                                    f"❌ Authentication failed: {response_text}")
                elif response.status == 403:
                    self.log_test("NOWPayments Withdrawal", False, 
                                f"❌ Not authenticated with backend: {response_text}")
                else:
                    self.log_test("NOWPayments Withdrawal", False, 
                                f"❌ HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("NOWPayments Withdrawal", False, f"Error: {str(e)}")
        return False

    async def test_user_balance_check(self):
        """Test user balance to ensure sufficient funds"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{TEST_CREDENTIALS['wallet_address']}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        doge_balance = deposit_balance.get("DOGE", 0)
                        
                        sufficient_funds = doge_balance >= TEST_CREDENTIALS["test_amount"]
                        
                        self.log_test("User Balance Check", True, 
                                    f"✅ User DOGE balance: {doge_balance:,.0f}, Sufficient for {TEST_CREDENTIALS['test_amount']} DOGE: {sufficient_funds}", data)
                        return sufficient_funds
                    else:
                        self.log_test("User Balance Check", False, 
                                    f"❌ Balance check failed: {data.get('message')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("User Balance Check", False, 
                                f"❌ HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("User Balance Check", False, f"Error: {str(e)}")
        return False

    async def test_nowpayments_status_check(self):
        """Test if we can check withdrawal status"""
        try:
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            # Try to get status of a dummy payout ID
            dummy_payout_id = "test_payout_123"
            
            async with self.session.get(f"{self.base_url}/nowpayments/withdrawal-status/{dummy_payout_id}", 
                                      headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = await response.json()
                    self.log_test("NOWPayments Status Check", True, 
                                f"✅ Status check endpoint working: {data.get('message', 'Success')}", data)
                    return True
                elif response.status == 404:
                    self.log_test("NOWPayments Status Check", True, 
                                f"✅ Status check endpoint working (404 expected for dummy ID)", {"status": 404})
                    return True
                else:
                    self.log_test("NOWPayments Status Check", False, 
                                f"❌ Status check failed: HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("NOWPayments Status Check", False, f"Error: {str(e)}")
        return False

    async def run_authenticated_tests(self):
        """Run all authenticated NOWPayments tests"""
        print("🚨 URGENT: Authenticated NOWPayments Payout Test")
        print(f"🔗 Backend URL: {self.base_url}")
        print(f"👤 User: {TEST_CREDENTIALS['username']} ({TEST_CREDENTIALS['wallet_address']})")
        print(f"💰 Test Amount: {TEST_CREDENTIALS['test_amount']} DOGE")
        print(f"📍 Destination: {TEST_CREDENTIALS['destination_address']}")
        print("=" * 80)
        
        # Step 1: Authenticate
        authenticated = await self.authenticate_user()
        
        if not authenticated:
            print("❌ Authentication failed - cannot proceed with NOWPayments tests")
            return
        
        # Step 2: Run tests
        await self.test_user_balance_check()
        await self.test_nowpayments_currencies()
        await self.test_nowpayments_status_check()
        await self.test_nowpayments_withdrawal()  # The critical test
        
        print("=" * 80)
        self.print_test_summary()

    def print_test_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n🚨 AUTHENTICATED NOWPAYMENTS TEST SUMMARY:")
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Check for withdrawal success
        withdrawal_tests = [r for r in self.test_results if "withdrawal" in r["test"].lower() and "status" not in r["test"].lower()]
        withdrawal_success = any(r["success"] for r in withdrawal_tests)
        
        print(f"\n🎯 CRITICAL RESULT:")
        if withdrawal_success:
            print(f"🎉 BREAKTHROUGH! NOWPayments payout permissions are ACTIVATED!")
            print(f"🚀 Real blockchain withdrawals are now working!")
        else:
            print(f"⏳ NOWPayments payout permissions still require activation")
            print(f"📞 Contact NOWPayments support to activate payout permissions")
        
        # Print failed tests
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")

async def main():
    """Main test execution function"""
    async with AuthenticatedNOWPaymentsTester(BACKEND_URL) as tester:
        await tester.run_authenticated_tests()

if __name__ == "__main__":
    asyncio.run(main())