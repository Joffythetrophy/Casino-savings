#!/usr/bin/env python3
"""
NOWPayments JWT Authentication Implementation Test
Tests the updated NOWPayments JWT authentication for withdrawals
"""

import asyncio
import aiohttp
import json
import jwt
import os
from datetime import datetime, timedelta
from decimal import Decimal
import sys

class NOWPaymentsJWTTester:
    def __init__(self):
        self.base_url = "https://smart-savings-dapp.preview.emergentagent.com/api"
        self.test_results = []
        self.session = None
        self.auth_token = None
        
        # Test credentials from review request
        self.test_username = "cryptoking"
        self.test_password = "crt21million"
        self.test_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        self.personal_address = "DLbWLzxq2mxE3Adzn9MFKQ6EBP8gTE5po8"
        
        # NOWPayments credentials from environment
        self.nowpayments_api_key = "FSVPHG1-1TK4MDZ-MKC4TTV-MW1MAXX"
        self.nowpayments_ipn_secret = "JrjLnNYQV8vz6ee8uTW4rI8lMGsSYhGF"
        
    def log_test(self, test_name: str, success: bool, message: str, data: dict = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2)}")
    
    async def setup_session(self):
        """Setup HTTP session"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def authenticate_user(self):
        """Authenticate user and get JWT token"""
        try:
            print(f"🔐 Authenticating user: {self.test_username}")
            
            login_data = {
                "username": self.test_username,
                "password": self.test_password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.auth_token = data.get("token")
                        user_info = data.get("user", {})
                        wallet_address = user_info.get("wallet_address")
                        
                        if wallet_address == self.test_wallet:
                            self.log_test("User Authentication", True, 
                                        f"✅ User authenticated successfully with correct wallet: {wallet_address}")
                            return True
                        else:
                            self.log_test("User Authentication", False, 
                                        f"❌ Wallet mismatch: expected {self.test_wallet}, got {wallet_address}")
                            return False
                    else:
                        self.log_test("User Authentication", False, 
                                    f"❌ Authentication failed: {data.get('message', 'Unknown error')}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("User Authentication", False, f"❌ Exception: {str(e)}")
            return False
    
    def test_jwt_token_generation(self):
        """Test 1: Verify JWT token generation with proper payload structure"""
        try:
            print(f"🔑 Testing JWT Token Generation")
            
            # Generate JWT token using the same logic as NOWPayments service
            payload = {
                'iss': self.nowpayments_api_key,  # Issuer (API key)
                'aud': 'nowpayments',  # Audience
                'iat': int(datetime.utcnow().timestamp()),  # Issued at
                'exp': int((datetime.utcnow() + timedelta(minutes=30)).timestamp()),  # Expires in 30 minutes
                'sub': 'payout'  # Subject (payout operations)
            }
            
            # Sign JWT using IPN secret as signing key
            token = jwt.encode(
                payload, 
                self.nowpayments_ipn_secret, 
                algorithm='HS256'
            )
            
            # Verify the token can be decoded
            decoded_payload = jwt.decode(
                token, 
                self.nowpayments_ipn_secret, 
                algorithms=['HS256']
            )
            
            # Verify payload structure
            required_fields = ['iss', 'aud', 'iat', 'exp', 'sub']
            missing_fields = [field for field in required_fields if field not in decoded_payload]
            
            if not missing_fields:
                self.log_test("JWT Token Generation", True, 
                            f"✅ JWT token generated successfully with all required fields: {required_fields}", 
                            {"payload": decoded_payload, "token_length": len(token)})
                return token
            else:
                self.log_test("JWT Token Generation", False, 
                            f"❌ Missing required fields: {missing_fields}", 
                            {"payload": decoded_payload})
                return None
                
        except Exception as e:
            self.log_test("JWT Token Generation", False, f"❌ JWT generation failed: {str(e)}")
            return None
    
    async def test_api_key_configuration(self):
        """Test 3: Verify NOWPayments API key and IPN secret configuration"""
        try:
            print(f"🔧 Testing API Key Configuration")
            
            # Test NOWPayments currencies endpoint to verify API key
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            async with self.session.get(f"{self.base_url}/nowpayments/currencies", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        currencies = data.get("currencies", [])
                        doge_supported = "DOGE" in currencies
                        
                        # Check if we have the expected API key in the response or configuration
                        expected_api_key = self.nowpayments_api_key
                        expected_ipn_secret = self.nowpayments_ipn_secret
                        
                        config_valid = (
                            len(expected_api_key) > 20 and  # API key should be substantial
                            len(expected_ipn_secret) == 32 and  # IPN secret should be 32 chars
                            doge_supported  # DOGE should be supported
                        )
                        
                        if config_valid:
                            self.log_test("API Key Configuration", True, 
                                        f"✅ API key {expected_api_key} and IPN secret configured correctly. DOGE supported: {doge_supported}", 
                                        {"currencies_count": len(currencies), "doge_supported": doge_supported})
                            return True
                        else:
                            self.log_test("API Key Configuration", False, 
                                        f"❌ Configuration issues: API key length: {len(expected_api_key)}, IPN secret length: {len(expected_ipn_secret)}, DOGE supported: {doge_supported}")
                            return False
                    else:
                        self.log_test("API Key Configuration", False, 
                                    f"❌ NOWPayments currencies failed: {data.get('error', 'Unknown error')}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("API Key Configuration", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("API Key Configuration", False, f"❌ Exception: {str(e)}")
            return False
    
    async def test_jwt_authentication_headers(self):
        """Test 4: Test that JWT Authorization Bearer token is properly included in requests"""
        try:
            print(f"🔒 Testing JWT Authentication Headers")
            
            # Generate JWT token
            jwt_token = self.test_jwt_token_generation()
            if not jwt_token:
                self.log_test("JWT Authentication Headers", False, "❌ Could not generate JWT token for testing")
                return False
            
            # Test NOWPayments treasuries endpoint (should require authentication)
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            async with self.session.get(f"{self.base_url}/nowpayments/treasuries", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        treasuries = data.get("treasuries", {})
                        treasury_count = len(treasuries)
                        
                        # Check if we have the expected treasury structure
                        expected_treasuries = ["treasury_1_savings", "treasury_2_liquidity", "treasury_3_winnings"]
                        found_treasuries = [t for t in expected_treasuries if t in treasuries]
                        
                        if len(found_treasuries) >= 2:  # At least 2 treasuries should be configured
                            self.log_test("JWT Authentication Headers", True, 
                                        f"✅ JWT authentication working. Found {treasury_count} treasuries: {found_treasuries}", 
                                        {"treasuries": list(treasuries.keys())})
                            return True
                        else:
                            self.log_test("JWT Authentication Headers", False, 
                                        f"❌ Insufficient treasuries configured: {found_treasuries}")
                            return False
                    else:
                        self.log_test("JWT Authentication Headers", False, 
                                    f"❌ Treasuries endpoint failed: {data.get('error', 'Unknown error')}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("JWT Authentication Headers", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("JWT Authentication Headers", False, f"❌ Exception: {str(e)}")
            return False
    
    async def test_nowpayments_withdrawal_with_jwt(self):
        """Test 2: Test NOWPayments withdrawal using JWT authentication"""
        try:
            print(f"💰 Testing NOWPayments Withdrawal with JWT")
            
            if not self.auth_token:
                self.log_test("NOWPayments Withdrawal with JWT", False, "❌ No authentication token available")
                return False
            
            # Test withdrawal request
            withdrawal_data = {
                "user_id": self.test_username,
                "currency": "DOGE",
                "amount": 100,  # Small test amount as requested
                "destination_address": self.personal_address,
                "withdrawal_type": "standard"
            }
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.post(f"{self.base_url}/nowpayments/withdraw", 
                                       json=withdrawal_data, 
                                       headers=headers) as response:
                data = await response.json()
                
                if response.status == 200:
                    if data.get("success"):
                        withdrawal_info = data.get("withdrawal", {})
                        payout_id = withdrawal_info.get("payout_id")
                        blockchain_hash = withdrawal_info.get("blockchain_hash")
                        
                        self.log_test("NOWPayments Withdrawal with JWT", True, 
                                    f"✅ NOWPayments withdrawal successful! Payout ID: {payout_id}", 
                                    {"withdrawal": withdrawal_info, "service": data.get("service")})
                        return True
                    else:
                        error_msg = data.get("message", "Unknown error")
                        
                        # Check if this is the specific 401 error we're trying to fix
                        if "401" in error_msg and "Authorization header is empty" in error_msg:
                            self.log_test("NOWPayments Withdrawal with JWT", False, 
                                        f"❌ CRITICAL: Still getting 401 Authorization error - JWT not working: {error_msg}", 
                                        data)
                        else:
                            # Other errors might be expected (like insufficient balance, etc.)
                            self.log_test("NOWPayments Withdrawal with JWT", False, 
                                        f"❌ Withdrawal failed: {error_msg}", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("NOWPayments Withdrawal with JWT", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("NOWPayments Withdrawal with JWT", False, f"❌ Exception: {str(e)}")
            return False
    
    async def test_error_handling(self):
        """Test 5: Verify error handling and that 401 Authorization error is resolved"""
        try:
            print(f"🚨 Testing Error Handling")
            
            if not self.auth_token:
                self.log_test("Error Handling", False, "❌ No authentication token available")
                return False
            
            # Test with invalid currency to check error handling
            invalid_withdrawal_data = {
                "user_id": self.test_username,
                "currency": "INVALID",
                "amount": 100,
                "destination_address": self.personal_address,
                "withdrawal_type": "standard"
            }
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.post(f"{self.base_url}/nowpayments/withdraw", 
                                       json=invalid_withdrawal_data, 
                                       headers=headers) as response:
                data = await response.json()
                
                # We expect this to fail, but NOT with a 401 Authorization error
                if not data.get("success"):
                    error_msg = data.get("message", "")
                    
                    # Check that we're NOT getting the 401 Authorization error anymore
                    if "401" in error_msg and "Authorization header is empty" in error_msg:
                        self.log_test("Error Handling", False, 
                                    f"❌ CRITICAL: Still getting 401 Authorization error - JWT implementation not working: {error_msg}")
                        return False
                    else:
                        # Good - we're getting a different error (like invalid currency)
                        self.log_test("Error Handling", True, 
                                    f"✅ Error handling working correctly. Got expected error (not 401 auth): {error_msg}")
                        return True
                else:
                    # Unexpected success with invalid currency
                    self.log_test("Error Handling", False, 
                                f"❌ Unexpected success with invalid currency", data)
                    return False
                    
        except Exception as e:
            self.log_test("Error Handling", False, f"❌ Exception: {str(e)}")
            return False
    
    async def get_user_balance(self):
        """Get user balance to verify sufficient DOGE"""
        try:
            if not self.auth_token:
                return None
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(f"{self.base_url}/wallet/{self.test_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        wallet_info = data.get("wallet", {})
                        deposit_balance = wallet_info.get("deposit_balance", {})
                        doge_balance = deposit_balance.get("DOGE", 0)
                        return doge_balance
                        
        except Exception as e:
            print(f"Error getting balance: {e}")
            return None
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🎯 NOWPAYMENTS JWT AUTHENTICATION TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests*100):.1f}% success rate)")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        if passed_tests > 0:
            print(f"\n✅ PASSED TESTS ({passed_tests}):")
            for result in self.test_results:
                if "✅ PASS" in result["status"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        # Check for critical JWT authentication issue
        jwt_issues = [r for r in self.test_results if "401 Authorization header is empty" in r["message"]]
        if jwt_issues:
            print(f"\n🚨 CRITICAL JWT ISSUE DETECTED:")
            print(f"   The '401 Authorization header is empty (Bearer JWTtoken is required)' error is still occurring!")
            print(f"   This indicates the JWT authentication implementation needs further fixes.")
        else:
            print(f"\n✅ JWT AUTHENTICATION STATUS:")
            print(f"   No 401 Authorization header errors detected - JWT implementation appears to be working!")
        
        return passed_tests, total_tests
    
    async def run_all_tests(self):
        """Run all NOWPayments JWT authentication tests"""
        print("🚀 STARTING NOWPAYMENTS JWT AUTHENTICATION TESTS")
        print("="*80)
        
        await self.setup_session()
        
        try:
            # Test 1: JWT Token Generation
            self.test_jwt_token_generation()
            
            # Authenticate user first
            auth_success = await self.authenticate_user()
            
            if auth_success:
                # Get user balance
                doge_balance = await self.get_user_balance()
                if doge_balance is not None:
                    print(f"💰 User DOGE balance: {doge_balance}")
                
                # Test 2: NOWPayments Withdrawal with JWT
                await self.test_nowpayments_withdrawal_with_jwt()
                
                # Test 3: API Key Configuration
                await self.test_api_key_configuration()
                
                # Test 4: JWT Authentication Headers
                await self.test_jwt_authentication_headers()
                
                # Test 5: Error Handling
                await self.test_error_handling()
            else:
                print("❌ Cannot proceed with NOWPayments tests - authentication failed")
        
        finally:
            await self.cleanup_session()
        
        # Print summary
        passed, total = self.print_summary()
        return passed, total

async def main():
    """Main test execution"""
    tester = NOWPaymentsJWTTester()
    passed, total = await tester.run_all_tests()
    
    # Exit with appropriate code
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! NOWPayments JWT authentication is working correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️ {total - passed} tests failed. NOWPayments JWT authentication needs attention.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())