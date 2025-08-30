#!/usr/bin/env python3
"""
Gaming Balance Menu Testing - Fix Balance Display Confusion
Tests the specific issues reported by user about gaming balance menu being "not right, not working, more confusion"

Focus Areas:
1. Balance Not Displaying Correctly - Test /api/wallet/{wallet_address} 
2. Menu Not Working - Verify balance fetching from backend
3. Too Much Confusion - Check DOGE balance clarity (should show 10,465,543.58 DOGE)
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Backend URL from frontend env
BACKEND_URL = "https://crypto-treasury-app.preview.emergentagent.com/api"

# User context from review request
USER_CONTEXT = {
    "username": "cryptoking",
    "password": "crt21million",
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
    "expected_doge": 10465543.58,  # Expected DOGE balance
    "expected_usd": 2312885  # Expected USD value (~$2.3M)
}

class GamingBalanceTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
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

    async def test_user_authentication(self):
        """Test 1: Authenticate user cryptoking"""
        try:
            login_payload = {
                "username": USER_CONTEXT["username"],
                "password": USER_CONTEXT["password"]
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if (data.get("success") and 
                        data.get("username") == USER_CONTEXT["username"] and
                        data.get("wallet_address") == USER_CONTEXT["wallet_address"]):
                        self.log_test("User Authentication", True, 
                                    f"User {USER_CONTEXT['username']} authenticated successfully", data)
                        return True
                    else:
                        self.log_test("User Authentication", False, 
                                    f"Authentication failed: {data.get('message', 'Unknown error')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
        return False

    async def test_balance_endpoint_structure(self):
        """Test 2: Balance Endpoint Structure - Check /api/wallet/{wallet_address}"""
        try:
            wallet_address = USER_CONTEXT["wallet_address"]
            
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        
                        # Check required balance structure
                        required_fields = ["deposit_balance", "winnings_balance", "savings_balance"]
                        missing_fields = [field for field in required_fields if field not in wallet]
                        
                        if not missing_fields:
                            # Check DOGE balance specifically
                            deposit_balance = wallet.get("deposit_balance", {})
                            doge_balance = deposit_balance.get("DOGE", 0)
                            
                            self.log_test("Balance Endpoint Structure", True, 
                                        f"Balance structure correct. DOGE balance: {doge_balance:,.2f} DOGE", 
                                        {
                                            "doge_balance": doge_balance,
                                            "deposit_balance": deposit_balance,
                                            "structure_valid": True
                                        })
                            return wallet
                        else:
                            self.log_test("Balance Endpoint Structure", False, 
                                        f"Missing required fields: {missing_fields}", data)
                    else:
                        self.log_test("Balance Endpoint Structure", False, 
                                    "Invalid wallet response format", data)
                else:
                    error_text = await response.text()
                    self.log_test("Balance Endpoint Structure", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Balance Endpoint Structure", False, f"Error: {str(e)}")
        return None

    async def test_doge_balance_accuracy(self, wallet_data: Dict):
        """Test 3: DOGE Balance Accuracy - Check if balance matches expected"""
        try:
            if not wallet_data:
                self.log_test("DOGE Balance Accuracy", False, "No wallet data available")
                return
            
            deposit_balance = wallet_data.get("deposit_balance", {})
            winnings_balance = wallet_data.get("winnings_balance", {})
            savings_balance = wallet_data.get("savings_balance", {})
            
            # Calculate total DOGE across all balance types
            total_doge = (
                deposit_balance.get("DOGE", 0) +
                winnings_balance.get("DOGE", 0) +
                savings_balance.get("DOGE", 0)
            )
            
            expected_doge = USER_CONTEXT["expected_doge"]
            
            # Check if balance is close to expected (within 1% tolerance)
            tolerance = expected_doge * 0.01  # 1% tolerance
            balance_diff = abs(total_doge - expected_doge)
            
            if balance_diff <= tolerance:
                self.log_test("DOGE Balance Accuracy", True, 
                            f"DOGE balance accurate: {total_doge:,.2f} DOGE (expected: {expected_doge:,.2f})", 
                            {
                                "total_doge": total_doge,
                                "expected_doge": expected_doge,
                                "difference": balance_diff,
                                "breakdown": {
                                    "deposit": deposit_balance.get("DOGE", 0),
                                    "winnings": winnings_balance.get("DOGE", 0),
                                    "savings": savings_balance.get("DOGE", 0)
                                }
                            })
            else:
                self.log_test("DOGE Balance Accuracy", False, 
                            f"DOGE balance mismatch: {total_doge:,.2f} DOGE (expected: {expected_doge:,.2f}, diff: {balance_diff:,.2f})", 
                            {
                                "total_doge": total_doge,
                                "expected_doge": expected_doge,
                                "difference": balance_diff,
                                "breakdown": {
                                    "deposit": deposit_balance.get("DOGE", 0),
                                    "winnings": winnings_balance.get("DOGE", 0),
                                    "savings": savings_balance.get("DOGE", 0)
                                }
                            })
                            
        except Exception as e:
            self.log_test("DOGE Balance Accuracy", False, f"Error: {str(e)}")

    async def test_balance_display_simplicity(self, wallet_data: Dict):
        """Test 4: Balance Display Simplicity - Check for confusion factors"""
        try:
            if not wallet_data:
                self.log_test("Balance Display Simplicity", False, "No wallet data available")
                return
            
            # Check for potential confusion factors
            confusion_factors = []
            
            # 1. Multiple currency types (should focus on DOGE)
            deposit_balance = wallet_data.get("deposit_balance", {})
            currencies = [curr for curr, balance in deposit_balance.items() if balance > 0]
            
            if len(currencies) > 3:
                confusion_factors.append(f"Too many currencies displayed: {currencies}")
            
            # 2. Complex balance structure (multiple wallet types)
            balance_types = ["deposit_balance", "winnings_balance", "savings_balance"]
            active_balance_types = []
            
            for balance_type in balance_types:
                balance_dict = wallet_data.get(balance_type, {})
                if any(balance > 0 for balance in balance_dict.values()):
                    active_balance_types.append(balance_type)
            
            if len(active_balance_types) > 2:
                confusion_factors.append(f"Too many balance types: {active_balance_types}")
            
            # 3. Check if DOGE is prominently displayed
            doge_balance = deposit_balance.get("DOGE", 0)
            if doge_balance == 0:
                confusion_factors.append("DOGE balance is 0 or not displayed")
            
            # 4. Check for unnecessary complexity in response
            if "balance_source" in wallet_data and wallet_data["balance_source"] == "hybrid_blockchain_database":
                confusion_factors.append("Complex balance source indication may confuse users")
            
            if not confusion_factors:
                self.log_test("Balance Display Simplicity", True, 
                            f"Balance display is simple: {len(currencies)} currencies, {len(active_balance_types)} balance types", 
                            {
                                "currencies": currencies,
                                "balance_types": active_balance_types,
                                "doge_balance": doge_balance
                            })
            else:
                self.log_test("Balance Display Simplicity", False, 
                            f"Balance display has confusion factors: {'; '.join(confusion_factors)}", 
                            {
                                "confusion_factors": confusion_factors,
                                "currencies": currencies,
                                "balance_types": active_balance_types
                            })
                            
        except Exception as e:
            self.log_test("Balance Display Simplicity", False, f"Error: {str(e)}")

    async def test_real_time_balance_updates(self):
        """Test 5: Real-time Balance Updates - Test if balance updates work"""
        try:
            wallet_address = USER_CONTEXT["wallet_address"]
            
            # Get initial balance
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status != 200:
                    self.log_test("Real-time Balance Updates", False, "Failed to get initial balance")
                    return
                
                initial_data = await response.json()
                if not initial_data.get("success"):
                    self.log_test("Real-time Balance Updates", False, "Initial balance request failed")
                    return
                
                initial_wallet = initial_data["wallet"]
                initial_doge = initial_wallet.get("deposit_balance", {}).get("DOGE", 0)
            
            # Wait a moment and get balance again
            await asyncio.sleep(1)
            
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    updated_data = await response.json()
                    if updated_data.get("success"):
                        updated_wallet = updated_data["wallet"]
                        updated_doge = updated_wallet.get("deposit_balance", {}).get("DOGE", 0)
                        
                        # Check if balance is consistent (real-time updates working)
                        if initial_doge == updated_doge:
                            self.log_test("Real-time Balance Updates", True, 
                                        f"Balance consistency maintained: {updated_doge:,.2f} DOGE", 
                                        {
                                            "initial_doge": initial_doge,
                                            "updated_doge": updated_doge,
                                            "consistent": True
                                        })
                        else:
                            # Balance changed - could be real-time update or error
                            change = updated_doge - initial_doge
                            self.log_test("Real-time Balance Updates", True, 
                                        f"Balance changed: {change:+,.2f} DOGE (from {initial_doge:,.2f} to {updated_doge:,.2f})", 
                                        {
                                            "initial_doge": initial_doge,
                                            "updated_doge": updated_doge,
                                            "change": change
                                        })
                    else:
                        self.log_test("Real-time Balance Updates", False, 
                                    "Updated balance request failed", updated_data)
                else:
                    self.log_test("Real-time Balance Updates", False, 
                                f"HTTP {response.status} on balance update check")
                                
        except Exception as e:
            self.log_test("Real-time Balance Updates", False, f"Error: {str(e)}")

    async def test_usd_value_calculation(self, wallet_data: Dict):
        """Test 6: USD Value Calculation - Check if USD values are accurate"""
        try:
            if not wallet_data:
                self.log_test("USD Value Calculation", False, "No wallet data available")
                return
            
            # Get current DOGE price
            async with self.session.get(f"{self.base_url}/crypto/price/DOGE") as response:
                if response.status == 200:
                    price_data = await response.json()
                    if price_data.get("success") and "data" in price_data:
                        doge_price = price_data["data"].get("price_usd", 0)
                        
                        # Calculate expected USD value
                        deposit_balance = wallet_data.get("deposit_balance", {})
                        doge_balance = deposit_balance.get("DOGE", 0)
                        calculated_usd = doge_balance * doge_price
                        
                        expected_usd = USER_CONTEXT["expected_usd"]
                        
                        # Check if USD calculation is reasonable
                        if doge_price > 0 and calculated_usd > 0:
                            self.log_test("USD Value Calculation", True, 
                                        f"USD calculation working: {doge_balance:,.2f} DOGE × ${doge_price:.3f} = ${calculated_usd:,.2f}", 
                                        {
                                            "doge_balance": doge_balance,
                                            "doge_price": doge_price,
                                            "calculated_usd": calculated_usd,
                                            "expected_usd": expected_usd
                                        })
                        else:
                            self.log_test("USD Value Calculation", False, 
                                        f"USD calculation failed: DOGE price: ${doge_price}, balance: {doge_balance}", 
                                        {
                                            "doge_balance": doge_balance,
                                            "doge_price": doge_price
                                        })
                    else:
                        self.log_test("USD Value Calculation", False, 
                                    "Failed to get DOGE price", price_data)
                else:
                    self.log_test("USD Value Calculation", False, 
                                f"Price endpoint failed: HTTP {response.status}")
                                
        except Exception as e:
            self.log_test("USD Value Calculation", False, f"Error: {str(e)}")

    async def test_balance_menu_responsiveness(self):
        """Test 7: Balance Menu Responsiveness - Test multiple rapid requests"""
        try:
            wallet_address = USER_CONTEXT["wallet_address"]
            
            # Make multiple rapid requests to test responsiveness
            start_time = datetime.utcnow()
            successful_requests = 0
            total_requests = 5
            
            for i in range(total_requests):
                try:
                    async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("success"):
                                successful_requests += 1
                except Exception:
                    pass  # Count as failed request
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            avg_response_time = duration / total_requests
            
            success_rate = (successful_requests / total_requests) * 100
            
            if success_rate >= 80 and avg_response_time < 2.0:
                self.log_test("Balance Menu Responsiveness", True, 
                            f"Menu responsive: {success_rate:.1f}% success rate, {avg_response_time:.3f}s avg response", 
                            {
                                "successful_requests": successful_requests,
                                "total_requests": total_requests,
                                "success_rate": success_rate,
                                "avg_response_time": avg_response_time
                            })
            else:
                self.log_test("Balance Menu Responsiveness", False, 
                            f"Menu not responsive enough: {success_rate:.1f}% success rate, {avg_response_time:.3f}s avg response", 
                            {
                                "successful_requests": successful_requests,
                                "total_requests": total_requests,
                                "success_rate": success_rate,
                                "avg_response_time": avg_response_time
                            })
                            
        except Exception as e:
            self.log_test("Balance Menu Responsiveness", False, f"Error: {str(e)}")

    async def test_gaming_balance_integration(self):
        """Test 8: Gaming Balance Integration - Test if balance works with gaming"""
        try:
            wallet_address = USER_CONTEXT["wallet_address"]
            
            # Test a small bet to see if gaming integration works
            bet_payload = {
                "wallet_address": wallet_address,
                "game_type": "Slot Machine",
                "bet_amount": 1.0,  # Small bet
                "currency": "DOGE",
                "network": "dogecoin"
            }
            
            async with self.session.post(f"{self.base_url}/games/bet", json=bet_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        # Check if bet was processed and balance updated
                        game_id = data.get("game_id")
                        result = data.get("result")
                        payout = data.get("payout", 0)
                        
                        self.log_test("Gaming Balance Integration", True, 
                                    f"Gaming integration working: Game {game_id}, result: {result}, payout: {payout}", 
                                    {
                                        "game_id": game_id,
                                        "result": result,
                                        "payout": payout,
                                        "bet_amount": bet_payload["bet_amount"]
                                    })
                    else:
                        self.log_test("Gaming Balance Integration", False, 
                                    f"Bet failed: {data.get('message', 'Unknown error')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("Gaming Balance Integration", False, 
                                f"Bet endpoint failed: HTTP {response.status}: {error_text}")
                                
        except Exception as e:
            self.log_test("Gaming Balance Integration", False, f"Error: {str(e)}")

    async def run_all_tests(self):
        """Run all gaming balance tests"""
        print("🎮 GAMING BALANCE MENU TESTING - Fix Balance Display Confusion")
        print("=" * 80)
        print(f"Testing user: {USER_CONTEXT['username']}")
        print(f"Wallet: {USER_CONTEXT['wallet_address']}")
        print(f"Expected DOGE: {USER_CONTEXT['expected_doge']:,.2f} DOGE")
        print("=" * 80)
        
        # Test 1: User Authentication
        auth_success = await self.test_user_authentication()
        
        if auth_success:
            # Test 2: Balance Endpoint Structure
            wallet_data = await self.test_balance_endpoint_structure()
            
            # Test 3: DOGE Balance Accuracy
            await self.test_doge_balance_accuracy(wallet_data)
            
            # Test 4: Balance Display Simplicity
            await self.test_balance_display_simplicity(wallet_data)
            
            # Test 5: Real-time Balance Updates
            await self.test_real_time_balance_updates()
            
            # Test 6: USD Value Calculation
            await self.test_usd_value_calculation(wallet_data)
            
            # Test 7: Balance Menu Responsiveness
            await self.test_balance_menu_responsiveness()
            
            # Test 8: Gaming Balance Integration
            await self.test_gaming_balance_integration()
        else:
            print("❌ Authentication failed - skipping balance tests")
        
        # Print summary
        print("\n" + "=" * 80)
        print("🎮 GAMING BALANCE TEST SUMMARY")
        print("=" * 80)
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Categorize issues
        critical_issues = []
        minor_issues = []
        
        for result in self.test_results:
            if not result["success"]:
                if any(keyword in result["test"].lower() for keyword in ["authentication", "balance accuracy", "structure"]):
                    critical_issues.append(result["test"])
                else:
                    minor_issues.append(result["test"])
        
        if critical_issues:
            print(f"\n❌ CRITICAL ISSUES ({len(critical_issues)}):")
            for issue in critical_issues:
                print(f"  - {issue}")
        
        if minor_issues:
            print(f"\n⚠️ MINOR ISSUES ({len(minor_issues)}):")
            for issue in minor_issues:
                print(f"  - {issue}")
        
        if not critical_issues and not minor_issues:
            print("\n✅ ALL TESTS PASSED - Gaming balance menu working correctly!")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "critical_issues": critical_issues,
            "minor_issues": minor_issues,
            "test_results": self.test_results
        }

async def main():
    """Main test execution"""
    async with GamingBalanceTester(BACKEND_URL) as tester:
        results = await tester.run_all_tests()
        
        # Return results for further processing
        return results

if __name__ == "__main__":
    asyncio.run(main())