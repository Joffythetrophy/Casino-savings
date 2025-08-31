#!/usr/bin/env python3
"""
CRITICAL CASINO BETTING SYSTEM DEBUG TEST
User 'cryptoking' reports: "Failing to place bets not working cant play"

This test focuses specifically on debugging the casino betting system failure
to identify why the user cannot place bets in casino games.
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Test Configuration
BACKEND_URL = "https://real-crt-casino.preview.emergentagent.com/api"
TEST_USER = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

class CasinoBettingDebugger:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.user_balances = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if data and not success:
            print(f"   Error Data: {json.dumps(data, indent=2)}")
    
    async def authenticate_user(self) -> bool:
        """Authenticate user cryptoking"""
        try:
            login_data = {
                "identifier": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        self.auth_token = result.get("token")
                        self.log_test(
                            "User Authentication", 
                            True, 
                            f"Successfully authenticated user '{TEST_USER['username']}' with wallet {TEST_USER['wallet_address']}"
                        )
                        return True
                    else:
                        self.log_test("User Authentication", False, f"Login failed: {result.get('message', 'Unknown error')}", result)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("User Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    async def check_user_balances(self) -> bool:
        """Check user's current balances across all wallet types"""
        try:
            async with self.session.get(f"{BACKEND_URL}/wallet/{TEST_USER['wallet_address']}") as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        wallet_data = result.get("wallet", {})
                        self.user_balances = {
                            "deposit": wallet_data.get("deposit_balance", {}),
                            "winnings": wallet_data.get("winnings_balance", {}),
                            "savings": wallet_data.get("savings_balance", {}),
                            "gaming": wallet_data.get("gaming_balance", {})
                        }
                        
                        # Calculate total balances per currency
                        total_balances = {}
                        for currency in ["CRT", "DOGE", "TRX", "USDC", "SOL"]:
                            total = 0
                            for wallet_type in self.user_balances:
                                total += self.user_balances[wallet_type].get(currency, 0)
                            total_balances[currency] = total
                        
                        balance_summary = ", ".join([f"{curr}: {bal:,.2f}" for curr, bal in total_balances.items() if bal > 0])
                        
                        self.log_test(
                            "User Balance Verification", 
                            True, 
                            f"Retrieved balances - {balance_summary}",
                            {"balances": self.user_balances, "totals": total_balances}
                        )
                        return True
                    else:
                        self.log_test("User Balance Verification", False, f"Failed to get wallet info: {result}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("User Balance Verification", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("User Balance Verification", False, f"Balance check error: {str(e)}")
            return False
    
    async def test_game_betting_api(self, game_type: str, currency: str, bet_amount: float) -> bool:
        """Test the /api/games/bet endpoint with specific parameters"""
        try:
            bet_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "game_type": game_type,
                "bet_amount": bet_amount,
                "currency": currency,
                "network": "Solana" if currency in ["CRT", "SOL", "USDC"] else ("TRON" if currency == "TRX" else "Dogecoin")
            }
            
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            async with self.session.post(f"{BACKEND_URL}/games/bet", json=bet_data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        result = await response.json() if response.content_type == 'application/json' else json.loads(response_text)
                        if result.get("success"):
                            game_result = result.get("result", "unknown")
                            payout = result.get("payout", 0)
                            self.log_test(
                                f"Game Betting - {game_type} ({currency})", 
                                True, 
                                f"Bet placed successfully: {bet_amount} {currency} → {game_result}, payout: {payout}",
                                result
                            )
                            return True
                        else:
                            self.log_test(
                                f"Game Betting - {game_type} ({currency})", 
                                False, 
                                f"Bet failed: {result.get('message', 'Unknown error')}", 
                                result
                            )
                            return False
                    except json.JSONDecodeError:
                        self.log_test(
                            f"Game Betting - {game_type} ({currency})", 
                            False, 
                            f"Invalid JSON response: {response_text}"
                        )
                        return False
                else:
                    self.log_test(
                        f"Game Betting - {game_type} ({currency})", 
                        False, 
                        f"HTTP {response.status}: {response_text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test(f"Game Betting - {game_type} ({currency})", False, f"Betting error: {str(e)}")
            return False
    
    async def test_authentication_requirements(self) -> bool:
        """Test if betting API requires authentication"""
        try:
            bet_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "game_type": "Slot Machine",
                "bet_amount": 10.0,
                "currency": "DOGE",
                "network": "Dogecoin"
            }
            
            # Test without authentication token
            async with self.session.post(f"{BACKEND_URL}/games/bet", json=bet_data) as response:
                response_text = await response.text()
                
                if response.status == 401 or response.status == 403:
                    self.log_test(
                        "Authentication Requirement Check", 
                        True, 
                        f"Betting API properly requires authentication (HTTP {response.status})"
                    )
                    return True
                elif response.status == 200:
                    self.log_test(
                        "Authentication Requirement Check", 
                        True, 
                        "Betting API allows unauthenticated access (no auth required)"
                    )
                    return True
                else:
                    self.log_test(
                        "Authentication Requirement Check", 
                        False, 
                        f"Unexpected response: HTTP {response.status}: {response_text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Authentication Requirement Check", False, f"Auth test error: {str(e)}")
            return False
    
    async def test_balance_deduction(self, currency: str, bet_amount: float) -> bool:
        """Test if balances are properly deducted after betting"""
        try:
            # Get initial balance
            initial_balance = 0
            for wallet_type in self.user_balances:
                initial_balance += self.user_balances[wallet_type].get(currency, 0)
            
            if initial_balance < bet_amount:
                self.log_test(
                    f"Balance Deduction Test ({currency})", 
                    False, 
                    f"Insufficient balance for test: {initial_balance} < {bet_amount}"
                )
                return False
            
            # Place bet
            bet_success = await self.test_game_betting_api("Dice", currency, bet_amount)
            
            if not bet_success:
                self.log_test(
                    f"Balance Deduction Test ({currency})", 
                    False, 
                    "Could not place bet to test balance deduction"
                )
                return False
            
            # Check balance after bet
            await asyncio.sleep(1)  # Wait for balance update
            await self.check_user_balances()
            
            final_balance = 0
            for wallet_type in self.user_balances:
                final_balance += self.user_balances[wallet_type].get(currency, 0)
            
            balance_change = initial_balance - final_balance
            
            if balance_change > 0:
                self.log_test(
                    f"Balance Deduction Test ({currency})", 
                    True, 
                    f"Balance properly deducted: {initial_balance} → {final_balance} (change: -{balance_change})"
                )
                return True
            else:
                self.log_test(
                    f"Balance Deduction Test ({currency})", 
                    False, 
                    f"Balance not deducted: {initial_balance} → {final_balance}"
                )
                return False
                
        except Exception as e:
            self.log_test(f"Balance Deduction Test ({currency})", False, f"Balance test error: {str(e)}")
            return False
    
    async def comprehensive_betting_test(self):
        """Run comprehensive casino betting system test"""
        print("🎰 CASINO BETTING SYSTEM DEBUG TEST - CRITICAL USER ISSUE")
        print("=" * 70)
        print(f"User Report: 'cryptoking' - 'Failing to place bets not working cant play'")
        print(f"Testing wallet: {TEST_USER['wallet_address']}")
        print("=" * 70)
        
        # 1. Authenticate user
        auth_success = await self.authenticate_user()
        if not auth_success:
            print("\n❌ CRITICAL: Authentication failed - user cannot access system")
            return
        
        # 2. Check user balances
        balance_success = await self.check_user_balances()
        if not balance_success:
            print("\n❌ CRITICAL: Cannot retrieve user balances")
            return
        
        # 3. Test authentication requirements
        await self.test_authentication_requirements()
        
        # 4. Test betting with different currencies and amounts
        test_scenarios = [
            ("Slot Machine", "DOGE", 10.0),
            ("Roulette", "DOGE", 50.0),
            ("Dice", "DOGE", 100.0),
            ("Slot Machine", "CRT", 10.0),
            ("Roulette", "TRX", 25.0),
            ("Dice", "USDC", 5.0)
        ]
        
        successful_bets = 0
        total_tests = len(test_scenarios)
        
        for game_type, currency, amount in test_scenarios:
            # Check if user has sufficient balance
            total_balance = 0
            for wallet_type in self.user_balances:
                total_balance += self.user_balances[wallet_type].get(currency, 0)
            
            if total_balance >= amount:
                success = await self.test_game_betting_api(game_type, currency, amount)
                if success:
                    successful_bets += 1
                    # Update balances after successful bet
                    await self.check_user_balances()
            else:
                self.log_test(
                    f"Game Betting - {game_type} ({currency})", 
                    False, 
                    f"Insufficient balance: {total_balance} < {amount}"
                )
        
        # 5. Test balance deduction for available currencies
        for currency in ["DOGE", "CRT", "TRX", "USDC"]:
            total_balance = 0
            for wallet_type in self.user_balances:
                total_balance += self.user_balances[wallet_type].get(currency, 0)
            
            if total_balance >= 10:  # Test with 10 units if available
                await self.test_balance_deduction(currency, 10.0)
        
        # Generate summary
        print("\n" + "=" * 70)
        print("🎯 CASINO BETTING SYSTEM DEBUG SUMMARY")
        print("=" * 70)
        
        total_tests_run = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["success"]])
        
        print(f"Total Tests: {total_tests_run}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests_run - successful_tests}")
        print(f"Success Rate: {(successful_tests/total_tests_run)*100:.1f}%")
        
        # Identify critical issues
        critical_issues = []
        for result in self.test_results:
            if not result["success"]:
                if "Authentication" in result["test"]:
                    critical_issues.append("🚨 AUTHENTICATION FAILURE - User cannot log in")
                elif "Balance" in result["test"] and "Verification" in result["test"]:
                    critical_issues.append("🚨 BALANCE ACCESS FAILURE - Cannot retrieve user balances")
                elif "Game Betting" in result["test"]:
                    critical_issues.append(f"🚨 BETTING FAILURE - {result['test']}: {result['details']}")
        
        if critical_issues:
            print("\n🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in critical_issues:
                print(f"   {issue}")
        else:
            print("\n✅ NO CRITICAL ISSUES FOUND - Betting system appears functional")
        
        # Specific diagnosis for user complaint
        if successful_bets == 0:
            print(f"\n🎯 DIAGNOSIS: User complaint CONFIRMED - NO BETS CAN BE PLACED")
            print("   Possible causes:")
            print("   - Authentication issues preventing bet placement")
            print("   - Insufficient balances in all currencies")
            print("   - Backend betting API failures")
            print("   - Database connection issues")
        elif successful_bets < total_tests // 2:
            print(f"\n🎯 DIAGNOSIS: PARTIAL BETTING FAILURE - Only {successful_bets}/{total_tests} bet types working")
            print("   Some games/currencies working, others failing")
        else:
            print(f"\n🎯 DIAGNOSIS: Betting system mostly functional - {successful_bets}/{total_tests} successful")
            print("   User issue may be specific to certain games or currencies")
        
        return self.test_results

async def main():
    """Run the casino betting debug test"""
    async with CasinoBettingDebugger() as tester:
        results = await tester.comprehensive_betting_test()
        
        # Save results to file for analysis
        with open("/app/casino_betting_debug_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: /app/casino_betting_debug_results.json")

if __name__ == "__main__":
    asyncio.run(main())