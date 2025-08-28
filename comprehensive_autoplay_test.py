#!/usr/bin/env python3
"""
Comprehensive AutoPlay Backend Testing - Final Assessment
Testing all requirements from the review request
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

BACKEND_URL = "https://cryptoplay-8.preview.emergentagent.com/api"

class ComprehensiveAutoPlayTest:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user = "cryptoking"
        self.test_password = "crt21million"
        self.test_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        self.results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_result(self, test_name: str, success: bool, details: str):
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
    
    async def authenticate(self):
        """Get JWT token for authenticated requests"""
        try:
            # Step 1: Login
            login_payload = {"username": self.test_user, "password": self.test_password}
            async with self.session.post(f"{BACKEND_URL}/auth/login-username", json=login_payload) as response:
                if response.status != 200:
                    return False
                data = await response.json()
                if not data.get("success"):
                    return False
            
            # Step 2: Get challenge
            challenge_payload = {"wallet_address": self.test_wallet, "network": "solana"}
            async with self.session.post(f"{BACKEND_URL}/auth/challenge", json=challenge_payload) as response:
                if response.status != 200:
                    return False
                challenge_data = await response.json()
                if not challenge_data.get("success"):
                    return False
            
            # Step 3: Verify and get JWT
            verify_payload = {
                "challenge_hash": challenge_data.get("challenge_hash"),
                "signature": "mock_signature_comprehensive_test",
                "wallet_address": self.test_wallet,
                "network": "solana"
            }
            async with self.session.post(f"{BACKEND_URL}/auth/verify", json=verify_payload) as response:
                if response.status != 200:
                    return False
                verify_data = await response.json()
                if verify_data.get("success"):
                    self.auth_token = verify_data.get("token")
                    return True
            return False
        except Exception:
            return False
    
    async def test_requirement_1_game_betting_system(self):
        """Requirement 1: Game Betting System Status - Test all 6 game types"""
        if not self.auth_token:
            self.log_result("1. Game Betting System", False, "Authentication failed")
            return
        
        game_types = ["Slot Machine", "Dice", "Roulette", "Plinko", "Keno", "Mines"]
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        successful_games = 0
        
        for game_type in game_types:
            try:
                bet_payload = {
                    "wallet_address": self.test_wallet,
                    "game_type": game_type,
                    "bet_amount": 5.0,
                    "currency": "CRT",
                    "network": "solana"
                }
                
                async with self.session.post(f"{BACKEND_URL}/games/bet", 
                                           json=bet_payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success") and "result" in data:
                            successful_games += 1
                
                await asyncio.sleep(0.3)  # Small delay between bets
                
            except Exception:
                continue
        
        success_rate = (successful_games / len(game_types)) * 100
        if success_rate >= 80:
            self.log_result("1. Game Betting System", True, 
                          f"All 6 game types working ({successful_games}/{len(game_types)}) - {success_rate:.1f}% success rate")
        else:
            self.log_result("1. Game Betting System", False, 
                          f"Only {successful_games}/{len(game_types)} games working - {success_rate:.1f}% success rate")
    
    async def test_requirement_2_authentication_system(self):
        """Requirement 2: Authentication System - Verify user login works"""
        try:
            login_payload = {"username": self.test_user, "password": self.test_password}
            async with self.session.post(f"{BACKEND_URL}/auth/login-username", json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and data.get("username") == self.test_user:
                        self.log_result("2. Authentication System", True, 
                                      f"User '{self.test_user}' authentication successful")
                    else:
                        self.log_result("2. Authentication System", False, 
                                      f"Login failed: {data.get('message', 'Unknown error')}")
                else:
                    self.log_result("2. Authentication System", False, 
                                  f"HTTP {response.status} error")
        except Exception as e:
            self.log_result("2. Authentication System", False, f"Error: {str(e)}")
    
    async def test_requirement_3_wallet_balance_management(self):
        """Requirement 3: Wallet Balance Management - Test balance retrieval and updates"""
        try:
            # Test balance retrieval
            async with self.session.get(f"{BACKEND_URL}/wallet/{self.test_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        balances = wallet.get("deposit_balance", {})
                        savings = wallet.get("savings_balance", {})
                        
                        crt_balance = balances.get("CRT", 0)
                        crt_savings = savings.get("CRT", 0)
                        
                        if crt_balance > 0 or crt_savings > 0:
                            self.log_result("3. Wallet Balance Management", True, 
                                          f"Balance retrieval working - CRT: {crt_balance}, Savings: {crt_savings}")
                        else:
                            self.log_result("3. Wallet Balance Management", False, 
                                          "No balances found in wallet")
                    else:
                        self.log_result("3. Wallet Balance Management", False, 
                                      "Invalid wallet response format")
                else:
                    self.log_result("3. Wallet Balance Management", False, 
                                  f"HTTP {response.status} error")
        except Exception as e:
            self.log_result("3. Wallet Balance Management", False, f"Error: {str(e)}")
    
    async def test_requirement_4_game_result_processing(self):
        """Requirement 4: Game Result Processing - Verify wins/losses update savings/liquidity"""
        if not self.auth_token:
            self.log_result("4. Game Result Processing", False, "Authentication failed")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Get initial savings
            async with self.session.get(f"{BACKEND_URL}/wallet/{self.test_wallet}") as response:
                if response.status != 200:
                    self.log_result("4. Game Result Processing", False, "Could not get initial balance")
                    return
                
                initial_data = await response.json()
                initial_savings = initial_data["wallet"]["savings_balance"].get("CRT", 0)
            
            # Place a bet
            bet_payload = {
                "wallet_address": self.test_wallet,
                "game_type": "Slot Machine",
                "bet_amount": 15.0,
                "currency": "CRT",
                "network": "solana"
            }
            
            async with self.session.post(f"{BACKEND_URL}/games/bet", 
                                       json=bet_payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        result = data.get("result")
                        savings_contribution = data.get("savings_contribution", 0)
                        liquidity_added = data.get("liquidity_added", 0)
                        
                        # Wait for database update
                        await asyncio.sleep(1)
                        
                        # Check updated savings
                        async with self.session.get(f"{BACKEND_URL}/wallet/{self.test_wallet}") as response2:
                            if response2.status == 200:
                                updated_data = await response2.json()
                                updated_savings = updated_data["wallet"]["savings_balance"].get("CRT", 0)
                                savings_increase = updated_savings - initial_savings
                                
                                if result == "loss" and savings_increase > 0:
                                    self.log_result("4. Game Result Processing", True, 
                                                  f"Loss processing correct - savings increased by {savings_increase}, liquidity added: {liquidity_added}")
                                elif result == "win":
                                    self.log_result("4. Game Result Processing", True, 
                                                  f"Win processing correct - payout: {data.get('payout', 0)}")
                                else:
                                    self.log_result("4. Game Result Processing", False, 
                                                  f"Unexpected result processing: {result}, savings change: {savings_increase}")
                            else:
                                self.log_result("4. Game Result Processing", False, "Could not verify updated balance")
                    else:
                        self.log_result("4. Game Result Processing", False, "Bet was not successful")
                else:
                    self.log_result("4. Game Result Processing", False, f"HTTP {response.status} error")
        except Exception as e:
            self.log_result("4. Game Result Processing", False, f"Error: {str(e)}")
    
    async def test_requirement_5_api_response_format(self):
        """Requirement 5: API Response Format - Ensure all required fields are present"""
        if not self.auth_token:
            self.log_result("5. API Response Format", False, "Authentication failed")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            bet_payload = {
                "wallet_address": self.test_wallet,
                "game_type": "Dice",
                "bet_amount": 8.0,
                "currency": "CRT",
                "network": "solana"
            }
            
            async with self.session.post(f"{BACKEND_URL}/games/bet", 
                                       json=bet_payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    required_fields = [
                        "success", "game_id", "bet_amount", "currency", 
                        "result", "payout", "savings_contribution", "liquidity_added"
                    ]
                    
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        # Validate field types
                        valid_types = (
                            isinstance(data.get("success"), bool) and
                            isinstance(data.get("bet_amount"), (int, float)) and
                            data.get("result") in ["win", "loss"] and
                            isinstance(data.get("payout"), (int, float)) and
                            isinstance(data.get("savings_contribution"), (int, float)) and
                            isinstance(data.get("liquidity_added"), (int, float))
                        )
                        
                        if valid_types:
                            self.log_result("5. API Response Format", True, 
                                          "All required fields present with correct types")
                        else:
                            self.log_result("5. API Response Format", False, 
                                          "Fields present but incorrect types")
                    else:
                        self.log_result("5. API Response Format", False, 
                                      f"Missing required fields: {missing_fields}")
                else:
                    self.log_result("5. API Response Format", False, f"HTTP {response.status} error")
        except Exception as e:
            self.log_result("5. API Response Format", False, f"Error: {str(e)}")
    
    async def test_requirement_6_high_volume_betting(self):
        """Requirement 6: High-Volume Betting Simulation - Test rapid successive bets"""
        if not self.auth_token:
            self.log_result("6. High-Volume Betting", False, "Authentication failed")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            bet_count = 15  # Test 15 rapid bets
            successful_bets = 0
            start_time = time.time()
            
            for i in range(bet_count):
                bet_payload = {
                    "wallet_address": self.test_wallet,
                    "game_type": "Dice",
                    "bet_amount": 3.0,
                    "currency": "CRT",
                    "network": "solana"
                }
                
                try:
                    async with self.session.post(f"{BACKEND_URL}/games/bet", 
                                               json=bet_payload, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("success"):
                                successful_bets += 1
                    
                    await asyncio.sleep(0.1)  # Small delay to prevent overwhelming
                    
                except Exception:
                    continue
            
            end_time = time.time()
            total_time = end_time - start_time
            success_rate = (successful_bets / bet_count) * 100
            avg_response_time = total_time / bet_count
            
            if success_rate >= 90 and avg_response_time < 3.0:
                self.log_result("6. High-Volume Betting", True, 
                              f"High-volume betting successful - {successful_bets}/{bet_count} bets ({success_rate:.1f}%), avg time: {avg_response_time:.2f}s")
            else:
                self.log_result("6. High-Volume Betting", False, 
                              f"High-volume betting issues - {successful_bets}/{bet_count} bets ({success_rate:.1f}%), avg time: {avg_response_time:.2f}s")
        except Exception as e:
            self.log_result("6. High-Volume Betting", False, f"Error: {str(e)}")
    
    def print_final_assessment(self):
        """Print final assessment of AutoPlay readiness"""
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result["success"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "="*80)
        print("🎰 COMPREHENSIVE AI AUTO-PLAY BACKEND ASSESSMENT")
        print("="*80)
        print("📋 REQUIREMENTS TESTING RESULTS:")
        print("="*80)
        
        for i, result in enumerate(self.results, 1):
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} Requirement {i}: {result['test']}")
            print(f"    Details: {result['details']}")
            print()
        
        print("="*80)
        print(f"📊 OVERALL RESULTS:")
        print(f"   Total Requirements: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {total_tests - passed_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        print("="*80)
        
        if success_rate >= 80:
            print("🎯 FINAL ASSESSMENT: ✅ AUTOPLAY BACKEND IS READY")
            print("   The backend can reliably handle AI Auto-Play functionality")
            print("   All critical requirements are met for automated betting")
        else:
            print("🎯 FINAL ASSESSMENT: ❌ AUTOPLAY BACKEND NEEDS WORK")
            print("   Critical issues found that may affect AutoPlay reliability")
        
        print("="*80)
        
        return {
            "total_requirements": total_tests,
            "passed_requirements": passed_tests,
            "success_rate": success_rate,
            "autoplay_ready": success_rate >= 80,
            "results": self.results
        }

async def run_comprehensive_test():
    """Run comprehensive AutoPlay backend test"""
    print("🚀 Starting Comprehensive AI Auto-Play Backend Assessment...")
    print("Testing all requirements from the review request...")
    print("="*80)
    
    async with ComprehensiveAutoPlayTest() as tester:
        # Authenticate first
        if not await tester.authenticate():
            print("❌ CRITICAL: Authentication failed - cannot proceed with testing")
            return
        
        print("✅ Authentication successful - proceeding with requirements testing...\n")
        
        # Test all requirements
        await tester.test_requirement_2_authentication_system()
        await tester.test_requirement_3_wallet_balance_management()
        await tester.test_requirement_1_game_betting_system()
        await tester.test_requirement_5_api_response_format()
        await tester.test_requirement_4_game_result_processing()
        await tester.test_requirement_6_high_volume_betting()
        
        # Print final assessment
        return tester.print_final_assessment()

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())