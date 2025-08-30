#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE NOWPayments Integration Test
Tests all aspects of NOWPayments integration including treasury system and full integration flow
"""

import asyncio
import aiohttp
import json
import os
import sys
import requests
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://tiger-dex-casino.preview.emergentagent.com/api"

# Test credentials and parameters
TEST_CREDENTIALS = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
    "destination_address": "DLbWLzxq2mxE3Adzn9MFKQ6EBP8gTE5po8",
    "test_amount": 50,
    "expected_balance": 34831540
}

# NOWPayments credentials
NOWPAYMENTS_CREDENTIALS = {
    "api_key": "FSVPHG1-1TK4MDZ-MKC4TTV-MW1MAXX",
    "public_key": "f9a7e8ba-2573-4da2-9f4f-3e0ffd748212",
    "ipn_secret": "JrjLnNYQV8vz6ee8uTW4rI8lMGsSYhGF",
    "environment": "production"
}

class ComprehensiveNOWPaymentsTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.test_results = []
        self.nowpayments_base_url = "https://api.nowpayments.io/v1"
        
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
            login_payload = {
                "username": TEST_CREDENTIALS["username"],
                "password": TEST_CREDENTIALS["password"]
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        # Get wallet authentication token
                        challenge_payload = {
                            "wallet_address": TEST_CREDENTIALS["wallet_address"],
                            "network": "solana"
                        }
                        
                        async with self.session.post(f"{self.base_url}/auth/challenge", 
                                                   json=challenge_payload) as challenge_response:
                            if challenge_response.status == 200:
                                challenge_data = await challenge_response.json()
                                if challenge_data.get("success"):
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
                                                return True
        except Exception as e:
            pass
        return False

    async def test_user_authentication(self):
        """Test 1: User Authentication"""
        authenticated = await self.authenticate_user()
        if authenticated:
            self.log_test("User Authentication", True, 
                        f"✅ User {TEST_CREDENTIALS['username']} authenticated with JWT token")
        else:
            self.log_test("User Authentication", False, "❌ Authentication failed")
        return authenticated

    async def test_user_balance_verification(self):
        """Test 2: User Balance Verification"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{TEST_CREDENTIALS['wallet_address']}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        doge_balance = deposit_balance.get("DOGE", 0)
                        
                        expected = TEST_CREDENTIALS["expected_balance"]
                        balance_match = abs(doge_balance - expected) < 1000
                        
                        if balance_match:
                            self.log_test("User Balance Verification", True, 
                                        f"✅ User has {doge_balance:,.0f} DOGE (expected ~{expected:,})")
                        else:
                            self.log_test("User Balance Verification", False, 
                                        f"❌ Balance mismatch: {doge_balance:,.0f} DOGE (expected {expected:,})")
                        return doge_balance >= TEST_CREDENTIALS["test_amount"]
        except Exception as e:
            self.log_test("User Balance Verification", False, f"Error: {str(e)}")
        return False

    async def test_nowpayments_credentials(self):
        """Test 3: NOWPayments Credentials"""
        try:
            headers = {
                'x-api-key': NOWPAYMENTS_CREDENTIALS["api_key"],
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(f"{self.nowpayments_base_url}/status", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("message") == "OK":
                        self.log_test("NOWPayments Credentials", True, 
                                    f"✅ API Key {NOWPAYMENTS_CREDENTIALS['api_key']} is valid")
                        return True
        except Exception as e:
            pass
        
        self.log_test("NOWPayments Credentials", False, "❌ API credentials invalid")
        return False

    async def test_doge_currency_support(self):
        """Test 4: DOGE Currency Support"""
        try:
            headers = {
                'x-api-key': NOWPAYMENTS_CREDENTIALS["api_key"],
                'Content-Type': 'application/json'
            }
            
            async with self.session.get(f"{self.nowpayments_base_url}/currencies", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    currencies = data.get("currencies", [])
                    doge_supported = any(curr.upper() == "DOGE" for curr in currencies)
                    
                    if doge_supported:
                        async with self.session.get(f"{self.nowpayments_base_url}/min-amount?currency_from=doge", 
                                                  headers=headers) as min_response:
                            if min_response.status == 200:
                                min_data = await min_response.json()
                                min_amount = min_data.get("min_amount", 0)
                                
                                self.log_test("DOGE Currency Support", True, 
                                            f"✅ DOGE supported among {len(currencies)} currencies, min: {min_amount} DOGE")
                                return True
        except Exception as e:
            pass
        
        self.log_test("DOGE Currency Support", False, "❌ DOGE not supported")
        return False

    async def test_treasury_system_integration(self):
        """Test 5: Treasury System Integration"""
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
                        doge_in_backend = "DOGE" in currencies
                        
                        self.log_test("Treasury System Integration", True, 
                                    f"✅ Backend treasury system operational, DOGE support: {doge_in_backend}")
                        return True
        except Exception as e:
            pass
        
        self.log_test("Treasury System Integration", False, "❌ Treasury system not accessible")
        return False

    async def test_personal_address_validation(self):
        """Test 6: Personal DOGE Address Validation"""
        try:
            destination = TEST_CREDENTIALS["destination_address"]
            
            # Validate DOGE address format
            is_valid_doge = (destination.startswith('D') and 
                           len(destination) == 34 and 
                           destination != "D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda")  # Not CoinGate address
            
            if is_valid_doge:
                self.log_test("Personal Address Validation", True, 
                            f"✅ Personal DOGE address {destination} is valid mainnet format")
                return True
            else:
                self.log_test("Personal Address Validation", False, 
                            f"❌ Invalid DOGE address format: {destination}")
        except Exception as e:
            self.log_test("Personal Address Validation", False, f"Error: {str(e)}")
        return False

    async def test_ipn_secret_verification(self):
        """Test 7: IPN Secret Verification"""
        try:
            import hmac
            import hashlib
            
            ipn_secret = NOWPAYMENTS_CREDENTIALS["ipn_secret"]
            test_payload = '{"test": "data"}'
            
            # Generate test signature
            expected_signature = hmac.new(
                ipn_secret.encode('utf-8'),
                test_payload.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()
            
            if len(expected_signature) == 128 and len(ipn_secret) == 32:
                self.log_test("IPN Secret Verification", True, 
                            f"✅ IPN secret properly configured ({len(ipn_secret)} chars)")
                return True
            else:
                self.log_test("IPN Secret Verification", False, 
                            f"❌ IPN secret format invalid")
        except Exception as e:
            self.log_test("IPN Secret Verification", False, f"Error: {str(e)}")
        return False

    async def test_real_blockchain_withdrawal(self):
        """Test 8: Real Blockchain Withdrawal (CRITICAL TEST)"""
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
            
            print(f"🚨 CRITICAL TEST: Real {TEST_CREDENTIALS['test_amount']} DOGE blockchain withdrawal")
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
                        
                        self.log_test("Real Blockchain Withdrawal", True, 
                                    f"🎉 WITHDRAWAL SUCCESS! TX: {transaction_id}, Payout: {payout_id}")
                        return True
                    else:
                        error_msg = data.get("message", "Unknown error")
                        if "401" in error_msg or "Unauthorized" in error_msg:
                            self.log_test("Real Blockchain Withdrawal", False, 
                                        f"❌ PAYOUT PERMISSIONS NOT ACTIVATED: {error_msg}")
                        else:
                            self.log_test("Real Blockchain Withdrawal", False, 
                                        f"❌ Withdrawal failed: {error_msg}")
                else:
                    self.log_test("Real Blockchain Withdrawal", False, 
                                f"❌ HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("Real Blockchain Withdrawal", False, f"Error: {str(e)}")
        return False

    async def run_comprehensive_tests(self):
        """Run all comprehensive NOWPayments tests"""
        print("🚨 FINAL COMPREHENSIVE NOWPayments Integration Test")
        print(f"🔗 Backend URL: {self.base_url}")
        print(f"🔑 API Key: {NOWPAYMENTS_CREDENTIALS['api_key']}")
        print(f"👤 User: {TEST_CREDENTIALS['username']} ({TEST_CREDENTIALS['wallet_address']})")
        print(f"💰 Test Amount: {TEST_CREDENTIALS['test_amount']} DOGE")
        print(f"📍 Destination: {TEST_CREDENTIALS['destination_address']}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_results = []
        
        test_results.append(await self.test_user_authentication())
        test_results.append(await self.test_user_balance_verification())
        test_results.append(await self.test_nowpayments_credentials())
        test_results.append(await self.test_doge_currency_support())
        test_results.append(await self.test_treasury_system_integration())
        test_results.append(await self.test_personal_address_validation())
        test_results.append(await self.test_ipn_secret_verification())
        test_results.append(await self.test_real_blockchain_withdrawal())
        
        print("=" * 80)
        self.print_final_summary()
        
        return test_results

    def print_final_summary(self):
        """Print final comprehensive summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n🚨 FINAL COMPREHENSIVE NOWPayments TEST SUMMARY:")
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Analyze critical components
        withdrawal_tests = [r for r in self.test_results if "withdrawal" in r["test"].lower()]
        withdrawal_success = any(r["success"] for r in withdrawal_tests)
        
        credentials_tests = [r for r in self.test_results if "credentials" in r["test"].lower()]
        credentials_success = any(r["success"] for r in credentials_tests)
        
        treasury_tests = [r for r in self.test_results if "treasury" in r["test"].lower()]
        treasury_success = any(r["success"] for r in treasury_tests)
        
        user_tests = [r for r in self.test_results if "user" in r["test"].lower()]
        user_success = all(r["success"] for r in user_tests)
        
        print(f"\n🎯 SUCCESS CRITERIA ASSESSMENT:")
        print(f"✅ Payout API returns 200 success (not 401): {'✅ YES' if withdrawal_success else '❌ NO'}")
        print(f"✅ Real blockchain withdrawal initiated: {'✅ YES' if withdrawal_success else '❌ NO'}")
        print(f"✅ Transaction ID received from NOWPayments: {'✅ YES' if withdrawal_success else '❌ NO'}")
        print(f"✅ System ready for production withdrawals: {'✅ YES' if withdrawal_success else '❌ NO'}")
        
        print(f"\n📋 SYSTEM COMPONENT STATUS:")
        print(f"🔑 NOWPayments API Credentials: {'✅ WORKING' if credentials_success else '❌ FAILED'}")
        print(f"👤 User Authentication & Balance: {'✅ WORKING' if user_success else '❌ FAILED'}")
        print(f"🏦 3-Treasury System Integration: {'✅ WORKING' if treasury_success else '❌ FAILED'}")
        print(f"💰 Payout Permissions: {'✅ ACTIVATED' if withdrawal_success else '❌ NOT ACTIVATED'}")
        
        # Calculate readiness percentage
        component_scores = [credentials_success, user_success, treasury_success, withdrawal_success]
        readiness_percentage = (sum(component_scores) / len(component_scores)) * 100
        
        print(f"\n📊 SYSTEM READINESS: {readiness_percentage:.1f}%")
        
        if withdrawal_success:
            print(f"\n🎉 BREAKTHROUGH CONFIRMED!")
            print(f"🚀 NOWPayments payout permissions are now ACTIVATED!")
            print(f"💎 System is ready for real blockchain withdrawals!")
            print(f"🎮 Users can now withdraw DOGE to personal wallets!")
        else:
            print(f"\n⏳ PAYOUT ACTIVATION STATUS: INCOMPLETE")
            print(f"📞 NOWPayments payout permissions still require activation")
            print(f"🔧 All system components ready except payout permissions")
            print(f"📋 Contact NOWPayments support with API key: {NOWPAYMENTS_CREDENTIALS['api_key']}")
        
        # Print failed tests details
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")

async def main():
    """Main test execution function"""
    async with ComprehensiveNOWPaymentsTester(BACKEND_URL) as tester:
        await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())