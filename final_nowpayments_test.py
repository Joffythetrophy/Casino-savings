#!/usr/bin/env python3
"""
FINAL URGENT: NOWPayments Real Treasury Withdrawal Test
Complete test with correct payload structure and authentication
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://solana-casino.preview.emergentagent.com/api"

# Test credentials from review request
TEST_CREDENTIALS = {
    "username": "cryptoking",
    "password": "crt21million", 
    "casino_wallet": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
    "treasury_wallet": "DLbWLzxq2mxE3Adzn9MFKQ6EBP8gTE5po8",
    "test_amount": 1000  # 1,000 DOGE safe test amount
}

class FinalNOWPaymentsTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        self.user_id = None
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
        
    async def authenticate_and_get_user_id(self):
        """Authenticate user and get user_id"""
        try:
            # Step 1: Login to get user data
            login_payload = {
                "username": TEST_CREDENTIALS["username"],
                "password": TEST_CREDENTIALS["password"]
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.user_id = data.get("user_id")
                        
                        # Step 2: Get JWT token for authenticated endpoints
                        challenge_payload = {
                            "wallet_address": TEST_CREDENTIALS["casino_wallet"],
                            "network": "solana"
                        }
                        
                        async with self.session.post(f"{self.base_url}/auth/challenge", 
                                                   json=challenge_payload) as challenge_response:
                            if challenge_response.status == 200:
                                challenge_data = await challenge_response.json()
                                
                                verify_payload = {
                                    "challenge_hash": challenge_data.get("challenge_hash"),
                                    "signature": "mock_signature_for_testing",
                                    "wallet_address": TEST_CREDENTIALS["casino_wallet"],
                                    "network": "solana"
                                }
                                
                                async with self.session.post(f"{self.base_url}/auth/verify", 
                                                           json=verify_payload) as verify_response:
                                    if verify_response.status == 200:
                                        verify_data = await verify_response.json()
                                        if verify_data.get("success"):
                                            self.auth_token = verify_data.get("token")
                        
                        self.log_test("Authentication & User ID", True, 
                                    f"User authenticated - ID: {self.user_id}, JWT: {'Yes' if self.auth_token else 'No'}", data)
                        return True
                    else:
                        self.log_test("Authentication & User ID", False, 
                                    f"Login failed: {data.get('message')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("Authentication & User ID", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Authentication & User ID", False, f"Error: {str(e)}")
        return False
    
    async def test_balance_verification(self):
        """Verify user has sufficient balance"""
        try:
            wallet_address = TEST_CREDENTIALS["casino_wallet"]
            
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        doge_balance = deposit_balance.get("DOGE", 0)
                        
                        test_amount = TEST_CREDENTIALS["test_amount"]
                        
                        if doge_balance >= test_amount:
                            self.log_test("Balance Verification", True, 
                                        f"Sufficient balance: {doge_balance:,.0f} DOGE (need {test_amount})", data)
                        else:
                            self.log_test("Balance Verification", False, 
                                        f"Insufficient balance: {doge_balance:,.0f} DOGE (need {test_amount})", data)
                    else:
                        self.log_test("Balance Verification", False, 
                                    "Failed to retrieve wallet information", data)
                else:
                    error_text = await response.text()
                    self.log_test("Balance Verification", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Balance Verification", False, f"Error: {str(e)}")
    
    async def test_nowpayments_withdrawal_complete(self):
        """Test complete NOWPayments withdrawal with correct payload"""
        try:
            if not self.user_id:
                self.log_test("NOWPayments Complete Withdrawal", False, 
                            "No user_id available - authentication failed")
                return
                
            headers = {"Content-Type": "application/json"}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
                
            # Correct payload structure based on NOWPaymentsWithdrawalRequest
            withdrawal_payload = {
                "user_id": self.user_id,
                "currency": "DOGE",
                "amount": TEST_CREDENTIALS["test_amount"],
                "destination_address": TEST_CREDENTIALS["treasury_wallet"],
                "treasury_type": "treasury_2_liquidity",  # Main treasury
                "withdrawal_type": "standard"
            }
            
            print(f"🔄 Attempting withdrawal: {withdrawal_payload}")
            
            async with self.session.post(f"{self.base_url}/nowpayments/withdraw", 
                                       json=withdrawal_payload, 
                                       headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        if data.get("success"):
                            payout_id = data.get("payout_id")
                            transaction_hash = data.get("blockchain_hash")
                            amount = data.get("amount")
                            self.log_test("NOWPayments Complete Withdrawal", True, 
                                        f"🎉 WITHDRAWAL SUCCESSFUL! Payout ID: {payout_id}, Amount: {amount} DOGE, Hash: {transaction_hash}", data)
                        else:
                            error_msg = data.get("message", "Unknown error")
                            if "401" in error_msg or "unauthorized" in error_msg.lower():
                                self.log_test("NOWPayments Complete Withdrawal", False, 
                                            f"❌ UNAUTHORIZED: {error_msg}", data)
                            elif "payout permission" in error_msg.lower() or "bearer jwt" in error_msg.lower():
                                self.log_test("NOWPayments Complete Withdrawal", False, 
                                            f"❌ PAYOUT PERMISSIONS NOT ACTIVATED: {error_msg}", data)
                            else:
                                self.log_test("NOWPayments Complete Withdrawal", False, 
                                            f"Withdrawal failed: {error_msg}", data)
                    except json.JSONDecodeError:
                        self.log_test("NOWPayments Complete Withdrawal", False, 
                                    f"Invalid JSON response: {response_text}")
                elif response.status == 401:
                    self.log_test("NOWPayments Complete Withdrawal", False, 
                                f"❌ 401 UNAUTHORIZED - Payout permissions not activated: {response_text}")
                elif response.status == 403:
                    self.log_test("NOWPayments Complete Withdrawal", False, 
                                f"❌ 403 FORBIDDEN - Authentication required: {response_text}")
                elif response.status == 422:
                    self.log_test("NOWPayments Complete Withdrawal", False, 
                                f"❌ 422 VALIDATION ERROR - Payload issue: {response_text}")
                else:
                    self.log_test("NOWPayments Complete Withdrawal", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("NOWPayments Complete Withdrawal", False, f"Error: {str(e)}")
    
    async def test_direct_nowpayments_api(self):
        """Test direct NOWPayments API to verify credentials"""
        try:
            # Test NOWPayments API directly
            nowpayments_url = "https://api.nowpayments.io/v1/payout"
            headers = {
                "x-api-key": "FSVPHG1-1TK4MDZ-MKC4TTV-MW1MAXX",
                "Content-Type": "application/json"
            }
            
            payout_payload = {
                "withdrawals": [
                    {
                        "address": TEST_CREDENTIALS["treasury_wallet"],
                        "currency": "doge",
                        "amount": TEST_CREDENTIALS["test_amount"]
                    }
                ]
            }
            
            async with self.session.post(nowpayments_url, 
                                       json=payout_payload, 
                                       headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        if "id" in data:
                            self.log_test("Direct NOWPayments API", True, 
                                        f"🎉 DIRECT API SUCCESS! Payout ID: {data.get('id')}", data)
                        else:
                            self.log_test("Direct NOWPayments API", False, 
                                        f"Unexpected response format", data)
                    except json.JSONDecodeError:
                        self.log_test("Direct NOWPayments API", False, 
                                    f"Invalid JSON: {response_text}")
                elif response.status == 401:
                    if "Bearer JWTtoken is required" in response_text:
                        self.log_test("Direct NOWPayments API", False, 
                                    f"❌ PAYOUT PERMISSIONS NOT ACTIVATED - Bearer JWT required: {response_text}")
                    else:
                        self.log_test("Direct NOWPayments API", False, 
                                    f"❌ API key not authorized for payouts: {response_text}")
                else:
                    self.log_test("Direct NOWPayments API", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("Direct NOWPayments API", False, f"Error: {str(e)}")
    
    async def test_balance_after_attempts(self):
        """Check balance after withdrawal attempts"""
        try:
            wallet_address = TEST_CREDENTIALS["casino_wallet"]
            
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        doge_balance = deposit_balance.get("DOGE", 0)
                        
                        self.log_test("Balance After Attempts", True, 
                                    f"Final balance: {doge_balance:,.0f} DOGE", data)
                    else:
                        self.log_test("Balance After Attempts", False, 
                                    "Failed to retrieve wallet information", data)
                else:
                    error_text = await response.text()
                    self.log_test("Balance After Attempts", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Balance After Attempts", False, f"Error: {str(e)}")
    
    def print_final_summary(self):
        """Print comprehensive final summary"""
        print("\n" + "="*80)
        print("🚨 FINAL URGENT: NOWPayments Real Treasury Withdrawal Test Results")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 FINAL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success)")
        
        # Check for successful withdrawals
        withdrawal_success = any("WITHDRAWAL SUCCESSFUL" in r["details"] or "DIRECT API SUCCESS" in r["details"] 
                               for r in self.test_results)
        
        print("\n🎯 CRITICAL ASSESSMENT:")
        if withdrawal_success:
            print("🎉 BREAKTHROUGH: NOWPayments withdrawals are NOW WORKING!")
            print("   ✅ User can proceed with real treasury withdrawals")
            print("   ✅ Payout permissions have been activated")
        else:
            # Check specific failure reasons
            payout_permission_issues = [r for r in self.test_results 
                                      if "PAYOUT PERMISSIONS NOT ACTIVATED" in r["details"] 
                                      or "Bearer JWT" in r["details"]]
            
            if payout_permission_issues:
                print("⏳ PAYOUT PERMISSIONS STILL PENDING:")
                print("   ❌ NOWPayments support has not yet activated payout permissions")
                print("   ❌ API key FSVPHG1-1TK4MDZ-MKC4TTV-MW1MAXX needs payout activation")
                print("   📞 Contact NOWPayments support to complete activation")
            else:
                print("🔧 TECHNICAL ISSUES DETECTED:")
                print("   ❌ System configuration or validation problems")
                print("   🔍 Manual investigation required")
        
        print("\n🔍 DETAILED TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result["success"] else "❌"
            print(f"{i:2d}. {status} {result['test']}")
            print(f"     {result['details']}")
        
        print("\n🎯 FINAL RECOMMENDATION:")
        if withdrawal_success:
            print("✅ PROCEED: Real treasury withdrawals are operational!")
        else:
            print("⏳ WAIT: Contact NOWPayments support to activate payout permissions")
            print("   API Key: FSVPHG1-1TK4MDZ-MKC4TTV-MW1MAXX")
            print("   Request: Activate payout/withdrawal permissions")
        
        print("="*80)

async def main():
    """Run final comprehensive NOWPayments test"""
    print("🚨 FINAL URGENT: Complete NOWPayments Treasury Withdrawal Test")
    print("Testing if payout permissions are finally activated for real withdrawals...")
    print()
    
    async with FinalNOWPaymentsTester(BACKEND_URL) as tester:
        # Step 1: Authenticate and get user ID
        authenticated = await tester.authenticate_and_get_user_id()
        
        if authenticated:
            # Step 2: Verify balance
            await tester.test_balance_verification()
            
            # Step 3: Test NOWPayments withdrawal with correct payload
            await tester.test_nowpayments_withdrawal_complete()
            
            # Step 4: Test direct NOWPayments API
            await tester.test_direct_nowpayments_api()
            
            # Step 5: Check final balance
            await tester.test_balance_after_attempts()
        
        # Print comprehensive summary
        tester.print_final_summary()

if __name__ == "__main__":
    asyncio.run(main())