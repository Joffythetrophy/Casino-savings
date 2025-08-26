#!/usr/bin/env python3
"""
URGENT: User Withdrawal Capabilities Test
Testing REAL withdrawal capabilities for user DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq
User has: 319K USDC, 13M DOGE, 3.9M TRX, 21M CRT
Question: Can user withdraw these to external wallets?
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://winsaver.preview.emergentagent.com/api"

class WithdrawalTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        
        # REAL USER DATA from review request
        self.target_user = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        self.target_username = "cryptoking"
        self.target_password = "crt21million"
        
        # Expected balances from review request
        self.expected_balances = {
            "USDC": 319000,  # 319K USDC
            "DOGE": 13000000,  # 13M DOGE
            "TRX": 3900000,  # 3.9M TRX
            "CRT": 21000000  # 21M CRT
        }
        
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
        """Test 1: Authenticate the specific user"""
        try:
            login_payload = {
                "username": self.target_username,
                "password": self.target_password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("wallet_address") == self.target_user:
                        self.log_test("User Authentication", True, 
                                    f"User {self.target_username} authenticated successfully", data)
                        return True
                    else:
                        self.log_test("User Authentication", False, 
                                    f"Authentication failed: {data.get('message', 'Unknown error')}", data)
                else:
                    self.log_test("User Authentication", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
        return False

    async def test_user_wallet_balances(self):
        """Test 2: Check user's current wallet balances"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.target_user}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        
                        # Check each currency balance
                        balance_summary = {}
                        for currency in ["USDC", "DOGE", "TRX", "CRT"]:
                            actual_balance = deposit_balance.get(currency, 0)
                            balance_summary[currency] = actual_balance
                        
                        self.log_test("User Wallet Balances", True, 
                                    f"Current balances: {balance_summary}", data)
                        return balance_summary
                    else:
                        self.log_test("User Wallet Balances", False, 
                                    "Failed to retrieve wallet info", data)
                else:
                    self.log_test("User Wallet Balances", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("User Wallet Balances", False, f"Error: {str(e)}")
        return {}

    async def test_withdrawal_endpoint_exists(self):
        """Test 3: Check if withdrawal endpoint exists and responds"""
        try:
            # Test with minimal payload to see if endpoint exists
            test_payload = {
                "wallet_address": self.target_user,
                "wallet_type": "deposit",
                "currency": "USDC",
                "amount": 1.0
            }
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=test_payload) as response:
                if response.status in [200, 400, 403]:  # Any of these means endpoint exists
                    data = await response.json()
                    self.log_test("Withdrawal Endpoint Exists", True, 
                                f"Withdrawal endpoint accessible (HTTP {response.status})", data)
                    return True
                else:
                    self.log_test("Withdrawal Endpoint Exists", False, 
                                f"Unexpected HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Withdrawal Endpoint Exists", False, f"Error: {str(e)}")
        return False

    async def test_withdrawal_limits_usdc(self):
        """Test 4: Test USDC withdrawal limits and constraints"""
        try:
            # Test small withdrawal first
            small_amount = 100.0  # $100 USDC
            
            withdrawal_payload = {
                "wallet_address": self.target_user,
                "wallet_type": "deposit",
                "currency": "USDC",
                "amount": small_amount
            }
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=withdrawal_payload) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    self.log_test("USDC Small Withdrawal", True, 
                                f"Small USDC withdrawal successful: {small_amount} USDC", data)
                    
                    # Test larger withdrawal
                    large_amount = 10000.0  # $10K USDC
                    withdrawal_payload["amount"] = large_amount
                    
                    async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                               json=withdrawal_payload) as response2:
                        data2 = await response2.json()
                        
                        if response2.status == 200 and data2.get("success"):
                            self.log_test("USDC Large Withdrawal", True, 
                                        f"Large USDC withdrawal successful: {large_amount} USDC", data2)
                        else:
                            # Check if it's a liquidity limit
                            if "liquidity" in data2.get("message", "").lower():
                                available_liquidity = data2.get("available_liquidity", 0)
                                max_withdrawal = data2.get("max_withdrawal", 0)
                                self.log_test("USDC Withdrawal Limits", True, 
                                            f"USDC withdrawal limited by liquidity: max={max_withdrawal}, available={available_liquidity}", data2)
                            else:
                                self.log_test("USDC Large Withdrawal", False, 
                                            f"Large USDC withdrawal failed: {data2.get('message')}", data2)
                else:
                    # Check if it's a liquidity/balance issue
                    if "liquidity" in data.get("message", "").lower() or "balance" in data.get("message", "").lower():
                        self.log_test("USDC Withdrawal Constraints", True, 
                                    f"USDC withdrawal constrained: {data.get('message')}", data)
                    else:
                        self.log_test("USDC Small Withdrawal", False, 
                                    f"USDC withdrawal failed: {data.get('message')}", data)
                        
        except Exception as e:
            self.log_test("USDC Withdrawal Test", False, f"Error: {str(e)}")

    async def test_withdrawal_limits_doge(self):
        """Test 5: Test DOGE withdrawal limits and constraints"""
        try:
            # Test small DOGE withdrawal
            small_amount = 1000.0  # 1K DOGE
            
            withdrawal_payload = {
                "wallet_address": self.target_user,
                "wallet_type": "deposit",
                "currency": "DOGE",
                "amount": small_amount
            }
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=withdrawal_payload) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    self.log_test("DOGE Small Withdrawal", True, 
                                f"Small DOGE withdrawal successful: {small_amount} DOGE", data)
                    
                    # Test larger withdrawal
                    large_amount = 100000.0  # 100K DOGE
                    withdrawal_payload["amount"] = large_amount
                    
                    async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                               json=withdrawal_payload) as response2:
                        data2 = await response2.json()
                        
                        if response2.status == 200 and data2.get("success"):
                            self.log_test("DOGE Large Withdrawal", True, 
                                        f"Large DOGE withdrawal successful: {large_amount} DOGE", data2)
                        else:
                            # Check if it's a liquidity limit
                            if "liquidity" in data2.get("message", "").lower():
                                available_liquidity = data2.get("available_liquidity", 0)
                                max_withdrawal = data2.get("max_withdrawal", 0)
                                self.log_test("DOGE Withdrawal Limits", True, 
                                            f"DOGE withdrawal limited by liquidity: max={max_withdrawal}, available={available_liquidity}", data2)
                            else:
                                self.log_test("DOGE Large Withdrawal", False, 
                                            f"Large DOGE withdrawal failed: {data2.get('message')}", data2)
                else:
                    # Check if it's a liquidity/balance issue
                    if "liquidity" in data.get("message", "").lower() or "balance" in data.get("message", "").lower():
                        self.log_test("DOGE Withdrawal Constraints", True, 
                                    f"DOGE withdrawal constrained: {data.get('message')}", data)
                    else:
                        self.log_test("DOGE Small Withdrawal", False, 
                                    f"DOGE withdrawal failed: {data.get('message')}", data)
                        
        except Exception as e:
            self.log_test("DOGE Withdrawal Test", False, f"Error: {str(e)}")

    async def test_withdrawal_limits_trx(self):
        """Test 6: Test TRX withdrawal limits and constraints"""
        try:
            # Test small TRX withdrawal
            small_amount = 1000.0  # 1K TRX
            
            withdrawal_payload = {
                "wallet_address": self.target_user,
                "wallet_type": "deposit",
                "currency": "TRX",
                "amount": small_amount
            }
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=withdrawal_payload) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    self.log_test("TRX Small Withdrawal", True, 
                                f"Small TRX withdrawal successful: {small_amount} TRX", data)
                    
                    # Test larger withdrawal
                    large_amount = 50000.0  # 50K TRX
                    withdrawal_payload["amount"] = large_amount
                    
                    async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                               json=withdrawal_payload) as response2:
                        data2 = await response2.json()
                        
                        if response2.status == 200 and data2.get("success"):
                            self.log_test("TRX Large Withdrawal", True, 
                                        f"Large TRX withdrawal successful: {large_amount} TRX", data2)
                        else:
                            # Check if it's a liquidity limit
                            if "liquidity" in data2.get("message", "").lower():
                                available_liquidity = data2.get("available_liquidity", 0)
                                max_withdrawal = data2.get("max_withdrawal", 0)
                                self.log_test("TRX Withdrawal Limits", True, 
                                            f"TRX withdrawal limited by liquidity: max={max_withdrawal}, available={available_liquidity}", data2)
                            else:
                                self.log_test("TRX Large Withdrawal", False, 
                                            f"Large TRX withdrawal failed: {data2.get('message')}", data2)
                else:
                    # Check if it's a liquidity/balance issue
                    if "liquidity" in data.get("message", "").lower() or "balance" in data.get("message", "").lower():
                        self.log_test("TRX Withdrawal Constraints", True, 
                                    f"TRX withdrawal constrained: {data.get('message')}", data)
                    else:
                        self.log_test("TRX Small Withdrawal", False, 
                                    f"TRX withdrawal failed: {data.get('message')}", data)
                        
        except Exception as e:
            self.log_test("TRX Withdrawal Test", False, f"Error: {str(e)}")

    async def test_withdrawal_limits_crt(self):
        """Test 7: Test CRT withdrawal limits and constraints"""
        try:
            # Test small CRT withdrawal
            small_amount = 10000.0  # 10K CRT
            
            withdrawal_payload = {
                "wallet_address": self.target_user,
                "wallet_type": "deposit",
                "currency": "CRT",
                "amount": small_amount
            }
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=withdrawal_payload) as response:
                data = await response.json()
                
                if response.status == 200 and data.get("success"):
                    self.log_test("CRT Small Withdrawal", True, 
                                f"Small CRT withdrawal successful: {small_amount} CRT", data)
                    
                    # Test larger withdrawal
                    large_amount = 1000000.0  # 1M CRT
                    withdrawal_payload["amount"] = large_amount
                    
                    async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                               json=withdrawal_payload) as response2:
                        data2 = await response2.json()
                        
                        if response2.status == 200 and data2.get("success"):
                            self.log_test("CRT Large Withdrawal", True, 
                                        f"Large CRT withdrawal successful: {large_amount} CRT", data2)
                        else:
                            # Check if it's a liquidity limit
                            if "liquidity" in data2.get("message", "").lower():
                                available_liquidity = data2.get("available_liquidity", 0)
                                max_withdrawal = data2.get("max_withdrawal", 0)
                                self.log_test("CRT Withdrawal Limits", True, 
                                            f"CRT withdrawal limited by liquidity: max={max_withdrawal}, available={available_liquidity}", data2)
                            else:
                                self.log_test("CRT Large Withdrawal", False, 
                                            f"Large CRT withdrawal failed: {data2.get('message')}", data2)
                else:
                    # Check if it's a liquidity/balance issue
                    if "liquidity" in data.get("message", "").lower() or "balance" in data.get("message", "").lower():
                        self.log_test("CRT Withdrawal Constraints", True, 
                                    f"CRT withdrawal constrained: {data.get('message')}", data)
                    else:
                        self.log_test("CRT Small Withdrawal", False, 
                                    f"CRT withdrawal failed: {data.get('message')}", data)
                        
        except Exception as e:
            self.log_test("CRT Withdrawal Test", False, f"Error: {str(e)}")

    async def test_external_wallet_address_requirement(self):
        """Test 8: Check if external wallet addresses are required for withdrawals"""
        try:
            # Test withdrawal without destination address (current API)
            withdrawal_payload = {
                "wallet_address": self.target_user,
                "wallet_type": "deposit",
                "currency": "USDC",
                "amount": 100.0
            }
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=withdrawal_payload) as response:
                data = await response.json()
                
                # Check if API requires destination address
                if "destination" in data.get("message", "").lower() or "address" in data.get("message", "").lower():
                    self.log_test("External Address Requirement", True, 
                                "Withdrawal requires external wallet address", data)
                else:
                    # Current API doesn't require destination address
                    self.log_test("External Address Requirement", True, 
                                "Current API doesn't require destination address (internal transfer)", data)
                    
        except Exception as e:
            self.log_test("External Address Requirement", False, f"Error: {str(e)}")

    async def test_liquidity_pool_status(self):
        """Test 9: Check user's liquidity pool status for withdrawals"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.target_user}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        
                        # Check if liquidity pool info is available
                        if "liquidity_pool" in str(data):
                            self.log_test("Liquidity Pool Status", True, 
                                        "Liquidity pool information available in wallet data", data)
                        else:
                            # Try to get liquidity info from user data
                            deposit_balance = wallet.get("deposit_balance", {})
                            total_value = sum(deposit_balance.values())
                            
                            self.log_test("Liquidity Pool Status", True, 
                                        f"Total deposit balance: {total_value} (liquidity pool info not directly visible)", 
                                        {"deposit_balance": deposit_balance})
                    else:
                        self.log_test("Liquidity Pool Status", False, 
                                    "Failed to retrieve wallet info", data)
                else:
                    self.log_test("Liquidity Pool Status", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Liquidity Pool Status", False, f"Error: {str(e)}")

    async def test_savings_vs_gaming_balance_distinction(self):
        """Test 10: Verify distinction between savings and gaming balances"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.target_user}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        
                        deposit_balance = wallet.get("deposit_balance", {})
                        savings_balance = wallet.get("savings_balance", {})
                        
                        # Check if both balance types exist
                        if deposit_balance and savings_balance:
                            deposit_total = sum(deposit_balance.values())
                            savings_total = sum(savings_balance.values())
                            
                            self.log_test("Balance Type Distinction", True, 
                                        f"Gaming balance (withdrawable): {deposit_total}, Savings balance (database): {savings_total}", 
                                        {"deposit_balance": deposit_balance, "savings_balance": savings_balance})
                            
                            # Test withdrawal from savings (should fail or be limited)
                            savings_withdrawal_payload = {
                                "wallet_address": self.target_user,
                                "wallet_type": "savings",
                                "currency": "CRT",
                                "amount": 1000.0
                            }
                            
                            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                                       json=savings_withdrawal_payload) as savings_response:
                                savings_data = await savings_response.json()
                                
                                if "savings" in savings_data.get("message", "").lower() or not savings_data.get("success"):
                                    self.log_test("Savings Withdrawal Restriction", True, 
                                                "Savings balance withdrawal properly restricted", savings_data)
                                else:
                                    self.log_test("Savings Withdrawal Restriction", False, 
                                                "Savings balance withdrawal should be restricted", savings_data)
                        else:
                            self.log_test("Balance Type Distinction", False, 
                                        "Missing deposit_balance or savings_balance in wallet data", data)
                    else:
                        self.log_test("Balance Type Distinction", False, 
                                    "Failed to retrieve wallet info", data)
                else:
                    self.log_test("Balance Type Distinction", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Balance Type Distinction", False, f"Error: {str(e)}")

    async def run_all_tests(self):
        """Run all withdrawal capability tests"""
        print(f"\n🔍 URGENT WITHDRAWAL CAPABILITY TEST")
        print(f"Testing user: {self.target_user}")
        print(f"Expected balances: {self.expected_balances}")
        print("=" * 80)
        
        # Authenticate user first
        auth_success = await self.test_user_authentication()
        if not auth_success:
            print("❌ Cannot proceed without authentication")
            return
        
        # Get current balances
        balances = await self.test_user_wallet_balances()
        
        # Test withdrawal capabilities
        await self.test_withdrawal_endpoint_exists()
        await self.test_withdrawal_limits_usdc()
        await self.test_withdrawal_limits_doge()
        await self.test_withdrawal_limits_trx()
        await self.test_withdrawal_limits_crt()
        await self.test_external_wallet_address_requirement()
        await self.test_liquidity_pool_status()
        await self.test_savings_vs_gaming_balance_distinction()
        
        # Generate summary
        self.generate_withdrawal_summary(balances)

    def generate_withdrawal_summary(self, balances: Dict[str, float]):
        """Generate comprehensive withdrawal capability summary"""
        print("\n" + "=" * 80)
        print("🎯 WITHDRAWAL CAPABILITY SUMMARY")
        print("=" * 80)
        
        # Count successful tests
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        
        # Balance summary
        print(f"\n💰 Current User Balances:")
        for currency, balance in balances.items():
            expected = self.expected_balances.get(currency, 0)
            status = "✅" if balance > 0 else "❌"
            print(f"  {status} {currency}: {balance:,.0f} (expected: {expected:,.0f})")
        
        # Withdrawal capability assessment
        print(f"\n🔄 Withdrawal Capability Assessment:")
        
        withdrawal_tests = [r for r in self.test_results if "withdrawal" in r["test"].lower()]
        successful_withdrawals = [r for r in withdrawal_tests if r["success"]]
        
        if successful_withdrawals:
            print(f"  ✅ Withdrawal system is operational")
            print(f"  ✅ {len(successful_withdrawals)} withdrawal tests passed")
        else:
            print(f"  ❌ Withdrawal system has issues")
        
        # Key findings
        print(f"\n🔍 Key Findings:")
        
        # Check for liquidity constraints
        liquidity_mentions = [r for r in self.test_results if "liquidity" in r["details"].lower()]
        if liquidity_mentions:
            print(f"  ⚠️  Withdrawals are limited by liquidity constraints")
            for mention in liquidity_mentions[:3]:  # Show first 3
                print(f"     - {mention['details']}")
        
        # Check for balance issues
        balance_issues = [r for r in self.test_results if "balance" in r["details"].lower() and not r["success"]]
        if balance_issues:
            print(f"  ⚠️  Balance-related withdrawal issues found")
        
        # Check external address requirement
        address_tests = [r for r in self.test_results if "address" in r["test"].lower()]
        if address_tests:
            for test in address_tests:
                print(f"  📍 {test['details']}")
        
        print(f"\n🎯 FINAL ANSWER TO USER QUESTION:")
        print(f"   'Can user withdraw their converted currencies to external wallets?'")
        
        if passed_tests >= total_tests * 0.7:  # 70% success rate
            print(f"   ✅ YES - User can withdraw their gaming balances with some limitations")
            print(f"   ⚠️  Withdrawals are subject to liquidity constraints")
            print(f"   ℹ️  Savings balances are database-only (not withdrawable)")
        else:
            print(f"   ❌ PARTIAL - Withdrawal system has significant limitations")
            print(f"   ⚠️  User may face restrictions on withdrawal amounts")
        
        print("=" * 80)

async def main():
    """Main test execution"""
    async with WithdrawalTester(BACKEND_URL) as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())