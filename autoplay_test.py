#!/usr/bin/env python3
"""
Casino Savings dApp - AI Auto-Play Backend Testing Suite
Comprehensive testing for AI Auto-Play feature implementation
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://winsaver.preview.emergentagent.com/api"

class AutoPlayTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        
        # Test user credentials from review request
        self.test_user = "cryptoking"
        self.test_password = "crt21million"
        self.test_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        self.auth_token = None
        
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
        """Test 1: Authentication System - Verify user login and get JWT token for AutoPlay"""
        try:
            # Step 1: Login to get user info
            login_payload = {
                "username": self.test_user,
                "password": self.test_password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("username") == self.test_user:
                        # Step 2: Get JWT token via wallet authentication
                        challenge_payload = {
                            "wallet_address": self.test_wallet,
                            "network": "solana"
                        }
                        
                        async with self.session.post(f"{self.base_url}/auth/challenge", 
                                                   json=challenge_payload) as challenge_response:
                            if challenge_response.status == 200:
                                challenge_data = await challenge_response.json()
                                if challenge_data.get("success"):
                                    # Step 3: Verify with mock signature to get JWT
                                    verify_payload = {
                                        "challenge_hash": challenge_data.get("challenge_hash"),
                                        "signature": "mock_signature_autoplay_test",
                                        "wallet_address": self.test_wallet,
                                        "network": "solana"
                                    }
                                    
                                    async with self.session.post(f"{self.base_url}/auth/verify", 
                                                               json=verify_payload) as verify_response:
                                        if verify_response.status == 200:
                                            verify_data = await verify_response.json()
                                            if verify_data.get("success"):
                                                self.auth_token = verify_data.get("token")
                                                self.log_test("User Authentication", True, 
                                                            f"✅ User '{self.test_user}' authenticated with JWT token for AutoPlay", verify_data)
                                                return True
                        
                        self.log_test("User Authentication", False, "Failed to get JWT token")
                    else:
                        self.log_test("User Authentication", False, 
                                    f"Login failed: {data.get('message', 'Unknown error')}", data)
                else:
                    self.log_test("User Authentication", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
        return False
    
    async def test_wallet_balance_retrieval(self):
        """Test 2: Wallet Balance Management - Test balance retrieval for AutoPlay"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.test_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        balances = {
                            "deposit": wallet.get("deposit_balance", {}),
                            "winnings": wallet.get("winnings_balance", {}),
                            "savings": wallet.get("savings_balance", {})
                        }
                        
                        # Check if user has sufficient balance for AutoPlay
                        total_crt = sum([
                            balances["deposit"].get("CRT", 0),
                            balances["winnings"].get("CRT", 0)
                        ])
                        
                        self.log_test("Wallet Balance Retrieval", True, 
                                    f"✅ Wallet balances retrieved - CRT: {total_crt}, Savings: {balances['savings'].get('CRT', 0)}", data)
                        return balances
                    else:
                        self.log_test("Wallet Balance Retrieval", False, 
                                    "Invalid wallet response format", data)
                else:
                    self.log_test("Wallet Balance Retrieval", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Wallet Balance Retrieval", False, f"Error: {str(e)}")
        return None
    
    async def test_game_betting_all_types(self):
        """Test 3: Game Betting System - Test all 6 game types for AutoPlay"""
        if not self.auth_token:
            self.log_test("Game Betting System Status", False, "No authentication token available")
            return [], []
            
        game_types = ["Slot Machine", "Dice", "Roulette", "Plinko", "Keno", "Mines"]
        successful_games = []
        failed_games = []
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        for game_type in game_types:
            try:
                bet_payload = {
                    "wallet_address": self.test_wallet,
                    "game_type": game_type,
                    "bet_amount": 10.0,  # Small test bet
                    "currency": "CRT",
                    "network": "solana"
                }
                
                async with self.session.post(f"{self.base_url}/games/bet", 
                                           json=bet_payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        required_fields = ["success", "game_id", "result", "payout", "savings_contribution", "liquidity_added"]
                        
                        if all(field in data for field in required_fields) and data.get("success"):
                            result = data.get("result")
                            payout = data.get("payout", 0)
                            savings = data.get("savings_contribution", 0)
                            liquidity = data.get("liquidity_added", 0)
                            
                            successful_games.append({
                                "game": game_type,
                                "result": result,
                                "payout": payout,
                                "savings": savings,
                                "liquidity": liquidity
                            })
                            
                            self.log_test(f"Game Betting - {game_type}", True, 
                                        f"✅ {result.upper()}: payout={payout}, savings={savings}, liquidity={liquidity}", data)
                        else:
                            failed_games.append(game_type)
                            self.log_test(f"Game Betting - {game_type}", False, 
                                        "Invalid bet response format", data)
                    else:
                        failed_games.append(game_type)
                        self.log_test(f"Game Betting - {game_type}", False, 
                                    f"HTTP {response.status}: {await response.text()}")
                        
                # Small delay between bets
                await asyncio.sleep(0.5)
                
            except Exception as e:
                failed_games.append(game_type)
                self.log_test(f"Game Betting - {game_type}", False, f"Error: {str(e)}")
        
        # Overall assessment
        success_rate = len(successful_games) / len(game_types) * 100
        if success_rate >= 80:  # At least 80% of games should work
            self.log_test("Game Betting System Status", True, 
                        f"✅ {len(successful_games)}/{len(game_types)} games working ({success_rate:.1f}%)", 
                        {"successful": successful_games, "failed": failed_games})
        else:
            self.log_test("Game Betting System Status", False, 
                        f"❌ Only {len(successful_games)}/{len(game_types)} games working ({success_rate:.1f}%)", 
                        {"successful": successful_games, "failed": failed_games})
        
        return successful_games, failed_games
    
    async def test_api_response_format(self):
        """Test 4: API Response Format - Ensure responses include all required fields for AutoPlay"""
        if not self.auth_token:
            self.log_test("API Response Format", False, "No authentication token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            bet_payload = {
                "wallet_address": self.test_wallet,
                "game_type": "Slot Machine",
                "bet_amount": 5.0,
                "currency": "CRT",
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/games/bet", 
                                       json=bet_payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check all required fields for AutoPlay system
                    required_fields = [
                        "success", "game_id", "bet_amount", "currency", 
                        "result", "payout", "savings_contribution", "liquidity_added"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        # Validate field types and values
                        validations = []
                        
                        if isinstance(data.get("success"), bool):
                            validations.append("success: bool ✓")
                        else:
                            validations.append("success: bool ✗")
                            
                        if isinstance(data.get("bet_amount"), (int, float)) and data.get("bet_amount") > 0:
                            validations.append("bet_amount: number ✓")
                        else:
                            validations.append("bet_amount: number ✗")
                            
                        if data.get("result") in ["win", "loss"]:
                            validations.append("result: win/loss ✓")
                        else:
                            validations.append("result: win/loss ✗")
                            
                        if isinstance(data.get("payout"), (int, float)) and data.get("payout") >= 0:
                            validations.append("payout: number ✓")
                        else:
                            validations.append("payout: number ✗")
                        
                        all_valid = all("✓" in v for v in validations)
                        
                        self.log_test("API Response Format", all_valid, 
                                    f"Response format validation: {', '.join(validations)}", data)
                    else:
                        self.log_test("API Response Format", False, 
                                    f"Missing required fields: {missing_fields}", data)
                else:
                    self.log_test("API Response Format", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("API Response Format", False, f"Error: {str(e)}")
    
    async def test_high_volume_betting_simulation(self):
        """Test 5: High-Volume Betting Simulation - Test rapid successive bets for AutoPlay"""
        if not self.auth_token:
            self.log_test("High-Volume Betting Simulation", False, "No authentication token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            bet_count = 10  # Number of rapid bets to simulate
            bet_results = []
            start_time = time.time()
            
            print(f"🚀 Starting high-volume betting simulation ({bet_count} rapid bets)...")
            
            for i in range(bet_count):
                bet_payload = {
                    "wallet_address": self.test_wallet,
                    "game_type": "Dice",  # Use Dice for consistent testing
                    "bet_amount": 5.0,
                    "currency": "CRT",
                    "network": "solana"
                }
                
                try:
                    async with self.session.post(f"{self.base_url}/games/bet", 
                                               json=bet_payload, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("success"):
                                bet_results.append({
                                    "bet_number": i + 1,
                                    "result": data.get("result"),
                                    "payout": data.get("payout", 0),
                                    "response_time": time.time() - start_time
                                })
                            else:
                                bet_results.append({
                                    "bet_number": i + 1,
                                    "error": "Bet not successful",
                                    "response_time": time.time() - start_time
                                })
                        else:
                            bet_results.append({
                                "bet_number": i + 1,
                                "error": f"HTTP {response.status}",
                                "response_time": time.time() - start_time
                            })
                except Exception as bet_error:
                    bet_results.append({
                        "bet_number": i + 1,
                        "error": str(bet_error),
                        "response_time": time.time() - start_time
                    })
                
                # Small delay to prevent overwhelming the server
                await asyncio.sleep(0.1)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Analyze results
            successful_bets = [r for r in bet_results if "error" not in r]
            failed_bets = [r for r in bet_results if "error" in r]
            
            success_rate = len(successful_bets) / bet_count * 100
            avg_response_time = sum(r["response_time"] for r in successful_bets) / len(successful_bets) if successful_bets else 0
            
            if success_rate >= 90 and avg_response_time < 2.0:  # 90% success rate, under 2s avg response
                self.log_test("High-Volume Betting Simulation", True, 
                            f"✅ {len(successful_bets)}/{bet_count} bets successful ({success_rate:.1f}%), avg response: {avg_response_time:.2f}s", 
                            {
                                "total_bets": bet_count,
                                "successful": len(successful_bets),
                                "failed": len(failed_bets),
                                "success_rate": success_rate,
                                "total_time": total_time,
                                "avg_response_time": avg_response_time,
                                "results": bet_results
                            })
            else:
                self.log_test("High-Volume Betting Simulation", False, 
                            f"❌ {len(successful_bets)}/{bet_count} bets successful ({success_rate:.1f}%), avg response: {avg_response_time:.2f}s", 
                            {
                                "total_bets": bet_count,
                                "successful": len(successful_bets),
                                "failed": len(failed_bets),
                                "success_rate": success_rate,
                                "total_time": total_time,
                                "avg_response_time": avg_response_time,
                                "results": bet_results
                            })
            
        except Exception as e:
            self.log_test("High-Volume Betting Simulation", False, f"Error: {str(e)}")
    
    async def test_game_result_processing(self):
        """Test 6: Game Result Processing - Verify wins/losses update savings/liquidity correctly"""
        try:
            # Get initial balances
            initial_balances = await self.test_wallet_balance_retrieval()
            if not initial_balances:
                self.log_test("Game Result Processing", False, "Could not retrieve initial balances")
                return
            
            initial_savings = initial_balances["savings"].get("CRT", 0)
            
            # Place a bet that should result in a loss (to test savings update)
            bet_payload = {
                "wallet_address": self.test_wallet,
                "game_type": "Slot Machine",  # Lower win rate
                "bet_amount": 20.0,
                "currency": "CRT",
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/games/bet", 
                                       json=bet_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        result = data.get("result")
                        bet_amount = data.get("bet_amount", 0)
                        savings_contribution = data.get("savings_contribution", 0)
                        liquidity_added = data.get("liquidity_added", 0)
                        
                        # Wait a moment for database update
                        await asyncio.sleep(1)
                        
                        # Get updated balances
                        updated_balances = await self.test_wallet_balance_retrieval()
                        if updated_balances:
                            updated_savings = updated_balances["savings"].get("CRT", 0)
                            
                            if result == "loss":
                                # For losses, savings should increase
                                expected_savings_increase = bet_amount
                                actual_savings_increase = updated_savings - initial_savings
                                
                                if abs(actual_savings_increase - expected_savings_increase) < 0.01:  # Allow small floating point differences
                                    self.log_test("Game Result Processing", True, 
                                                f"✅ Loss processing correct: bet={bet_amount}, savings_increase={actual_savings_increase}, liquidity_added={liquidity_added}", 
                                                {
                                                    "result": result,
                                                    "bet_amount": bet_amount,
                                                    "initial_savings": initial_savings,
                                                    "updated_savings": updated_savings,
                                                    "savings_increase": actual_savings_increase,
                                                    "expected_increase": expected_savings_increase,
                                                    "liquidity_added": liquidity_added
                                                })
                                else:
                                    self.log_test("Game Result Processing", False, 
                                                f"❌ Savings update incorrect: expected +{expected_savings_increase}, got +{actual_savings_increase}", 
                                                {
                                                    "result": result,
                                                    "expected_increase": expected_savings_increase,
                                                    "actual_increase": actual_savings_increase
                                                })
                            else:
                                # For wins, just verify the system processed correctly
                                payout = data.get("payout", 0)
                                self.log_test("Game Result Processing", True, 
                                            f"✅ Win processing correct: bet={bet_amount}, payout={payout}", 
                                            {
                                                "result": result,
                                                "bet_amount": bet_amount,
                                                "payout": payout
                                            })
                        else:
                            self.log_test("Game Result Processing", False, "Could not retrieve updated balances")
                    else:
                        self.log_test("Game Result Processing", False, "Bet was not successful", data)
                else:
                    self.log_test("Game Result Processing", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Game Result Processing", False, f"Error: {str(e)}")
    
    async def test_autoplay_endpoints(self):
        """Test 7: AutoPlay Endpoints - Test start/stop/status endpoints"""
        try:
            # Test AutoPlay start endpoint
            autoplay_settings = {
                "wallet_address": self.test_wallet,
                "settings": {
                    "games": ["Slot Machine", "Dice"],
                    "currency": "CRT",
                    "crt_bet": 10,
                    "max_loss": 1000,
                    "max_duration": 1,  # 1 hour
                    "bet_frequency": 10  # 10 seconds between bets
                }
            }
            
            async with self.session.post(f"{self.base_url}/autoplay/start", 
                                       json=autoplay_settings) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        session_id = data.get("session_id")
                        self.log_test("AutoPlay Start", True, 
                                    f"✅ AutoPlay session started: {session_id}", data)
                        
                        # Test AutoPlay status endpoint
                        await asyncio.sleep(1)
                        async with self.session.get(f"{self.base_url}/autoplay/status/{self.test_wallet}") as status_response:
                            if status_response.status == 200:
                                status_data = await status_response.json()
                                if status_data.get("success"):
                                    active_sessions = status_data.get("active_sessions", 0)
                                    self.log_test("AutoPlay Status", True, 
                                                f"✅ AutoPlay status retrieved: {active_sessions} active sessions", status_data)
                                else:
                                    self.log_test("AutoPlay Status", False, "AutoPlay status not successful", status_data)
                            else:
                                self.log_test("AutoPlay Status", False, 
                                            f"HTTP {status_response.status}: {await status_response.text()}")
                        
                        # Test AutoPlay stop endpoint
                        stop_payload = {"wallet_address": self.test_wallet}
                        async with self.session.post(f"{self.base_url}/autoplay/stop", 
                                                   json=stop_payload) as stop_response:
                            if stop_response.status == 200:
                                stop_data = await stop_response.json()
                                if stop_data.get("success"):
                                    sessions_stopped = stop_data.get("sessions_stopped", 0)
                                    self.log_test("AutoPlay Stop", True, 
                                                f"✅ AutoPlay stopped: {sessions_stopped} sessions stopped", stop_data)
                                else:
                                    self.log_test("AutoPlay Stop", False, "AutoPlay stop not successful", stop_data)
                            else:
                                self.log_test("AutoPlay Stop", False, 
                                            f"HTTP {stop_response.status}: {await stop_response.text()}")
                    else:
                        self.log_test("AutoPlay Start", False, "AutoPlay start not successful", data)
                else:
                    self.log_test("AutoPlay Start", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("AutoPlay Endpoints", False, f"Error: {str(e)}")
    
    async def test_autoplay_bet_processing(self):
        """Test 8: AutoPlay Bet Processing - Test the automated bet processing endpoint"""
        try:
            # First start an AutoPlay session
            autoplay_settings = {
                "wallet_address": self.test_wallet,
                "settings": {
                    "games": ["Dice"],
                    "currency": "CRT",
                    "crt_bet": 5,
                    "max_loss": 100,
                    "max_duration": 1,
                    "bet_frequency": 1  # 1 second for quick testing
                }
            }
            
            async with self.session.post(f"{self.base_url}/autoplay/start", 
                                       json=autoplay_settings) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        # Wait a moment then test the bet processing
                        await asyncio.sleep(2)
                        
                        async with self.session.post(f"{self.base_url}/autoplay/process-bets") as process_response:
                            if process_response.status == 200:
                                process_data = await process_response.json()
                                if process_data.get("success"):
                                    processed_bets = process_data.get("processed_bets", 0)
                                    self.log_test("AutoPlay Bet Processing", True, 
                                                f"✅ AutoPlay bet processing working: {processed_bets} bets processed", process_data)
                                else:
                                    self.log_test("AutoPlay Bet Processing", False, 
                                                "AutoPlay bet processing not successful", process_data)
                            else:
                                self.log_test("AutoPlay Bet Processing", False, 
                                            f"HTTP {process_response.status}: {await process_response.text()}")
                        
                        # Stop the session
                        stop_payload = {"wallet_address": self.test_wallet}
                        await self.session.post(f"{self.base_url}/autoplay/stop", json=stop_payload)
                    else:
                        self.log_test("AutoPlay Bet Processing", False, "Could not start AutoPlay session for testing")
                else:
                    self.log_test("AutoPlay Bet Processing", False, "Could not start AutoPlay session for testing")
        except Exception as e:
            self.log_test("AutoPlay Bet Processing", False, f"Error: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*80)
        print("🎰 AI AUTO-PLAY BACKEND TESTING SUMMARY")
        print("="*80)
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print("="*80)
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
        
        print(f"\n🎯 AUTOPLAY READINESS: {'✅ READY' if success_rate >= 80 else '❌ NOT READY'}")
        print("="*80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "autoplay_ready": success_rate >= 80
        }

async def run_autoplay_tests():
    """Run all AutoPlay tests"""
    print("🚀 Starting AI Auto-Play Backend Testing Suite...")
    print("="*80)
    
    async with AutoPlayTester(BACKEND_URL) as tester:
        # Run all tests in sequence
        await tester.test_user_authentication()
        await tester.test_wallet_balance_retrieval()
        await tester.test_game_betting_all_types()
        await tester.test_api_response_format()
        await tester.test_high_volume_betting_simulation()
        await tester.test_game_result_processing()
        await tester.test_autoplay_endpoints()
        await tester.test_autoplay_bet_processing()
        
        # Print summary
        summary = tester.print_summary()
        return summary

if __name__ == "__main__":
    asyncio.run(run_autoplay_tests())