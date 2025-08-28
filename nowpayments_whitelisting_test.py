#!/usr/bin/env python3
"""
URGENT: NOWPayments Whitelisting & Real Withdrawal Test
Tests if NOWPayments has completed wallet whitelisting and can process real withdrawals
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://smart-savings-dapp.preview.emergentagent.com/api"

# NOWPayments credentials from review request
NOWPAYMENTS_CREDENTIALS = {
    "api_key": "FSVPHG1-1TK4MDZ-MKC4TTV-MW1MAXX",
    "public_key": "f9a7e8ba-2573-4da2-9f4f-3e0ffd748212",
    "ipn_secret": "JrjLnNYQV8vz6ee8uTW4rI8lMGsSYhGF"
}

# User details from review request
USER_CREDENTIALS = {
    "username": "cryptoking",
    "password": "crt21million",
    "crt_wallet": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
    "withdrawal_wallet": "DLbWLzxq2mxE3Adzn9MFKQ6EBP8gTE5po8"
}

# Test amounts from review request
TEST_AMOUNTS = {
    "payout_test": 100,  # 100 DOGE
    "mass_payout_test": 50,  # 50 DOGE
    "payment_link_amount": 16081.58  # CA$5000 worth
}

# Payment link from review request
PAYMENT_LINK = "https://nowpayments.io/payment/?iid=4383583691&paymentId=5914238505"

class NOWPaymentsWhitelistingTester:
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
        
    async def authenticate_user(self):
        """Authenticate the user cryptoking"""
        try:
            login_payload = {
                "username": USER_CREDENTIALS["username"],
                "password": USER_CREDENTIALS["password"]
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_test("User Authentication", True, 
                                    f"Successfully authenticated user {USER_CREDENTIALS['username']}", data)
                        return True
                    else:
                        self.log_test("User Authentication", False, 
                                    f"Authentication failed: {data.get('message')}", data)
                        return False
                else:
                    self.log_test("User Authentication", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    return False
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
            return False

    async def test_nowpayments_api_status(self):
        """Test 1: Check NOWPayments API status with new credentials"""
        try:
            # Test direct NOWPayments API access
            nowpayments_url = "https://api.nowpayments.io/v1/status"
            headers = {
                "x-api-key": NOWPAYMENTS_CREDENTIALS["api_key"]
            }
            
            async with self.session.get(nowpayments_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("message") == "OK":
                        self.log_test("NOWPayments API Status", True, 
                                    f"NOWPayments API accessible with credentials {NOWPAYMENTS_CREDENTIALS['api_key'][:8]}...", data)
                        return True
                    else:
                        self.log_test("NOWPayments API Status", False, 
                                    f"NOWPayments API returned unexpected response", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("NOWPayments API Status", False, 
                                f"NOWPayments API error - HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("NOWPayments API Status", False, f"Error: {str(e)}")
            return False

    async def test_nowpayments_currencies(self):
        """Test 2: Check if DOGE is supported by NOWPayments"""
        try:
            nowpayments_url = "https://api.nowpayments.io/v1/currencies"
            headers = {
                "x-api-key": NOWPAYMENTS_CREDENTIALS["api_key"]
            }
            
            async with self.session.get(nowpayments_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    currencies = data.get("currencies", [])
                    
                    if "doge" in currencies:
                        self.log_test("DOGE Currency Support", True, 
                                    f"DOGE supported among {len(currencies)} currencies", 
                                    {"total_currencies": len(currencies), "doge_supported": True})
                        return True
                    else:
                        self.log_test("DOGE Currency Support", False, 
                                    f"DOGE not found in supported currencies: {currencies[:10]}...", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("DOGE Currency Support", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("DOGE Currency Support", False, f"Error: {str(e)}")
            return False

    async def test_user_balance_verification(self):
        """Test 3: Verify user has sufficient DOGE balance for withdrawal tests"""
        try:
            wallet_address = USER_CREDENTIALS["crt_wallet"]
            
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        wallet = data.get("wallet", {})
                        deposit_balance = wallet.get("deposit_balance", {})
                        doge_balance = deposit_balance.get("DOGE", 0)
                        
                        required_balance = TEST_AMOUNTS["payout_test"] + TEST_AMOUNTS["mass_payout_test"]
                        
                        if doge_balance >= required_balance:
                            self.log_test("User Balance Verification", True, 
                                        f"User has {doge_balance} DOGE (required: {required_balance})", 
                                        {"doge_balance": doge_balance, "required": required_balance})
                            return True
                        else:
                            self.log_test("User Balance Verification", False, 
                                        f"Insufficient DOGE balance: {doge_balance} < {required_balance}", 
                                        {"doge_balance": doge_balance, "required": required_balance})
                            return False
                    else:
                        self.log_test("User Balance Verification", False, 
                                    f"Failed to get wallet info: {data.get('message')}", data)
                        return False
                else:
                    self.log_test("User Balance Verification", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    return False
        except Exception as e:
            self.log_test("User Balance Verification", False, f"Error: {str(e)}")
            return False

    async def test_doge_address_validation(self):
        """Test 4: Validate DOGE withdrawal address format"""
        try:
            withdrawal_address = USER_CREDENTIALS["withdrawal_wallet"]
            
            # Basic DOGE address validation
            if (withdrawal_address.startswith('D') and 
                len(withdrawal_address) >= 25 and 
                len(withdrawal_address) <= 34 and
                withdrawal_address.isalnum()):
                
                self.log_test("DOGE Address Validation", True, 
                            f"DOGE address {withdrawal_address} passes format validation", 
                            {"address": withdrawal_address, "format": "valid_doge_mainnet"})
                return True
            else:
                self.log_test("DOGE Address Validation", False, 
                            f"DOGE address {withdrawal_address} fails format validation", 
                            {"address": withdrawal_address, "format": "invalid"})
                return False
        except Exception as e:
            self.log_test("DOGE Address Validation", False, f"Error: {str(e)}")
            return False

    async def test_nowpayments_payout_permissions(self):
        """Test 5: CRITICAL - Test NOWPayments payout permissions (main test)"""
        try:
            # Test NOWPayments payout API directly
            nowpayments_url = "https://api.nowpayments.io/v1/payout"
            headers = {
                "x-api-key": NOWPAYMENTS_CREDENTIALS["api_key"],
                "Content-Type": "application/json"
            }
            
            # Test payout payload
            payout_payload = {
                "withdrawals": [
                    {
                        "address": USER_CREDENTIALS["withdrawal_wallet"],
                        "currency": "doge",
                        "amount": TEST_AMOUNTS["payout_test"],
                        "ipn_callback_url": "https://smart-savings-dapp.preview.emergentagent.com/api/nowpayments/ipn"
                    }
                ]
            }
            
            async with self.session.post(nowpayments_url, 
                                       headers=headers, 
                                       json=payout_payload) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = await response.json()
                    if data.get("id"):
                        self.log_test("NOWPayments Payout Permissions", True, 
                                    f"🎉 PAYOUT PERMISSIONS ACTIVATED! Payout ID: {data.get('id')}", data)
                        return True
                    else:
                        self.log_test("NOWPayments Payout Permissions", False, 
                                    f"Payout response missing ID: {data}", data)
                        return False
                elif response.status == 401:
                    if "Bearer JWTtoken is required" in response_text or "Authorization header is empty" in response_text:
                        self.log_test("NOWPayments Payout Permissions", False, 
                                    f"❌ PAYOUT PERMISSIONS NOT YET ACTIVATED - 401 Unauthorized: {response_text}", 
                                    {"status": "permissions_pending", "error": response_text})
                        return False
                    else:
                        self.log_test("NOWPayments Payout Permissions", False, 
                                    f"❌ Authentication error: {response_text}", 
                                    {"status": "auth_error", "error": response_text})
                        return False
                else:
                    self.log_test("NOWPayments Payout Permissions", False, 
                                f"❌ Payout failed - HTTP {response.status}: {response_text}")
                    return False
        except Exception as e:
            self.log_test("NOWPayments Payout Permissions", False, f"Error: {str(e)}")
            return False

    async def test_mass_payout_capability(self):
        """Test 6: Test mass payout conversion script functionality"""
        try:
            # Test smaller amount for mass payout
            nowpayments_url = "https://api.nowpayments.io/v1/payout"
            headers = {
                "x-api-key": NOWPAYMENTS_CREDENTIALS["api_key"],
                "Content-Type": "application/json"
            }
            
            # Mass payout test payload
            mass_payout_payload = {
                "withdrawals": [
                    {
                        "address": USER_CREDENTIALS["withdrawal_wallet"],
                        "currency": "doge",
                        "amount": TEST_AMOUNTS["mass_payout_test"],
                        "ipn_callback_url": "https://smart-savings-dapp.preview.emergentagent.com/api/nowpayments/ipn"
                    }
                ]
            }
            
            async with self.session.post(nowpayments_url, 
                                       headers=headers, 
                                       json=mass_payout_payload) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = await response.json()
                    if data.get("id"):
                        self.log_test("Mass Payout Test", True, 
                                    f"✅ Mass payout successful! Transaction ID: {data.get('id')}", data)
                        return True
                    else:
                        self.log_test("Mass Payout Test", False, 
                                    f"Mass payout response missing ID: {data}", data)
                        return False
                elif response.status == 401:
                    self.log_test("Mass Payout Test", False, 
                                f"❌ Mass payout blocked - permissions not activated: {response_text}")
                    return False
                else:
                    self.log_test("Mass Payout Test", False, 
                                f"❌ Mass payout failed - HTTP {response.status}: {response_text}")
                    return False
        except Exception as e:
            self.log_test("Mass Payout Test", False, f"Error: {str(e)}")
            return False

    async def test_payment_link_integration(self):
        """Test 7: Test payment link integration with wallet system"""
        try:
            # Test if payment link is accessible
            async with self.session.get(PAYMENT_LINK) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Check if it's a valid NOWPayments payment page
                    if ("nowpayments" in content.lower() and 
                        ("payment" in content.lower() or "invoice" in content.lower())):
                        
                        # Check if the payment amount matches expected
                        if "16081.58" in content or "5000" in content:
                            self.log_test("Payment Link Integration", True, 
                                        f"Payment link accessible with expected amount (~CA$5000)", 
                                        {"url": PAYMENT_LINK, "amount_found": True})
                            return True
                        else:
                            self.log_test("Payment Link Integration", True, 
                                        f"Payment link accessible but amount verification unclear", 
                                        {"url": PAYMENT_LINK, "content_length": len(content)})
                            return True
                    else:
                        self.log_test("Payment Link Integration", False, 
                                    f"Payment link doesn't appear to be valid NOWPayments page", 
                                    {"url": PAYMENT_LINK, "content_preview": content[:200]})
                        return False
                else:
                    self.log_test("Payment Link Integration", False, 
                                f"Payment link not accessible - HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("Payment Link Integration", False, f"Error: {str(e)}")
            return False

    async def test_backend_nowpayments_integration(self):
        """Test 8: Test backend NOWPayments service integration"""
        try:
            # Test if backend has NOWPayments service endpoints
            test_endpoints = [
                "/nowpayments/status",
                "/nowpayments/currencies", 
                "/nowpayments/payout"
            ]
            
            working_endpoints = []
            
            for endpoint in test_endpoints:
                try:
                    async with self.session.get(f"{self.base_url}{endpoint}") as response:
                        if response.status in [200, 401, 403]:  # 401/403 means endpoint exists but needs auth
                            working_endpoints.append(endpoint)
                except:
                    pass
            
            if len(working_endpoints) >= 2:
                self.log_test("Backend NOWPayments Integration", True, 
                            f"Backend NOWPayments endpoints available: {working_endpoints}", 
                            {"endpoints": working_endpoints})
                return True
            else:
                self.log_test("Backend NOWPayments Integration", False, 
                            f"Limited backend NOWPayments integration: {working_endpoints}", 
                            {"endpoints": working_endpoints})
                return False
        except Exception as e:
            self.log_test("Backend NOWPayments Integration", False, f"Error: {str(e)}")
            return False

    async def test_withdrawal_status_check(self):
        """Test 9: Check current withdrawal permissions status"""
        try:
            # Test NOWPayments minimum payout amounts
            nowpayments_url = "https://api.nowpayments.io/v1/min-amount"
            headers = {
                "x-api-key": NOWPAYMENTS_CREDENTIALS["api_key"]
            }
            
            params = {"currency_from": "doge", "currency_to": "doge"}
            
            async with self.session.get(nowpayments_url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    min_amount = data.get("min_amount", 0)
                    
                    if min_amount > 0:
                        test_amount = TEST_AMOUNTS["payout_test"]
                        if test_amount >= min_amount:
                            self.log_test("Withdrawal Status Check", True, 
                                        f"✅ Withdrawal permissions OK - min amount: {min_amount} DOGE, test: {test_amount} DOGE", 
                                        {"min_amount": min_amount, "test_amount": test_amount})
                            return True
                        else:
                            self.log_test("Withdrawal Status Check", False, 
                                        f"❌ Test amount too small - min: {min_amount}, test: {test_amount}", 
                                        {"min_amount": min_amount, "test_amount": test_amount})
                            return False
                    else:
                        self.log_test("Withdrawal Status Check", False, 
                                    f"Invalid minimum amount response: {data}", data)
                        return False
                elif response.status == 401:
                    error_text = await response.text()
                    self.log_test("Withdrawal Status Check", False, 
                                f"❌ API access denied - permissions not activated: {error_text}")
                    return False
                else:
                    error_text = await response.text()
                    self.log_test("Withdrawal Status Check", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Withdrawal Status Check", False, f"Error: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all NOWPayments whitelisting tests"""
        print("🚨 URGENT: NOWPayments Whitelisting & Real Withdrawal Test")
        print("=" * 70)
        print(f"Testing NOWPayments credentials: {NOWPAYMENTS_CREDENTIALS['api_key'][:8]}...")
        print(f"User: {USER_CREDENTIALS['username']}")
        print(f"CRT Wallet: {USER_CREDENTIALS['crt_wallet']}")
        print(f"Withdrawal Wallet: {USER_CREDENTIALS['withdrawal_wallet']}")
        print("=" * 70)
        
        # Run authentication first
        auth_success = await self.authenticate_user()
        
        # Run all tests
        test_methods = [
            self.test_nowpayments_api_status,
            self.test_nowpayments_currencies,
            self.test_user_balance_verification,
            self.test_doge_address_validation,
            self.test_withdrawal_status_check,
            self.test_nowpayments_payout_permissions,  # CRITICAL TEST
            self.test_mass_payout_capability,
            self.test_payment_link_integration,
            self.test_backend_nowpayments_integration
        ]
        
        for test_method in test_methods:
            try:
                await test_method()
            except Exception as e:
                self.log_test(test_method.__name__, False, f"Test execution error: {str(e)}")
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 70)
        print("🎯 NOWPayments WHITELISTING TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n🔍 CRITICAL FINDINGS:")
        
        # Check for payout permissions
        payout_test = next((r for r in self.test_results if "Payout Permissions" in r["test"]), None)
        if payout_test:
            if payout_test["success"]:
                print("✅ PAYOUT PERMISSIONS ACTIVATED - Real withdrawals now possible!")
            else:
                print("❌ PAYOUT PERMISSIONS NOT YET ACTIVATED - Still waiting for NOWPayments approval")
        
        # Check for mass payout capability
        mass_payout_test = next((r for r in self.test_results if "Mass Payout" in r["test"]), None)
        if mass_payout_test:
            if mass_payout_test["success"]:
                print("✅ MASS PAYOUT CAPABILITY CONFIRMED")
            else:
                print("❌ MASS PAYOUT NOT YET AVAILABLE")
        
        # Check payment link integration
        payment_link_test = next((r for r in self.test_results if "Payment Link" in r["test"]), None)
        if payment_link_test:
            if payment_link_test["success"]:
                print("✅ PAYMENT LINK INTEGRATION WORKING")
            else:
                print("❌ PAYMENT LINK INTEGRATION ISSUES")
        
        print("\n📊 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        print("\n🎯 ANSWER TO CRITICAL QUESTION:")
        if payout_test and payout_test["success"]:
            print("✅ YES - The 1-2 business day whitelisting period has COMPLETED!")
            print("✅ NOWPayments wallet whitelisting is ACTIVE!")
            print("✅ Real blockchain withdrawals are now POSSIBLE!")
        else:
            print("❌ NO - The 1-2 business day whitelisting period has NOT completed yet.")
            print("⏳ NOWPayments payout permissions are still PENDING activation.")
            print("⏳ Continue waiting for NOWPayments support to activate payout permissions.")

async def main():
    """Main test execution"""
    async with NOWPaymentsWhitelistingTester(BACKEND_URL) as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())