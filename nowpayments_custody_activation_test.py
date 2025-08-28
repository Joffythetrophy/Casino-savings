#!/usr/bin/env python3
"""
URGENT: NOWPayments Custody Activation Test with New Credentials
Tests the NOWPayments integration after custody activation with new API credentials
"""

import asyncio
import aiohttp
import json
import os
import sys
import hmac
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

# Backend URL from environment
BACKEND_URL = "https://smart-savings-dapp.preview.emergentagent.com/api"

# New NOWPayments credentials from review request
NEW_CREDENTIALS = {
    "api_key": "FSVPHG1-1TK4MDZ-MKC4TTV-MW1MAXX",
    "public_key": "f9a7e8ba-2573-4da2-9f4f-3e0ffd748212",
    "ipn_secret": "JrjLnNYQV8vz6ee8uTW4rI8lMGsSYhGF"
}

# Test user credentials
TEST_USER = {
    "username": "cryptoking",
    "password": "crt21million",
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
    "personal_doge_address": "DLbWLzxq2mxE3Adzn9MFKQ6EBP8gTE5po8",
    "expected_balance": 34831540  # Expected DOGE balance
}

class NOWPaymentsCustodyTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        self.auth_token: Optional[str] = None
        
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
        """Test 1: User Authentication with cryptoking credentials"""
        try:
            login_payload = {
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if (data.get("success") and 
                        data.get("username") == TEST_USER["username"] and
                        data.get("wallet_address") == TEST_USER["wallet_address"]):
                        
                        # Now get JWT token for API access
                        await self.get_jwt_token()
                        
                        self.log_test("User Authentication", True, 
                                    f"User {TEST_USER['username']} authenticated successfully", data)
                        return True
                    else:
                        self.log_test("User Authentication", False, 
                                    f"Authentication failed: {data.get('message', 'Unknown error')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
        return False
    
    async def get_jwt_token(self):
        """Get JWT token for API authentication"""
        try:
            # Step 1: Generate challenge
            challenge_payload = {
                "wallet_address": TEST_USER["wallet_address"],
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/auth/challenge", 
                                       json=challenge_payload) as response:
                if response.status == 200:
                    challenge_data = await response.json()
                    if challenge_data.get("success"):
                        # Step 2: Verify with mock signature (demo mode)
                        verify_payload = {
                            "challenge_hash": challenge_data.get("challenge_hash"),
                            "signature": "mock_signature_for_nowpayments_test",
                            "wallet_address": TEST_USER["wallet_address"],
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
            print(f"JWT token generation failed: {e}")
        return False
    
    async def test_user_balance_verification(self):
        """Test 2: Verify user balance matches expected amount"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{TEST_USER['wallet_address']}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        doge_balance = wallet.get("deposit_balance", {}).get("DOGE", 0)
                        
                        if doge_balance == TEST_USER["expected_balance"]:
                            self.log_test("User Balance Verification", True, 
                                        f"User has exactly {doge_balance:,} DOGE (matches expected)", data)
                            return True
                        else:
                            self.log_test("User Balance Verification", False, 
                                        f"Balance mismatch: expected {TEST_USER['expected_balance']:,}, got {doge_balance:,}", data)
                    else:
                        self.log_test("User Balance Verification", False, 
                                    "Failed to retrieve wallet info", data)
                else:
                    error_text = await response.text()
                    self.log_test("User Balance Verification", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("User Balance Verification", False, f"Error: {str(e)}")
        return False
    
    async def test_nowpayments_credentials(self):
        """Test 3: Test NOWPayments API access with new credentials"""
        try:
            # Test direct NOWPayments API status
            headers = {
                'x-api-key': NEW_CREDENTIALS["api_key"],
                'Content-Type': 'application/json'
            }
            
            nowpayments_url = "https://api.nowpayments.io/v1/status"
            
            async with self.session.get(nowpayments_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("NOWPayments Credentials", True, 
                                f"API access successful with new credentials", data)
                    return True
                elif response.status == 401:
                    error_text = await response.text()
                    self.log_test("NOWPayments Credentials", False, 
                                f"401 Unauthorized - credentials may not be activated yet: {error_text}")
                else:
                    error_text = await response.text()
                    self.log_test("NOWPayments Credentials", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("NOWPayments Credentials", False, f"Error: {str(e)}")
        return False
    
    async def test_doge_currency_support(self):
        """Test 4: Verify DOGE is still supported with new credentials"""
        try:
            headers = {
                'x-api-key': NEW_CREDENTIALS["api_key"],
                'Content-Type': 'application/json'
            }
            
            nowpayments_url = "https://api.nowpayments.io/v1/currencies"
            
            async with self.session.get(nowpayments_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    currencies = data.get("currencies", [])
                    
                    # Check if DOGE is supported
                    doge_supported = any(curr.upper() == "DOGE" for curr in currencies)
                    
                    if doge_supported:
                        self.log_test("DOGE Currency Support", True, 
                                    f"DOGE supported among {len(currencies)} currencies", 
                                    {"total_currencies": len(currencies), "doge_supported": True})
                        return True
                    else:
                        self.log_test("DOGE Currency Support", False, 
                                    f"DOGE not found in {len(currencies)} supported currencies", data)
                else:
                    error_text = await response.text()
                    self.log_test("DOGE Currency Support", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("DOGE Currency Support", False, f"Error: {str(e)}")
        return False
    
    async def test_real_blockchain_withdrawal(self):
        """Test 5: Test real blockchain withdrawal with new credentials"""
        try:
            if not self.auth_token:
                self.log_test("Real Blockchain Withdrawal", False, "No authentication token available")
                return False
            
            # Test the actual withdrawal endpoint with smaller amount
            withdrawal_payload = {
                "destination_address": TEST_USER["personal_doge_address"],
                "amount": 50,  # 50 DOGE test amount
                "currency": "DOGE",
                "user_id": TEST_USER["wallet_address"]
            }
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test via backend NOWPayments endpoint
            async with self.session.post(f"{self.base_url}/nowpayments/withdraw", 
                                       json=withdrawal_payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_test("Real Blockchain Withdrawal", True, 
                                    f"Withdrawal successful: {data.get('message', 'Success')}", data)
                        return True
                    else:
                        self.log_test("Real Blockchain Withdrawal", False, 
                                    f"Withdrawal failed: {data.get('error', 'Unknown error')}", data)
                elif response.status == 401:
                    error_text = await response.text()
                    self.log_test("Real Blockchain Withdrawal", False, 
                                f"401 Unauthorized - custody not yet activated: {error_text}")
                else:
                    error_text = await response.text()
                    self.log_test("Real Blockchain Withdrawal", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Real Blockchain Withdrawal", False, f"Error: {str(e)}")
        return False
    
    async def test_treasury_integration(self):
        """Test 6: Test 3-treasury system integration"""
        try:
            # Test treasury configuration endpoint
            async with self.session.get(f"{self.base_url}/nowpayments/treasuries") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "treasuries" in data:
                        treasuries = data["treasuries"]
                        
                        # Check for 3 treasuries
                        expected_treasuries = ["treasury_1_savings", "treasury_2_liquidity", "treasury_3_winnings"]
                        found_treasuries = []
                        
                        for treasury_id, treasury_info in treasuries.items():
                            if treasury_id in expected_treasuries:
                                found_treasuries.append(treasury_id)
                                # Check if DOGE is supported in this treasury
                                if "DOGE" in treasury_info.get("currencies", []):
                                    found_treasuries.append(f"{treasury_id}_doge_support")
                        
                        if len(found_treasuries) >= 6:  # 3 treasuries + 3 DOGE supports
                            self.log_test("Treasury Integration", True, 
                                        f"3-Treasury system configured with DOGE support: {found_treasuries}", data)
                            return True
                        else:
                            self.log_test("Treasury Integration", False, 
                                        f"Incomplete treasury configuration: {found_treasuries}", data)
                    else:
                        self.log_test("Treasury Integration", False, 
                                    "Invalid treasury response format", data)
                else:
                    error_text = await response.text()
                    self.log_test("Treasury Integration", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Treasury Integration", False, f"Error: {str(e)}")
        return False
    
    async def test_ipn_verification(self):
        """Test 7: Test IPN webhook signature validation"""
        try:
            # Test the IPN webhook endpoint directly (simulating NOWPayments callback)
            test_payload = '{"payout_id":"test123","status":"finished","amount":"50","currency":"doge"}'
            
            # Generate valid signature using the IPN secret
            valid_signature = hmac.new(
                NEW_CREDENTIALS["ipn_secret"].encode('utf-8'),
                test_payload.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()
            
            # Test webhook endpoint with valid signature
            headers = {
                "x-nowpayments-sig": valid_signature,
                "Content-Type": "application/json"
            }
            
            async with self.session.post(f"{self.base_url}/webhooks/nowpayments/payout", 
                                       data=test_payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        # Test with invalid signature
                        invalid_headers = {
                            "x-nowpayments-sig": "invalid_signature_12345",
                            "Content-Type": "application/json"
                        }
                        
                        async with self.session.post(f"{self.base_url}/webhooks/nowpayments/payout", 
                                                   data=test_payload, headers=invalid_headers) as invalid_response:
                            if invalid_response.status == 400:  # Should reject invalid signature
                                self.log_test("IPN Verification", True, 
                                            f"IPN signature validation working: valid accepted, invalid rejected", 
                                            {"valid_response": data, "invalid_rejected": True})
                                return True
                            else:
                                invalid_data = await invalid_response.json()
                                self.log_test("IPN Verification", False, 
                                            f"Invalid signature not properly rejected: HTTP {invalid_response.status}", invalid_data)
                    else:
                        self.log_test("IPN Verification", False, 
                                    f"Valid signature not accepted: {data}", data)
                else:
                    error_text = await response.text()
                    self.log_test("IPN Verification", False, 
                                f"IPN webhook test failed: HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("IPN Verification", False, f"Error: {str(e)}")
        return False
    
    async def run_comprehensive_test(self):
        """Run all NOWPayments custody activation tests"""
        print("🚨 URGENT: NOWPayments Custody Activation Test with New Credentials")
        print("=" * 80)
        print(f"Testing with API Key: {NEW_CREDENTIALS['api_key']}")
        print(f"Testing with Public Key: {NEW_CREDENTIALS['public_key']}")
        print(f"User: {TEST_USER['username']} ({TEST_USER['wallet_address']})")
        print(f"Personal DOGE Address: {TEST_USER['personal_doge_address']}")
        print(f"Expected Balance: {TEST_USER['expected_balance']:,} DOGE")
        print("=" * 80)
        
        # Run all tests
        test_functions = [
            self.test_user_authentication,
            self.test_user_balance_verification,
            self.test_nowpayments_credentials,
            self.test_doge_currency_support,
            self.test_real_blockchain_withdrawal,
            self.test_treasury_integration,
            self.test_ipn_verification
        ]
        
        passed_tests = 0
        total_tests = len(test_functions)
        
        for test_func in test_functions:
            try:
                result = await test_func()
                if result:
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test_func.__name__} crashed: {str(e)}")
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 CUSTODY ACTIVATION TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - NOWPayments custody activation successful!")
            print("✅ System ready for live blockchain withdrawals!")
        elif passed_tests >= 5:
            print("⚠️ PARTIAL SUCCESS - Most components working")
            print("🔧 Minor issues detected, but core functionality operational")
        else:
            print("❌ CUSTODY ACTIVATION INCOMPLETE")
            print("🚨 Major issues detected - custody may not be fully activated")
        
        # Detailed results
        print("\n📊 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        # Critical assessment
        print("\n🎯 CRITICAL ASSESSMENT:")
        
        # Check authentication
        auth_passed = any(r["test"] == "User Authentication" and r["success"] for r in self.test_results)
        balance_passed = any(r["test"] == "User Balance Verification" and r["success"] for r in self.test_results)
        credentials_passed = any(r["test"] == "NOWPayments Credentials" and r["success"] for r in self.test_results)
        withdrawal_passed = any(r["test"] == "Real Blockchain Withdrawal" and r["success"] for r in self.test_results)
        
        if auth_passed and balance_passed:
            print("✅ User authentication and balance verification successful")
        else:
            print("❌ User authentication or balance issues detected")
        
        if credentials_passed:
            print("✅ New NOWPayments credentials are valid and accessible")
        else:
            print("❌ NOWPayments credentials may not be activated yet")
        
        if withdrawal_passed:
            print("✅ Real blockchain withdrawals are now working!")
            print("🎉 CUSTODY ACTIVATION CONFIRMED - Live crypto transfers enabled!")
        else:
            print("❌ Real blockchain withdrawals still failing")
            print("⏳ Custody activation may still be in progress")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "custody_activated": withdrawal_passed,
            "credentials_valid": credentials_passed,
            "user_verified": auth_passed and balance_passed,
            "test_results": self.test_results
        }

async def main():
    """Main test execution"""
    async with NOWPaymentsCustodyTester(BACKEND_URL) as tester:
        results = await tester.run_comprehensive_test()
        
        # Exit with appropriate code
        if results["custody_activated"]:
            print("\n🎉 SUCCESS: NOWPayments custody activation confirmed!")
            sys.exit(0)
        else:
            print("\n⏳ PENDING: Custody activation still in progress")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())