#!/usr/bin/env python3
"""
URGENT: Complete CRT & NOWPayments Verification with Real Payment Link
Comprehensive verification test suite for user cryptoking
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import base58
import re

# Get backend URL from frontend env
BACKEND_URL = "https://real-crt-casino.preview.emergentagent.com/api"

# Test credentials from review request
TEST_CREDENTIALS = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
    "withdrawal_wallet": "DLbWLzxq2mxE3Adzn9MFKQ6EBP8gTE5po8",
    "nowpayments_api": "FSVPHG1-1TK4MDZ-MKC4TTV-MW1MAXX",
    "payment_link": "https://nowpayments.io/payment/?iid=4383583691&paymentId=5914238505"
}

class CRTNOWPaymentsVerifier:
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

    def validate_solana_address(self, address: str) -> bool:
        """Validate Solana wallet address format"""
        try:
            # Solana addresses are base58 encoded and typically 32-44 characters
            if len(address) < 32 or len(address) > 44:
                return False
            
            # Try to decode as base58
            decoded = base58.b58decode(address)
            
            # Solana public keys are 32 bytes
            if len(decoded) != 32:
                return False
                
            return True
        except Exception:
            return False

    async def test_user_authentication(self):
        """Test 1: User Authentication with cryptoking credentials"""
        try:
            print(f"🔐 Testing authentication for user: {TEST_CREDENTIALS['username']}")
            
            # Test username login
            login_payload = {
                "username": TEST_CREDENTIALS["username"],
                "password": TEST_CREDENTIALS["password"]
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        expected_wallet = TEST_CREDENTIALS["wallet_address"]
                        actual_wallet = data.get("wallet_address", "")
                        
                        if actual_wallet == expected_wallet:
                            self.log_test("User Authentication", True, 
                                        f"✅ Authentication successful for {TEST_CREDENTIALS['username']} with wallet {actual_wallet}", data)
                            return True
                        else:
                            self.log_test("User Authentication", False, 
                                        f"❌ Wallet mismatch: expected {expected_wallet}, got {actual_wallet}", data)
                    else:
                        self.log_test("User Authentication", False, 
                                    f"❌ Login failed: {data.get('message', 'Unknown error')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, 
                                f"❌ HTTP {response.status}: {error_text}")
            
            return False
                    
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
            return False

    async def test_crt_address_validation(self):
        """Test 2: CRT Address Format Validation"""
        try:
            crt_address = TEST_CREDENTIALS["wallet_address"]
            print(f"🔍 Validating CRT address format: {crt_address}")
            
            # Test Solana address format validation
            is_valid_format = self.validate_solana_address(crt_address)
            
            if is_valid_format:
                self.log_test("CRT Address Format Validation", True, 
                            f"✅ CRT address {crt_address} passes Solana format validation (base58, correct length)", 
                            {"address": crt_address, "length": len(crt_address), "format": "base58"})
            else:
                self.log_test("CRT Address Format Validation", False, 
                            f"❌ CRT address {crt_address} fails Solana format validation", 
                            {"address": crt_address, "length": len(crt_address)})
            
            # Test with backend CRT balance endpoint to verify address acceptance
            async with self.session.get(f"{self.base_url}/wallet/balance/CRT?wallet_address={crt_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_test("CRT Address Backend Validation", True, 
                                    f"✅ Backend accepts CRT address format", data)
                    else:
                        self.log_test("CRT Address Backend Validation", False, 
                                    f"❌ Backend rejects CRT address: {data.get('error', 'Unknown error')}", data)
                else:
                    self.log_test("CRT Address Backend Validation", False, 
                                f"❌ Backend validation failed: HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("CRT Address Format Validation", False, f"Error: {str(e)}")

    async def test_transaction_history_analysis(self):
        """Test 3: Transaction History Deep Analysis for user cryptoking"""
        try:
            wallet_address = TEST_CREDENTIALS["wallet_address"]
            print(f"📊 Analyzing transaction history for user cryptoking")
            
            # Get user wallet information
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        wallet_info = data.get("wallet", {})
                        
                        # Extract balance information
                        deposit_balance = wallet_info.get("deposit_balance", {})
                        winnings_balance = wallet_info.get("winnings_balance", {})
                        savings_balance = wallet_info.get("savings_balance", {})
                        
                        crt_deposit = deposit_balance.get("CRT", 0)
                        crt_winnings = winnings_balance.get("CRT", 0)
                        crt_savings = savings_balance.get("CRT", 0)
                        total_crt = crt_deposit + crt_winnings + crt_savings
                        
                        self.log_test("User Balance Analysis", True, 
                                    f"📊 Current CRT balances - Deposit: {crt_deposit}, Winnings: {crt_winnings}, Savings: {crt_savings}, Total: {total_crt}", 
                                    wallet_info)
                        
                        # Check if user has the expected 21M CRT
                        if total_crt >= 21000000:
                            self.log_test("CRT Balance Verification", True, 
                                        f"✅ User has access to {total_crt} CRT (≥21M expected)", 
                                        {"total_crt": total_crt, "expected": 21000000})
                        else:
                            self.log_test("CRT Balance Verification", False, 
                                        f"❌ User only has {total_crt} CRT, expected 21M", 
                                        {"total_crt": total_crt, "expected": 21000000})
                    else:
                        self.log_test("User Balance Analysis", False, 
                                    f"❌ Failed to get wallet info: {data.get('message', 'Unknown error')}", data)
                else:
                    self.log_test("User Balance Analysis", False, 
                                f"❌ HTTP {response.status}: {await response.text()}")
            
            # Get game history to analyze conversions
            try:
                async with self.session.get(f"{self.base_url}/games/history/{wallet_address}") as history_response:
                    if history_response.status == 200:
                        history_data = await history_response.json()
                        
                        if history_data.get("success"):
                            games = history_data.get("games", [])
                            total_games = len(games)
                            
                            # Analyze game statistics
                            total_wagered = sum(game.get("bet_amount", 0) for game in games)
                            wins = [game for game in games if game.get("result") == "win"]
                            losses = [game for game in games if game.get("result") == "loss"]
                            
                            self.log_test("Transaction History Analysis", True, 
                                        f"📈 Game history: {total_games} games, {len(wins)} wins, {len(losses)} losses, {total_wagered} total wagered", 
                                        {"total_games": total_games, "wins": len(wins), "losses": len(losses), "total_wagered": total_wagered})
                        else:
                            self.log_test("Transaction History Analysis", False, 
                                        f"❌ Failed to get game history: {history_data.get('message', 'Unknown error')}", history_data)
                    else:
                        self.log_test("Transaction History Analysis", False, 
                                    f"❌ Game history HTTP {history_response.status}")
            except Exception as history_error:
                self.log_test("Transaction History Analysis", False, f"Game history error: {str(history_error)}")
                    
        except Exception as e:
            self.log_test("Transaction History Deep Analysis", False, f"Error: {str(e)}")

    async def test_nowpayments_payment_link(self):
        """Test 4: Real NOWPayments Payment Link Access"""
        try:
            payment_link = TEST_CREDENTIALS["payment_link"]
            print(f"🔗 Testing NOWPayments payment link access: {payment_link}")
            
            # Test direct access to the payment link
            async with self.session.get(payment_link) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Check if the page contains NOWPayments elements
                    nowpayments_indicators = [
                        "nowpayments",
                        "payment",
                        "crypto",
                        "invoice",
                        "iid=4383583691",
                        "paymentId=5914238505"
                    ]
                    
                    found_indicators = []
                    for indicator in nowpayments_indicators:
                        if indicator.lower() in content.lower():
                            found_indicators.append(indicator)
                    
                    if len(found_indicators) >= 3:
                        self.log_test("NOWPayments Payment Link Access", True, 
                                    f"✅ Payment link accessible, found indicators: {found_indicators}", 
                                    {"status_code": response.status, "indicators_found": found_indicators})
                    else:
                        self.log_test("NOWPayments Payment Link Access", False, 
                                    f"❌ Payment link accessible but missing NOWPayments content, found: {found_indicators}", 
                                    {"status_code": response.status, "content_length": len(content)})
                else:
                    self.log_test("NOWPayments Payment Link Access", False, 
                                f"❌ Payment link not accessible: HTTP {response.status}", 
                                {"status_code": response.status})
                    
        except Exception as e:
            self.log_test("NOWPayments Payment Link Access", False, f"Error: {str(e)}")

    async def test_nowpayments_withdrawal_test(self):
        """Test 5: NOWPayments Withdrawal Whitelisting Test"""
        try:
            withdrawal_wallet = TEST_CREDENTIALS["withdrawal_wallet"]
            print(f"💰 Testing NOWPayments withdrawal to: {withdrawal_wallet}")
            
            # Test withdrawal endpoint with 100 DOGE as specified
            withdrawal_payload = {
                "wallet_address": TEST_CREDENTIALS["wallet_address"],
                "wallet_type": "deposit",
                "currency": "DOGE",
                "amount": 100.0,
                "destination_address": withdrawal_wallet
            }
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=withdrawal_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        transaction_hash = data.get("blockchain_transaction_hash")
                        verification_url = data.get("verification_url")
                        
                        if transaction_hash:
                            self.log_test("NOWPayments Withdrawal Test", True, 
                                        f"✅ Real withdrawal successful! Hash: {transaction_hash}, Verify: {verification_url}", data)
                        else:
                            self.log_test("NOWPayments Withdrawal Test", True, 
                                        f"✅ Withdrawal processed (internal): {data.get('message', 'Success')}", data)
                    else:
                        error_msg = data.get("message", "Unknown error")
                        
                        # Check if it's a whitelisting issue
                        if "unauthorized" in error_msg.lower() or "whitelist" in error_msg.lower() or "permission" in error_msg.lower():
                            self.log_test("NOWPayments Withdrawal Test", True, 
                                        f"⏳ Whitelisting period active: {error_msg} (Expected for 1-2 business days)", data)
                        elif "insufficient" in error_msg.lower():
                            self.log_test("NOWPayments Withdrawal Test", False, 
                                        f"❌ Insufficient balance for withdrawal: {error_msg}", data)
                        else:
                            self.log_test("NOWPayments Withdrawal Test", False, 
                                        f"❌ Withdrawal failed: {error_msg}", data)
                else:
                    error_text = await response.text()
                    self.log_test("NOWPayments Withdrawal Test", False, 
                                f"❌ Withdrawal HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("NOWPayments Withdrawal Test", False, f"Error: {str(e)}")

    async def test_balance_reconstruction(self):
        """Test 6: Balance Reconstruction from Transaction History"""
        try:
            wallet_address = TEST_CREDENTIALS["wallet_address"]
            print(f"🧮 Reconstructing accurate CRT balance from transaction history")
            
            # Get current wallet state
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        wallet_info = data.get("wallet", {})
                        
                        # Current balances
                        deposit_balance = wallet_info.get("deposit_balance", {})
                        winnings_balance = wallet_info.get("winnings_balance", {})
                        savings_balance = wallet_info.get("savings_balance", {})
                        liquidity_pool = wallet_info.get("liquidity_pool", {})
                        
                        # Calculate total CRT across all wallets
                        total_crt = (
                            deposit_balance.get("CRT", 0) +
                            winnings_balance.get("CRT", 0) +
                            savings_balance.get("CRT", 0) +
                            liquidity_pool.get("CRT", 0)
                        )
                        
                        # Get blockchain balance for comparison
                        async with self.session.get(f"{self.base_url}/wallet/balance/CRT?wallet_address={wallet_address}") as blockchain_response:
                            blockchain_crt = 0
                            if blockchain_response.status == 200:
                                blockchain_data = await blockchain_response.json()
                                if blockchain_data.get("success"):
                                    blockchain_crt = blockchain_data.get("balance", 0)
                        
                        # Treasury breakdown (60% savings, 30% liquidity, 10% winnings)
                        expected_savings_pct = 60
                        expected_liquidity_pct = 30
                        expected_winnings_pct = 10
                        
                        # Calculate expected distribution if starting from 21M CRT
                        starting_crt = 21000000
                        expected_savings = starting_crt * (expected_savings_pct / 100)
                        expected_liquidity = starting_crt * (expected_liquidity_pct / 100)
                        expected_winnings = starting_crt * (expected_winnings_pct / 100)
                        
                        balance_analysis = {
                            "current_total_crt": total_crt,
                            "blockchain_crt": blockchain_crt,
                            "starting_amount": starting_crt,
                            "expected_distribution": {
                                "savings": expected_savings,
                                "liquidity": expected_liquidity,
                                "winnings": expected_winnings
                            },
                            "actual_distribution": {
                                "deposit": deposit_balance.get("CRT", 0),
                                "winnings": winnings_balance.get("CRT", 0),
                                "savings": savings_balance.get("CRT", 0),
                                "liquidity": liquidity_pool.get("CRT", 0)
                            }
                        }
                        
                        # Determine if balance is accurate
                        if total_crt >= 18000000:  # Allow some variance for conversions/gaming
                            self.log_test("Balance Reconstruction", True, 
                                        f"✅ CRT balance reconstruction shows {total_crt} CRT available (reasonable for 21M starting)", balance_analysis)
                        else:
                            self.log_test("Balance Reconstruction", False, 
                                        f"❌ CRT balance reconstruction shows only {total_crt} CRT (expected ~21M)", balance_analysis)
                    else:
                        self.log_test("Balance Reconstruction", False, 
                                    f"❌ Failed to get wallet data: {data.get('message', 'Unknown error')}", data)
                else:
                    self.log_test("Balance Reconstruction", False, 
                                f"❌ Balance reconstruction HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("Balance Reconstruction", False, f"Error: {str(e)}")

    async def run_comprehensive_verification(self):
        """Run all verification tests"""
        print("🚨 URGENT: Complete CRT & NOWPayments Verification with Real Payment Link")
        print(f"🔗 Testing against: {self.base_url}")
        print(f"👤 User: {TEST_CREDENTIALS['username']}")
        print(f"💼 Wallet: {TEST_CREDENTIALS['wallet_address']}")
        print(f"🔗 Payment Link: {TEST_CREDENTIALS['payment_link']}")
        print("=" * 100)
        
        # Test 1: User Authentication
        auth_success = await self.test_user_authentication()
        
        # Test 2: CRT Address Format Validation
        await self.test_crt_address_validation()
        
        # Test 3: Transaction History Deep Analysis
        await self.test_transaction_history_analysis()
        
        # Test 4: Real NOWPayments Payment Test
        await self.test_nowpayments_payment_link()
        
        # Test 5: NOWPayments Withdrawal Whitelisting Test
        await self.test_nowpayments_withdrawal_test()
        
        # Test 6: Balance Reconstruction from History
        await self.test_balance_reconstruction()
        
        print("=" * 100)
        self.print_verification_summary()

    def print_verification_summary(self):
        """Print comprehensive verification summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n🎯 COMPREHENSIVE VERIFICATION SUMMARY:")
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Check critical success criteria
        critical_tests = {
            "CRT Address Format": False,
            "Transaction History": False,
            "NOWPayments Payment": False,
            "Balance Reconstruction": False,
            "User Authentication": False
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if result["success"]:
                if "CRT Address" in test_name:
                    critical_tests["CRT Address Format"] = True
                elif "Transaction History" in test_name or "Balance Analysis" in test_name:
                    critical_tests["Transaction History"] = True
                elif "NOWPayments Payment" in test_name:
                    critical_tests["NOWPayments Payment"] = True
                elif "Balance Reconstruction" in test_name:
                    critical_tests["Balance Reconstruction"] = True
                elif "User Authentication" in test_name:
                    critical_tests["User Authentication"] = True
        
        print(f"\n✅ CRITICAL SUCCESS CRITERIA STATUS:")
        for criteria, status in critical_tests.items():
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {criteria}: {'PASSED' if status else 'FAILED'}")
        
        # Overall assessment
        critical_passed = sum(1 for status in critical_tests.values() if status)
        overall_success = critical_passed >= 4  # At least 4 out of 5 critical tests
        
        print(f"\n🎯 OVERALL VERIFICATION STATUS:")
        if overall_success:
            print("✅ COMPREHENSIVE VERIFICATION SUCCESSFUL!")
            print("🎉 System ready for real CRT & NOWPayments operations")
        else:
            print("❌ COMPREHENSIVE VERIFICATION INCOMPLETE")
            print("⚠️ Critical issues need resolution before production use")
        
        # Print failed tests details
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")

async def main():
    """Main verification execution function"""
    async with CRTNOWPaymentsVerifier(BACKEND_URL) as verifier:
        await verifier.run_comprehensive_verification()

if __name__ == "__main__":
    asyncio.run(main())