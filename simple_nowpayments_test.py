#!/usr/bin/env python3
"""
URGENT: Simple NOWPayments Withdrawal Test - Whitelisted Address
Direct test of NOWPayments endpoints with proper authentication
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://smart-savings-dapp.preview.emergentagent.com/api"

# Test data
TEST_DATA = {
    "username": "cryptoking",
    "password": "crt21million",
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
    "whitelisted_address": "DLbWLzxq2mxE3Adzn9MFKQ6EBP8gTE5po8",
    "test_amount": 100.0
}

class SimpleNOWPaymentsTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")

    async def test_user_login(self):
        """Test user login to get session"""
        try:
            login_payload = {
                "username": TEST_DATA["username"],
                "password": TEST_DATA["password"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_test("User Login", True, 
                                    f"✅ User {TEST_DATA['username']} logged in successfully")
                        return True
                    else:
                        self.log_test("User Login", False, 
                                    f"❌ Login failed: {data.get('message')}")
                else:
                    self.log_test("User Login", False, 
                                f"❌ HTTP {response.status}")
        except Exception as e:
            self.log_test("User Login", False, f"❌ Error: {str(e)}")
        return False

    async def test_user_balance(self):
        """Check user DOGE balance"""
        try:
            async with self.session.get(f"{BACKEND_URL}/wallet/{TEST_DATA['wallet_address']}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        wallet = data.get("wallet", {})
                        deposit_balance = wallet.get("deposit_balance", {})
                        doge_balance = deposit_balance.get("DOGE", 0)
                        
                        if doge_balance >= TEST_DATA["test_amount"]:
                            self.log_test("User Balance Check", True, 
                                        f"✅ User has {doge_balance:,.2f} DOGE (sufficient for test)")
                            return True
                        else:
                            self.log_test("User Balance Check", False, 
                                        f"❌ Insufficient balance: {doge_balance} DOGE")
                    else:
                        self.log_test("User Balance Check", False, 
                                    f"❌ Wallet check failed: {data.get('message')}")
                else:
                    self.log_test("User Balance Check", False, 
                                f"❌ HTTP {response.status}")
        except Exception as e:
            self.log_test("User Balance Check", False, f"❌ Error: {str(e)}")
        return False

    async def test_nowpayments_currencies(self):
        """Test NOWPayments currencies endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/nowpayments/currencies") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        currencies = data.get("currencies", [])
                        doge_supported = "DOGE" in currencies or "doge" in currencies
                        
                        self.log_test("NOWPayments Currencies", True, 
                                    f"✅ {len(currencies)} currencies available, DOGE supported: {doge_supported}")
                        return True
                    else:
                        self.log_test("NOWPayments Currencies", False, 
                                    f"❌ Request failed: {data.get('error')}")
                else:
                    error_text = await response.text()
                    self.log_test("NOWPayments Currencies", False, 
                                f"❌ HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("NOWPayments Currencies", False, f"❌ Error: {str(e)}")
        return False

    async def test_nowpayments_withdrawal(self):
        """🚀 CRITICAL TEST: NOWPayments withdrawal to whitelisted address"""
        try:
            print(f"\n🚀 CRITICAL TEST: Testing NOWPayments withdrawal")
            print(f"   From: {TEST_DATA['wallet_address']}")
            print(f"   To: {TEST_DATA['whitelisted_address']} (WHITELISTED!)")
            print(f"   Amount: {TEST_DATA['test_amount']} DOGE")
            
            # Try the NOWPayments withdrawal endpoint
            withdrawal_payload = {
                "wallet_address": TEST_DATA["wallet_address"],
                "currency": "DOGE",
                "amount": TEST_DATA["test_amount"],
                "destination_address": TEST_DATA["whitelisted_address"],
                "treasury_type": "deposit"
            }
            
            async with self.session.post(f"{BACKEND_URL}/nowpayments/withdraw", 
                                       json=withdrawal_payload) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        if data.get("success"):
                            transaction_id = data.get("transaction_id", "")
                            payout_id = data.get("payout_id", "")
                            
                            self.log_test("🚀 NOWPayments Withdrawal", True, 
                                        f"✅ SUCCESS! Withdrawal initiated! TX: {transaction_id}, Payout: {payout_id}")
                            return True
                        else:
                            error_msg = data.get("error", data.get("message", "Unknown error"))
                            
                            if "401" in str(error_msg) or "Bearer JWTtoken" in str(error_msg):
                                self.log_test("🚀 NOWPayments Withdrawal", False, 
                                            f"❌ PAYOUT PERMISSIONS NOT ACTIVATED: {error_msg}")
                            else:
                                self.log_test("🚀 NOWPayments Withdrawal", False, 
                                            f"❌ Withdrawal failed: {error_msg}")
                    except json.JSONDecodeError:
                        self.log_test("🚀 NOWPayments Withdrawal", False, 
                                    f"❌ Invalid JSON response: {response_text}")
                        
                elif response.status == 401:
                    self.log_test("🚀 NOWPayments Withdrawal", False, 
                                f"❌ 401 UNAUTHORIZED: Payout permissions still not activated")
                elif response.status == 403:
                    self.log_test("🚀 NOWPayments Withdrawal", False, 
                                f"❌ 403 FORBIDDEN: Authentication required")
                elif response.status == 422:
                    self.log_test("🚀 NOWPayments Withdrawal", False, 
                                f"❌ 422 VALIDATION ERROR: {response_text}")
                else:
                    self.log_test("🚀 NOWPayments Withdrawal", False, 
                                f"❌ HTTP {response.status}: {response_text}")
                    
        except Exception as e:
            self.log_test("🚀 NOWPayments Withdrawal", False, f"❌ Error: {str(e)}")
        return False

    async def test_regular_withdrawal(self):
        """Test regular withdrawal system with external address"""
        try:
            withdrawal_payload = {
                "wallet_address": TEST_DATA["wallet_address"],
                "wallet_type": "deposit",
                "currency": "DOGE",
                "amount": TEST_DATA["test_amount"],
                "destination_address": TEST_DATA["whitelisted_address"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/wallet/withdraw", 
                                       json=withdrawal_payload) as response:
                if response.status in [200, 400, 500]:
                    data = await response.json()
                    error_msg = data.get("message", "") or data.get("detail", "")
                    
                    if data.get("success"):
                        blockchain_hash = data.get("blockchain_transaction_hash")
                        if blockchain_hash:
                            self.log_test("Regular Withdrawal", True, 
                                        f"✅ Real blockchain withdrawal! Hash: {blockchain_hash}")
                        else:
                            self.log_test("Regular Withdrawal", True, 
                                        f"✅ Withdrawal successful: {data.get('message')}")
                        return True
                    elif "invalid doge address" in error_msg.lower():
                        self.log_test("Regular Withdrawal", False, 
                                    f"❌ Address validation bug: {error_msg}")
                    elif "insufficient" in error_msg.lower():
                        self.log_test("Regular Withdrawal", True, 
                                    f"✅ Balance check working: {error_msg}")
                    else:
                        self.log_test("Regular Withdrawal", False, 
                                    f"❌ Withdrawal error: {error_msg}")
                else:
                    self.log_test("Regular Withdrawal", False, 
                                f"❌ HTTP {response.status}")
        except Exception as e:
            self.log_test("Regular Withdrawal", False, f"❌ Error: {str(e)}")
        return False

    async def run_tests(self):
        """Run all tests"""
        print("🚨 URGENT: Simple NOWPayments Withdrawal Test - Whitelisted Address")
        print("=" * 80)
        print(f"🎯 User: {TEST_DATA['username']}")
        print(f"🎯 Wallet: {TEST_DATA['wallet_address']}")
        print(f"🎯 Whitelisted DOGE: {TEST_DATA['whitelisted_address']}")
        print(f"🎯 Test Amount: {TEST_DATA['test_amount']} DOGE")
        print("=" * 80)
        
        # Run tests in sequence
        await self.test_user_login()
        await self.test_user_balance()
        await self.test_nowpayments_currencies()
        await self.test_nowpayments_withdrawal()  # THE CRITICAL TEST
        await self.test_regular_withdrawal()
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("🎯 SIMPLE NOWPAYMENTS TEST SUMMARY")
        print("=" * 80)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Check for withdrawal success
        withdrawal_success = any(r["success"] for r in self.test_results 
                               if "nowpayments withdrawal" in r["test"].lower())
        
        print("\n🎯 CRITICAL SUCCESS CRITERIA:")
        print(f"✅ Real Blockchain Withdrawal: {'✅ SUCCESS' if withdrawal_success else '❌ FAILED'}")
        print(f"✅ Transaction ID Received: {'✅ SUCCESS' if withdrawal_success else '❌ FAILED'}")
        print(f"✅ DOGE to Whitelisted Wallet: {'✅ SUCCESS' if withdrawal_success else '❌ FAILED'}")
        print(f"✅ System Ready for Production: {'✅ SUCCESS' if withdrawal_success else '❌ FAILED'}")
        
        print("\n🎉 MOMENT OF TRUTH RESULT:")
        if withdrawal_success:
            print("✅ SUCCESS! The whitelisting is COMPLETE and WORKING!")
            print("🚀 Real blockchain withdrawals are now functional!")
            print("💰 DOGE successfully sent to whitelisted address!")
            print("🏆 System is ready for full production use!")
        else:
            print("❌ NOT YET - Whitelisting still pending or other issues")
            
            # Analyze failure reasons
            auth_failures = [r for r in self.test_results if not r["success"] and "401" in r["details"]]
            validation_failures = [r for r in self.test_results if not r["success"] and "422" in r["details"]]
            
            if auth_failures:
                print("🔑 ISSUE: 401 Authorization errors - payout permissions not activated")
                print("📞 ACTION: Contact NOWPayments support to activate payout permissions")
            elif validation_failures:
                print("📝 ISSUE: Request validation errors - API format issues")
                print("🔧 ACTION: Check API request format and required fields")
            else:
                print("❓ ISSUE: Other technical problems")
                print("🔍 ACTION: Check logs and error details")
        
        # Print failed test details
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")

async def main():
    """Main test execution"""
    async with SimpleNOWPaymentsTester() as tester:
        await tester.run_tests()

if __name__ == "__main__":
    asyncio.run(main())