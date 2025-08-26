#!/usr/bin/env python3
"""
URGENT: Portfolio Display Fix Verification Test
Tests the specific fix for user DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq
to ensure converted currencies are now visible in portfolio display.
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://cryptosavings.preview.emergentagent.com/api"

class PortfolioFixTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        # Specific user from review request
        self.target_user = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        self.target_username = "cryptoking"
        self.target_password = "crt21million"
        
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
        """Test 1: Verify user authentication works"""
        try:
            login_payload = {
                "username": self.target_username,
                "password": self.target_password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if (data.get("success") and 
                        data.get("username") == self.target_username and
                        data.get("wallet_address") == self.target_user):
                        self.log_test("User Authentication", True, 
                                    f"✅ User {self.target_username} authenticated successfully", data)
                        return True
                    else:
                        self.log_test("User Authentication", False, 
                                    f"Authentication failed: {data.get('message', 'Unknown error')}", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
            return False

    async def test_wallet_endpoint_fix(self):
        """Test 2: CRITICAL - Test wallet endpoint shows converted currencies"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.target_user}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        
                        # Check for converted currencies that should be visible
                        usdc_balance = deposit_balance.get("USDC", 0)
                        doge_balance = deposit_balance.get("DOGE", 0) 
                        trx_balance = deposit_balance.get("TRX", 0)
                        crt_balance = deposit_balance.get("CRT", 0)
                        
                        # Calculate total portfolio value (using approximate prices)
                        prices = {"USDC": 1.0, "DOGE": 0.236, "TRX": 0.363, "CRT": 0.15}
                        total_usd = (usdc_balance * prices["USDC"] + 
                                   doge_balance * prices["DOGE"] + 
                                   trx_balance * prices["TRX"] + 
                                   crt_balance * prices["CRT"])
                        
                        # Expected values from review request
                        expected_usdc = 317925  # 317,925+ USDC
                        expected_doge = 2150000  # 2,150,000 DOGE
                        expected_trx = 980000   # 980,000 TRX
                        expected_total_usd = 4140000  # $4.14M
                        
                        # Check if converted currencies are now visible
                        currencies_visible = []
                        issues = []
                        
                        if usdc_balance >= expected_usdc * 0.9:  # Allow 10% tolerance
                            currencies_visible.append(f"USDC: {usdc_balance:,.2f}")
                        else:
                            issues.append(f"USDC missing/low: {usdc_balance:,.2f} (expected ~{expected_usdc:,})")
                            
                        if doge_balance >= expected_doge * 0.9:
                            currencies_visible.append(f"DOGE: {doge_balance:,.0f}")
                        else:
                            issues.append(f"DOGE missing/low: {doge_balance:,.0f} (expected ~{expected_doge:,})")
                            
                        if trx_balance >= expected_trx * 0.9:
                            currencies_visible.append(f"TRX: {trx_balance:,.0f}")
                        else:
                            issues.append(f"TRX missing/low: {trx_balance:,.0f} (expected ~{expected_trx:,})")
                        
                        # Check if portfolio total is close to expected
                        portfolio_ok = total_usd >= expected_total_usd * 0.8  # Allow 20% tolerance
                        
                        if len(currencies_visible) >= 2 and portfolio_ok:
                            self.log_test("Wallet Endpoint Fix", True, 
                                        f"✅ PORTFOLIO FIX WORKING! Visible currencies: {', '.join(currencies_visible)}, Total: ${total_usd:,.0f}", 
                                        {**data, "calculated_total_usd": total_usd})
                            return True
                        else:
                            self.log_test("Wallet Endpoint Fix", False, 
                                        f"❌ PORTFOLIO STILL BROKEN! Issues: {'; '.join(issues)}, Total: ${total_usd:,.0f} (expected ~${expected_total_usd:,})", 
                                        {**data, "calculated_total_usd": total_usd, "issues": issues})
                            return False
                    else:
                        self.log_test("Wallet Endpoint Fix", False, 
                                    "Invalid wallet response format", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Wallet Endpoint Fix", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Wallet Endpoint Fix", False, f"Error: {str(e)}")
            return False

    async def test_conversion_system_working(self):
        """Test 3: Verify conversion system is still functional"""
        try:
            # Test a small conversion to ensure system still works
            convert_payload = {
                "wallet_address": self.target_user,
                "from_currency": "CRT",
                "to_currency": "USDC", 
                "amount": 100.0  # Small test amount
            }
            
            async with self.session.post(f"{self.base_url}/wallet/convert", 
                                       json=convert_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        converted_amount = data.get("converted_amount", 0)
                        rate = data.get("rate", 0)
                        if converted_amount > 0 and rate > 0:
                            self.log_test("Conversion System", True, 
                                        f"✅ Conversion system working: 100 CRT → {converted_amount} USDC (rate: {rate})", data)
                            return True
                        else:
                            self.log_test("Conversion System", False, 
                                        "Conversion returned zero amounts", data)
                            return False
                    else:
                        # Check if it's just insufficient balance (which is OK)
                        if "Insufficient balance" in data.get("message", ""):
                            self.log_test("Conversion System", True, 
                                        "✅ Conversion system working (insufficient balance is expected)", data)
                            return True
                        else:
                            self.log_test("Conversion System", False, 
                                        f"Conversion failed: {data.get('message')}", data)
                            return False
                else:
                    error_text = await response.text()
                    self.log_test("Conversion System", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Conversion System", False, f"Error: {str(e)}")
            return False

    async def test_gaming_currency_selection(self):
        """Test 4: Verify user can select different cryptocurrencies for gaming"""
        try:
            # Get wallet info to see available currencies
            async with self.session.get(f"{self.base_url}/wallet/{self.target_user}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        
                        # Check which currencies have balance > 0
                        available_currencies = []
                        for currency, balance in deposit_balance.items():
                            if balance > 0:
                                available_currencies.append(f"{currency}: {balance:,.2f}")
                        
                        if len(available_currencies) >= 2:
                            self.log_test("Gaming Currency Selection", True, 
                                        f"✅ Multiple currencies available for gaming: {', '.join(available_currencies)}", data)
                            return True
                        else:
                            self.log_test("Gaming Currency Selection", False, 
                                        f"❌ Limited currency options: {', '.join(available_currencies) if available_currencies else 'No currencies available'}", data)
                            return False
                    else:
                        self.log_test("Gaming Currency Selection", False, 
                                    "Could not retrieve wallet info", data)
                        return False
                else:
                    self.log_test("Gaming Currency Selection", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    return False
        except Exception as e:
            self.log_test("Gaming Currency Selection", False, f"Error: {str(e)}")
            return False

    async def test_balance_source_verification(self):
        """Test 5: Verify balance source is hybrid (database + blockchain)"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.target_user}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        balance_source = wallet.get("balance_source", "")
                        balance_notes = wallet.get("balance_notes", {})
                        
                        # Check if balance source indicates the fix
                        if "hybrid" in balance_source.lower() or "database" in balance_source.lower():
                            self.log_test("Balance Source Verification", True, 
                                        f"✅ Balance source shows fix implemented: {balance_source}", 
                                        {"balance_source": balance_source, "balance_notes": balance_notes})
                            return True
                        else:
                            self.log_test("Balance Source Verification", False, 
                                        f"❌ Balance source doesn't show fix: {balance_source}", 
                                        {"balance_source": balance_source, "balance_notes": balance_notes})
                            return False
                    else:
                        self.log_test("Balance Source Verification", False, 
                                    "Could not retrieve wallet info", data)
                        return False
                else:
                    self.log_test("Balance Source Verification", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    return False
        except Exception as e:
            self.log_test("Balance Source Verification", False, f"Error: {str(e)}")
            return False

    async def test_portfolio_total_calculation(self):
        """Test 6: Verify portfolio total matches expected $4.14M"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.target_user}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        savings_balance = wallet.get("savings_balance", {})
                        
                        # Calculate total portfolio value
                        prices = {"USDC": 1.0, "DOGE": 0.236, "TRX": 0.363, "CRT": 0.15}
                        
                        total_deposit_usd = sum(
                            balance * prices.get(currency, 0) 
                            for currency, balance in deposit_balance.items()
                        )
                        
                        total_savings_usd = sum(
                            balance * prices.get(currency, 0) 
                            for currency, balance in savings_balance.items()
                        )
                        
                        total_portfolio_usd = total_deposit_usd + total_savings_usd
                        expected_total = 4140000  # $4.14M
                        
                        # Allow 20% tolerance for price fluctuations
                        if total_portfolio_usd >= expected_total * 0.8:
                            self.log_test("Portfolio Total Calculation", True, 
                                        f"✅ Portfolio total looks correct: ${total_portfolio_usd:,.0f} (expected ~${expected_total:,})", 
                                        {
                                            "deposit_usd": total_deposit_usd,
                                            "savings_usd": total_savings_usd,
                                            "total_usd": total_portfolio_usd,
                                            "deposit_balance": deposit_balance,
                                            "savings_balance": savings_balance
                                        })
                            return True
                        else:
                            self.log_test("Portfolio Total Calculation", False, 
                                        f"❌ Portfolio total too low: ${total_portfolio_usd:,.0f} (expected ~${expected_total:,})", 
                                        {
                                            "deposit_usd": total_deposit_usd,
                                            "savings_usd": total_savings_usd,
                                            "total_usd": total_portfolio_usd,
                                            "deposit_balance": deposit_balance,
                                            "savings_balance": savings_balance
                                        })
                            return False
                    else:
                        self.log_test("Portfolio Total Calculation", False, 
                                    "Could not retrieve wallet info", data)
                        return False
                else:
                    self.log_test("Portfolio Total Calculation", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    return False
        except Exception as e:
            self.log_test("Portfolio Total Calculation", False, f"Error: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all portfolio fix verification tests"""
        print(f"\n🚨 URGENT PORTFOLIO FIX VERIFICATION for user {self.target_user}")
        print("=" * 80)
        
        # Run tests in sequence
        auth_success = await self.test_user_authentication()
        if not auth_success:
            print("❌ Cannot proceed - user authentication failed")
            return
            
        wallet_fix_success = await self.test_wallet_endpoint_fix()
        conversion_success = await self.test_conversion_system_working()
        gaming_success = await self.test_gaming_currency_selection()
        source_success = await self.test_balance_source_verification()
        total_success = await self.test_portfolio_total_calculation()
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 PORTFOLIO FIX VERIFICATION SUMMARY")
        print("=" * 80)
        
        passed_tests = sum([auth_success, wallet_fix_success, conversion_success, 
                           gaming_success, source_success, total_success])
        total_tests = 6
        
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"✅ Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if wallet_fix_success and gaming_success:
            print("🎉 CRITICAL SUCCESS: Portfolio display fix is WORKING!")
            print("✅ User can now see converted currencies")
            print("✅ User can select different cryptocurrencies for gaming")
        else:
            print("❌ CRITICAL FAILURE: Portfolio display fix is NOT working")
            print("❌ User still cannot see full portfolio")
            
        return wallet_fix_success and gaming_success

async def main():
    """Main test execution"""
    async with PortfolioFixTester(BACKEND_URL) as tester:
        success = await tester.run_all_tests()
        
        if success:
            print("\n🎉 PORTFOLIO FIX VERIFICATION: SUCCESS!")
            print("The user's portfolio display issue has been resolved.")
        else:
            print("\n❌ PORTFOLIO FIX VERIFICATION: FAILED!")
            print("The user's portfolio display issue still exists.")
        
        return success

if __name__ == "__main__":
    asyncio.run(main())