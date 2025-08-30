#!/usr/bin/env python3
"""
DOGE Withdrawal Test Suite - Real External Withdrawal Testing with Authentication
Tests REAL external DOGE withdrawal for user cryptoking to CoinGate address
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://tiger-dex-casino.preview.emergentagent.com/api"

class AuthenticatedDogeWithdrawalTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        self.auth_token = None
        
        # User credentials from review request
        self.user_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        self.username = "cryptoking"
        self.password = "crt21million"
        self.coingate_address = "D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda"
        self.withdrawal_amount = 1000.0  # 1000 DOGE test withdrawal
        
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
        """Test 1: Authenticate user cryptoking and get JWT token"""
        try:
            # Test username login
            login_payload = {
                "username": self.username,
                "password": self.password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("wallet_address") == self.user_wallet:
                        self.log_test("User Authentication", True, 
                                    f"✅ User {self.username} authenticated successfully with wallet {self.user_wallet}", data)
                        
                        # Now get JWT token for API calls
                        await self.get_jwt_token()
                        return True
                    else:
                        self.log_test("User Authentication", False, 
                                    f"Authentication failed or wallet mismatch: {data}", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
            return False
    
    async def get_jwt_token(self):
        """Get JWT token for authenticated API calls"""
        try:
            # Generate challenge
            challenge_payload = {
                "wallet_address": self.user_wallet,
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/auth/challenge", 
                                       json=challenge_payload) as response:
                if response.status == 200:
                    challenge_data = await response.json()
                    if challenge_data.get("success"):
                        # Verify with mock signature (as backend accepts mock signatures)
                        verify_payload = {
                            "challenge_hash": challenge_data.get("challenge_hash"),
                            "signature": "mock_signature_for_withdrawal_test",
                            "wallet_address": self.user_wallet,
                            "network": "solana"
                        }
                        
                        async with self.session.post(f"{self.base_url}/auth/verify", 
                                                   json=verify_payload) as verify_response:
                            if verify_response.status == 200:
                                verify_data = await verify_response.json()
                                if verify_data.get("success"):
                                    self.auth_token = verify_data.get("token")
                                    self.log_test("JWT Token Generation", True, 
                                                f"✅ JWT token obtained for authenticated API calls")
                                    return True
                                    
            self.log_test("JWT Token Generation", False, "Failed to obtain JWT token")
            return False
        except Exception as e:
            self.log_test("JWT Token Generation", False, f"Error: {str(e)}")
            return False
    
    async def test_user_balance_verification(self):
        """Test 2: Verify user has sufficient DOGE balance for withdrawal"""
        try:
            # Get user wallet info
            async with self.session.get(f"{self.base_url}/wallet/{self.user_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        doge_balance = deposit_balance.get("DOGE", 0)
                        
                        if doge_balance >= self.withdrawal_amount:
                            self.log_test("Balance Verification", True, 
                                        f"✅ Sufficient DOGE balance: {doge_balance:,.2f} DOGE (need {self.withdrawal_amount})", data)
                            return True, doge_balance
                        else:
                            self.log_test("Balance Verification", False, 
                                        f"❌ Insufficient DOGE balance: {doge_balance:,.2f} DOGE (need {self.withdrawal_amount})", data)
                            return False, doge_balance
                    else:
                        self.log_test("Balance Verification", False, 
                                    "Failed to retrieve wallet info", data)
                        return False, 0
                else:
                    error_text = await response.text()
                    self.log_test("Balance Verification", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False, 0
        except Exception as e:
            self.log_test("Balance Verification", False, f"Error: {str(e)}")
            return False, 0
    
    async def test_coinpayments_withdraw_endpoint(self):
        """Test 3: Test /api/coinpayments/withdraw endpoint with authentication"""
        try:
            if not self.auth_token:
                self.log_test("CoinPayments Withdraw Endpoint", False, 
                            "No authentication token available")
                return False, {"error": "no_auth_token"}
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get user ID first
            user_id = "0834c788-b59e-4656-9c8b-19a16a446747"  # From test_result.md
            
            withdraw_payload = {
                "user_id": user_id,
                "currency": "DOGE",
                "amount": self.withdrawal_amount,
                "destination_address": self.coingate_address
            }
            
            async with self.session.post(f"{self.base_url}/coinpayments/withdraw", 
                                       json=withdraw_payload, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        data = await response.json() if response.content_type == 'application/json' else {"raw_response": response_text}
                        if data.get("success"):
                            withdrawal_id = data.get("withdrawal", {}).get("withdrawal_id")
                            self.log_test("CoinPayments Withdraw Endpoint", True, 
                                        f"✅ CoinPayments withdrawal successful! Withdrawal ID: {withdrawal_id}", data)
                            return True, data
                        else:
                            self.log_test("CoinPayments Withdraw Endpoint", False, 
                                        f"CoinPayments withdrawal failed: {data.get('message', 'Unknown error')}", data)
                            return False, data
                    except json.JSONDecodeError:
                        self.log_test("CoinPayments Withdraw Endpoint", False, 
                                    f"Invalid JSON response: {response_text}")
                        return False, {"raw_response": response_text}
                else:
                    self.log_test("CoinPayments Withdraw Endpoint", False, 
                                f"HTTP {response.status}: {response_text}")
                    return False, {"error": response_text}
        except Exception as e:
            self.log_test("CoinPayments Withdraw Endpoint", False, f"Error: {str(e)}")
            return False, {"error": str(e)}
    
    async def test_standard_withdraw_with_destination(self):
        """Test 4: Test standard /api/wallet/withdraw endpoint with destination address"""
        try:
            withdraw_payload = {
                "wallet_address": self.user_wallet,
                "wallet_type": "deposit",
                "currency": "DOGE",
                "amount": self.withdrawal_amount,
                "destination_address": self.coingate_address
            }
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=withdraw_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        transaction_id = data.get("transaction_id")
                        blockchain_hash = data.get("blockchain_transaction_hash")
                        verification_url = data.get("verification_url")
                        self.log_test("Standard Withdraw with Destination", True, 
                                    f"✅ Standard withdrawal with destination successful! TX ID: {transaction_id}, Blockchain: {blockchain_hash}, Verify: {verification_url}", data)
                        return True, data
                    else:
                        self.log_test("Standard Withdraw with Destination", False, 
                                    f"Standard withdrawal failed: {data.get('message', 'Unknown error')}", data)
                        return False, data
                else:
                    error_text = await response.text()
                    self.log_test("Standard Withdraw with Destination", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False, {"error": error_text}
        except Exception as e:
            self.log_test("Standard Withdraw with Destination", False, f"Error: {str(e)}")
            return False, {"error": str(e)}
    
    async def test_vault_withdrawal_system(self):
        """Test 5: Test non-custodial vault withdrawal system"""
        try:
            # First get vault address
            async with self.session.get(f"{self.base_url}/savings/vault/address/{self.user_wallet}") as response:
                if response.status == 200:
                    vault_data = await response.json()
                    if vault_data.get("success"):
                        vault_addresses = vault_data.get("vault_addresses", {})
                        doge_vault_address = vault_addresses.get("DOGE")
                        
                        if doge_vault_address:
                            # Test vault withdrawal
                            vault_withdraw_payload = {
                                "user_wallet": self.user_wallet,
                                "currency": "DOGE",
                                "amount": self.withdrawal_amount,
                                "destination_address": self.coingate_address
                            }
                            
                            async with self.session.post(f"{self.base_url}/savings/vault/withdraw", 
                                                       json=vault_withdraw_payload) as withdraw_response:
                                if withdraw_response.status == 200:
                                    withdraw_data = await withdraw_response.json()
                                    if withdraw_data.get("success"):
                                        transaction_id = withdraw_data.get("transaction_id")
                                        requires_signature = withdraw_data.get("requires_user_signature")
                                        self.log_test("Vault Withdrawal System", True, 
                                                    f"✅ Vault withdrawal created! TX ID: {transaction_id}, Requires signature: {requires_signature}, Vault: {doge_vault_address}", withdraw_data)
                                        return True, withdraw_data
                                    else:
                                        self.log_test("Vault Withdrawal System", False, 
                                                    f"Vault withdrawal failed: {withdraw_data.get('message', 'Unknown error')}", withdraw_data)
                                        return False, withdraw_data
                                else:
                                    error_text = await withdraw_response.text()
                                    self.log_test("Vault Withdrawal System", False, 
                                                f"Vault withdrawal HTTP {withdraw_response.status}: {error_text}")
                                    return False, {"error": error_text}
                        else:
                            self.log_test("Vault Withdrawal System", False, 
                                        "No DOGE vault address found", vault_data)
                            return False, vault_data
                    else:
                        self.log_test("Vault Withdrawal System", False, 
                                    "Failed to get vault addresses", vault_data)
                        return False, vault_data
                else:
                    error_text = await response.text()
                    self.log_test("Vault Withdrawal System", False, 
                                f"Vault address HTTP {response.status}: {error_text}")
                    return False, {"error": error_text}
        except Exception as e:
            self.log_test("Vault Withdrawal System", False, f"Error: {str(e)}")
            return False, {"error": str(e)}
    
    async def test_coingate_address_validation(self):
        """Test 6: Validate CoinGate DOGE address format"""
        try:
            # Validate the CoinGate address format
            if (self.coingate_address.startswith('D') and 
                len(self.coingate_address) >= 25 and 
                len(self.coingate_address) <= 34 and
                self.coingate_address.isalnum()):
                
                self.log_test("CoinGate Address Validation", True, 
                            f"✅ CoinGate address {self.coingate_address} has valid DOGE format")
                return True
            else:
                self.log_test("CoinGate Address Validation", False, 
                            f"❌ CoinGate address {self.coingate_address} has invalid DOGE format")
                return False
        except Exception as e:
            self.log_test("CoinGate Address Validation", False, f"Error: {str(e)}")
            return False
    
    async def test_balance_after_withdrawal(self):
        """Test 7: Verify balance is deducted after successful withdrawal"""
        try:
            # Get updated wallet balance
            async with self.session.get(f"{self.base_url}/wallet/{self.user_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        current_doge_balance = deposit_balance.get("DOGE", 0)
                        
                        # Expected balance should be reduced by withdrawal amount
                        expected_balance = 35982539.79 - self.withdrawal_amount  # Original balance minus withdrawal
                        
                        if abs(current_doge_balance - expected_balance) < 0.01:  # Allow small floating point differences
                            self.log_test("Balance After Withdrawal", True, 
                                        f"✅ Balance correctly updated: {current_doge_balance:,.2f} DOGE (expected ~{expected_balance:,.2f})", data)
                            return True, current_doge_balance
                        else:
                            self.log_test("Balance After Withdrawal", False, 
                                        f"❌ Balance not updated correctly: {current_doge_balance:,.2f} DOGE (expected ~{expected_balance:,.2f})", data)
                            return False, current_doge_balance
                    else:
                        self.log_test("Balance After Withdrawal", False, 
                                    "Failed to retrieve updated wallet info", data)
                        return False, 0
                else:
                    error_text = await response.text()
                    self.log_test("Balance After Withdrawal", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False, 0
        except Exception as e:
            self.log_test("Balance After Withdrawal", False, f"Error: {str(e)}")
            return False, 0
    
    async def run_comprehensive_test(self):
        """Run all DOGE withdrawal tests in sequence"""
        print("🚀 Starting Authenticated DOGE Withdrawal Test Suite")
        print(f"User: {self.username} (Wallet: {self.user_wallet})")
        print(f"Destination: {self.coingate_address} (CoinGate)")
        print(f"Amount: {self.withdrawal_amount} DOGE")
        print("=" * 80)
        
        # Test 1: Authentication
        auth_success = await self.test_user_authentication()
        if not auth_success:
            print("❌ Authentication failed - cannot proceed with withdrawal tests")
            return self.test_results
        
        # Test 2: Balance verification
        balance_success, current_balance = await self.test_user_balance_verification()
        if not balance_success:
            print(f"❌ Insufficient balance ({current_balance:,.2f} DOGE) - cannot proceed with withdrawal")
            return self.test_results
        
        # Test 3: Address validation
        await self.test_coingate_address_validation()
        
        # Test 4-6: Try different withdrawal endpoints
        coinpayments_success, coinpayments_data = await self.test_coinpayments_withdraw_endpoint()
        standard_success, standard_data = await self.test_standard_withdraw_with_destination()
        vault_success, vault_data = await self.test_vault_withdrawal_system()
        
        # Test 7: Post-withdrawal verification
        if any([coinpayments_success, standard_success, vault_success]):
            await self.test_balance_after_withdrawal()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 DOGE WITHDRAWAL TEST SUMMARY")
        print("=" * 80)
        
        successful_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"✅ Successful Tests: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Withdrawal method results
        withdrawal_methods = [
            ("CoinPayments", coinpayments_success),
            ("Standard with Destination", standard_success),
            ("Vault System", vault_success)
        ]
        
        successful_methods = [method for method, success in withdrawal_methods if success]
        
        if successful_methods:
            print(f"🎉 SUCCESSFUL WITHDRAWAL METHODS: {', '.join(successful_methods)}")
            print(f"💰 WITHDRAWAL EXECUTED: {self.withdrawal_amount} DOGE to {self.coingate_address}")
        else:
            print("❌ NO WITHDRAWAL METHODS SUCCESSFUL")
        
        print("\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return self.test_results

async def main():
    """Main test execution"""
    async with AuthenticatedDogeWithdrawalTester(BACKEND_URL) as tester:
        results = await tester.run_comprehensive_test()
        
        # Return exit code based on critical tests
        critical_tests = ["User Authentication", "Balance Verification"]
        critical_failures = [r for r in results if r["test"] in critical_tests and not r["success"]]
        
        if critical_failures:
            print(f"\n❌ CRITICAL TEST FAILURES: {len(critical_failures)}")
            sys.exit(1)
        else:
            withdrawal_tests = [r for r in results if "Withdraw" in r["test"]]
            successful_withdrawals = [r for r in withdrawal_tests if r["success"]]
            
            if successful_withdrawals:
                print(f"\n🎉 SUCCESS: {len(successful_withdrawals)} withdrawal method(s) working!")
                sys.exit(0)
            else:
                print(f"\n⚠️ WARNING: No withdrawal methods successful")
                sys.exit(2)

if __name__ == "__main__":
    asyncio.run(main())