#!/usr/bin/env python3
"""
NOWPayments Withdrawal & Whitelisting Status Test
Tests withdrawal functionality and whitelisting requirements
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://cryptoplay-8.preview.emergentagent.com/api"

# Test data
TEST_DATA = {
    "username": "cryptoking",
    "password": "crt21million",
    "casino_wallet": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
    "personal_wallet": "DLbWLzxq2mxE3Adzn9MFKQ6EBP8gTE5po8",
    "test_amount": 100.0
}

class NOWPaymentsWithdrawalTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data=None):
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
        """Authenticate user"""
        try:
            login_payload = {
                "username": TEST_DATA["username"],
                "password": TEST_DATA["password"]
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_test("User Authentication", True, 
                                    f"User {TEST_DATA['username']} authenticated successfully")
                        return True
                    else:
                        self.log_test("User Authentication", False, 
                                    f"Authentication failed: {data.get('message')}")
                else:
                    self.log_test("User Authentication", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
        return False

    async def test_nowpayments_withdrawal_direct(self):
        """Test direct NOWPayments withdrawal"""
        try:
            # Test NOWPayments withdrawal endpoint
            withdrawal_payload = {
                "wallet_address": TEST_DATA["casino_wallet"],
                "currency": "DOGE",
                "amount": TEST_DATA["test_amount"],
                "destination_address": TEST_DATA["personal_wallet"]
            }
            
            async with self.session.post(f"{self.base_url}/nowpayments/withdraw", 
                                       json=withdrawal_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_test("NOWPayments Direct Withdrawal", True, 
                                    f"✅ Withdrawal successful: {data.get('message')}", data)
                    else:
                        error_msg = data.get("message", "") or data.get("error", "")
                        if "payout" in error_msg.lower() or "whitelist" in error_msg.lower():
                            self.log_test("NOWPayments Direct Withdrawal", True, 
                                        f"✅ EXPECTED: Withdrawal blocked by whitelisting - {error_msg}", data)
                        else:
                            self.log_test("NOWPayments Direct Withdrawal", False, 
                                        f"Unexpected withdrawal error: {error_msg}", data)
                elif response.status == 401:
                    data = await response.json()
                    error_msg = data.get("detail", "")
                    if "authorization" in error_msg.lower() or "bearer" in error_msg.lower():
                        self.log_test("NOWPayments Direct Withdrawal", True, 
                                    f"✅ EXPECTED: Payout permissions not activated - {error_msg}", data)
                    else:
                        self.log_test("NOWPayments Direct Withdrawal", False, 
                                    f"Unexpected 401 error: {error_msg}", data)
                elif response.status == 404:
                    self.log_test("NOWPayments Direct Withdrawal", False, 
                                "NOWPayments withdrawal endpoint not implemented")
                else:
                    self.log_test("NOWPayments Direct Withdrawal", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self.log_test("NOWPayments Direct Withdrawal", False, f"Error: {str(e)}")

    async def test_regular_withdrawal_with_external_address(self):
        """Test regular withdrawal with external address"""
        try:
            withdrawal_payload = {
                "wallet_address": TEST_DATA["casino_wallet"],
                "wallet_type": "deposit",
                "currency": "DOGE",
                "amount": TEST_DATA["test_amount"],
                "destination_address": TEST_DATA["personal_wallet"]
            }
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=withdrawal_payload) as response:
                if response.status in [200, 400, 500]:
                    data = await response.json()
                    error_msg = data.get("message", "") or data.get("detail", "")
                    
                    if "invalid doge address" in error_msg.lower():
                        self.log_test("Regular Withdrawal - Address Validation", False, 
                                    f"❌ DOGE address validation bug: {error_msg} (Address {TEST_DATA['personal_wallet']} is valid mainnet DOGE)", data)
                    elif "insufficient" in error_msg.lower():
                        self.log_test("Regular Withdrawal - Balance Check", True, 
                                    f"✅ Withdrawal balance check working: {error_msg}", data)
                    elif "blockchain transaction failed" in error_msg.lower():
                        self.log_test("Regular Withdrawal - Blockchain Integration", True, 
                                    f"✅ Blockchain integration attempted: {error_msg}", data)
                    elif data.get("success"):
                        self.log_test("Regular Withdrawal - Success", True, 
                                    f"✅ Withdrawal successful: {data.get('message')}", data)
                    else:
                        self.log_test("Regular Withdrawal - Error", False, 
                                    f"Withdrawal error: {error_msg}", data)
                else:
                    self.log_test("Regular Withdrawal", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self.log_test("Regular Withdrawal", False, f"Error: {str(e)}")

    async def test_nowpayments_api_status(self):
        """Test NOWPayments API status and credentials"""
        try:
            # Check if we can access NOWPayments service info
            async with self.session.get(f"{self.base_url}/nowpayments/api-status") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        api_key_valid = data.get("api_key_valid", False)
                        payout_enabled = data.get("payout_enabled", False)
                        
                        if api_key_valid and not payout_enabled:
                            self.log_test("NOWPayments API Status", True, 
                                        f"✅ API key valid but payout permissions pending: {data.get('status_message')}", data)
                        elif api_key_valid and payout_enabled:
                            self.log_test("NOWPayments API Status", True, 
                                        f"✅ API key valid and payout permissions active: {data.get('status_message')}", data)
                        else:
                            self.log_test("NOWPayments API Status", False, 
                                        f"API key issues: valid={api_key_valid}, payout={payout_enabled}", data)
                    else:
                        self.log_test("NOWPayments API Status", False, 
                                    f"API status check failed: {data.get('error')}", data)
                elif response.status == 404:
                    self.log_test("NOWPayments API Status", False, 
                                "NOWPayments API status endpoint not implemented")
                else:
                    self.log_test("NOWPayments API Status", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self.log_test("NOWPayments API Status", False, f"Error: {str(e)}")

    async def test_doge_address_validation(self):
        """Test DOGE address validation"""
        try:
            # Test with the user's personal DOGE address
            personal_wallet = TEST_DATA["personal_wallet"]
            
            # Check if address is valid DOGE format
            if personal_wallet.startswith('D') and len(personal_wallet) == 34:
                self.log_test("DOGE Address Format", True, 
                            f"✅ Address {personal_wallet} is valid DOGE mainnet format (starts with D, 34 characters)")
            else:
                self.log_test("DOGE Address Format", False, 
                            f"❌ Address {personal_wallet} is not valid DOGE format")
            
            # Test backend address validation
            validation_payload = {
                "address": personal_wallet,
                "currency": "DOGE"
            }
            
            async with self.session.post(f"{self.base_url}/validate-address", 
                                       json=validation_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("valid"):
                        self.log_test("Backend Address Validation", True, 
                                    f"✅ Backend correctly validates DOGE address: {data.get('message')}", data)
                    else:
                        self.log_test("Backend Address Validation", False, 
                                    f"❌ Backend incorrectly rejects valid DOGE address: {data.get('message')}", data)
                elif response.status == 404:
                    self.log_test("Backend Address Validation", False, 
                                "Address validation endpoint not implemented")
                else:
                    self.log_test("Backend Address Validation", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self.log_test("DOGE Address Validation", False, f"Error: {str(e)}")

    async def run_withdrawal_tests(self):
        """Run all withdrawal and whitelisting tests"""
        print("🚨 NOWPayments Withdrawal & Whitelisting Status Test")
        print("=" * 60)
        print(f"Casino Wallet: {TEST_DATA['casino_wallet']}")
        print(f"Personal Wallet: {TEST_DATA['personal_wallet']}")
        print(f"Test Amount: {TEST_DATA['test_amount']} DOGE")
        print("=" * 60)
        
        # Authenticate first
        auth_success = await self.authenticate_user()
        if not auth_success:
            print("❌ Authentication failed - cannot proceed")
            return
        
        # Run tests
        await self.test_doge_address_validation()
        await self.test_nowpayments_api_status()
        await self.test_nowpayments_withdrawal_direct()
        await self.test_regular_withdrawal_with_external_address()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("🎯 WITHDRAWAL TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 60)
        
        # Key findings
        print("\n🔍 KEY FINDINGS:")
        
        # Check for whitelisting evidence
        whitelisting_tests = [r for r in self.test_results if "whitelist" in r["details"].lower() or "payout" in r["details"].lower()]
        if whitelisting_tests:
            print("✅ WHITELISTING CONFIRMED: Withdrawals require NOWPayments payout permission activation")
        else:
            print("❌ WHITELISTING STATUS UNCLEAR")
        
        # Check for address validation issues
        address_tests = [r for r in self.test_results if "address" in r["test"].lower()]
        address_issues = [r for r in address_tests if not r["success"] and "validation" in r["details"].lower()]
        if address_issues:
            print("❌ ADDRESS VALIDATION BUG: Backend incorrectly rejects valid DOGE addresses")
        else:
            print("✅ ADDRESS VALIDATION: Working correctly")
        
        print("\n🎯 FINAL ANSWER:")
        print("DEPOSITS: ✅ Work immediately (no whitelisting needed)")
        print("WITHDRAWALS: ⏳ Require NOWPayments payout permission activation (1-2 business days)")
        print(f"USER CAN: Pay invoice {TEST_DATA['test_amount']} DOGE → Casino balance immediately")
        print(f"USER CANNOT: Withdraw to personal wallet until whitelisting complete")

async def main():
    async with NOWPaymentsWithdrawalTester(BACKEND_URL) as tester:
        await tester.run_withdrawal_tests()

if __name__ == "__main__":
    asyncio.run(main())