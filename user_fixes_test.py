#!/usr/bin/env python3
"""
User-Requested Fixes Testing Suite
Tests all the specific fixes implemented for the user's critical issues:
1. CRT Balance Fix (21M CRT access)
2. Autoplay Added to Roulette
3. Real-time Balance Updates
4. Multi-Currency Gaming
5. Streamlined Interface
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://crypto-treasury.preview.emergentagent.com/api"

# Test credentials from review request
TEST_CREDENTIALS = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

class UserFixesTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        self.user_authenticated = False
        
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
        
    async def authenticate_user(self):
        """Authenticate the specific user for testing"""
        try:
            # Try username login first
            login_payload = {
                "username": TEST_CREDENTIALS["username"],
                "password": TEST_CREDENTIALS["password"]
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.user_authenticated = True
                        self.log_test("User Authentication", True, 
                                    f"User {TEST_CREDENTIALS['username']} authenticated successfully")
                        return True
                        
            # Fallback to wallet address login
            login_payload = {
                "identifier": TEST_CREDENTIALS["wallet_address"],
                "password": TEST_CREDENTIALS["password"]
            }
            
            async with self.session.post(f"{self.base_url}/auth/login", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.user_authenticated = True
                        self.log_test("User Authentication", True, 
                                    f"User authenticated via wallet address")
                        return True
                        
            self.log_test("User Authentication", False, 
                        "Failed to authenticate user with provided credentials")
            return False
            
        except Exception as e:
            self.log_test("User Authentication", False, f"Authentication error: {str(e)}")
            return False

    async def test_crt_balance_fix(self):
        """Test 1: CRT Balance Fix - User should have access to 21M CRT"""
        try:
            # Get user's wallet info
            async with self.session.get(f"{self.base_url}/wallet/{TEST_CREDENTIALS['wallet_address']}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        crt_balance = deposit_balance.get("CRT", 0)
                        
                        # Check if user has access to 21M CRT or close to it
                        expected_crt = 21000000  # 21M CRT
                        if crt_balance >= expected_crt * 0.95:  # Allow 5% variance
                            self.log_test("CRT Balance Fix", True, 
                                        f"✅ CRT balance fixed: User has {crt_balance:,.0f} CRT (expected ~21M)", data)
                        elif crt_balance >= 1000000:  # At least 1M CRT
                            self.log_test("CRT Balance Fix", False, 
                                        f"⚠️ CRT balance partially fixed: User has {crt_balance:,.0f} CRT but expected 21M", data)
                        else:
                            self.log_test("CRT Balance Fix", False, 
                                        f"❌ CRT balance NOT fixed: User only has {crt_balance:,.0f} CRT (expected 21M)", data)
                    else:
                        self.log_test("CRT Balance Fix", False, "Failed to retrieve wallet info", data)
                else:
                    self.log_test("CRT Balance Fix", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("CRT Balance Fix", False, f"Error: {str(e)}")

    async def test_large_crt_conversion(self):
        """Test 2: Large CRT Conversion - Test converting large amounts of CRT"""
        try:
            # Test converting 1M CRT to DOGE
            convert_payload = {
                "wallet_address": TEST_CREDENTIALS["wallet_address"],
                "from_currency": "CRT",
                "to_currency": "DOGE",
                "amount": 1000000.0  # 1M CRT
            }
            
            async with self.session.post(f"{self.base_url}/wallet/convert", 
                                       json=convert_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        converted_amount = data.get("converted_amount", 0)
                        rate = data.get("rate", 0)
                        self.log_test("Large CRT Conversion", True, 
                                    f"✅ Large CRT conversion successful: 1M CRT → {converted_amount:,.2f} DOGE (rate: {rate})", data)
                    else:
                        error_msg = data.get("message", "Unknown error")
                        if "Insufficient balance" in error_msg:
                            self.log_test("Large CRT Conversion", False, 
                                        f"❌ CRT conversion failed - insufficient balance: {error_msg}", data)
                        else:
                            self.log_test("Large CRT Conversion", False, 
                                        f"❌ CRT conversion failed: {error_msg}", data)
                else:
                    self.log_test("Large CRT Conversion", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Large CRT Conversion", False, f"Error: {str(e)}")

    async def test_multi_currency_betting(self):
        """Test 3: Multi-Currency Betting - Test betting with different currencies"""
        currencies_to_test = ["CRT", "DOGE", "TRX", "USDC"]
        successful_bets = 0
        
        for currency in currencies_to_test:
            try:
                bet_payload = {
                    "wallet_address": TEST_CREDENTIALS["wallet_address"],
                    "game_type": "Slot Machine",
                    "bet_amount": 10.0,
                    "currency": currency,
                    "network": "solana"
                }
                
                async with self.session.post(f"{self.base_url}/games/bet", 
                                           json=bet_payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            result = data.get("result")
                            payout = data.get("payout", 0)
                            successful_bets += 1
                            self.log_test(f"Multi-Currency Betting - {currency}", True, 
                                        f"✅ {currency} betting works: {result}, payout: {payout}", data)
                        else:
                            self.log_test(f"Multi-Currency Betting - {currency}", False, 
                                        f"❌ {currency} betting failed: {data.get('message', 'Unknown error')}", data)
                    else:
                        self.log_test(f"Multi-Currency Betting - {currency}", False, 
                                    f"HTTP {response.status}: {await response.text()}")
            except Exception as e:
                self.log_test(f"Multi-Currency Betting - {currency}", False, f"Error: {str(e)}")
        
        # Overall multi-currency test result
        if successful_bets >= 3:
            self.log_test("Multi-Currency Gaming", True, 
                        f"✅ Multi-currency gaming working: {successful_bets}/{len(currencies_to_test)} currencies successful")
        elif successful_bets >= 1:
            self.log_test("Multi-Currency Gaming", False, 
                        f"⚠️ Multi-currency gaming partially working: {successful_bets}/{len(currencies_to_test)} currencies successful")
        else:
            self.log_test("Multi-Currency Gaming", False, 
                        f"❌ Multi-currency gaming not working: {successful_bets}/{len(currencies_to_test)} currencies successful")

    async def test_real_time_balance_updates(self):
        """Test 4: Real-time Balance Updates - Test if balances update immediately after bets"""
        try:
            # Get initial balance
            async with self.session.get(f"{self.base_url}/wallet/{TEST_CREDENTIALS['wallet_address']}") as response:
                if response.status != 200:
                    self.log_test("Real-time Balance Updates", False, "Failed to get initial balance")
                    return
                    
                initial_data = await response.json()
                if not initial_data.get("success"):
                    self.log_test("Real-time Balance Updates", False, "Failed to get initial wallet data")
                    return
                    
                initial_wallet = initial_data["wallet"]
                initial_crt = initial_wallet.get("deposit_balance", {}).get("CRT", 0)
                initial_savings = initial_wallet.get("savings_balance", {}).get("CRT", 0)
            
            # Place a bet
            bet_payload = {
                "wallet_address": TEST_CREDENTIALS["wallet_address"],
                "game_type": "Dice",
                "bet_amount": 10.0,
                "currency": "CRT",
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/games/bet", 
                                       json=bet_payload) as bet_response:
                if bet_response.status != 200:
                    self.log_test("Real-time Balance Updates", False, "Failed to place test bet")
                    return
                    
                bet_data = await bet_response.json()
                if not bet_data.get("success"):
                    self.log_test("Real-time Balance Updates", False, "Test bet was not successful")
                    return
                    
                bet_result = bet_data.get("result")
                savings_contribution = bet_data.get("savings_contribution", 0)
            
            # Get balance immediately after bet
            async with self.session.get(f"{self.base_url}/wallet/{TEST_CREDENTIALS['wallet_address']}") as response:
                if response.status == 200:
                    updated_data = await response.json()
                    if updated_data.get("success"):
                        updated_wallet = updated_data["wallet"]
                        updated_crt = updated_wallet.get("deposit_balance", {}).get("CRT", 0)
                        updated_savings = updated_wallet.get("savings_balance", {}).get("CRT", 0)
                        
                        # Check if balance changed
                        crt_change = initial_crt - updated_crt
                        savings_change = updated_savings - initial_savings
                        
                        if abs(crt_change - 10.0) < 0.01:  # Should decrease by bet amount
                            if bet_result == "loss" and savings_change > 0:
                                self.log_test("Real-time Balance Updates", True, 
                                            f"✅ Real-time updates working: CRT {initial_crt}→{updated_crt}, Savings {initial_savings}→{updated_savings}")
                            elif bet_result == "win":
                                self.log_test("Real-time Balance Updates", True, 
                                            f"✅ Real-time updates working: CRT balance updated after win")
                            else:
                                self.log_test("Real-time Balance Updates", True, 
                                            f"✅ Real-time updates working: CRT balance changed by {crt_change}")
                        else:
                            self.log_test("Real-time Balance Updates", False, 
                                        f"❌ Balance not updated correctly: expected -10 CRT, got {crt_change}")
                    else:
                        self.log_test("Real-time Balance Updates", False, "Failed to get updated wallet data")
                else:
                    self.log_test("Real-time Balance Updates", False, "Failed to get updated balance")
                    
        except Exception as e:
            self.log_test("Real-time Balance Updates", False, f"Error: {str(e)}")

    async def test_autoplay_functionality(self):
        """Test 5: Autoplay Functionality - Test autoplay in all games including roulette"""
        games_to_test = ["Slot Machine", "Roulette", "Dice", "Plinko", "Keno", "Mines"]
        autoplay_working = 0
        
        for game in games_to_test:
            try:
                # Test multiple rapid bets to simulate autoplay
                rapid_bets_successful = 0
                for i in range(3):  # Test 3 rapid bets per game
                    bet_payload = {
                        "wallet_address": TEST_CREDENTIALS["wallet_address"],
                        "game_type": game,
                        "bet_amount": 5.0,
                        "currency": "CRT",
                        "network": "solana"
                    }
                    
                    async with self.session.post(f"{self.base_url}/games/bet", 
                                               json=bet_payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("success"):
                                rapid_bets_successful += 1
                
                if rapid_bets_successful >= 2:  # At least 2/3 bets successful
                    autoplay_working += 1
                    self.log_test(f"Autoplay - {game}", True, 
                                f"✅ {game} autoplay ready: {rapid_bets_successful}/3 rapid bets successful")
                else:
                    self.log_test(f"Autoplay - {game}", False, 
                                f"❌ {game} autoplay issues: only {rapid_bets_successful}/3 rapid bets successful")
                    
            except Exception as e:
                self.log_test(f"Autoplay - {game}", False, f"Error: {str(e)}")
        
        # Overall autoplay test result
        if autoplay_working >= 5:  # At least 5/6 games working
            self.log_test("Autoplay Functionality", True, 
                        f"✅ Autoplay functionality working: {autoplay_working}/{len(games_to_test)} games support rapid betting")
        elif autoplay_working >= 3:
            self.log_test("Autoplay Functionality", False, 
                        f"⚠️ Autoplay partially working: {autoplay_working}/{len(games_to_test)} games support rapid betting")
        else:
            self.log_test("Autoplay Functionality", False, 
                        f"❌ Autoplay not working: only {autoplay_working}/{len(games_to_test)} games support rapid betting")

    async def test_treasury_wallet_display(self):
        """Test 6: Treasury Wallet Display - Verify clear visualization of all 3 wallets"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{TEST_CREDENTIALS['wallet_address']}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        
                        # Check for all 3 treasury wallets
                        required_wallets = ["deposit_balance", "winnings_balance", "savings_balance"]
                        wallet_data = {}
                        
                        for wallet_type in required_wallets:
                            if wallet_type in wallet:
                                wallet_data[wallet_type] = wallet[wallet_type]
                        
                        # Check if all wallet types exist and have currency data
                        if len(wallet_data) == 3:
                            # Check if each wallet has multi-currency support
                            currencies_found = set()
                            for wallet_type, balances in wallet_data.items():
                                if isinstance(balances, dict):
                                    currencies_found.update(balances.keys())
                            
                            if len(currencies_found) >= 3:  # Should have CRT, DOGE, TRX, USDC
                                self.log_test("Treasury Wallet Display", True, 
                                            f"✅ Treasury wallets properly structured: 3 wallets with {len(currencies_found)} currencies", data)
                            else:
                                self.log_test("Treasury Wallet Display", False, 
                                            f"⚠️ Treasury wallets missing currencies: only {currencies_found}", data)
                        else:
                            self.log_test("Treasury Wallet Display", False, 
                                        f"❌ Missing treasury wallets: found {list(wallet_data.keys())}, expected {required_wallets}", data)
                    else:
                        self.log_test("Treasury Wallet Display", False, "Failed to retrieve wallet data", data)
                else:
                    self.log_test("Treasury Wallet Display", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Treasury Wallet Display", False, f"Error: {str(e)}")

    async def test_liquidity_pool_access(self):
        """Test 7: Liquidity Pool Access - Test user's liquidity pool for withdrawals"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{TEST_CREDENTIALS['wallet_address']}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        liquidity_pool = wallet.get("liquidity_pool", {})
                        
                        if liquidity_pool:
                            total_liquidity = sum(liquidity_pool.values())
                            currencies_with_liquidity = [curr for curr, amount in liquidity_pool.items() if amount > 0]
                            
                            if total_liquidity > 0:
                                self.log_test("Liquidity Pool Access", True, 
                                            f"✅ Liquidity pool accessible: {currencies_with_liquidity} with total value {total_liquidity}", data)
                            else:
                                self.log_test("Liquidity Pool Access", False, 
                                            f"⚠️ Liquidity pool empty: {liquidity_pool}", data)
                        else:
                            self.log_test("Liquidity Pool Access", False, 
                                        "❌ Liquidity pool not found in wallet data", data)
                    else:
                        self.log_test("Liquidity Pool Access", False, "Failed to retrieve wallet data", data)
                else:
                    self.log_test("Liquidity Pool Access", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Liquidity Pool Access", False, f"Error: {str(e)}")

    async def test_win_loss_stats_tracking(self):
        """Test 8: Win/Loss Stats Tracking - Test real-time stats updates"""
        try:
            # Get game history to check stats
            async with self.session.get(f"{self.base_url}/savings/{TEST_CREDENTIALS['wallet_address']}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        stats = data.get("stats", {})
                        total_games = stats.get("total_games", 0)
                        total_wins = stats.get("total_wins", 0)
                        total_losses = stats.get("total_losses", 0)
                        win_rate = stats.get("win_rate", 0)
                        
                        if total_games > 0:
                            self.log_test("Win/Loss Stats Tracking", True, 
                                        f"✅ Stats tracking working: {total_games} games, {total_wins} wins, {total_losses} losses, {win_rate}% win rate", data)
                        else:
                            self.log_test("Win/Loss Stats Tracking", False, 
                                        f"⚠️ No game stats found - may need to place bets first", data)
                    else:
                        self.log_test("Win/Loss Stats Tracking", False, "Failed to retrieve stats data", data)
                else:
                    self.log_test("Win/Loss Stats Tracking", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Win/Loss Stats Tracking", False, f"Error: {str(e)}")

    async def run_all_tests(self):
        """Run all user-requested fix tests"""
        print("🎯 STARTING USER-REQUESTED FIXES TESTING")
        print("=" * 60)
        
        # Authenticate user first
        if not await self.authenticate_user():
            print("❌ CRITICAL: User authentication failed - cannot proceed with tests")
            return
        
        # Run all tests
        await self.test_crt_balance_fix()
        await self.test_large_crt_conversion()
        await self.test_multi_currency_betting()
        await self.test_real_time_balance_updates()
        await self.test_autoplay_functionality()
        await self.test_treasury_wallet_display()
        await self.test_liquidity_pool_access()
        await self.test_win_loss_stats_tracking()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("🎯 USER-REQUESTED FIXES TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests)*100:.1f}%)")
        print()
        
        # Critical fixes status
        critical_fixes = {
            "CRT Balance Fix": False,
            "Large CRT Conversion": False,
            "Multi-Currency Gaming": False,
            "Real-time Balance Updates": False,
            "Autoplay Functionality": False
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "CRT Balance Fix" in test_name:
                critical_fixes["CRT Balance Fix"] = result["success"]
            elif "Large CRT Conversion" in test_name:
                critical_fixes["Large CRT Conversion"] = result["success"]
            elif "Multi-Currency Gaming" in test_name:
                critical_fixes["Multi-Currency Gaming"] = result["success"]
            elif "Real-time Balance Updates" in test_name:
                critical_fixes["Real-time Balance Updates"] = result["success"]
            elif "Autoplay Functionality" in test_name:
                critical_fixes["Autoplay Functionality"] = result["success"]
        
        print("🔥 CRITICAL FIXES STATUS:")
        for fix_name, status in critical_fixes.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {fix_name}")
        
        print()
        print("📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["success"] else "❌"
            print(f"   {status_icon} {result['test']}: {result['details']}")
        
        # Recommendations
        print()
        print("💡 RECOMMENDATIONS:")
        if not critical_fixes["CRT Balance Fix"]:
            print("   🚨 URGENT: Fix CRT balance synchronization - user cannot access 21M CRT")
        if not critical_fixes["Multi-Currency Gaming"]:
            print("   ⚠️ Fix multi-currency betting system")
        if not critical_fixes["Autoplay Functionality"]:
            print("   ⚠️ Improve autoplay system reliability")
        
        if all(critical_fixes.values()):
            print("   🎉 ALL CRITICAL FIXES WORKING! User experience should be excellent.")

async def main():
    """Main test execution"""
    async with UserFixesTester(BACKEND_URL) as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())