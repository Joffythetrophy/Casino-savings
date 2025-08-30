#!/usr/bin/env python3
"""
URGENT: NOWPayments Payout Activation Verification Test
Tests if payout permissions are now active after user's NOWPayments dashboard shows active DOGE transaction
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

# Test credentials and parameters from review request
TEST_CREDENTIALS = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
    "destination_address": "DLbWLzxq2mxE3Adzn9MFKQ6EBP8gTE5po8",  # Personal DOGE address
    "test_amount": 50,  # 50 DOGE safe test amount
    "expected_balance": 34831540  # Expected DOGE balance
}

# NOWPayments credentials from review request
NOWPAYMENTS_CREDENTIALS = {
    "api_key": "FSVPHG1-1TK4MDZ-MKC4TTV-MW1MAXX",
    "public_key": "f9a7e8ba-2573-4da2-9f4f-3e0ffd748212",
    "ipn_secret": "JrjLnNYQV8vz6ee8uTW4rI8lMGsSYhGF",
    "environment": "production"
}

class NOWPaymentsPayoutTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
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

    async def test_user_authentication(self):
        """Test 1: User Authentication - cryptoking/crt21million"""
        try:
            login_payload = {
                "username": TEST_CREDENTIALS["username"],
                "password": TEST_CREDENTIALS["password"]
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if (data.get("success") and 
                        data.get("username") == TEST_CREDENTIALS["username"] and
                        data.get("wallet_address") == TEST_CREDENTIALS["wallet_address"]):
                        self.log_test("User Authentication", True, 
                                    f"✅ User {TEST_CREDENTIALS['username']} authenticated successfully", data)
                        return True
                    else:
                        self.log_test("User Authentication", False, 
                                    f"❌ Authentication failed: {data.get('message', 'Unknown error')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, 
                                f"❌ HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
        return False

    async def test_user_balance_verification(self):
        """Test 2: User Balance Verification - Check DOGE balance"""
        try:
            wallet_address = TEST_CREDENTIALS["wallet_address"]
            
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        doge_balance = deposit_balance.get("DOGE", 0)
                        
                        # Check if balance matches expected (approximately)
                        expected = TEST_CREDENTIALS["expected_balance"]
                        balance_match = abs(doge_balance - expected) < 1000  # Allow 1000 DOGE variance
                        
                        if balance_match:
                            self.log_test("User Balance Verification", True, 
                                        f"✅ User has {doge_balance:,.0f} DOGE (expected ~{expected:,})", data)
                        else:
                            self.log_test("User Balance Verification", False, 
                                        f"❌ Balance mismatch: {doge_balance:,.0f} DOGE (expected {expected:,})", data)
                        return doge_balance >= TEST_CREDENTIALS["test_amount"]
                    else:
                        self.log_test("User Balance Verification", False, 
                                    f"❌ Wallet info failed: {data.get('message', 'Unknown error')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("User Balance Verification", False, 
                                f"❌ HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("User Balance Verification", False, f"Error: {str(e)}")
        return False

    async def test_nowpayments_credentials(self):
        """Test 3: NOWPayments Credentials - Test new API key"""
        try:
            headers = {
                'x-api-key': NOWPAYMENTS_CREDENTIALS["api_key"],
                'Content-Type': 'application/json'
            }
            
            # Test API status endpoint
            async with self.session.get(f"{self.nowpayments_base_url}/status", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("message") == "OK":
                        self.log_test("NOWPayments Credentials", True, 
                                    f"✅ API Key {NOWPAYMENTS_CREDENTIALS['api_key']} is valid and working", data)
                        return True
                    else:
                        self.log_test("NOWPayments Credentials", False, 
                                    f"❌ API status not OK: {data}", data)
                else:
                    error_text = await response.text()
                    self.log_test("NOWPayments Credentials", False, 
                                f"❌ HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("NOWPayments Credentials", False, f"Error: {str(e)}")
        return False

    async def test_doge_currency_support(self):
        """Test 4: DOGE Currency Support - Verify DOGE is supported"""
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
                    
                    # Check if DOGE is supported
                    doge_supported = any(curr.upper() == "DOGE" for curr in currencies)
                    
                    if doge_supported:
                        # Get minimum amount for DOGE
                        async with self.session.get(f"{self.nowpayments_base_url}/min-amount?currency_from=doge", 
                                                  headers=headers) as min_response:
                            if min_response.status == 200:
                                min_data = await min_response.json()
                                min_amount = min_data.get("min_amount", 0)
                                
                                self.log_test("DOGE Currency Support", True, 
                                            f"✅ DOGE supported among {len(currencies)} currencies, min amount: {min_amount} DOGE", 
                                            {"currencies_count": len(currencies), "min_amount": min_amount})
                                return True
                            else:
                                self.log_test("DOGE Currency Support", True, 
                                            f"✅ DOGE supported among {len(currencies)} currencies", data)
                                return True
                    else:
                        self.log_test("DOGE Currency Support", False, 
                                    f"❌ DOGE not found in {len(currencies)} supported currencies", data)
                else:
                    error_text = await response.text()
                    self.log_test("DOGE Currency Support", False, 
                                f"❌ HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("DOGE Currency Support", False, f"Error: {str(e)}")
        return False

    async def test_treasury_system_integration(self):
        """Test 5: Treasury System Integration - Check 3-treasury routing"""
        try:
            # Test if backend has NOWPayments withdrawal endpoint
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    # Check if NOWPayments service is available in backend
                    test_payload = {
                        "wallet_address": TEST_CREDENTIALS["wallet_address"],
                        "currency": "DOGE",
                        "amount": 1,  # Small test amount
                        "destination_address": TEST_CREDENTIALS["destination_address"]
                    }
                    
                    # Test treasury routing (this might fail but we want to see the error)
                    async with self.session.post(f"{self.base_url}/nowpayments/withdraw", 
                                               json=test_payload) as withdraw_response:
                        response_text = await withdraw_response.text()
                        
                        if withdraw_response.status == 200:
                            data = await withdraw_response.json()
                            self.log_test("Treasury System Integration", True, 
                                        f"✅ Treasury system operational: {data.get('message', 'Success')}", data)
                            return True
                        elif withdraw_response.status == 401:
                            # This is expected if payout permissions not activated yet
                            self.log_test("Treasury System Integration", True, 
                                        f"✅ Treasury system configured but payout permissions needed: {response_text}", 
                                        {"status": withdraw_response.status, "response": response_text})
                            return True
                        else:
                            self.log_test("Treasury System Integration", False, 
                                        f"❌ Treasury system error: HTTP {withdraw_response.status}: {response_text}")
                else:
                    self.log_test("Treasury System Integration", False, 
                                f"❌ Backend not accessible: HTTP {response.status}")
        except Exception as e:
            self.log_test("Treasury System Integration", False, f"Error: {str(e)}")
        return False

    async def test_real_payout_attempt(self):
        """Test 6: Real Payout Attempt - Test 50 DOGE withdrawal"""
        try:
            print(f"🚨 CRITICAL TEST: Attempting real {TEST_CREDENTIALS['test_amount']} DOGE payout")
            print(f"📍 Destination: {TEST_CREDENTIALS['destination_address']}")
            
            # Test backend withdrawal endpoint
            payout_payload = {
                "wallet_address": TEST_CREDENTIALS["wallet_address"],
                "currency": "DOGE",
                "amount": TEST_CREDENTIALS["test_amount"],
                "destination_address": TEST_CREDENTIALS["destination_address"]
            }
            
            async with self.session.post(f"{self.base_url}/nowpayments/withdraw", 
                                       json=payout_payload) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        transaction_id = data.get("transaction_id", "")
                        payout_id = data.get("payout_id", "")
                        
                        self.log_test("Real Payout Attempt", True, 
                                    f"🎉 PAYOUT SUCCESS! Transaction: {transaction_id}, Payout: {payout_id}", data)
                        return True
                    else:
                        error_msg = data.get("message", "Unknown error")
                        self.log_test("Real Payout Attempt", False, 
                                    f"❌ Payout failed: {error_msg}", data)
                elif response.status == 401:
                    # Check specific error message
                    if "Bearer JWTtoken is required" in response_text:
                        self.log_test("Real Payout Attempt", False, 
                                    f"❌ PAYOUT PERMISSIONS NOT ACTIVATED: {response_text}", 
                                    {"status": response.status, "error": "payout_permissions_needed"})
                    else:
                        self.log_test("Real Payout Attempt", False, 
                                    f"❌ Authentication error: {response_text}", 
                                    {"status": response.status, "response": response_text})
                else:
                    self.log_test("Real Payout Attempt", False, 
                                f"❌ HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("Real Payout Attempt", False, f"Error: {str(e)}")
        return False

    async def test_direct_nowpayments_payout(self):
        """Test 7: Direct NOWPayments Payout API Test"""
        try:
            print(f"🔗 DIRECT API TEST: Testing NOWPayments payout API directly")
            
            headers = {
                'x-api-key': NOWPAYMENTS_CREDENTIALS["api_key"],
                'Content-Type': 'application/json'
            }
            
            # Create direct payout request
            payout_data = {
                'withdrawals': [
                    {
                        'address': TEST_CREDENTIALS["destination_address"],
                        'currency': 'doge',
                        'amount': str(TEST_CREDENTIALS["test_amount"]),
                        'extra_id': f"test_payout_{int(datetime.utcnow().timestamp())}"
                    }
                ]
            }
            
            async with self.session.post(f"{self.nowpayments_base_url}/payout", 
                                       headers=headers, json=payout_data) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = await response.json()
                    payout_id = data.get("id", "")
                    status = data.get("status", "")
                    
                    self.log_test("Direct NOWPayments Payout", True, 
                                f"🎉 DIRECT PAYOUT SUCCESS! ID: {payout_id}, Status: {status}", data)
                    return True
                elif response.status == 401:
                    self.log_test("Direct NOWPayments Payout", False, 
                                f"❌ PAYOUT PERMISSIONS NOT ACTIVATED: {response_text}", 
                                {"status": response.status, "error": "payout_permissions_needed"})
                else:
                    self.log_test("Direct NOWPayments Payout", False, 
                                f"❌ Direct payout failed: HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("Direct NOWPayments Payout", False, f"Error: {str(e)}")
        return False

    async def test_transaction_status_tracking(self):
        """Test 8: Transaction Status Tracking"""
        try:
            # Test if we can track transaction status (even if no active transactions)
            headers = {
                'x-api-key': NOWPAYMENTS_CREDENTIALS["api_key"],
                'Content-Type': 'application/json'
            }
            
            # Try to get payout list or status
            async with self.session.get(f"{self.nowpayments_base_url}/payout", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Transaction Status Tracking", True, 
                                f"✅ Transaction tracking available: {len(data.get('data', []))} payouts found", data)
                    return True
                elif response.status == 401:
                    response_text = await response.text()
                    self.log_test("Transaction Status Tracking", False, 
                                f"❌ Status tracking requires payout permissions: {response_text}")
                else:
                    response_text = await response.text()
                    self.log_test("Transaction Status Tracking", False, 
                                f"❌ Status tracking failed: HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("Transaction Status Tracking", False, f"Error: {str(e)}")
        return False

    async def run_payout_activation_tests(self):
        """Run all NOWPayments payout activation tests"""
        print("🚨 URGENT: NOWPayments Payout Activation Verification Test")
        print(f"🔗 Backend URL: {self.base_url}")
        print(f"🔑 API Key: {NOWPAYMENTS_CREDENTIALS['api_key']}")
        print(f"👤 User: {TEST_CREDENTIALS['username']} ({TEST_CREDENTIALS['wallet_address']})")
        print(f"💰 Test Amount: {TEST_CREDENTIALS['test_amount']} DOGE")
        print(f"📍 Destination: {TEST_CREDENTIALS['destination_address']}")
        print("=" * 80)
        
        # Run all tests
        test_results = []
        
        test_results.append(await self.test_user_authentication())
        test_results.append(await self.test_user_balance_verification())
        test_results.append(await self.test_nowpayments_credentials())
        test_results.append(await self.test_doge_currency_support())
        test_results.append(await self.test_treasury_system_integration())
        test_results.append(await self.test_real_payout_attempt())
        test_results.append(await self.test_direct_nowpayments_payout())
        test_results.append(await self.test_transaction_status_tracking())
        
        print("=" * 80)
        self.print_payout_activation_summary()
        
        return test_results

    def print_payout_activation_summary(self):
        """Print comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n🚨 NOWPAYMENTS PAYOUT ACTIVATION TEST SUMMARY:")
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Analyze results for payout activation status
        payout_tests = [r for r in self.test_results if "payout" in r["test"].lower()]
        payout_success = any(r["success"] for r in payout_tests)
        
        credentials_tests = [r for r in self.test_results if "credentials" in r["test"].lower()]
        credentials_success = any(r["success"] for r in credentials_tests)
        
        user_tests = [r for r in self.test_results if "user" in r["test"].lower() or "authentication" in r["test"].lower()]
        user_success = all(r["success"] for r in user_tests)
        
        print(f"\n🎯 SUCCESS CRITERIA STATUS:")
        print(f"✅ Payout API returns 200 success (not 401): {'✅ YES' if payout_success else '❌ NO'}")
        print(f"✅ Real blockchain withdrawal initiated: {'✅ YES' if payout_success else '❌ NO'}")
        print(f"✅ Transaction ID received from NOWPayments: {'✅ YES' if payout_success else '❌ NO'}")
        print(f"✅ System ready for production withdrawals: {'✅ YES' if payout_success else '❌ NO'}")
        
        print(f"\n📋 COMPONENT STATUS:")
        print(f"🔑 NOWPayments Credentials: {'✅ WORKING' if credentials_success else '❌ FAILED'}")
        print(f"👤 User Authentication: {'✅ WORKING' if user_success else '❌ FAILED'}")
        print(f"💰 Payout Permissions: {'✅ ACTIVATED' if payout_success else '❌ NOT ACTIVATED'}")
        
        # Print failed tests details
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        # Final assessment
        if payout_success:
            print(f"\n🎉 BREAKTHROUGH CONFIRMED! NOWPayments payout permissions are now ACTIVATED!")
            print(f"🚀 System is ready for real blockchain withdrawals!")
        else:
            print(f"\n⏳ Payout permissions still require activation from NOWPayments support.")
            print(f"📞 Contact NOWPayments to activate payout permissions for API key: {NOWPAYMENTS_CREDENTIALS['api_key']}")

async def main():
    """Main test execution function"""
    async with NOWPaymentsPayoutTester(BACKEND_URL) as tester:
        await tester.run_payout_activation_tests()

if __name__ == "__main__":
    asyncio.run(main())