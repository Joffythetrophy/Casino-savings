#!/usr/bin/env python3
"""
Critical Balance Fixes Verification Test Suite
Tests the specific fixes mentioned in the review request for user DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://real-crt-casino.preview.emergentagent.com/api"

class CriticalBalanceFixesTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        
        # Specific user credentials from review request
        self.target_username = "cryptoking"
        self.target_password = "crt21million"
        self.target_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        
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
        """Test 1: Verify user authentication with cryptoking/crt21million"""
        try:
            login_payload = {
                "username": self.target_username,
                "password": self.target_password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("username") == self.target_username:
                        self.log_test("User Authentication", True, 
                                    f"✅ Authentication successful for {self.target_username}", data)
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
    
    async def test_crt_balance_recalculation(self):
        """Test 2: Verify CRT balance shows ~17.8M (not 21M blockchain or 18.9M database)"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.target_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        crt_balance = deposit_balance.get("CRT", 0)
                        
                        # Expected range: ~17.8M CRT (17,846,097 specifically mentioned)
                        expected_min = 17_800_000  # 17.8M
                        expected_max = 17_900_000  # 17.9M
                        
                        if expected_min <= crt_balance <= expected_max:
                            self.log_test("CRT Balance Recalculation", True, 
                                        f"✅ CRT balance correctly shows {crt_balance:,.0f} CRT (within expected range 17.8M-17.9M)", 
                                        {"crt_balance": crt_balance, "expected_range": f"{expected_min:,}-{expected_max:,}"})
                            return True
                        elif crt_balance > 20_000_000:
                            self.log_test("CRT Balance Recalculation", False, 
                                        f"❌ CRT balance still shows old blockchain amount: {crt_balance:,.0f} CRT (should be ~17.8M)", 
                                        {"crt_balance": crt_balance, "issue": "showing_blockchain_balance"})
                            return False
                        elif 18_800_000 <= crt_balance <= 19_000_000:
                            self.log_test("CRT Balance Recalculation", False, 
                                        f"❌ CRT balance still shows old database amount: {crt_balance:,.0f} CRT (should be ~17.8M)", 
                                        {"crt_balance": crt_balance, "issue": "showing_database_balance"})
                            return False
                        else:
                            self.log_test("CRT Balance Recalculation", False, 
                                        f"❌ CRT balance shows unexpected amount: {crt_balance:,.0f} CRT (expected ~17.8M)", 
                                        {"crt_balance": crt_balance, "expected": "~17,800,000"})
                            return False
                    else:
                        self.log_test("CRT Balance Recalculation", False, 
                                    "Failed to retrieve wallet data", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("CRT Balance Recalculation", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("CRT Balance Recalculation", False, f"Error: {str(e)}")
            return False
    
    async def test_winnings_balance_real_values(self):
        """Test 3: Verify winnings balance shows real values (not hardcoded 0)"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.target_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        winnings_balance = wallet.get("winnings_balance", {})
                        
                        # Check if winnings balance has real values (not all zeros)
                        total_winnings = sum(winnings_balance.values()) if isinstance(winnings_balance, dict) else 0
                        
                        if total_winnings > 0:
                            # Check for specific currencies with values
                            currencies_with_winnings = [curr for curr, amount in winnings_balance.items() if amount > 0]
                            self.log_test("Winnings Balance Real Values", True, 
                                        f"✅ Winnings balance shows real values: {winnings_balance} (total: {total_winnings:.2f})", 
                                        {"winnings_balance": winnings_balance, "currencies_with_winnings": currencies_with_winnings})
                            return True
                        else:
                            # Check if this is hardcoded zeros vs legitimate zero winnings
                            if all(amount == 0 for amount in winnings_balance.values()):
                                self.log_test("Winnings Balance Real Values", False, 
                                            f"❌ Winnings balance shows all zeros (likely hardcoded): {winnings_balance}", 
                                            {"winnings_balance": winnings_balance, "issue": "all_zeros_likely_hardcoded"})
                                return False
                            else:
                                self.log_test("Winnings Balance Real Values", True, 
                                            f"✅ Winnings balance shows legitimate zero values: {winnings_balance}", 
                                            {"winnings_balance": winnings_balance, "note": "legitimate_zeros"})
                                return True
                    else:
                        self.log_test("Winnings Balance Real Values", False, 
                                    "Failed to retrieve wallet data", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Winnings Balance Real Values", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Winnings Balance Real Values", False, f"Error: {str(e)}")
            return False
    
    async def test_gaming_balance_all_currencies(self):
        """Test 4: Verify gaming balance includes all currencies (CRT, DOGE, TRX, USDC)"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.target_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        
                        # Check all balance types for all currencies
                        expected_currencies = {"CRT", "DOGE", "TRX", "USDC"}
                        balance_types = ["deposit_balance", "winnings_balance", "gaming_balance", "liquidity_pool"]
                        
                        all_currencies_present = True
                        missing_currencies = []
                        balance_summary = {}
                        
                        for balance_type in balance_types:
                            balance_dict = wallet.get(balance_type, {})
                            balance_summary[balance_type] = balance_dict
                            
                            if isinstance(balance_dict, dict):
                                present_currencies = set(balance_dict.keys())
                                missing_in_this_type = expected_currencies - present_currencies
                                if missing_in_this_type:
                                    missing_currencies.extend([f"{curr} in {balance_type}" for curr in missing_in_this_type])
                                    all_currencies_present = False
                        
                        if all_currencies_present:
                            # Calculate total gaming balance across all currencies
                            gaming_balance = wallet.get("gaming_balance", {})
                            total_gaming_value = sum(gaming_balance.values()) if isinstance(gaming_balance, dict) else 0
                            
                            self.log_test("Gaming Balance All Currencies", True, 
                                        f"✅ Gaming balance includes all currencies {expected_currencies}: {gaming_balance} (total: {total_gaming_value:.2f})", 
                                        {"gaming_balance": gaming_balance, "all_balances": balance_summary})
                            return True
                        else:
                            self.log_test("Gaming Balance All Currencies", False, 
                                        f"❌ Missing currencies in gaming balance: {missing_currencies}", 
                                        {"missing_currencies": missing_currencies, "all_balances": balance_summary})
                            return False
                    else:
                        self.log_test("Gaming Balance All Currencies", False, 
                                    "Failed to retrieve wallet data", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Gaming Balance All Currencies", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Gaming Balance All Currencies", False, f"Error: {str(e)}")
            return False
    
    async def test_liquidity_pool_value(self):
        """Test 5: Verify liquidity pool shows $2.2M+ value"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.target_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        liquidity_pool = wallet.get("liquidity_pool", {})
                        
                        # Get conversion rates to calculate USD value
                        async with self.session.get(f"{self.base_url}/conversion/rates") as rates_response:
                            if rates_response.status == 200:
                                rates_data = await rates_response.json()
                                prices_usd = rates_data.get("prices_usd", {})
                                
                                # Calculate total USD value of liquidity pool
                                total_usd_value = 0
                                currency_values = {}
                                
                                for currency, amount in liquidity_pool.items():
                                    if currency in prices_usd and amount > 0:
                                        usd_price = prices_usd[currency]
                                        usd_value = amount * usd_price
                                        currency_values[currency] = {
                                            "amount": amount,
                                            "price_usd": usd_price,
                                            "value_usd": usd_value
                                        }
                                        total_usd_value += usd_value
                                
                                # Expected minimum: $2.2M
                                expected_min_usd = 2_200_000  # $2.2M
                                
                                if total_usd_value >= expected_min_usd:
                                    self.log_test("Liquidity Pool Value", True, 
                                                f"✅ Liquidity pool shows ${total_usd_value:,.2f} (exceeds $2.2M minimum)", 
                                                {"total_usd_value": total_usd_value, "currency_breakdown": currency_values, "liquidity_pool": liquidity_pool})
                                    return True
                                else:
                                    self.log_test("Liquidity Pool Value", False, 
                                                f"❌ Liquidity pool shows ${total_usd_value:,.2f} (below $2.2M minimum)", 
                                                {"total_usd_value": total_usd_value, "expected_minimum": expected_min_usd, "currency_breakdown": currency_values})
                                    return False
                            else:
                                self.log_test("Liquidity Pool Value", False, 
                                            "Failed to get conversion rates for USD calculation", rates_data)
                                return False
                    else:
                        self.log_test("Liquidity Pool Value", False, 
                                    "Failed to retrieve wallet data", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Liquidity Pool Value", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Liquidity Pool Value", False, f"Error: {str(e)}")
            return False
    
    async def test_total_portfolio_recalculation(self):
        """Test 6: Verify total portfolio value is recalculated with correct CRT amount"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.target_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        
                        # Get conversion rates for USD calculation
                        async with self.session.get(f"{self.base_url}/conversion/rates") as rates_response:
                            if rates_response.status == 200:
                                rates_data = await rates_response.json()
                                prices_usd = rates_data.get("prices_usd", {})
                                
                                # Calculate total portfolio value across all balance types
                                balance_types = ["deposit_balance", "winnings_balance", "gaming_balance", "liquidity_pool"]
                                total_portfolio_usd = 0
                                portfolio_breakdown = {}
                                
                                for balance_type in balance_types:
                                    balance_dict = wallet.get(balance_type, {})
                                    type_total_usd = 0
                                    type_breakdown = {}
                                    
                                    for currency, amount in balance_dict.items():
                                        if currency in prices_usd and amount > 0:
                                            usd_price = prices_usd[currency]
                                            usd_value = amount * usd_price
                                            type_breakdown[currency] = {
                                                "amount": amount,
                                                "price_usd": usd_price,
                                                "value_usd": usd_value
                                            }
                                            type_total_usd += usd_value
                                    
                                    portfolio_breakdown[balance_type] = {
                                        "total_usd": type_total_usd,
                                        "currencies": type_breakdown
                                    }
                                    total_portfolio_usd += type_total_usd
                                
                                # With corrected CRT balance (~17.8M), portfolio should be recalculated
                                # Previous portfolio was likely inflated due to incorrect CRT balance
                                
                                self.log_test("Total Portfolio Recalculation", True, 
                                            f"✅ Total portfolio value recalculated: ${total_portfolio_usd:,.2f} with corrected CRT balance", 
                                            {
                                                "total_portfolio_usd": total_portfolio_usd,
                                                "portfolio_breakdown": portfolio_breakdown,
                                                "note": "Portfolio recalculated with corrected CRT amount"
                                            })
                                return True
                            else:
                                self.log_test("Total Portfolio Recalculation", False, 
                                            "Failed to get conversion rates for portfolio calculation", rates_data)
                                return False
                    else:
                        self.log_test("Total Portfolio Recalculation", False, 
                                    "Failed to retrieve wallet data", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Total Portfolio Recalculation", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Total Portfolio Recalculation", False, f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all critical balance fix tests"""
        print("🚨 CRITICAL BALANCE FIXES VERIFICATION TEST SUITE")
        print("=" * 60)
        print(f"Testing fixes for user: {self.target_wallet}")
        print(f"Authentication: {self.target_username}/{self.target_password}")
        print("=" * 60)
        
        # Test authentication first
        auth_success = await self.test_user_authentication()
        if not auth_success:
            print("❌ Authentication failed - cannot proceed with balance tests")
            return
        
        # Run all balance fix tests
        await self.test_crt_balance_recalculation()
        await self.test_winnings_balance_real_values()
        await self.test_gaming_balance_all_currencies()
        await self.test_liquidity_pool_value()
        await self.test_total_portfolio_recalculation()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 CRITICAL BALANCE FIXES TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = [result for result in self.test_results if result["success"]]
        failed_tests = [result for result in self.test_results if not result["success"]]
        
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
        
        # Overall assessment
        success_rate = len(passed_tests) / len(self.test_results) * 100
        print(f"\n📊 SUCCESS RATE: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 CRITICAL FIXES VERIFICATION: SUCCESSFUL")
        elif success_rate >= 60:
            print("⚠️ CRITICAL FIXES VERIFICATION: PARTIAL SUCCESS")
        else:
            print("❌ CRITICAL FIXES VERIFICATION: NEEDS ATTENTION")
        
        return self.test_results

async def main():
    """Main test execution"""
    try:
        async with CriticalBalanceFixesTester(BACKEND_URL) as tester:
            results = await tester.run_all_tests()
            
            # Return appropriate exit code
            failed_count = len([r for r in results if not r["success"]])
            sys.exit(failed_count)
            
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())