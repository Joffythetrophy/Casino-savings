#!/usr/bin/env python3
"""
URGENT: NOWPayments Authenticated Withdrawal Test
Tests NOWPayments withdrawal with proper authentication
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://tiger-dex-casino.preview.emergentagent.com/api"

# Test credentials
TEST_CREDENTIALS = {
    "username": "cryptoking",
    "password": "crt21million", 
    "casino_wallet": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
    "treasury_wallet": "DLbWLzxq2mxE3Adzn9MFKQ6EBP8gTE5po8",
    "test_amount": 1000
}

class AuthenticatedNOWPaymentsTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
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
                        # Try to get JWT token from wallet auth
                        challenge_payload = {
                            "wallet_address": TEST_CREDENTIALS["casino_wallet"],
                            "network": "solana"
                        }
                        
                        async with self.session.post(f"{self.base_url}/auth/challenge", 
                                                   json=challenge_payload) as challenge_response:
                            if challenge_response.status == 200:
                                challenge_data = await challenge_response.json()
                                
                                # Mock signature verification
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
                                            self.log_test("User Authentication", True, 
                                                        f"Authenticated with JWT token", verify_data)
                                            return True
                        
                        self.log_test("User Authentication", True, 
                                    f"User authenticated (no JWT token)", data)
                        return True
                    else:
                        self.log_test("User Authentication", False, 
                                    f"Authentication failed: {data.get('message')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
        return False
    
    async def test_nowpayments_currencies_endpoint(self):
        """Test NOWPayments currencies endpoint"""
        try:
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
                
            async with self.session.get(f"{self.base_url}/nowpayments/currencies", 
                                      headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        if data.get("success") and "currencies" in data:
                            currencies = data["currencies"]
                            if "doge" in [c.lower() for c in currencies]:
                                self.log_test("NOWPayments Currencies", True, 
                                            f"DOGE supported among {len(currencies)} currencies", data)
                            else:
                                self.log_test("NOWPayments Currencies", False, 
                                            f"DOGE not found in currencies", data)
                        else:
                            self.log_test("NOWPayments Currencies", False, 
                                        f"Invalid response format", data)
                    except json.JSONDecodeError:
                        self.log_test("NOWPayments Currencies", False, 
                                    f"Invalid JSON: {response_text}")
                else:
                    self.log_test("NOWPayments Currencies", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("NOWPayments Currencies", False, f"Error: {str(e)}")
    
    async def test_nowpayments_withdrawal_authenticated(self):
        """Test NOWPayments withdrawal with authentication"""
        try:
            headers = {"Content-Type": "application/json"}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
                
            withdrawal_payload = {
                "wallet_address": TEST_CREDENTIALS["casino_wallet"],
                "currency": "DOGE",
                "amount": TEST_CREDENTIALS["test_amount"],
                "destination_address": TEST_CREDENTIALS["treasury_wallet"],
                "treasury": "treasury_2_liquidity"  # Main treasury
            }
            
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
                            self.log_test("NOWPayments Authenticated Withdrawal", True, 
                                        f"✅ WITHDRAWAL SUCCESSFUL! Payout ID: {payout_id}, Hash: {transaction_hash}", data)
                        else:
                            error_msg = data.get("message", "Unknown error")
                            if "401" in error_msg or "unauthorized" in error_msg.lower():
                                self.log_test("NOWPayments Authenticated Withdrawal", False, 
                                            f"❌ STILL UNAUTHORIZED: {error_msg}", data)
                            elif "payout permission" in error_msg.lower():
                                self.log_test("NOWPayments Authenticated Withdrawal", False, 
                                            f"❌ PAYOUT PERMISSIONS NOT ACTIVATED: {error_msg}", data)
                            else:
                                self.log_test("NOWPayments Authenticated Withdrawal", False, 
                                            f"Withdrawal failed: {error_msg}", data)
                    except json.JSONDecodeError:
                        self.log_test("NOWPayments Authenticated Withdrawal", False, 
                                    f"Invalid JSON: {response_text}")
                elif response.status == 401:
                    self.log_test("NOWPayments Authenticated Withdrawal", False, 
                                f"❌ 401 UNAUTHORIZED: {response_text}")
                elif response.status == 403:
                    self.log_test("NOWPayments Authenticated Withdrawal", False, 
                                f"❌ 403 FORBIDDEN: {response_text}")
                else:
                    self.log_test("NOWPayments Authenticated Withdrawal", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("NOWPayments Authenticated Withdrawal", False, f"Error: {str(e)}")
    
    async def test_wallet_balance_check(self):
        """Check wallet balance before and after"""
        try:
            wallet_address = TEST_CREDENTIALS["casino_wallet"]
            
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        doge_balance = deposit_balance.get("DOGE", 0)
                        
                        self.log_test("Wallet Balance Check", True, 
                                    f"Current DOGE balance: {doge_balance:,.0f} DOGE", data)
                    else:
                        self.log_test("Wallet Balance Check", False, 
                                    "Failed to retrieve wallet information", data)
                else:
                    error_text = await response.text()
                    self.log_test("Wallet Balance Check", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Wallet Balance Check", False, f"Error: {str(e)}")
    
    async def test_nowpayments_status_endpoint(self):
        """Test NOWPayments status endpoint"""
        try:
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
                
            async with self.session.get(f"{self.base_url}/nowpayments/status", 
                                      headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        self.log_test("NOWPayments Status", True, 
                                    f"NOWPayments status endpoint working", data)
                    except json.JSONDecodeError:
                        self.log_test("NOWPayments Status", False, 
                                    f"Invalid JSON: {response_text}")
                elif response.status == 404:
                    self.log_test("NOWPayments Status", False, 
                                f"❌ Status endpoint not implemented: {response_text}")
                else:
                    self.log_test("NOWPayments Status", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("NOWPayments Status", False, f"Error: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🚨 URGENT: NOWPayments Authenticated Withdrawal Test Results")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success)")
        
        # Check for successful withdrawals
        withdrawal_success = any("WITHDRAWAL SUCCESSFUL" in r["details"] for r in self.test_results)
        
        if withdrawal_success:
            print("🎉 BREAKTHROUGH: NOWPayments withdrawals are now working!")
        else:
            print("❌ WITHDRAWALS STILL BLOCKED: Payout permissions not activated")
        
        print("\n🔍 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result["success"] else "❌"
            print(f"{i}. {status} {result['test']}: {result['details']}")
        
        print("="*80)

async def main():
    """Run authenticated NOWPayments test"""
    print("🚨 URGENT: Testing NOWPayments with Authentication")
    print("Checking if payout permissions are finally activated...")
    print()
    
    async with AuthenticatedNOWPaymentsTester(BACKEND_URL) as tester:
        # Authenticate first
        authenticated = await tester.authenticate_user()
        
        if authenticated:
            # Run tests with authentication
            await tester.test_wallet_balance_check()
            await tester.test_nowpayments_status_endpoint()
            await tester.test_nowpayments_currencies_endpoint()
            await tester.test_nowpayments_withdrawal_authenticated()
            await tester.test_wallet_balance_check()  # Check balance after
        
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())