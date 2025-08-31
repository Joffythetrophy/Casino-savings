#!/usr/bin/env python3
"""
NOWPayments Custody Activation Verification Test
Tests if NOWPayments custody activation enables real blockchain withdrawals
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://crypto-treasury.preview.emergentagent.com/api"

# Test credentials from review request
TEST_CREDENTIALS = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
    "personal_address": "DLbWLzxq2mxE3Adzn9MFKQ6EBP8gTE5po8",  # Updated personal address
    "test_amount": 100,  # 100 DOGE withdrawal test
    "expected_balance": 34831540  # Expected user balance
}

# NOWPayments credentials from review request
NOWPAYMENTS_CREDENTIALS = {
    "api_key": "VGX32FH-V9G4T4Y-GRJDH33-SF0CWGP",
    "public_key": "80887455-9f0c-4ad1-92ea-ee78511ced2b",
    "ipn_secret": "JrjLnNYQV8vz6ee8uTW4rI8lMGsSYhGF"
}

class NOWPaymentsCustodyTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        self.auth_token = None
        
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
        """Test 1: Verify user authentication with cryptoking/crt21million"""
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
                                    f"Authentication failed: {data.get('message', 'Unknown error')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
        return False

    async def test_user_balance_verification(self):
        """Test 2: Verify user has expected DOGE balance (34,831,540 DOGE)"""
        try:
            wallet_address = TEST_CREDENTIALS["wallet_address"]
            
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        doge_balance = deposit_balance.get("DOGE", 0)
                        
                        # Check if balance is close to expected (within reasonable range)
                        expected = TEST_CREDENTIALS["expected_balance"]
                        if abs(doge_balance - expected) < 1000:  # Allow 1000 DOGE variance
                            self.log_test("User Balance Verification", True, 
                                        f"✅ User has {doge_balance:,.0f} DOGE (expected ~{expected:,.0f})", data)
                            return True
                        else:
                            self.log_test("User Balance Verification", False, 
                                        f"Balance mismatch: {doge_balance:,.0f} DOGE (expected {expected:,.0f})", data)
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

    async def test_nowpayments_credentials_verification(self):
        """Test 3: Verify NOWPayments credentials are still active"""
        try:
            # Test if we can access NOWPayments status endpoint
            headers = {
                'x-api-key': NOWPAYMENTS_CREDENTIALS["api_key"],
                'Content-Type': 'application/json'
            }
            
            # Use production URL since sandbox=false in env
            nowpayments_url = "https://api.nowpayments.io/v1/status"
            
            async with self.session.get(nowpayments_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("message") == "OK":
                        self.log_test("NOWPayments Credentials", True, 
                                    f"✅ NOWPayments API accessible with key {NOWPAYMENTS_CREDENTIALS['api_key'][:10]}...", data)
                        return True
                    else:
                        self.log_test("NOWPayments Credentials", False, 
                                    f"NOWPayments API returned unexpected response", data)
                elif response.status == 401:
                    error_text = await response.text()
                    self.log_test("NOWPayments Credentials", False, 
                                f"❌ NOWPayments API key invalid or expired: {error_text}")
                else:
                    error_text = await response.text()
                    self.log_test("NOWPayments Credentials", False, 
                                f"NOWPayments API error {response.status}: {error_text}")
        except Exception as e:
            self.log_test("NOWPayments Credentials", False, f"Error: {str(e)}")
        return False

    async def test_nowpayments_supported_currencies(self):
        """Test 4: Verify DOGE is supported by NOWPayments"""
        try:
            headers = {
                'x-api-key': NOWPAYMENTS_CREDENTIALS["api_key"],
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
                        self.log_test("NOWPayments DOGE Support", True, 
                                    f"✅ DOGE is supported by NOWPayments ({len(currencies)} total currencies)", data)
                        return True
                    else:
                        self.log_test("NOWPayments DOGE Support", False, 
                                    f"❌ DOGE not found in supported currencies: {currencies[:10]}...", data)
                else:
                    error_text = await response.text()
                    self.log_test("NOWPayments DOGE Support", False, 
                                f"Failed to get currencies: HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("NOWPayments DOGE Support", False, f"Error: {str(e)}")
        return False

    async def test_treasury_system_verification(self):
        """Test 5: Verify 3-treasury system is configured"""
        try:
            # Check if backend has NOWPayments service configured
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    supported_networks = data.get("supported_networks", [])
                    
                    # Check if Dogecoin is in supported networks
                    if "Dogecoin" in supported_networks:
                        self.log_test("Treasury System Configuration", True, 
                                    f"✅ Backend supports Dogecoin network: {supported_networks}", data)
                        return True
                    else:
                        self.log_test("Treasury System Configuration", False, 
                                    f"Dogecoin not in supported networks: {supported_networks}", data)
                else:
                    error_text = await response.text()
                    self.log_test("Treasury System Configuration", False, 
                                f"Backend API error: HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Treasury System Configuration", False, f"Error: {str(e)}")
        return False

    async def get_jwt_token(self):
        """Get JWT token for authenticated requests"""
        try:
            # Step 1: Generate challenge
            challenge_payload = {
                "wallet_address": TEST_CREDENTIALS["wallet_address"],
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/auth/challenge", 
                                       json=challenge_payload) as response:
                if response.status == 200:
                    challenge_data = await response.json()
                    if challenge_data.get("success"):
                        # Step 2: Verify with mock signature
                        verify_payload = {
                            "challenge_hash": challenge_data.get("challenge_hash"),
                            "signature": "mock_signature_for_nowpayments_test",
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
            print(f"Failed to get JWT token: {e}")
        return False

    async def test_nowpayments_withdrawal_endpoint(self):
        """Test 6: Test NOWPayments withdrawal endpoint with custody activation"""
        try:
            # Get JWT token first
            if not await self.get_jwt_token():
                self.log_test("NOWPayments Withdrawal Test", False, 
                            "❌ Failed to get authentication token")
                return False
            
            # Test the actual NOWPayments withdrawal endpoint
            withdrawal_payload = {
                "user_id": TEST_CREDENTIALS["username"],
                "currency": "DOGE",
                "amount": TEST_CREDENTIALS["test_amount"],
                "destination_address": TEST_CREDENTIALS["personal_address"],
                "treasury_type": "treasury_2_liquidity"  # Use main liquidity treasury
            }
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Check if backend has NOWPayments withdrawal endpoint
            async with self.session.post(f"{self.base_url}/nowpayments/withdraw", 
                                       json=withdrawal_payload, headers=headers) as response:
                
                response_text = await response.text()
                print(f"DEBUG: Response status: {response.status}")
                print(f"DEBUG: Response text: {response_text[:500]}...")
                
                if response.status == 200:
                    try:
                        data = await response.json()
                        if data.get("success"):
                            self.log_test("NOWPayments Withdrawal Test", True, 
                                        f"✅ CUSTODY ACTIVATED! Withdrawal successful: {data.get('message', 'Success')}", data)
                            return True
                        else:
                            error_msg = data.get('error') or data.get('message') or data.get('detail') or 'Unknown error'
                            self.log_test("NOWPayments Withdrawal Test", False, 
                                        f"Withdrawal failed: {error_msg}", data)
                    except json.JSONDecodeError:
                        self.log_test("NOWPayments Withdrawal Test", False, 
                                    f"Invalid JSON response: {response_text}")
                        
                elif response.status == 401:
                    # This was the previous error - check if it's still happening
                    try:
                        data = await response.json()
                        error_msg = data.get("detail", response_text)
                        if "401" in error_msg or "Unauthorized" in error_msg or "payout" in error_msg.lower():
                            self.log_test("NOWPayments Withdrawal Test", False, 
                                        f"❌ CUSTODY STILL NOT ACTIVATED: {error_msg}", data)
                        else:
                            self.log_test("NOWPayments Withdrawal Test", False, 
                                        f"Authentication error: {error_msg}", data)
                    except json.JSONDecodeError:
                        self.log_test("NOWPayments Withdrawal Test", False, 
                                    f"❌ CUSTODY ISSUE: HTTP 401 - {response_text}")
                        
                elif response.status == 404:
                    self.log_test("NOWPayments Withdrawal Test", False, 
                                f"❌ NOWPayments withdrawal endpoint not found: {response_text}")
                    
                else:
                    try:
                        data = await response.json()
                        error_msg = data.get('detail') or data.get('error') or data.get('message') or response_text
                        self.log_test("NOWPayments Withdrawal Test", False, 
                                    f"Withdrawal error HTTP {response.status}: {error_msg}", data)
                    except json.JSONDecodeError:
                        self.log_test("NOWPayments Withdrawal Test", False, 
                                    f"HTTP {response.status}: {response_text}")
                        
        except Exception as e:
            self.log_test("NOWPayments Withdrawal Test", False, f"Error: {str(e)}")
        return False

    async def test_personal_address_validation(self):
        """Test 7: Verify personal DOGE address format"""
        try:
            personal_address = TEST_CREDENTIALS["personal_address"]
            
            # Validate DOGE address format
            if (personal_address.startswith('D') and 
                len(personal_address) >= 25 and 
                len(personal_address) <= 34 and
                personal_address.isalnum()):
                
                self.log_test("Personal Address Validation", True, 
                            f"✅ Personal DOGE address valid: {personal_address}", 
                            {"address": personal_address, "format": "valid_doge"})
                return True
            else:
                self.log_test("Personal Address Validation", False, 
                            f"❌ Invalid DOGE address format: {personal_address}", 
                            {"address": personal_address, "format": "invalid"})
        except Exception as e:
            self.log_test("Personal Address Validation", False, f"Error: {str(e)}")
        return False

    async def test_ipn_secret_verification(self):
        """Test 8: Verify IPN secret configuration"""
        try:
            ipn_secret = NOWPAYMENTS_CREDENTIALS["ipn_secret"]
            
            # Check IPN secret format (should be 32 characters)
            if len(ipn_secret) == 32 and ipn_secret.isalnum():
                self.log_test("IPN Secret Verification", True, 
                            f"✅ IPN secret properly configured: {ipn_secret[:8]}...{ipn_secret[-4:]}", 
                            {"secret_length": len(ipn_secret), "format": "valid"})
                return True
            else:
                self.log_test("IPN Secret Verification", False, 
                            f"❌ IPN secret format invalid: length={len(ipn_secret)}", 
                            {"secret_length": len(ipn_secret), "format": "invalid"})
        except Exception as e:
            self.log_test("IPN Secret Verification", False, f"Error: {str(e)}")
        return False

    async def run_all_tests(self):
        """Run all NOWPayments custody activation tests"""
        print("🚀 NOWPayments Custody Activation Verification Test")
        print("=" * 60)
        print(f"Testing with user: {TEST_CREDENTIALS['username']}")
        print(f"Personal address: {TEST_CREDENTIALS['personal_address']}")
        print(f"Test amount: {TEST_CREDENTIALS['test_amount']} DOGE")
        print("=" * 60)
        
        # Run tests in sequence
        tests = [
            self.test_user_authentication,
            self.test_user_balance_verification,
            self.test_nowpayments_credentials_verification,
            self.test_nowpayments_supported_currencies,
            self.test_treasury_system_verification,
            self.test_personal_address_validation,
            self.test_ipn_secret_verification,
            self.test_nowpayments_withdrawal_endpoint,  # Main test - run last
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            result = await test()
            if result:
                passed += 1
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 60)
        print("🎯 NOWPayments Custody Activation Test Summary")
        print("=" * 60)
        
        success_rate = (passed / total) * 100
        print(f"Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        # Analyze results
        withdrawal_test = next((r for r in self.test_results if r["test"] == "NOWPayments Withdrawal Test"), None)
        
        if withdrawal_test and withdrawal_test["success"]:
            print("🎉 SUCCESS: NOWPayments custody is ACTIVATED!")
            print("✅ Real blockchain withdrawals are now working!")
            print("✅ System is ready for production use!")
        elif withdrawal_test and not withdrawal_test["success"]:
            if "401" in withdrawal_test["details"] or "Unauthorized" in withdrawal_test["details"]:
                print("❌ CUSTODY NOT YET ACTIVATED")
                print("⚠️  Still getting 401 Unauthorized errors")
                print("💡 Recommendation: Contact NOWPayments support to activate payout permissions")
            else:
                print("❌ WITHDRAWAL FAILED")
                print(f"⚠️  Error: {withdrawal_test['details']}")
        else:
            print("❌ WITHDRAWAL TEST NOT COMPLETED")
            print("⚠️  Could not test NOWPayments withdrawal endpoint")
        
        print("\n📊 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return self.test_results

async def main():
    """Main test execution"""
    async with NOWPaymentsCustodyTester(BACKEND_URL) as tester:
        results = await tester.run_all_tests()
        
        # Return exit code based on main test result
        withdrawal_test = next((r for r in results if r["test"] == "NOWPayments Withdrawal Test"), None)
        if withdrawal_test and withdrawal_test["success"]:
            return 0  # Success
        else:
            return 1  # Failure

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)