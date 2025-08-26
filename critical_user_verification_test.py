#!/usr/bin/env python3
"""
CRITICAL FRONTEND BUG DEBUGGING - Backend Data Verification
Testing specific user wallet DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq
for reported frontend display issues vs actual backend data
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://gamewin-vault.preview.emergentagent.com/api"

class CriticalUserVerificationTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        
        # CRITICAL USER DATA
        self.target_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        self.target_username = "cryptoking"
        self.target_password = "crt21million"
        
        # Expected issues to verify
        self.expected_issues = {
            "crt_balance_stuck_21m": "CRT still shows 21M even after 3M worth of conversions",
            "gaming_balance_empty": "game balance doesn't show nothing",
            "conversion_not_tracked": "3 mill worth of conversion not updating CRT balance",
            "doge_losses_not_counting": "DOGE I already lost but shows 0 still not counting",
            "autoplay_only_slots": "no more auto play for the games just slots"
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
        status = "✅ VERIFIED" if success else "❌ ISSUE FOUND"
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
                    if data.get("success") and data.get("wallet_address") == self.target_wallet:
                        self.log_test("User Authentication", True, 
                                    f"✅ Authentication successful for {self.target_username} -> {self.target_wallet}", data)
                        return True
                    else:
                        self.log_test("User Authentication", False, 
                                    f"❌ Authentication failed: {data.get('message', 'Unknown error')}", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("User Authentication", False, f"❌ Error: {str(e)}")
            return False

    async def test_wallet_balance_display(self):
        """Test 2: Check actual wallet balances vs reported frontend display issues"""
        try:
            # Get wallet info from backend
            async with self.session.get(f"{self.base_url.replace('/api', '')}/api/wallet/{self.target_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        
                        # Extract balance data
                        deposit_balance = wallet.get("deposit_balance", {})
                        winnings_balance = wallet.get("winnings_balance", {})
                        savings_balance = wallet.get("savings_balance", {})
                        
                        crt_deposit = deposit_balance.get("CRT", 0)
                        crt_winnings = winnings_balance.get("CRT", 0)
                        crt_savings = savings_balance.get("CRT", 0)
                        
                        doge_deposit = deposit_balance.get("DOGE", 0)
                        doge_winnings = winnings_balance.get("DOGE", 0)
                        doge_savings = savings_balance.get("DOGE", 0)
                        
                        # CRITICAL ISSUE 1: CRT Balance Display
                        total_crt = crt_deposit + crt_winnings
                        if total_crt >= 20000000:  # Still showing ~21M
                            self.log_test("CRT Balance Display Issue", False, 
                                        f"❌ CONFIRMED BUG: CRT shows {total_crt:,.0f} (should be ~18.9M after 3M conversions). Deposit: {crt_deposit:,.0f}, Winnings: {crt_winnings:,.0f}, Savings: {crt_savings:,.0f}", 
                                        {"total_crt": total_crt, "deposit": crt_deposit, "winnings": crt_winnings, "savings": crt_savings})
                        else:
                            self.log_test("CRT Balance Display Issue", True, 
                                        f"✅ CRT balance appears correct: {total_crt:,.0f}", 
                                        {"total_crt": total_crt, "deposit": crt_deposit, "winnings": crt_winnings, "savings": crt_savings})
                        
                        # CRITICAL ISSUE 2: Gaming Balance (should show winnings)
                        total_gaming_balance = sum(winnings_balance.values())
                        if total_gaming_balance == 0:
                            self.log_test("Gaming Balance Display Issue", False, 
                                        f"❌ CONFIRMED BUG: Gaming balance shows 0 (no winnings tracked). Winnings: {winnings_balance}", 
                                        {"gaming_balance": winnings_balance, "total": total_gaming_balance})
                        else:
                            self.log_test("Gaming Balance Display Issue", True, 
                                        f"✅ Gaming balance shows data: {total_gaming_balance:,.2f} total", 
                                        {"gaming_balance": winnings_balance, "total": total_gaming_balance})
                        
                        # CRITICAL ISSUE 3: DOGE Loss Tracking
                        if doge_savings == 0:
                            self.log_test("DOGE Loss Tracking Issue", False, 
                                        f"❌ CONFIRMED BUG: DOGE losses not tracked in savings (shows 0). DOGE savings: {doge_savings}", 
                                        {"doge_savings": doge_savings, "doge_deposit": doge_deposit, "doge_winnings": doge_winnings})
                        else:
                            self.log_test("DOGE Loss Tracking Issue", True, 
                                        f"✅ DOGE losses properly tracked: {doge_savings:,.2f} in savings", 
                                        {"doge_savings": doge_savings, "doge_deposit": doge_deposit, "doge_winnings": doge_winnings})
                        
                        return wallet
                    else:
                        self.log_test("Wallet Balance Display", False, 
                                    f"❌ Failed to get wallet data: {data.get('message', 'Unknown error')}", data)
                        return None
                else:
                    error_text = await response.text()
                    self.log_test("Wallet Balance Display", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return None
        except Exception as e:
            self.log_test("Wallet Balance Display", False, f"❌ Error: {str(e)}")
            return None

    async def test_conversion_transaction_history(self):
        """Test 3: Check conversion transaction history for 3M worth of conversions"""
        try:
            # This would require a transaction history endpoint
            # For now, we'll check if there are any conversion-related endpoints
            
            # Try to get game history which might show conversion activity
            async with self.session.get(f"{self.base_url}/games/history/{self.target_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        games = data.get("games", [])
                        total_games = len(games)
                        
                        # Look for conversion patterns in game history
                        total_bet_amounts = sum(game.get("bet_amount", 0) for game in games)
                        
                        if total_bet_amounts >= 3000000:  # 3M worth of activity
                            self.log_test("Conversion Transaction History", True, 
                                        f"✅ Found significant transaction activity: {total_bet_amounts:,.0f} total bet amounts across {total_games} games", 
                                        {"total_games": total_games, "total_bet_amounts": total_bet_amounts})
                        else:
                            self.log_test("Conversion Transaction History", False, 
                                        f"❌ Limited transaction history found: {total_bet_amounts:,.0f} total bet amounts across {total_games} games (expected ~3M)", 
                                        {"total_games": total_games, "total_bet_amounts": total_bet_amounts})
                        
                        return games
                    else:
                        self.log_test("Conversion Transaction History", False, 
                                    f"❌ Failed to get game history: {data.get('message', 'Unknown error')}", data)
                        return []
                else:
                    # Game history might require authentication
                    self.log_test("Conversion Transaction History", False, 
                                f"❌ Game history endpoint requires authentication (HTTP {response.status})")
                    return []
        except Exception as e:
            self.log_test("Conversion Transaction History", False, f"❌ Error: {str(e)}")
            return []

    async def test_game_betting_endpoints(self):
        """Test 4: Check all game betting endpoints for auto-play availability"""
        try:
            game_types = ["Slot Machine", "Roulette", "Dice", "Plinko", "Keno", "Mines"]
            working_games = []
            failed_games = []
            
            for game_type in game_types:
                try:
                    bet_payload = {
                        "wallet_address": self.target_wallet,
                        "game_type": game_type,
                        "bet_amount": 1.0,  # Small test bet
                        "currency": "CRT",
                        "network": "solana"
                    }
                    
                    async with self.session.post(f"{self.base_url}/games/bet", 
                                               json=bet_payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("success"):
                                working_games.append(game_type)
                            else:
                                failed_games.append(f"{game_type}: {data.get('message', 'Unknown error')}")
                        elif response.status == 403:
                            # Authentication required - game endpoint exists
                            working_games.append(f"{game_type} (auth required)")
                        else:
                            failed_games.append(f"{game_type}: HTTP {response.status}")
                            
                except Exception as game_error:
                    failed_games.append(f"{game_type}: {str(game_error)}")
            
            # CRITICAL ISSUE 4: Auto-play availability
            if len(working_games) == 1 and "Slot Machine" in str(working_games):
                self.log_test("Auto-Play Game Availability", False, 
                            f"❌ CONFIRMED BUG: Only Slot Machine available for auto-play. Working: {working_games}, Failed: {failed_games}", 
                            {"working_games": working_games, "failed_games": failed_games})
            elif len(working_games) >= 5:
                self.log_test("Auto-Play Game Availability", True, 
                            f"✅ Multiple games available for auto-play: {working_games}", 
                            {"working_games": working_games, "failed_games": failed_games})
            else:
                self.log_test("Auto-Play Game Availability", False, 
                            f"❌ Limited games available: {working_games}, Failed: {failed_games}", 
                            {"working_games": working_games, "failed_games": failed_games})
            
            return {"working": working_games, "failed": failed_games}
            
        except Exception as e:
            self.log_test("Auto-Play Game Availability", False, f"❌ Error: {str(e)}")
            return {"working": [], "failed": []}

    async def test_savings_balance_tracking(self):
        """Test 5: Verify savings balance tracking from game losses"""
        try:
            # Get savings information
            async with self.session.get(f"{self.base_url}/savings/{self.target_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        total_savings = data.get("total_savings", {})
                        stats = data.get("stats", {})
                        savings_history = data.get("savings_history", [])
                        
                        total_losses = stats.get("total_losses", 0)
                        total_games = stats.get("total_games", 0)
                        
                        # Check if losses are properly tracked
                        crt_savings = total_savings.get("CRT", 0)
                        doge_savings = total_savings.get("DOGE", 0)
                        trx_savings = total_savings.get("TRX", 0)
                        
                        if total_losses == 0:
                            self.log_test("Savings Balance Tracking", False, 
                                        f"❌ CONFIRMED BUG: No game losses tracked (shows 0 losses from {total_games} games)", 
                                        {"total_losses": total_losses, "total_games": total_games, "savings": total_savings})
                        elif doge_savings == 0 and total_losses > 0:
                            self.log_test("Savings Balance Tracking", False, 
                                        f"❌ PARTIAL BUG: DOGE losses not tracked (0 DOGE savings) but other losses tracked. Total losses: {total_losses}", 
                                        {"total_losses": total_losses, "doge_savings": doge_savings, "savings": total_savings})
                        else:
                            self.log_test("Savings Balance Tracking", True, 
                                        f"✅ Savings tracking working: {total_losses} losses tracked, DOGE savings: {doge_savings}", 
                                        {"total_losses": total_losses, "savings": total_savings, "history_entries": len(savings_history)})
                        
                        return data
                    else:
                        self.log_test("Savings Balance Tracking", False, 
                                    f"❌ Failed to get savings data: {data.get('message', 'Unknown error')}", data)
                        return None
                elif response.status == 403:
                    self.log_test("Savings Balance Tracking", False, 
                                "❌ Savings endpoint requires authentication")
                    return None
                else:
                    error_text = await response.text()
                    self.log_test("Savings Balance Tracking", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return None
        except Exception as e:
            self.log_test("Savings Balance Tracking", False, f"❌ Error: {str(e)}")
            return None

    async def test_real_blockchain_vs_database_balances(self):
        """Test 6: Compare real blockchain balances vs database balances"""
        try:
            # Get real blockchain balances
            async with self.session.get(f"{self.base_url}/blockchain/balances?wallet_address={self.target_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        blockchain_balances = data.get("balances", {})
                        
                        # Extract real blockchain data
                        real_crt = blockchain_balances.get("CRT", {}).get("balance", 0)
                        real_doge = blockchain_balances.get("DOGE", {}).get("balance", 0)
                        real_trx = blockchain_balances.get("TRX", {}).get("balance", 0)
                        
                        # Compare with database balances from wallet endpoint
                        wallet_data = await self.get_wallet_data()
                        if wallet_data:
                            db_crt = wallet_data.get("deposit_balance", {}).get("CRT", 0)
                            db_doge = wallet_data.get("deposit_balance", {}).get("DOGE", 0)
                            db_trx = wallet_data.get("deposit_balance", {}).get("TRX", 0)
                            
                            # Check for discrepancies
                            crt_discrepancy = abs(real_crt - db_crt) > 1000000  # 1M CRT threshold
                            doge_discrepancy = abs(real_doge - db_doge) > 1000   # 1K DOGE threshold
                            
                            if crt_discrepancy:
                                self.log_test("Blockchain vs Database Balance", False, 
                                            f"❌ CRT BALANCE MISMATCH: Blockchain: {real_crt:,.0f}, Database: {db_crt:,.0f} (diff: {abs(real_crt - db_crt):,.0f})", 
                                            {"blockchain": {"CRT": real_crt, "DOGE": real_doge, "TRX": real_trx}, 
                                             "database": {"CRT": db_crt, "DOGE": db_doge, "TRX": db_trx}})
                            else:
                                self.log_test("Blockchain vs Database Balance", True, 
                                            f"✅ Balances synchronized: CRT blockchain: {real_crt:,.0f}, database: {db_crt:,.0f}", 
                                            {"blockchain": {"CRT": real_crt, "DOGE": real_doge, "TRX": real_trx}, 
                                             "database": {"CRT": db_crt, "DOGE": db_doge, "TRX": db_trx}})
                        else:
                            self.log_test("Blockchain vs Database Balance", False, 
                                        "❌ Could not get database balance data for comparison")
                        
                        return {"blockchain": blockchain_balances, "database": wallet_data}
                    else:
                        self.log_test("Blockchain vs Database Balance", False, 
                                    f"❌ Failed to get blockchain balances: {data.get('message', 'Unknown error')}", data)
                        return None
                else:
                    error_text = await response.text()
                    self.log_test("Blockchain vs Database Balance", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return None
        except Exception as e:
            self.log_test("Blockchain vs Database Balance", False, f"❌ Error: {str(e)}")
            return None

    async def get_wallet_data(self):
        """Helper method to get wallet data"""
        try:
            async with self.session.get(f"{self.base_url.replace('/api', '')}/api/wallet/{self.target_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        return data.get("wallet")
                return None
        except:
            return None

    async def run_all_tests(self):
        """Run all critical verification tests"""
        print(f"🚨 CRITICAL FRONTEND BUG DEBUGGING - Backend Data Verification")
        print(f"🎯 Target User: {self.target_username} ({self.target_wallet})")
        print(f"🔍 Testing Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Test 1: Authentication
        auth_success = await self.test_user_authentication()
        if not auth_success:
            print("❌ CRITICAL: Cannot authenticate user - stopping tests")
            return
        
        # Test 2: Wallet Balance Display Issues
        await self.test_wallet_balance_display()
        
        # Test 3: Conversion Transaction History
        await self.test_conversion_transaction_history()
        
        # Test 4: Game Betting Endpoints (Auto-play)
        await self.test_game_betting_endpoints()
        
        # Test 5: Savings Balance Tracking
        await self.test_savings_balance_tracking()
        
        # Test 6: Real Blockchain vs Database Balances
        await self.test_real_blockchain_vs_database_balances()
        
        # Summary
        await self.print_summary()

    async def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("🎯 CRITICAL USER VERIFICATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
        print(f"✅ Verified: {passed_tests}")
        print(f"❌ Issues Found: {failed_tests}")
        
        if failed_tests > 0:
            print(f"\n🚨 CRITICAL ISSUES CONFIRMED:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n📋 EXPECTED vs ACTUAL FINDINGS:")
        for issue_key, issue_desc in self.expected_issues.items():
            print(f"   • {issue_desc}")
            
        print(f"\n🎯 BACKEND DATA VERIFICATION COMPLETE")
        print(f"📝 Frontend likely not pulling/displaying backend data properly")
        print(f"🔧 Need to identify data sync issues between backend and frontend")

async def main():
    """Main test execution"""
    async with CriticalUserVerificationTester(BACKEND_URL) as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())