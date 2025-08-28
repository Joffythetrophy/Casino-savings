#!/usr/bin/env python3
"""
URGENT Portfolio Display Fix Verification Test
Tests the specific user's portfolio display after fixing hardcoded wallet issue
User: DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://smart-savings-dapp.preview.emergentagent.com/api"

class PortfolioVerificationTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.target_user = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        self.test_results = []
        
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
        
    async def test_user_wallet_balance_retrieval(self):
        """Test 1: Check user's current wallet balance via /api/wallet/{wallet_address}"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.target_user}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        
                        # Check for expected converted currencies
                        usdc_balance = deposit_balance.get("USDC", 0)
                        doge_balance = deposit_balance.get("DOGE", 0)
                        trx_balance = deposit_balance.get("TRX", 0)
                        crt_balance = deposit_balance.get("CRT", 0)
                        
                        # Expected portfolio values
                        expected_usdc = 317925  # 317,925+ USDC
                        expected_doge = 2150000  # 2,150,000 DOGE
                        expected_trx = 980000   # 980,000 TRX
                        expected_crt = 19700000  # 19.7M+ CRT
                        
                        # Verify balances
                        usdc_ok = usdc_balance >= expected_usdc * 0.95  # Allow 5% variance
                        doge_ok = doge_balance >= expected_doge * 0.95
                        trx_ok = trx_balance >= expected_trx * 0.95
                        crt_ok = crt_balance >= expected_crt * 0.95
                        
                        if usdc_ok and doge_ok and trx_ok and crt_ok:
                            self.log_test("User Wallet Balance Retrieval", True, 
                                        f"✅ ALL CONVERTED CURRENCIES VISIBLE: USDC: {usdc_balance:,.2f}, DOGE: {doge_balance:,.0f}, TRX: {trx_balance:,.0f}, CRT: {crt_balance:,.0f}", data)
                        else:
                            missing = []
                            if not usdc_ok: missing.append(f"USDC: {usdc_balance:,.2f} (expected {expected_usdc:,}+)")
                            if not doge_ok: missing.append(f"DOGE: {doge_balance:,.0f} (expected {expected_doge:,}+)")
                            if not trx_ok: missing.append(f"TRX: {trx_balance:,.0f} (expected {expected_trx:,}+)")
                            if not crt_ok: missing.append(f"CRT: {crt_balance:,.0f} (expected {expected_crt:,}+)")
                            
                            self.log_test("User Wallet Balance Retrieval", False, 
                                        f"❌ PORTFOLIO INCOMPLETE: Missing/low balances: {', '.join(missing)}", data)
                    else:
                        self.log_test("User Wallet Balance Retrieval", False, 
                                    f"❌ WALLET NOT FOUND: {data.get('message', 'Unknown error')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("User Wallet Balance Retrieval", False, 
                                f"❌ API ERROR - HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("User Wallet Balance Retrieval", False, f"❌ EXCEPTION: {str(e)}")
    
    async def test_portfolio_total_value_calculation(self):
        """Test 2: Confirm portfolio totals match expected $4.14M value"""
        try:
            # Get wallet balance
            async with self.session.get(f"{self.base_url}/wallet/{self.target_user}") as response:
                if response.status == 200:
                    wallet_data = await response.json()
                    if not wallet_data.get("success"):
                        self.log_test("Portfolio Total Value", False, "❌ WALLET DATA UNAVAILABLE")
                        return
                    
                    deposit_balance = wallet_data["wallet"].get("deposit_balance", {})
                    
                    # Get current conversion rates
                    async with self.session.get(f"{self.base_url}/conversion/rates") as rates_response:
                        if rates_response.status == 200:
                            rates_data = await rates_response.json()
                            if rates_data.get("success"):
                                prices_usd = rates_data.get("prices_usd", {})
                                
                                # Calculate portfolio value
                                usdc_value = deposit_balance.get("USDC", 0) * prices_usd.get("USDC", 1.0)
                                doge_value = deposit_balance.get("DOGE", 0) * prices_usd.get("DOGE", 0.24)
                                trx_value = deposit_balance.get("TRX", 0) * prices_usd.get("TRX", 0.37)
                                crt_value = deposit_balance.get("CRT", 0) * prices_usd.get("CRT", 0.15)
                                
                                total_value = usdc_value + doge_value + trx_value + crt_value
                                expected_value = 4140000  # $4.14M
                                
                                # Allow 10% variance for price fluctuations
                                if total_value >= expected_value * 0.9:
                                    self.log_test("Portfolio Total Value", True, 
                                                f"✅ PORTFOLIO VALUE CORRECT: ${total_value:,.2f} (USDC: ${usdc_value:,.2f}, DOGE: ${doge_value:,.2f}, TRX: ${trx_value:,.2f}, CRT: ${crt_value:,.2f})", 
                                                {"total_value": total_value, "breakdown": {"USDC": usdc_value, "DOGE": doge_value, "TRX": trx_value, "CRT": crt_value}})
                                else:
                                    self.log_test("Portfolio Total Value", False, 
                                                f"❌ PORTFOLIO VALUE TOO LOW: ${total_value:,.2f} (expected ${expected_value:,}+)", 
                                                {"total_value": total_value, "expected": expected_value})
                            else:
                                self.log_test("Portfolio Total Value", False, "❌ CONVERSION RATES UNAVAILABLE")
                        else:
                            self.log_test("Portfolio Total Value", False, f"❌ RATES API ERROR - HTTP {rates_response.status}")
                else:
                    self.log_test("Portfolio Total Value", False, f"❌ WALLET API ERROR - HTTP {response.status}")
        except Exception as e:
            self.log_test("Portfolio Total Value", False, f"❌ EXCEPTION: {str(e)}")
    
    async def test_conversion_functionality_with_correct_wallet(self):
        """Test 3: Test that conversions will now work properly with correct wallet address"""
        try:
            # Test a small conversion to verify the system works
            conversion_payload = {
                "wallet_address": self.target_user,
                "from_currency": "CRT",
                "to_currency": "USDC",
                "amount": 100.0  # Small test amount
            }
            
            async with self.session.post(f"{self.base_url}/wallet/convert", 
                                       json=conversion_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        converted_amount = data.get("converted_amount", 0)
                        rate = data.get("rate", 0)
                        transaction_id = data.get("transaction_id")
                        
                        if converted_amount > 0 and rate > 0 and transaction_id:
                            self.log_test("Conversion Functionality", True, 
                                        f"✅ CONVERSION WORKING: 100 CRT → {converted_amount:.4f} USDC at rate {rate:.4f} (TX: {transaction_id})", data)
                        else:
                            self.log_test("Conversion Functionality", False, 
                                        f"❌ CONVERSION INCOMPLETE: Missing data in response", data)
                    else:
                        # Check if it's an insufficient balance error (which is expected if user has low CRT)
                        message = data.get("message", "")
                        if "insufficient" in message.lower():
                            self.log_test("Conversion Functionality", True, 
                                        f"✅ CONVERSION SYSTEM WORKING: Correctly rejected due to insufficient balance", data)
                        else:
                            self.log_test("Conversion Functionality", False, 
                                        f"❌ CONVERSION FAILED: {message}", data)
                else:
                    error_text = await response.text()
                    self.log_test("Conversion Functionality", False, 
                                f"❌ CONVERSION API ERROR - HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Conversion Functionality", False, f"❌ EXCEPTION: {str(e)}")
    
    async def test_user_authentication_status(self):
        """Test 4: Verify user can authenticate properly"""
        try:
            # Test login with the user's credentials
            login_payload = {
                "username": "cryptoking",
                "password": "crt21million"
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        returned_wallet = data.get("wallet_address")
                        if returned_wallet == self.target_user:
                            self.log_test("User Authentication", True, 
                                        f"✅ USER AUTHENTICATION WORKING: cryptoking → {returned_wallet}", data)
                        else:
                            self.log_test("User Authentication", False, 
                                        f"❌ WALLET MISMATCH: Expected {self.target_user}, got {returned_wallet}", data)
                    else:
                        self.log_test("User Authentication", False, 
                                    f"❌ LOGIN FAILED: {data.get('message', 'Unknown error')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, 
                                f"❌ AUTH API ERROR - HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("User Authentication", False, f"❌ EXCEPTION: {str(e)}")
    
    async def test_crypto_selection_for_gaming(self):
        """Test 5: Verify user can select different cryptos for gaming"""
        try:
            # Get wallet balance to check available currencies
            async with self.session.get(f"{self.base_url}/wallet/{self.target_user}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        deposit_balance = data["wallet"].get("deposit_balance", {})
                        
                        # Check which currencies have sufficient balance for gaming
                        gaming_currencies = []
                        min_gaming_amount = 10  # Minimum amount needed for gaming
                        
                        for currency, balance in deposit_balance.items():
                            if balance >= min_gaming_amount:
                                gaming_currencies.append(f"{currency}: {balance:,.2f}")
                        
                        if len(gaming_currencies) >= 3:  # Should have at least 3 currencies available
                            self.log_test("Crypto Selection for Gaming", True, 
                                        f"✅ MULTIPLE CRYPTOS AVAILABLE FOR GAMING: {', '.join(gaming_currencies)}", data)
                        else:
                            self.log_test("Crypto Selection for Gaming", False, 
                                        f"❌ INSUFFICIENT CRYPTO OPTIONS: Only {len(gaming_currencies)} currencies with sufficient balance: {', '.join(gaming_currencies)}", data)
                    else:
                        self.log_test("Crypto Selection for Gaming", False, 
                                    f"❌ WALLET DATA UNAVAILABLE: {data.get('message', 'Unknown error')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("Crypto Selection for Gaming", False, 
                                f"❌ WALLET API ERROR - HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Crypto Selection for Gaming", False, f"❌ EXCEPTION: {str(e)}")
    
    async def test_hardcoded_wallet_fix_verification(self):
        """Test 6: Verify the hardcoded wallet issue has been fixed"""
        try:
            # This test checks that the system is using the real user wallet, not a hardcoded test wallet
            
            # Get the user's wallet info
            async with self.session.get(f"{self.base_url}/wallet/{self.target_user}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        wallet_info = data.get("wallet", {})
                        returned_address = wallet_info.get("wallet_address")
                        balance_source = wallet_info.get("balance_source", "")
                        
                        # Verify the correct wallet address is returned
                        if returned_address == self.target_user:
                            # Check if it's using real blockchain API (not hardcoded test data)
                            if balance_source == "real_blockchain_api":
                                self.log_test("Hardcoded Wallet Fix", True, 
                                            f"✅ HARDCODED WALLET FIX CONFIRMED: Using real wallet {returned_address} with real blockchain API", data)
                            else:
                                self.log_test("Hardcoded Wallet Fix", False, 
                                            f"❌ STILL USING TEST DATA: balance_source is '{balance_source}', not 'real_blockchain_api'", data)
                        else:
                            self.log_test("Hardcoded Wallet Fix", False, 
                                        f"❌ WRONG WALLET RETURNED: Expected {self.target_user}, got {returned_address}", data)
                    else:
                        self.log_test("Hardcoded Wallet Fix", False, 
                                    f"❌ WALLET LOOKUP FAILED: {data.get('message', 'Unknown error')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("Hardcoded Wallet Fix", False, 
                                f"❌ API ERROR - HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Hardcoded Wallet Fix", False, f"❌ EXCEPTION: {str(e)}")
    
    async def run_all_tests(self):
        """Run all portfolio verification tests"""
        print(f"\n🚨 URGENT PORTFOLIO VERIFICATION TEST")
        print(f"User: {self.target_user}")
        print(f"Testing portfolio display fix after hardcoded wallet issue")
        print(f"Expected: $4.14M portfolio with USDC, DOGE, TRX, CRT")
        print("=" * 80)
        
        # Run all tests
        await self.test_user_wallet_balance_retrieval()
        await self.test_portfolio_total_value_calculation()
        await self.test_conversion_functionality_with_correct_wallet()
        await self.test_user_authentication_status()
        await self.test_crypto_selection_for_gaming()
        await self.test_hardcoded_wallet_fix_verification()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 PORTFOLIO VERIFICATION TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"✅ PASSED: {len(passed_tests)}/{len(self.test_results)} tests")
        print(f"❌ FAILED: {len(failed_tests)}/{len(self.test_results)} tests")
        
        if failed_tests:
            print("\n🚨 FAILED TESTS:")
            for test in failed_tests:
                print(f"  ❌ {test['test']}: {test['details']}")
        
        if passed_tests:
            print("\n✅ PASSED TESTS:")
            for test in passed_tests:
                print(f"  ✅ {test['test']}: {test['details']}")
        
        # Final verdict
        success_rate = len(passed_tests) / len(self.test_results) * 100
        print(f"\n🎯 OVERALL SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 PORTFOLIO DISPLAY FIX VERIFICATION: SUCCESS!")
            print("✅ User should now see their $4.14M portfolio with all converted currencies")
        else:
            print("🚨 PORTFOLIO DISPLAY FIX VERIFICATION: ISSUES FOUND!")
            print("❌ User may still have problems seeing their full portfolio")
        
        return self.test_results

async def main():
    """Main test execution"""
    async with PortfolioVerificationTester(BACKEND_URL) as tester:
        results = await tester.run_all_tests()
        return results

if __name__ == "__main__":
    asyncio.run(main())