#!/usr/bin/env python3
"""
URGENT: NOWPayments Real Treasury Withdrawal Test
Tests if NOWPayments payout permissions are finally activated for real blockchain withdrawals
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

# Test credentials from review request
TEST_CREDENTIALS = {
    "username": "cryptoking",
    "password": "crt21million", 
    "casino_wallet": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
    "treasury_wallet": "DLbWLzxq2mxE3Adzn9MFKQ6EBP8gTE5po8",
    "test_amount": 1000,  # 1,000 DOGE safe test amount
    "expected_balance": 34869237  # 34,869,237 DOGE
}

# NOWPayments credentials
NOWPAYMENTS_CREDENTIALS = {
    "api_key": "FSVPHG1-1TK4MDZ-MKC4TTV-MW1MAXX",
    "public_key": "f9a7e8ba-2573-4da2-9f4f-3e0ffd748212"
}

class NOWPaymentsWithdrawalTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.test_results = []
        self.user_data = None
        
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
        """Test 1: Authenticate user cryptoking"""
        try:
            login_payload = {
                "username": TEST_CREDENTIALS["username"],
                "password": TEST_CREDENTIALS["password"]
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("username") == "cryptoking":
                        self.user_data = data
                        expected_wallet = TEST_CREDENTIALS["casino_wallet"]
                        if data.get("wallet_address") == expected_wallet:
                            self.log_test("User Authentication", True, 
                                        f"User cryptoking authenticated successfully with wallet {expected_wallet}", data)
                        else:
                            self.log_test("User Authentication", False, 
                                        f"Wallet mismatch: expected {expected_wallet}, got {data.get('wallet_address')}", data)
                    else:
                        self.log_test("User Authentication", False, 
                                    f"Authentication failed: {data.get('message', 'Unknown error')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
    
    async def test_user_balance_verification(self):
        """Test 2: Verify user has sufficient DOGE balance for withdrawal"""
        try:
            wallet_address = TEST_CREDENTIALS["casino_wallet"]
            
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        doge_balance = deposit_balance.get("DOGE", 0)
                        
                        expected_balance = TEST_CREDENTIALS["expected_balance"]
                        test_amount = TEST_CREDENTIALS["test_amount"]
                        
                        if doge_balance >= test_amount:
                            self.log_test("User Balance Verification", True, 
                                        f"User has {doge_balance:,.0f} DOGE (sufficient for {test_amount} DOGE test)", data)
                        else:
                            self.log_test("User Balance Verification", False, 
                                        f"Insufficient balance: {doge_balance:,.0f} DOGE (need {test_amount} DOGE)", data)
                    else:
                        self.log_test("User Balance Verification", False, 
                                    "Failed to retrieve wallet information", data)
                else:
                    error_text = await response.text()
                    self.log_test("User Balance Verification", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("User Balance Verification", False, f"Error: {str(e)}")
    
    async def test_nowpayments_api_access(self):
        """Test 3: Test NOWPayments API access with new credentials"""
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
                        self.log_test("NOWPayments API Access", True, 
                                    f"NOWPayments API accessible with key {NOWPAYMENTS_CREDENTIALS['api_key']}", data)
                    else:
                        self.log_test("NOWPayments API Access", False, 
                                    f"NOWPayments API returned unexpected response", data)
                else:
                    error_text = await response.text()
                    self.log_test("NOWPayments API Access", False, 
                                f"NOWPayments API error - HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("NOWPayments API Access", False, f"Error: {str(e)}")
    
    async def test_nowpayments_currencies(self):
        """Test 4: Verify DOGE is supported by NOWPayments"""
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
                        self.log_test("NOWPayments DOGE Support", True, 
                                    f"DOGE supported among {len(currencies)} currencies", data)
                    else:
                        self.log_test("NOWPayments DOGE Support", False, 
                                    f"DOGE not found in supported currencies: {currencies[:10]}...", data)
                else:
                    error_text = await response.text()
                    self.log_test("NOWPayments DOGE Support", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("NOWPayments DOGE Support", False, f"Error: {str(e)}")
    
    async def test_treasury_wallet_validation(self):
        """Test 5: Validate treasury wallet address format"""
        try:
            treasury_wallet = TEST_CREDENTIALS["treasury_wallet"]
            
            # DOGE address validation
            if (treasury_wallet.startswith('D') and 
                len(treasury_wallet) == 34 and 
                treasury_wallet.isalnum()):
                self.log_test("Treasury Wallet Validation", True, 
                            f"Treasury wallet {treasury_wallet} is valid DOGE mainnet format", 
                            {"address": treasury_wallet, "format": "DOGE_mainnet"})
            else:
                self.log_test("Treasury Wallet Validation", False, 
                            f"Treasury wallet {treasury_wallet} is not valid DOGE format", 
                            {"address": treasury_wallet, "issues": "Invalid format"})
        except Exception as e:
            self.log_test("Treasury Wallet Validation", False, f"Error: {str(e)}")
    
    async def test_nowpayments_withdrawal_endpoint(self):
        """Test 6: Test NOWPayments withdrawal endpoint directly"""
        try:
            withdrawal_payload = {
                "wallet_address": TEST_CREDENTIALS["casino_wallet"],
                "currency": "DOGE",
                "amount": TEST_CREDENTIALS["test_amount"],
                "destination_address": TEST_CREDENTIALS["treasury_wallet"]
            }
            
            async with self.session.post(f"{self.base_url}/nowpayments/withdraw", 
                                       json=withdrawal_payload) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        if data.get("success"):
                            transaction_id = data.get("transaction_id")
                            self.log_test("NOWPayments Withdrawal Endpoint", True, 
                                        f"✅ WITHDRAWAL SUCCESSFUL! Transaction ID: {transaction_id}", data)
                        else:
                            self.log_test("NOWPayments Withdrawal Endpoint", False, 
                                        f"Withdrawal failed: {data.get('message', 'Unknown error')}", data)
                    except json.JSONDecodeError:
                        self.log_test("NOWPayments Withdrawal Endpoint", False, 
                                    f"Invalid JSON response: {response_text}")
                elif response.status == 401:
                    self.log_test("NOWPayments Withdrawal Endpoint", False, 
                                f"❌ 401 UNAUTHORIZED - Payout permissions still not activated: {response_text}")
                elif response.status == 403:
                    self.log_test("NOWPayments Withdrawal Endpoint", False, 
                                f"❌ 403 FORBIDDEN - Authentication required: {response_text}")
                elif response.status == 404:
                    self.log_test("NOWPayments Withdrawal Endpoint", False, 
                                f"❌ 404 NOT FOUND - Endpoint not implemented: {response_text}")
                else:
                    self.log_test("NOWPayments Withdrawal Endpoint", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("NOWPayments Withdrawal Endpoint", False, f"Error: {str(e)}")
    
    async def test_wallet_external_withdraw(self):
        """Test 7: Test wallet manager external withdrawal endpoint"""
        try:
            withdrawal_payload = {
                "wallet_address": TEST_CREDENTIALS["casino_wallet"],
                "wallet_type": "deposit",
                "currency": "DOGE",
                "amount": TEST_CREDENTIALS["test_amount"],
                "destination_address": TEST_CREDENTIALS["treasury_wallet"]
            }
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=withdrawal_payload) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        if data.get("success"):
                            transaction_hash = data.get("blockchain_transaction_hash")
                            if transaction_hash:
                                self.log_test("Wallet External Withdraw", True, 
                                            f"✅ EXTERNAL WITHDRAWAL SUCCESSFUL! Blockchain hash: {transaction_hash}", data)
                            else:
                                self.log_test("Wallet External Withdraw", True, 
                                            f"✅ WITHDRAWAL PROCESSED: {data.get('message')}", data)
                        else:
                            error_msg = data.get("message", "Unknown error")
                            if "Invalid DOGE address format" in error_msg:
                                self.log_test("Wallet External Withdraw", False, 
                                            f"❌ DOGE ADDRESS VALIDATION BUG: {error_msg}", data)
                            elif "Insufficient" in error_msg:
                                self.log_test("Wallet External Withdraw", False, 
                                            f"❌ INSUFFICIENT BALANCE: {error_msg}", data)
                            else:
                                self.log_test("Wallet External Withdraw", False, 
                                            f"Withdrawal failed: {error_msg}", data)
                    except json.JSONDecodeError:
                        self.log_test("Wallet External Withdraw", False, 
                                    f"Invalid JSON response: {response_text}")
                else:
                    self.log_test("Wallet External Withdraw", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("Wallet External Withdraw", False, f"Error: {str(e)}")
    
    async def test_treasury_transfer_internal(self):
        """Test 8: Test internal treasury transfer functionality"""
        try:
            # Test internal transfer between treasury wallets
            transfer_payload = {
                "wallet_address": TEST_CREDENTIALS["casino_wallet"],
                "from_wallet": "deposit",
                "to_wallet": "savings",
                "currency": "DOGE",
                "amount": 100  # Small internal transfer
            }
            
            async with self.session.post(f"{self.base_url}/treasury/transfer", 
                                       json=transfer_payload) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = json.loads(response_text)
                        if data.get("success"):
                            self.log_test("Treasury Transfer Internal", True, 
                                        f"✅ INTERNAL TRANSFER SUCCESSFUL: {data.get('message')}", data)
                        else:
                            self.log_test("Treasury Transfer Internal", False, 
                                        f"Internal transfer failed: {data.get('message')}", data)
                    except json.JSONDecodeError:
                        self.log_test("Treasury Transfer Internal", False, 
                                    f"Invalid JSON response: {response_text}")
                elif response.status == 404:
                    self.log_test("Treasury Transfer Internal", False, 
                                f"❌ Treasury transfer endpoint not implemented: {response_text}")
                else:
                    self.log_test("Treasury Transfer Internal", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("Treasury Transfer Internal", False, f"Error: {str(e)}")
    
    async def test_nowpayments_payout_direct(self):
        """Test 9: Direct NOWPayments payout API test"""
        try:
            # Test NOWPayments payout API directly
            nowpayments_url = "https://api.nowpayments.io/v1/payout"
            headers = {
                "x-api-key": NOWPAYMENTS_CREDENTIALS["api_key"],
                "Content-Type": "application/json"
            }
            
            payout_payload = {
                "withdrawals": [
                    {
                        "address": TEST_CREDENTIALS["treasury_wallet"],
                        "currency": "doge",
                        "amount": TEST_CREDENTIALS["test_amount"],
                        "ipn_callback_url": f"{self.base_url}/nowpayments/ipn"
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
                            self.log_test("NOWPayments Payout Direct", True, 
                                        f"✅ DIRECT PAYOUT SUCCESSFUL! Payout ID: {data.get('id')}", data)
                        else:
                            self.log_test("NOWPayments Payout Direct", False, 
                                        f"Unexpected payout response format", data)
                    except json.JSONDecodeError:
                        self.log_test("NOWPayments Payout Direct", False, 
                                    f"Invalid JSON response: {response_text}")
                elif response.status == 401:
                    if "Bearer JWTtoken is required" in response_text:
                        self.log_test("NOWPayments Payout Direct", False, 
                                    f"❌ 401 UNAUTHORIZED - Bearer JWT token required: {response_text}")
                    else:
                        self.log_test("NOWPayments Payout Direct", False, 
                                    f"❌ 401 UNAUTHORIZED - API key not authorized for payouts: {response_text}")
                elif response.status == 403:
                    self.log_test("NOWPayments Payout Direct", False, 
                                f"❌ 403 FORBIDDEN - Payout permissions not activated: {response_text}")
                else:
                    self.log_test("NOWPayments Payout Direct", False, 
                                f"HTTP {response.status}: {response_text}")
        except Exception as e:
            self.log_test("NOWPayments Payout Direct", False, f"Error: {str(e)}")
    
    async def test_balance_after_withdrawal_attempt(self):
        """Test 10: Check balance after withdrawal attempts"""
        try:
            wallet_address = TEST_CREDENTIALS["casino_wallet"]
            
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        doge_balance = deposit_balance.get("DOGE", 0)
                        
                        expected_balance = TEST_CREDENTIALS["expected_balance"]
                        
                        # Check if balance changed (indicating successful withdrawal)
                        if doge_balance < expected_balance:
                            difference = expected_balance - doge_balance
                            self.log_test("Balance After Withdrawal", True, 
                                        f"✅ BALANCE DECREASED by {difference:,.0f} DOGE - withdrawal may have succeeded! New balance: {doge_balance:,.0f}", data)
                        else:
                            self.log_test("Balance After Withdrawal", True, 
                                        f"Balance unchanged: {doge_balance:,.0f} DOGE - withdrawals likely failed as expected", data)
                    else:
                        self.log_test("Balance After Withdrawal", False, 
                                    "Failed to retrieve wallet information", data)
                else:
                    error_text = await response.text()
                    self.log_test("Balance After Withdrawal", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Balance After Withdrawal", False, f"Error: {str(e)}")
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🚨 URGENT: NOWPayments Real Treasury Withdrawal Test Results")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        print(f"✅ PASSED: {passed_tests}")
        print(f"❌ FAILED: {failed_tests}")
        print()
        
        # Critical findings
        print("🎯 CRITICAL FINDINGS:")
        
        # Check for successful withdrawals
        withdrawal_tests = [r for r in self.test_results if "withdrawal" in r["test"].lower() or "payout" in r["test"].lower()]
        successful_withdrawals = [r for r in withdrawal_tests if r["success"]]
        
        if successful_withdrawals:
            print("✅ BREAKTHROUGH: Real withdrawals are working!")
            for test in successful_withdrawals:
                print(f"   - {test['test']}: {test['details']}")
        else:
            print("❌ WITHDRAWALS STILL BLOCKED: Payout permissions not yet activated")
            
        # Check authentication
        auth_test = next((r for r in self.test_results if "authentication" in r["test"].lower()), None)
        if auth_test and auth_test["success"]:
            print(f"✅ USER ACCESS: {auth_test['details']}")
        else:
            print("❌ USER ACCESS: Authentication failed")
            
        # Check balance
        balance_test = next((r for r in self.test_results if "balance verification" in r["test"].lower()), None)
        if balance_test and balance_test["success"]:
            print(f"✅ BALANCE STATUS: {balance_test['details']}")
        else:
            print("❌ BALANCE STATUS: Insufficient funds or access issues")
            
        # Check NOWPayments API
        api_test = next((r for r in self.test_results if "nowpayments api" in r["test"].lower()), None)
        if api_test and api_test["success"]:
            print(f"✅ NOWPAYMENTS API: {api_test['details']}")
        else:
            print("❌ NOWPAYMENTS API: Connection or authentication issues")
        
        print()
        print("🔍 DETAILED TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result["success"] else "❌"
            print(f"{i:2d}. {status} {result['test']}")
            print(f"    {result['details']}")
        
        print()
        print("🎯 FINAL ASSESSMENT:")
        if any("WITHDRAWAL SUCCESSFUL" in r["details"] for r in self.test_results):
            print("🎉 SUCCESS: NOWPayments withdrawals are now working!")
            print("   The user can proceed with real treasury withdrawals.")
        elif any("401 UNAUTHORIZED" in r["details"] or "403 FORBIDDEN" in r["details"] for r in self.test_results):
            print("⏳ PENDING: Payout permissions still not activated by NOWPayments support.")
            print("   The system is ready but waiting for final activation.")
        elif any("Invalid DOGE address" in r["details"] for r in self.test_results):
            print("🔧 TECHNICAL ISSUE: DOGE address validation bug needs fixing.")
            print("   Backend incorrectly rejects valid DOGE addresses.")
        else:
            print("❓ UNCLEAR: Mixed results - manual investigation needed.")
        
        print("="*80)

async def main():
    """Run the NOWPayments withdrawal test suite"""
    print("🚨 URGENT: Testing NOWPayments Real Treasury Withdrawal")
    print("Testing if payout permissions are finally activated...")
    print()
    
    async with NOWPaymentsWithdrawalTester(BACKEND_URL) as tester:
        # Run all tests in sequence
        await tester.test_user_authentication()
        await tester.test_user_balance_verification()
        await tester.test_nowpayments_api_access()
        await tester.test_nowpayments_currencies()
        await tester.test_treasury_wallet_validation()
        await tester.test_nowpayments_withdrawal_endpoint()
        await tester.test_wallet_external_withdraw()
        await tester.test_treasury_transfer_internal()
        await tester.test_nowpayments_payout_direct()
        await tester.test_balance_after_withdrawal_attempt()
        
        # Print comprehensive summary
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())