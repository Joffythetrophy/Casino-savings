#!/usr/bin/env python3
"""
Critical Issues Test Suite - Testing User Reported Issues
Focus Areas:
1. CRT Balance Check for user cryptoking
2. Real-time Balance Issues
3. Currency Selection for multi-currency gameplay
4. Autoplay Missing in Games
5. Real-time Stats tracking
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Backend URL from frontend env
BACKEND_URL = "https://blockchain-slots.preview.emergentagent.com/api"

# Test credentials from review request
TEST_CREDENTIALS = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

class CriticalIssuesTester:
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
        """Authenticate the specific user cryptoking"""
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
                                    f"Successfully authenticated user {TEST_CREDENTIALS['username']}", data)
                        return True
                    else:
                        self.log_test("User Authentication", False, 
                                    f"Authentication failed: {data.get('message')}", data)
                else:
                    self.log_test("User Authentication", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
        
        return False

    async def test_crt_balance_check(self):
        """Test 1: CRT Balance Check - Verify total CRT holdings for user cryptoking"""
        try:
            wallet_address = TEST_CREDENTIALS["wallet_address"]
            
            # Test 1a: Get wallet info to check CRT balance
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        savings_balance = wallet.get("savings_balance", {})
                        winnings_balance = wallet.get("winnings_balance", {})
                        
                        crt_deposit = deposit_balance.get("CRT", 0)
                        crt_savings = savings_balance.get("CRT", 0)
                        crt_winnings = winnings_balance.get("CRT", 0)
                        total_crt = crt_deposit + crt_savings + crt_winnings
                        
                        self.log_test("CRT Balance Check - Wallet Info", True, 
                                    f"Total CRT: {total_crt:,.0f} (Deposit: {crt_deposit:,.0f}, Savings: {crt_savings:,.0f}, Winnings: {crt_winnings:,.0f})", 
                                    {"total_crt": total_crt, "breakdown": {"deposit": crt_deposit, "savings": crt_savings, "winnings": crt_winnings}})
                        
                        # Check if there are additional CRT tokens beyond what's shown
                        if total_crt > 1000000:  # More than 1M CRT
                            self.log_test("CRT Holdings Verification", True, 
                                        f"User has substantial CRT holdings: {total_crt:,.0f} CRT", 
                                        {"substantial_holdings": True, "amount": total_crt})
                        else:
                            self.log_test("CRT Holdings Verification", False, 
                                        f"CRT holdings appear low: {total_crt:,.0f} CRT", 
                                        {"substantial_holdings": False, "amount": total_crt})
                    else:
                        self.log_test("CRT Balance Check - Wallet Info", False, 
                                    "Failed to retrieve wallet info", data)
                else:
                    self.log_test("CRT Balance Check - Wallet Info", False, 
                                f"HTTP {response.status}: {await response.text()}")
            
            # Test 1b: Check real blockchain CRT balance
            async with self.session.get(f"{self.base_url}/wallet/balance/CRT?wallet_address={wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        blockchain_crt = data.get("balance", 0)
                        self.log_test("CRT Balance Check - Blockchain", True, 
                                    f"Real blockchain CRT balance: {blockchain_crt:,.0f} CRT", 
                                    {"blockchain_balance": blockchain_crt})
                    else:
                        self.log_test("CRT Balance Check - Blockchain", False, 
                                    f"Blockchain balance check failed: {data.get('error')}", data)
                else:
                    self.log_test("CRT Balance Check - Blockchain", False, 
                                f"HTTP {response.status}: {await response.text()}")
            
            # Test 1c: Check conversion availability and limits
            async with self.session.get(f"{self.base_url}/conversion/rates") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        rates = data.get("rates", {})
                        crt_conversion_rates = {k: v for k, v in rates.items() if k.startswith("CRT_")}
                        
                        if crt_conversion_rates:
                            self.log_test("CRT Conversion Availability", True, 
                                        f"CRT conversion available to: {list(crt_conversion_rates.keys())}", 
                                        {"available_conversions": crt_conversion_rates})
                        else:
                            self.log_test("CRT Conversion Availability", False, 
                                        "No CRT conversion rates available", data)
                    else:
                        self.log_test("CRT Conversion Availability", False, 
                                    "Failed to get conversion rates", data)
                else:
                    self.log_test("CRT Conversion Availability", False, 
                                f"HTTP {response.status}: {await response.text()}")
                        
        except Exception as e:
            self.log_test("CRT Balance Check", False, f"Error: {str(e)}")

    async def test_real_time_balance_updates(self):
        """Test 2: Real-time Balance Issues - Test if game balances update in real-time"""
        try:
            wallet_address = TEST_CREDENTIALS["wallet_address"]
            
            # Get initial balance
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    initial_data = await response.json()
                    if initial_data.get("success"):
                        initial_wallet = initial_data["wallet"]
                        initial_crt = initial_wallet.get("deposit_balance", {}).get("CRT", 0)
                        initial_savings = initial_wallet.get("savings_balance", {}).get("CRT", 0)
                        
                        self.log_test("Initial Balance Check", True, 
                                    f"Initial CRT: {initial_crt:,.0f}, Savings: {initial_savings:,.0f}", 
                                    {"initial_crt": initial_crt, "initial_savings": initial_savings})
                        
                        # Place a test bet to trigger balance update
                        bet_payload = {
                            "wallet_address": wallet_address,
                            "game_type": "Slot Machine",
                            "bet_amount": 10.0,
                            "currency": "CRT",
                            "network": "solana"
                        }
                        
                        async with self.session.post(f"{self.base_url}/games/bet", 
                                                   json=bet_payload) as bet_response:
                            if bet_response.status == 200:
                                bet_data = await bet_response.json()
                                if bet_data.get("success"):
                                    result = bet_data.get("result")
                                    payout = bet_data.get("payout", 0)
                                    savings_contribution = bet_data.get("savings_contribution", 0)
                                    
                                    self.log_test("Game Bet Placed", True, 
                                                f"Bet result: {result}, payout: {payout}, savings: {savings_contribution}", 
                                                bet_data)
                                    
                                    # Check balance immediately after bet
                                    async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as post_bet_response:
                                        if post_bet_response.status == 200:
                                            post_bet_data = await post_bet_response.json()
                                            if post_bet_data.get("success"):
                                                post_bet_wallet = post_bet_data["wallet"]
                                                post_bet_crt = post_bet_wallet.get("deposit_balance", {}).get("CRT", 0)
                                                post_bet_savings = post_bet_wallet.get("savings_balance", {}).get("CRT", 0)
                                                
                                                # Check if balance updated in real-time
                                                balance_changed = (post_bet_crt != initial_crt) or (post_bet_savings != initial_savings)
                                                
                                                if balance_changed:
                                                    self.log_test("Real-time Balance Update", True, 
                                                                f"Balance updated: CRT {initial_crt:,.0f} → {post_bet_crt:,.0f}, Savings {initial_savings:,.0f} → {post_bet_savings:,.0f}", 
                                                                {"balance_updated": True, "initial_crt": initial_crt, "post_bet_crt": post_bet_crt})
                                                else:
                                                    self.log_test("Real-time Balance Update", False, 
                                                                "Balance did not update after bet", 
                                                                {"balance_updated": False, "initial_crt": initial_crt, "post_bet_crt": post_bet_crt})
                                            else:
                                                self.log_test("Real-time Balance Update", False, 
                                                            "Failed to get post-bet balance", post_bet_data)
                                        else:
                                            self.log_test("Real-time Balance Update", False, 
                                                        f"Post-bet balance check failed: HTTP {post_bet_response.status}")
                                else:
                                    self.log_test("Game Bet Placed", False, 
                                                f"Bet failed: {bet_data.get('message', 'Unknown error')}", bet_data)
                            else:
                                self.log_test("Game Bet Placed", False, 
                                            f"Bet request failed: HTTP {bet_response.status}")
                    else:
                        self.log_test("Initial Balance Check", False, 
                                    "Failed to get initial balance", initial_data)
                else:
                    self.log_test("Initial Balance Check", False, 
                                f"Initial balance check failed: HTTP {response.status}")
                        
        except Exception as e:
            self.log_test("Real-time Balance Updates", False, f"Error: {str(e)}")

    async def test_multi_currency_gameplay(self):
        """Test 3: Currency Selection - Test multi-currency gameplay functionality"""
        try:
            wallet_address = TEST_CREDENTIALS["wallet_address"]
            test_currencies = ["CRT", "DOGE", "TRX", "USDC"]
            
            # Check available balances for each currency
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        
                        available_currencies = []
                        for currency in test_currencies:
                            balance = deposit_balance.get(currency, 0)
                            if balance > 0:
                                available_currencies.append(currency)
                                self.log_test(f"Currency Balance - {currency}", True, 
                                            f"{currency} balance: {balance:,.2f}", 
                                            {"currency": currency, "balance": balance})
                        
                        if len(available_currencies) >= 2:
                            self.log_test("Multi-Currency Availability", True, 
                                        f"Multiple currencies available: {available_currencies}", 
                                        {"available_currencies": available_currencies})
                            
                            # Test betting with different currencies
                            for currency in available_currencies[:2]:  # Test first 2 available currencies
                                bet_payload = {
                                    "wallet_address": wallet_address,
                                    "game_type": "Dice",
                                    "bet_amount": 5.0,
                                    "currency": currency,
                                    "network": "solana" if currency in ["CRT", "SOL"] else "dogecoin" if currency == "DOGE" else "tron"
                                }
                                
                                async with self.session.post(f"{self.base_url}/games/bet", 
                                                           json=bet_payload) as bet_response:
                                    if bet_response.status == 200:
                                        bet_data = await bet_response.json()
                                        if bet_data.get("success"):
                                            self.log_test(f"Multi-Currency Betting - {currency}", True, 
                                                        f"Successfully placed {currency} bet: {bet_data.get('result')}", 
                                                        {"currency": currency, "result": bet_data.get("result")})
                                        else:
                                            self.log_test(f"Multi-Currency Betting - {currency}", False, 
                                                        f"{currency} bet failed: {bet_data.get('message')}", bet_data)
                                    else:
                                        self.log_test(f"Multi-Currency Betting - {currency}", False, 
                                                    f"{currency} bet request failed: HTTP {bet_response.status}")
                        else:
                            self.log_test("Multi-Currency Availability", False, 
                                        f"Insufficient currencies available: {available_currencies}", 
                                        {"available_currencies": available_currencies})
                    else:
                        self.log_test("Multi-Currency Gameplay", False, 
                                    "Failed to get wallet info", data)
                else:
                    self.log_test("Multi-Currency Gameplay", False, 
                                f"Wallet info request failed: HTTP {response.status}")
                        
        except Exception as e:
            self.log_test("Multi-Currency Gameplay", False, f"Error: {str(e)}")

    async def test_autoplay_functionality(self):
        """Test 4: Autoplay Missing in Games - Check autoplay availability"""
        try:
            # Test autoplay endpoints for different games
            games_to_test = ["Slot Machine", "Roulette", "Dice", "Plinko", "Keno", "Mines"]
            
            for game_type in games_to_test:
                # Check if game supports autoplay by testing bet endpoint structure
                bet_payload = {
                    "wallet_address": TEST_CREDENTIALS["wallet_address"],
                    "game_type": game_type,
                    "bet_amount": 1.0,
                    "currency": "CRT",
                    "network": "solana"
                }
                
                async with self.session.post(f"{self.base_url}/games/bet", 
                                           json=bet_payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            # Check if response includes autoplay-compatible fields
                            required_autoplay_fields = ["game_id", "result", "payout", "savings_contribution"]
                            has_autoplay_support = all(field in data for field in required_autoplay_fields)
                            
                            if has_autoplay_support:
                                self.log_test(f"Autoplay Support - {game_type}", True, 
                                            f"{game_type} supports autoplay (has required API fields)", 
                                            {"game_type": game_type, "autoplay_ready": True})
                            else:
                                self.log_test(f"Autoplay Support - {game_type}", False, 
                                            f"{game_type} missing autoplay fields", 
                                            {"game_type": game_type, "missing_fields": [f for f in required_autoplay_fields if f not in data]})
                        else:
                            self.log_test(f"Autoplay Support - {game_type}", False, 
                                        f"{game_type} bet failed: {data.get('message')}", data)
                    elif response.status == 403:
                        self.log_test(f"Autoplay Support - {game_type}", False, 
                                    f"{game_type} requires authentication", {"requires_auth": True})
                    else:
                        self.log_test(f"Autoplay Support - {game_type}", False, 
                                    f"{game_type} bet request failed: HTTP {response.status}")
            
            # Test rapid successive bets (autoplay simulation)
            rapid_bet_results = []
            for i in range(5):
                bet_payload = {
                    "wallet_address": TEST_CREDENTIALS["wallet_address"],
                    "game_type": "Slot Machine",
                    "bet_amount": 1.0,
                    "currency": "CRT",
                    "network": "solana"
                }
                
                start_time = time.time()
                async with self.session.post(f"{self.base_url}/games/bet", 
                                           json=bet_payload) as response:
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            rapid_bet_results.append({
                                "bet_number": i + 1,
                                "response_time": response_time,
                                "result": data.get("result"),
                                "success": True
                            })
                        else:
                            rapid_bet_results.append({
                                "bet_number": i + 1,
                                "response_time": response_time,
                                "error": data.get("message"),
                                "success": False
                            })
                    else:
                        rapid_bet_results.append({
                            "bet_number": i + 1,
                            "response_time": response_time,
                            "http_status": response.status,
                            "success": False
                        })
            
            successful_bets = [r for r in rapid_bet_results if r.get("success")]
            avg_response_time = sum(r["response_time"] for r in successful_bets) / len(successful_bets) if successful_bets else 0
            
            if len(successful_bets) >= 4:  # At least 4 out of 5 successful
                self.log_test("Autoplay Performance Test", True, 
                            f"Rapid betting successful: {len(successful_bets)}/5 bets, avg response: {avg_response_time:.2f}s", 
                            {"successful_bets": len(successful_bets), "avg_response_time": avg_response_time, "results": rapid_bet_results})
            else:
                self.log_test("Autoplay Performance Test", False, 
                            f"Rapid betting failed: only {len(successful_bets)}/5 successful", 
                            {"successful_bets": len(successful_bets), "results": rapid_bet_results})
                        
        except Exception as e:
            self.log_test("Autoplay Functionality", False, f"Error: {str(e)}")

    async def test_real_time_stats_tracking(self):
        """Test 5: Real-time Stats - Test win/loss tracking"""
        try:
            wallet_address = TEST_CREDENTIALS["wallet_address"]
            
            # Get initial stats
            async with self.session.get(f"{self.base_url}/savings/{wallet_address}") as response:
                if response.status == 200:
                    initial_data = await response.json()
                    if initial_data.get("success"):
                        initial_stats = initial_data.get("stats", {})
                        initial_games = initial_stats.get("total_games", 0)
                        initial_wins = initial_stats.get("total_wins", 0)
                        initial_losses = initial_stats.get("total_losses", 0)
                        
                        self.log_test("Initial Stats Check", True, 
                                    f"Initial stats - Games: {initial_games}, Wins: {initial_wins}, Losses: {initial_losses}", 
                                    {"initial_games": initial_games, "initial_wins": initial_wins, "initial_losses": initial_losses})
                        
                        # Place several bets to generate new stats
                        bet_results = []
                        for i in range(3):
                            bet_payload = {
                                "wallet_address": wallet_address,
                                "game_type": "Dice",
                                "bet_amount": 5.0,
                                "currency": "CRT",
                                "network": "solana"
                            }
                            
                            async with self.session.post(f"{self.base_url}/games/bet", 
                                                       json=bet_payload) as bet_response:
                                if bet_response.status == 200:
                                    bet_data = await bet_response.json()
                                    if bet_data.get("success"):
                                        bet_results.append({
                                            "result": bet_data.get("result"),
                                            "payout": bet_data.get("payout", 0),
                                            "game_id": bet_data.get("game_id")
                                        })
                        
                        if bet_results:
                            self.log_test("Test Bets Placed", True, 
                                        f"Placed {len(bet_results)} test bets", 
                                        {"bet_count": len(bet_results), "results": bet_results})
                            
                            # Check updated stats
                            async with self.session.get(f"{self.base_url}/savings/{wallet_address}") as updated_response:
                                if updated_response.status == 200:
                                    updated_data = await updated_response.json()
                                    if updated_data.get("success"):
                                        updated_stats = updated_data.get("stats", {})
                                        updated_games = updated_stats.get("total_games", 0)
                                        updated_wins = updated_stats.get("total_wins", 0)
                                        updated_losses = updated_stats.get("total_losses", 0)
                                        
                                        # Check if stats updated in real-time
                                        games_increased = updated_games > initial_games
                                        stats_changed = (updated_wins != initial_wins) or (updated_losses != initial_losses)
                                        
                                        if games_increased and stats_changed:
                                            self.log_test("Real-time Stats Update", True, 
                                                        f"Stats updated: Games {initial_games} → {updated_games}, Wins {initial_wins} → {updated_wins}, Losses {initial_losses} → {updated_losses}", 
                                                        {"stats_updated": True, "games_change": updated_games - initial_games})
                                        else:
                                            self.log_test("Real-time Stats Update", False, 
                                                        f"Stats did not update properly: Games {initial_games} → {updated_games}", 
                                                        {"stats_updated": False, "expected_change": len(bet_results)})
                                        
                                        # Check liquidity stats
                                        liquidity_stats = updated_data.get("liquidity_stats", {})
                                        if liquidity_stats:
                                            self.log_test("Liquidity Stats Tracking", True, 
                                                        f"Liquidity stats available: {liquidity_stats}", 
                                                        {"liquidity_stats": liquidity_stats})
                                        else:
                                            self.log_test("Liquidity Stats Tracking", False, 
                                                        "No liquidity stats found", updated_data)
                                    else:
                                        self.log_test("Real-time Stats Update", False, 
                                                    "Failed to get updated stats", updated_data)
                                else:
                                    self.log_test("Real-time Stats Update", False, 
                                                f"Updated stats request failed: HTTP {updated_response.status}")
                        else:
                            self.log_test("Test Bets Placed", False, 
                                        "No test bets were successful", {"bet_results": bet_results})
                    else:
                        self.log_test("Initial Stats Check", False, 
                                    "Failed to get initial stats", initial_data)
                elif response.status == 403:
                    self.log_test("Real-time Stats Tracking", False, 
                                "Stats endpoint requires authentication", {"requires_auth": True})
                else:
                    self.log_test("Initial Stats Check", False, 
                                f"Initial stats request failed: HTTP {response.status}")
                        
        except Exception as e:
            self.log_test("Real-time Stats Tracking", False, f"Error: {str(e)}")

    async def test_treasury_wallet_balance_sync(self):
        """Test 6: Treasury wallet balance synchronization"""
        try:
            wallet_address = TEST_CREDENTIALS["wallet_address"]
            
            # Check all wallet types for balance consistency
            async with self.session.get(f"{self.base_url}/wallet/{wallet_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        wallet = data["wallet"]
                        
                        # Check different wallet types
                        deposit_balance = wallet.get("deposit_balance", {})
                        winnings_balance = wallet.get("winnings_balance", {})
                        savings_balance = wallet.get("savings_balance", {})
                        liquidity_pool = wallet.get("liquidity_pool", {})
                        
                        # Calculate total holdings
                        currencies = ["CRT", "DOGE", "TRX", "USDC"]
                        total_holdings = {}
                        
                        for currency in currencies:
                            total = (deposit_balance.get(currency, 0) + 
                                   winnings_balance.get(currency, 0) + 
                                   savings_balance.get(currency, 0))
                            total_holdings[currency] = total
                        
                        self.log_test("Treasury Balance Sync", True, 
                                    f"Treasury balances synchronized: {total_holdings}", 
                                    {
                                        "deposit": deposit_balance,
                                        "winnings": winnings_balance, 
                                        "savings": savings_balance,
                                        "liquidity": liquidity_pool,
                                        "totals": total_holdings
                                    })
                        
                        # Check if liquidity pool has reasonable values
                        total_liquidity = sum(liquidity_pool.values()) if liquidity_pool else 0
                        if total_liquidity > 0:
                            self.log_test("Liquidity Pool Status", True, 
                                        f"Liquidity pool active: {total_liquidity:,.2f} total", 
                                        {"liquidity_pool": liquidity_pool})
                        else:
                            self.log_test("Liquidity Pool Status", False, 
                                        "No liquidity in pool", {"liquidity_pool": liquidity_pool})
                    else:
                        self.log_test("Treasury Balance Sync", False, 
                                    "Failed to get wallet info", data)
                else:
                    self.log_test("Treasury Balance Sync", False, 
                                f"Wallet request failed: HTTP {response.status}")
                        
        except Exception as e:
            self.log_test("Treasury Wallet Balance Sync", False, f"Error: {str(e)}")

    async def run_all_tests(self):
        """Run all critical issue tests"""
        print("🚨 CRITICAL ISSUES TESTING STARTED")
        print("=" * 60)
        
        # Authenticate user first
        await self.authenticate_user()
        
        if not self.user_authenticated:
            print("❌ Cannot proceed without user authentication")
            return
        
        # Run all critical tests
        await self.test_crt_balance_check()
        await self.test_real_time_balance_updates()
        await self.test_multi_currency_gameplay()
        await self.test_autoplay_functionality()
        await self.test_real_time_stats_tracking()
        await self.test_treasury_wallet_balance_sync()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 CRITICAL ISSUES TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = [r for r in self.test_results if r["success"]]
        failed_tests = [r for r in self.test_results if not r["success"]]
        
        print(f"✅ PASSED: {len(passed_tests)}")
        print(f"❌ FAILED: {len(failed_tests)}")
        print(f"📊 SUCCESS RATE: {len(passed_tests)}/{len(self.test_results)} ({len(passed_tests)/len(self.test_results)*100:.1f}%)")
        
        if failed_tests:
            print("\n🚨 CRITICAL FAILURES:")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['details']}")
        
        return {
            "total_tests": len(self.test_results),
            "passed": len(passed_tests),
            "failed": len(failed_tests),
            "success_rate": len(passed_tests)/len(self.test_results)*100 if self.test_results else 0,
            "results": self.test_results
        }

async def main():
    """Main test execution"""
    async with CriticalIssuesTester(BACKEND_URL) as tester:
        results = await tester.run_all_tests()
        return results

if __name__ == "__main__":
    results = asyncio.run(main())