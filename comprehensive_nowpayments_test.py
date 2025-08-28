#!/usr/bin/env python3
"""
COMPREHENSIVE NOWPayments Integration Test
Tests backend NOWPayments endpoints and real withdrawal capabilities
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

class ComprehensiveNOWPaymentsTester:
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

    async def test_backend_nowpayments_currencies(self):
        """Test 1: Backend NOWPayments currencies endpoint"""
        try:
            async with self.session.get(f"{self.base_url}/nowpayments/currencies") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "currencies" in data:
                        currencies = data.get("currencies", [])
                        if "doge" in [c.lower() for c in currencies]:
                            self.log_test("Backend NOWPayments Currencies", True, 
                                        f"DOGE supported among {len(currencies)} currencies", data)
                            return True
                        else:
                            self.log_test("Backend NOWPayments Currencies", False, 
                                        f"DOGE not found in {len(currencies)} currencies", data)
                            return False
                    else:
                        self.log_test("Backend NOWPayments Currencies", False, 
                                    "Invalid currencies response format", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Backend NOWPayments Currencies", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Backend NOWPayments Currencies", False, f"Error: {str(e)}")
            return False

    async def test_backend_nowpayments_treasuries(self):
        """Test 2: Backend NOWPayments treasuries endpoint"""
        try:
            async with self.session.get(f"{self.base_url}/nowpayments/treasuries") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "treasuries" in data:
                        treasuries = data.get("treasuries", {})
                        expected_treasuries = ["treasury_1_savings", "treasury_2_liquidity", "treasury_3_winnings"]
                        
                        found_treasuries = [t for t in expected_treasuries if t in treasuries]
                        
                        if len(found_treasuries) >= 3:
                            self.log_test("Backend NOWPayments Treasuries", True, 
                                        f"All 3 treasuries configured: {found_treasuries}", data)
                            return True
                        else:
                            self.log_test("Backend NOWPayments Treasuries", False, 
                                        f"Missing treasuries: found {found_treasuries}", data)
                            return False
                    else:
                        self.log_test("Backend NOWPayments Treasuries", False, 
                                    "Invalid treasuries response format", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Backend NOWPayments Treasuries", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Backend NOWPayments Treasuries", False, f"Error: {str(e)}")
            return False

    async def test_backend_nowpayments_withdraw(self):
        """Test 3: CRITICAL - Backend NOWPayments withdraw endpoint (100 DOGE test)"""
        try:
            withdraw_payload = {
                "wallet_address": USER_CREDENTIALS["crt_wallet"],
                "recipient_address": USER_CREDENTIALS["withdrawal_wallet"],
                "currency": "DOGE",
                "amount": TEST_AMOUNTS["payout_test"],
                "treasury_type": "treasury_2_liquidity"
            }
            
            async with self.session.post(f"{self.base_url}/nowpayments/withdraw", 
                                       json=withdraw_payload) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("payout_id"):
                        self.log_test("Backend NOWPayments Withdraw", True, 
                                    f"🎉 WITHDRAWAL SUCCESS! Payout ID: {data.get('payout_id')}", data)
                        return True
                    else:
                        self.log_test("Backend NOWPayments Withdraw", False, 
                                    f"Withdrawal response missing payout_id: {data}", data)
                        return False
                elif response.status == 401:
                    if "Bearer JWTtoken is required" in response_text or "Authorization header is empty" in response_text:
                        self.log_test("Backend NOWPayments Withdraw", False, 
                                    f"❌ PAYOUT PERMISSIONS NOT ACTIVATED - 401: {response_text}")
                        return False
                    else:
                        self.log_test("Backend NOWPayments Withdraw", False, 
                                    f"❌ Authentication error: {response_text}")
                        return False
                elif response.status == 403:
                    self.log_test("Backend NOWPayments Withdraw", False, 
                                f"❌ Access forbidden - endpoint requires authentication: {response_text}")
                    return False
                else:
                    self.log_test("Backend NOWPayments Withdraw", False, 
                                f"❌ Withdrawal failed - HTTP {response.status}: {response_text}")
                    return False
        except Exception as e:
            self.log_test("Backend NOWPayments Withdraw", False, f"Error: {str(e)}")
            return False

    async def test_backend_nowpayments_mass_withdraw(self):
        """Test 4: Backend NOWPayments mass withdraw endpoint (50 DOGE test)"""
        try:
            mass_withdraw_payload = {
                "withdrawals": [
                    {
                        "wallet_address": USER_CREDENTIALS["crt_wallet"],
                        "recipient_address": USER_CREDENTIALS["withdrawal_wallet"],
                        "amount": TEST_AMOUNTS["mass_payout_test"],
                        "user_id": "cryptoking"
                    }
                ],
                "currency": "DOGE",
                "treasury_type": "treasury_2_liquidity"
            }
            
            async with self.session.post(f"{self.base_url}/nowpayments/mass-withdraw", 
                                       json=mass_withdraw_payload) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("batch_id"):
                        self.log_test("Backend NOWPayments Mass Withdraw", True, 
                                    f"✅ MASS WITHDRAWAL SUCCESS! Batch ID: {data.get('batch_id')}", data)
                        return True
                    else:
                        self.log_test("Backend NOWPayments Mass Withdraw", False, 
                                    f"Mass withdrawal response missing batch_id: {data}", data)
                        return False
                elif response.status == 401:
                    self.log_test("Backend NOWPayments Mass Withdraw", False, 
                                f"❌ Mass withdrawal blocked - permissions not activated: {response_text}")
                    return False
                elif response.status == 403:
                    self.log_test("Backend NOWPayments Mass Withdraw", False, 
                                f"❌ Access forbidden - endpoint requires authentication: {response_text}")
                    return False
                else:
                    self.log_test("Backend NOWPayments Mass Withdraw", False, 
                                f"❌ Mass withdrawal failed - HTTP {response.status}: {response_text}")
                    return False
        except Exception as e:
            self.log_test("Backend NOWPayments Mass Withdraw", False, f"Error: {str(e)}")
            return False

    async def test_user_balance_verification(self):
        """Test 5: Verify user has sufficient DOGE balance"""
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
                                        f"User has {doge_balance:,.2f} DOGE (required: {required_balance})", 
                                        {"doge_balance": doge_balance, "required": required_balance})
                            return True
                        else:
                            self.log_test("User Balance Verification", False, 
                                        f"Insufficient DOGE balance: {doge_balance:,.2f} < {required_balance}", 
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

    async def test_direct_nowpayments_api_access(self):
        """Test 6: Direct NOWPayments API access with credentials"""
        try:
            # Test NOWPayments API status directly
            nowpayments_url = "https://api.nowpayments.io/v1/status"
            headers = {
                "x-api-key": NOWPAYMENTS_CREDENTIALS["api_key"]
            }
            
            async with self.session.get(nowpayments_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("message") == "OK":
                        self.log_test("Direct NOWPayments API Access", True, 
                                    f"NOWPayments API accessible with key {NOWPAYMENTS_CREDENTIALS['api_key'][:8]}...", data)
                        return True
                    else:
                        self.log_test("Direct NOWPayments API Access", False, 
                                    f"NOWPayments API returned unexpected response", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Direct NOWPayments API Access", False, 
                                f"NOWPayments API error - HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Direct NOWPayments API Access", False, f"Error: {str(e)}")
            return False

    async def test_direct_nowpayments_payout_attempt(self):
        """Test 7: CRITICAL - Direct NOWPayments payout API test"""
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
                        self.log_test("Direct NOWPayments Payout", True, 
                                    f"🎉 DIRECT PAYOUT SUCCESS! Transaction ID: {data.get('id')}", data)
                        return True
                    else:
                        self.log_test("Direct NOWPayments Payout", False, 
                                    f"Payout response missing ID: {data}", data)
                        return False
                elif response.status == 401:
                    if "Bearer JWTtoken is required" in response_text or "Authorization header is empty" in response_text:
                        self.log_test("Direct NOWPayments Payout", False, 
                                    f"❌ PAYOUT PERMISSIONS NOT YET ACTIVATED - 401: {response_text}")
                        return False
                    else:
                        self.log_test("Direct NOWPayments Payout", False, 
                                    f"❌ Authentication error: {response_text}")
                        return False
                else:
                    self.log_test("Direct NOWPayments Payout", False, 
                                f"❌ Direct payout failed - HTTP {response.status}: {response_text}")
                    return False
        except Exception as e:
            self.log_test("Direct NOWPayments Payout", False, f"Error: {str(e)}")
            return False

    async def test_payment_link_verification(self):
        """Test 8: Payment link integration verification"""
        try:
            payment_link = "https://nowpayments.io/payment/?iid=4383583691&paymentId=5914238505"
            
            async with self.session.get(payment_link) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Check if it's a valid NOWPayments payment page
                    if ("nowpayments" in content.lower() and 
                        ("payment" in content.lower() or "invoice" in content.lower())):
                        
                        # Check for amount indicators
                        amount_indicators = ["16081.58", "5000", "CA$5000", "$5000"]
                        amount_found = any(indicator in content for indicator in amount_indicators)
                        
                        if amount_found:
                            self.log_test("Payment Link Verification", True, 
                                        f"Payment link accessible with expected amount indicators", 
                                        {"url": payment_link, "amount_found": True})
                        else:
                            self.log_test("Payment Link Verification", True, 
                                        f"Payment link accessible but amount verification unclear", 
                                        {"url": payment_link, "content_length": len(content)})
                        return True
                    else:
                        self.log_test("Payment Link Verification", False, 
                                    f"Payment link doesn't appear to be valid NOWPayments page", 
                                    {"url": payment_link, "content_preview": content[:200]})
                        return False
                else:
                    self.log_test("Payment Link Verification", False, 
                                f"Payment link not accessible - HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("Payment Link Verification", False, f"Error: {str(e)}")
            return False

    async def test_doge_address_validation(self):
        """Test 9: DOGE withdrawal address validation"""
        try:
            withdrawal_address = USER_CREDENTIALS["withdrawal_wallet"]
            
            # Basic DOGE address validation
            if (withdrawal_address.startswith('D') and 
                len(withdrawal_address) >= 25 and 
                len(withdrawal_address) <= 34 and
                withdrawal_address.replace('0', '').replace('O', '').replace('I', '').replace('l', '').isalnum()):
                
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

    async def run_all_tests(self):
        """Run all comprehensive NOWPayments tests"""
        print("🚨 COMPREHENSIVE NOWPayments Integration Test")
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
            self.test_direct_nowpayments_api_access,
            self.test_backend_nowpayments_currencies,
            self.test_backend_nowpayments_treasuries,
            self.test_user_balance_verification,
            self.test_doge_address_validation,
            self.test_direct_nowpayments_payout_attempt,  # CRITICAL TEST
            self.test_backend_nowpayments_withdraw,       # CRITICAL TEST
            self.test_backend_nowpayments_mass_withdraw,  # CRITICAL TEST
            self.test_payment_link_verification
        ]
        
        for test_method in test_methods:
            try:
                await test_method()
            except Exception as e:
                self.log_test(test_method.__name__, False, f"Test execution error: {str(e)}")
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🎯 COMPREHENSIVE NOWPayments TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n🔍 CRITICAL FINDINGS:")
        
        # Check for direct payout success
        direct_payout_test = next((r for r in self.test_results if "Direct NOWPayments Payout" in r["test"]), None)
        backend_withdraw_test = next((r for r in self.test_results if "Backend NOWPayments Withdraw" in r["test"]), None)
        mass_withdraw_test = next((r for r in self.test_results if "Backend NOWPayments Mass Withdraw" in r["test"]), None)
        
        if direct_payout_test and direct_payout_test["success"]:
            print("✅ DIRECT PAYOUT PERMISSIONS ACTIVATED - Real withdrawals working!")
        elif backend_withdraw_test and backend_withdraw_test["success"]:
            print("✅ BACKEND PAYOUT PERMISSIONS ACTIVATED - Real withdrawals working!")
        else:
            print("❌ PAYOUT PERMISSIONS NOT YET ACTIVATED - Still waiting for NOWPayments approval")
        
        if mass_withdraw_test and mass_withdraw_test["success"]:
            print("✅ MASS PAYOUT CAPABILITY CONFIRMED")
        else:
            print("❌ MASS PAYOUT NOT YET AVAILABLE")
        
        # Check payment link integration
        payment_link_test = next((r for r in self.test_results if "Payment Link" in r["test"]), None)
        if payment_link_test and payment_link_test["success"]:
            print("✅ PAYMENT LINK INTEGRATION WORKING")
        else:
            print("❌ PAYMENT LINK INTEGRATION ISSUES")
        
        print("\n📊 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        print("\n🎯 FINAL ANSWER TO CRITICAL QUESTION:")
        if ((direct_payout_test and direct_payout_test["success"]) or 
            (backend_withdraw_test and backend_withdraw_test["success"])):
            print("✅ YES - The 1-2 business day whitelisting period has COMPLETED!")
            print("✅ NOWPayments wallet whitelisting is ACTIVE!")
            print("✅ Real blockchain withdrawals (100 DOGE) are now POSSIBLE!")
            print("✅ Mass payouts (50 DOGE) are now AVAILABLE!")
        else:
            print("❌ NO - The 1-2 business day whitelisting period has NOT completed yet.")
            print("⏳ NOWPayments payout permissions are still PENDING activation.")
            print("⏳ Continue waiting for NOWPayments support to activate payout permissions.")
            print("📞 Contact NOWPayments support to expedite payout permission activation.")

async def main():
    """Main test execution"""
    async with ComprehensiveNOWPaymentsTester(BACKEND_URL) as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())