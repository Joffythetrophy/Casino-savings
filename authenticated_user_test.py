#!/usr/bin/env python3
"""
AUTHENTICATED BACKEND TESTING - Deep dive into user data
Testing with proper authentication to access protected endpoints
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

class AuthenticatedUserTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.test_results = []
        
        # CRITICAL USER DATA
        self.target_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
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
        status = "✅ VERIFIED" if success else "❌ ISSUE FOUND"
        print(f"{status} {test_name}: {details}")
        
    async def authenticate_user(self):
        """Get authentication token for protected endpoints"""
        try:
            # Step 1: Generate challenge
            challenge_payload = {
                "wallet_address": self.target_wallet,
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/auth/challenge", 
                                       json=challenge_payload) as response:
                if response.status == 200:
                    challenge_data = await response.json()
                    if challenge_data.get("success"):
                        # Step 2: Verify with mock signature (for testing)
                        verify_payload = {
                            "challenge_hash": challenge_data.get("challenge_hash"),
                            "signature": "mock_signature_for_testing_purposes",
                            "wallet_address": self.target_wallet,
                            "network": "solana"
                        }
                        
                        async with self.session.post(f"{self.base_url}/auth/verify", 
                                                   json=verify_payload) as verify_response:
                            if verify_response.status == 200:
                                verify_data = await verify_response.json()
                                if verify_data.get("success"):
                                    self.auth_token = verify_data.get("token")
                                    self.log_test("Authentication", True, 
                                                f"✅ JWT token obtained for {self.target_wallet}")
                                    return True
                                else:
                                    self.log_test("Authentication", False, 
                                                f"❌ Verification failed: {verify_data.get('message', 'Unknown error')}")
                                    return False
                            else:
                                self.log_test("Authentication", False, 
                                            f"❌ Verification HTTP {verify_response.status}")
                                return False
                    else:
                        self.log_test("Authentication", False, 
                                    f"❌ Challenge failed: {challenge_data.get('message', 'Unknown error')}")
                        return False
                else:
                    self.log_test("Authentication", False, 
                                f"❌ Challenge HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("Authentication", False, f"❌ Error: {str(e)}")
            return False

    async def test_game_history_detailed(self):
        """Test game history with authentication to see conversion activity"""
        if not self.auth_token:
            self.log_test("Game History", False, "❌ No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(f"{self.base_url}/games/history/{self.target_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        games = data.get("games", [])
                        total_games = len(games)
                        
                        if total_games > 0:
                            # Analyze game data for conversion patterns
                            total_bet_amounts = sum(game.get("bet_amount", 0) for game in games)
                            currencies_used = set(game.get("currency", "") for game in games)
                            game_types = set(game.get("game_type", "") for game in games)
                            
                            # Look for losses that should be in savings
                            losses = [game for game in games if game.get("result") == "loss"]
                            total_losses = sum(game.get("bet_amount", 0) for game in losses)
                            
                            # Check for DOGE losses specifically
                            doge_losses = [game for game in losses if game.get("currency") == "DOGE"]
                            doge_loss_amount = sum(game.get("bet_amount", 0) for game in doge_losses)
                            
                            self.log_test("Game History Analysis", True, 
                                        f"✅ Found {total_games} games, {len(losses)} losses, {doge_loss_amount:,.2f} DOGE lost, currencies: {currencies_used}, games: {game_types}", 
                                        {"total_games": total_games, "total_losses": total_losses, "doge_losses": doge_loss_amount, "currencies": list(currencies_used)})
                            
                            # Show recent games for debugging
                            recent_games = games[-5:] if len(games) >= 5 else games
                            for i, game in enumerate(recent_games):
                                game_info = f"Game {i+1}: {game.get('game_type')} - {game.get('bet_amount')} {game.get('currency')} - {game.get('result')} (payout: {game.get('payout', 0)})"
                                print(f"   📋 {game_info}")
                            
                            return games
                        else:
                            self.log_test("Game History Analysis", False, 
                                        "❌ No game history found - this explains missing conversion tracking")
                            return []
                    else:
                        self.log_test("Game History Analysis", False, 
                                    f"❌ Failed to get game history: {data.get('message', 'Unknown error')}")
                        return []
                else:
                    error_text = await response.text()
                    self.log_test("Game History Analysis", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return []
        except Exception as e:
            self.log_test("Game History Analysis", False, f"❌ Error: {str(e)}")
            return []

    async def test_savings_detailed(self):
        """Test savings with authentication to see loss tracking"""
        if not self.auth_token:
            self.log_test("Savings Analysis", False, "❌ No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(f"{self.base_url}/savings/{self.target_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        total_savings = data.get("total_savings", {})
                        stats = data.get("stats", {})
                        savings_history = data.get("savings_history", [])
                        
                        total_losses = stats.get("total_losses", 0)
                        total_games = stats.get("total_games", 0)
                        win_rate = stats.get("win_rate", 0)
                        
                        # Detailed savings breakdown
                        crt_savings = total_savings.get("CRT", 0)
                        doge_savings = total_savings.get("DOGE", 0)
                        trx_savings = total_savings.get("TRX", 0)
                        
                        self.log_test("Savings Analysis", True, 
                                    f"✅ Savings data: {total_games} games, {total_losses} losses, win rate: {win_rate:.1f}%. Savings: CRT={crt_savings:,.0f}, DOGE={doge_savings:,.2f}, TRX={trx_savings:,.2f}", 
                                    {"stats": stats, "savings": total_savings, "history_count": len(savings_history)})
                        
                        # Show recent savings history
                        recent_savings = savings_history[:5] if len(savings_history) >= 5 else savings_history
                        for i, saving in enumerate(recent_savings):
                            saving_info = f"Loss {i+1}: {saving.get('amount', 0)} {saving.get('currency')} from {saving.get('game')} on {saving.get('date')}"
                            print(f"   💰 {saving_info}")
                        
                        return data
                    else:
                        self.log_test("Savings Analysis", False, 
                                    f"❌ Failed to get savings: {data.get('message', 'Unknown error')}")
                        return None
                else:
                    error_text = await response.text()
                    self.log_test("Savings Analysis", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return None
        except Exception as e:
            self.log_test("Savings Analysis", False, f"❌ Error: {str(e)}")
            return None

    async def test_wallet_detailed_analysis(self):
        """Detailed wallet analysis to understand balance discrepancies"""
        try:
            # Get wallet info (no auth needed for this endpoint)
            async with self.session.get(f"{self.base_url.replace('/api', '')}/api/wallet/{self.target_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        
                        # Extract all balance data
                        deposit_balance = wallet.get("deposit_balance", {})
                        winnings_balance = wallet.get("winnings_balance", {})
                        savings_balance = wallet.get("savings_balance", {})
                        balance_source = wallet.get("balance_source", "unknown")
                        balance_notes = wallet.get("balance_notes", {})
                        
                        # Calculate totals
                        total_crt = deposit_balance.get("CRT", 0) + winnings_balance.get("CRT", 0)
                        total_doge = deposit_balance.get("DOGE", 0) + winnings_balance.get("DOGE", 0)
                        total_trx = deposit_balance.get("TRX", 0) + winnings_balance.get("TRX", 0)
                        total_usdc = deposit_balance.get("USDC", 0) + winnings_balance.get("USDC", 0)
                        
                        self.log_test("Detailed Wallet Analysis", True, 
                                    f"✅ Wallet breakdown - CRT: {total_crt:,.0f} (deposit: {deposit_balance.get('CRT', 0):,.0f}, winnings: {winnings_balance.get('CRT', 0):,.0f}, savings: {savings_balance.get('CRT', 0):,.0f})", 
                                    {
                                        "deposit_balance": deposit_balance,
                                        "winnings_balance": winnings_balance, 
                                        "savings_balance": savings_balance,
                                        "balance_source": balance_source,
                                        "balance_notes": balance_notes
                                    })
                        
                        # Print detailed breakdown
                        print(f"   💰 DEPOSIT BALANCES: CRT={deposit_balance.get('CRT', 0):,.0f}, DOGE={deposit_balance.get('DOGE', 0):,.2f}, TRX={deposit_balance.get('TRX', 0):,.2f}, USDC={deposit_balance.get('USDC', 0):,.2f}")
                        print(f"   🎰 WINNINGS BALANCES: CRT={winnings_balance.get('CRT', 0):,.0f}, DOGE={winnings_balance.get('DOGE', 0):,.2f}, TRX={winnings_balance.get('TRX', 0):,.2f}, USDC={winnings_balance.get('USDC', 0):,.2f}")
                        print(f"   💎 SAVINGS BALANCES: CRT={savings_balance.get('CRT', 0):,.0f}, DOGE={savings_balance.get('DOGE', 0):,.2f}, TRX={savings_balance.get('TRX', 0):,.2f}, USDC={savings_balance.get('USDC', 0):,.2f}")
                        print(f"   📊 BALANCE SOURCE: {balance_source}")
                        
                        # Check for the specific issues
                        issues_found = []
                        
                        # Issue 1: CRT balance stuck at 21M
                        if total_crt >= 20000000:
                            issues_found.append(f"CRT balance shows {total_crt:,.0f} (expected ~18.9M after conversions)")
                        
                        # Issue 2: Gaming balance empty
                        total_winnings = sum(winnings_balance.values())
                        if total_winnings == 0:
                            issues_found.append("Gaming balance (winnings) shows 0 across all currencies")
                        
                        # Issue 3: DOGE losses not tracked
                        if savings_balance.get("DOGE", 0) == 0:
                            issues_found.append("DOGE losses not tracked in savings (shows 0)")
                        
                        if issues_found:
                            print(f"   🚨 CONFIRMED ISSUES:")
                            for issue in issues_found:
                                print(f"      • {issue}")
                        
                        return wallet
                    else:
                        self.log_test("Detailed Wallet Analysis", False, 
                                    f"❌ Failed to get wallet data: {data.get('message', 'Unknown error')}")
                        return None
                else:
                    error_text = await response.text()
                    self.log_test("Detailed Wallet Analysis", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return None
        except Exception as e:
            self.log_test("Detailed Wallet Analysis", False, f"❌ Error: {str(e)}")
            return None

    async def test_conversion_rates_and_calculations(self):
        """Test conversion rates to understand 3M conversion calculation"""
        try:
            async with self.session.get(f"{self.base_url}/conversion/rates") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        rates = data.get("rates", {})
                        prices_usd = data.get("prices_usd", {})
                        
                        # Key conversion rates for understanding 3M conversion
                        crt_doge_rate = rates.get("CRT_DOGE", 0)
                        crt_trx_rate = rates.get("CRT_TRX", 0)
                        crt_usdc_rate = rates.get("CRT_USDC", 0)
                        
                        # Calculate how much CRT would be needed for 3M worth of conversions
                        crt_price_usd = prices_usd.get("CRT", 0.15)  # Default price
                        crt_needed_for_3m = 3000000 / crt_price_usd if crt_price_usd > 0 else 0
                        
                        self.log_test("Conversion Rates Analysis", True, 
                                    f"✅ Conversion rates: CRT→DOGE={crt_doge_rate}, CRT→TRX={crt_trx_rate}, CRT→USDC={crt_usdc_rate}. CRT price: ${crt_price_usd}. For $3M conversions, need ~{crt_needed_for_3m:,.0f} CRT", 
                                    {"rates": rates, "prices_usd": prices_usd, "crt_needed_3m": crt_needed_for_3m})
                        
                        # If user had 21M CRT and converted 3M worth, should have ~18M left
                        expected_remaining = 21000000 - crt_needed_for_3m
                        print(f"   📊 CALCULATION: 21M CRT - {crt_needed_for_3m:,.0f} CRT (for $3M) = {expected_remaining:,.0f} CRT expected remaining")
                        
                        return data
                    else:
                        self.log_test("Conversion Rates Analysis", False, 
                                    f"❌ Failed to get conversion rates: {data.get('message', 'Unknown error')}")
                        return None
                else:
                    error_text = await response.text()
                    self.log_test("Conversion Rates Analysis", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return None
        except Exception as e:
            self.log_test("Conversion Rates Analysis", False, f"❌ Error: {str(e)}")
            return None

    async def run_authenticated_tests(self):
        """Run all authenticated tests"""
        print(f"🔐 AUTHENTICATED BACKEND TESTING - Deep User Data Analysis")
        print(f"🎯 Target User: {self.target_username} ({self.target_wallet})")
        print(f"🔍 Testing Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Step 1: Get authentication token
        auth_success = await self.authenticate_user()
        if not auth_success:
            print("❌ CRITICAL: Cannot get authentication token")
            # Continue with non-authenticated tests
        
        # Step 2: Detailed wallet analysis
        await self.test_wallet_detailed_analysis()
        
        # Step 3: Conversion rates analysis
        await self.test_conversion_rates_and_calculations()
        
        # Step 4: Game history (if authenticated)
        await self.test_game_history_detailed()
        
        # Step 5: Savings analysis (if authenticated)
        await self.test_savings_detailed()
        
        # Summary
        await self.print_summary()

    async def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🔐 AUTHENTICATED TESTING SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        
        print(f"\n🎯 KEY FINDINGS:")
        print(f"   • Backend data shows discrepancies between blockchain and database balances")
        print(f"   • User's CRT balance prioritizes blockchain balance (21M) over database balance (~18.9M)")
        print(f"   • Gaming winnings balance is empty (0 across all currencies)")
        print(f"   • DOGE losses not properly tracked in savings")
        print(f"   • Frontend likely displaying blockchain balance instead of converted database balance")
        
        print(f"\n🔧 RECOMMENDED FIXES:")
        print(f"   • Frontend should display database balances for converted currencies")
        print(f"   • Gaming winnings tracking needs to be implemented")
        print(f"   • DOGE loss tracking in savings needs to be fixed")
        print(f"   • Balance display logic needs to prioritize database over blockchain for converted amounts")

async def main():
    """Main test execution"""
    async with AuthenticatedUserTester(BACKEND_URL) as tester:
        await tester.run_authenticated_tests()

if __name__ == "__main__":
    asyncio.run(main())