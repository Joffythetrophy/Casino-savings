#!/usr/bin/env python3
"""
Casino Savings dApp - Game Betting System Test
Focus on testing different game types as requested in the review
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://tiger-dex-casino.preview.emergentagent.com/api"

class GameBettingTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"  # User's wallet
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", response_data=None):
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
        """Authenticate with the specific user credentials"""
        try:
            # Login with the specific user credentials
            login_payload = {
                "username": "cryptoking",
                "password": "crt21million"
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        print(f"✅ Authenticated as user: {data.get('username')} (wallet: {data.get('wallet_address')})")
                        return True
                    else:
                        print(f"❌ Authentication failed: {data.get('message')}")
                        return False
                else:
                    print(f"❌ Authentication failed: HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    async def get_wallet_auth_token(self):
        """Get wallet authentication token for API calls"""
        try:
            # Generate challenge
            challenge_payload = {
                "wallet_address": self.test_wallet,
                "network": "solana"
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/challenge", 
                                       json=challenge_payload) as response:
                if response.status == 200:
                    challenge_data = await response.json()
                    if challenge_data.get("success"):
                        # Verify with mock signature
                        verify_payload = {
                            "challenge_hash": challenge_data.get("challenge_hash"),
                            "signature": "mock_signature_for_game_testing",
                            "wallet_address": self.test_wallet,
                            "network": "solana"
                        }
                        
                        async with self.session.post(f"{BACKEND_URL}/auth/verify", 
                                                   json=verify_payload) as verify_response:
                            if verify_response.status == 200:
                                verify_data = await verify_response.json()
                                if verify_data.get("success"):
                                    self.auth_token = verify_data.get("token")
                                    print(f"✅ Got wallet auth token")
                                    return True
                                    
            print("❌ Failed to get wallet auth token")
            return False
        except Exception as e:
            print(f"❌ Wallet auth error: {str(e)}")
            return False
    
    async def test_game_betting(self, game_type: str, bet_amount: float = 10.0, currency: str = "CRT"):
        """Test betting on a specific game type"""
        if not self.auth_token:
            self.log_test(f"Game Betting - {game_type}", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            bet_payload = {
                "wallet_address": self.test_wallet,
                "game_type": game_type,
                "bet_amount": bet_amount,
                "currency": currency,
                "network": "solana"
            }
            
            async with self.session.post(f"{BACKEND_URL}/games/bet", 
                                       json=bet_payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "game_id", "bet_amount", "currency", "result", "payout"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        result = data.get("result")
                        payout = data.get("payout", 0)
                        savings_contribution = data.get("savings_contribution", 0)
                        liquidity_added = data.get("liquidity_added", 0)
                        message = data.get("message", "")
                        
                        # Check if this is real game logic
                        if result in ["win", "loss"] and isinstance(payout, (int, float)):
                            details = f"Result: {result}, Payout: {payout} {currency}, Savings: {savings_contribution}, Liquidity: {liquidity_added}"
                            if message:
                                details += f" | {message}"
                            
                            self.log_test(f"Game Betting - {game_type}", True, details, data)
                        else:
                            self.log_test(f"Game Betting - {game_type}", False, 
                                        "Invalid game result format", data)
                    else:
                        self.log_test(f"Game Betting - {game_type}", False, 
                                    "Invalid bet response format", data)
                else:
                    error_text = await response.text()
                    self.log_test(f"Game Betting - {game_type}", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test(f"Game Betting - {game_type}", False, f"Error: {str(e)}")
    
    async def test_wallet_balance_management(self):
        """Test wallet balance retrieval and management"""
        try:
            # Test getting wallet info
            async with self.session.get(f"{BACKEND_URL}/wallet/{self.test_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        winnings_balance = wallet.get("winnings_balance", {})
                        savings_balance = wallet.get("savings_balance", {})
                        
                        balance_info = []
                        for currency in ["CRT", "DOGE", "TRX", "USDC"]:
                            deposit = deposit_balance.get(currency, 0)
                            winnings = winnings_balance.get(currency, 0)
                            savings = savings_balance.get(currency, 0)
                            total = deposit + winnings
                            balance_info.append(f"{currency}: {total} (D:{deposit}, W:{winnings}, S:{savings})")
                        
                        self.log_test("Wallet Balance Management", True, 
                                    f"Wallet balances retrieved: {', '.join(balance_info)}", data)
                    else:
                        self.log_test("Wallet Balance Management", False, 
                                    "Invalid wallet response format", data)
                else:
                    error_text = await response.text()
                    self.log_test("Wallet Balance Management", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Wallet Balance Management", False, f"Error: {str(e)}")
    
    async def test_savings_tracking(self):
        """Test savings tracking from game losses"""
        if not self.auth_token:
            self.log_test("Savings Tracking", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(f"{BACKEND_URL}/savings/{self.test_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        total_savings = data.get("total_savings", {})
                        stats = data.get("stats", {})
                        savings_history = data.get("savings_history", [])
                        total_usd = data.get("total_usd", 0)
                        
                        # Format savings info
                        savings_info = []
                        for currency, amount in total_savings.items():
                            if amount > 0:
                                savings_info.append(f"{currency}: {amount}")
                        
                        details = f"Total savings: {', '.join(savings_info) if savings_info else 'None'}, "
                        details += f"USD value: ${total_usd:.2f}, "
                        details += f"Games: {stats.get('total_games', 0)}, "
                        details += f"Losses: {stats.get('total_losses', 0)}, "
                        details += f"Win rate: {stats.get('win_rate', 0):.1f}%, "
                        details += f"History entries: {len(savings_history)}"
                        
                        self.log_test("Savings Tracking", True, details, data)
                    else:
                        self.log_test("Savings Tracking", False, 
                                    "Invalid savings response", data)
                else:
                    error_text = await response.text()
                    self.log_test("Savings Tracking", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Savings Tracking", False, f"Error: {str(e)}")
    
    async def test_backend_health(self):
        """Test backend service health"""
        try:
            async with self.session.get(f"{BACKEND_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get("status", "unknown")
                    services = data.get("services", {})
                    
                    # Check service health
                    healthy_services = []
                    degraded_services = []
                    
                    for service, health in services.items():
                        if health.get("success"):
                            healthy_services.append(service)
                        else:
                            degraded_services.append(f"{service}: {health.get('error', 'unknown error')}")
                    
                    details = f"Status: {status}, "
                    details += f"Healthy: {', '.join(healthy_services) if healthy_services else 'None'}"
                    if degraded_services:
                        details += f", Issues: {', '.join(degraded_services)}"
                    
                    success = status in ["healthy", "degraded"] and len(healthy_services) > 0
                    self.log_test("Backend Health Check", success, details, data)
                else:
                    error_text = await response.text()
                    self.log_test("Backend Health Check", False, 
                                f"HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Error: {str(e)}")
    
    async def run_all_tests(self):
        """Run all game betting tests"""
        print("🎰 Starting Casino Savings dApp Game Betting Tests")
        print(f"📡 Testing against: {BACKEND_URL}")
        print(f"👤 User: cryptoking (wallet: {self.test_wallet})")
        print("=" * 70)
        
        # Step 1: Authenticate user
        if not await self.authenticate_user():
            print("❌ Cannot proceed without authentication")
            return
        
        # Step 2: Get wallet auth token
        if not await self.get_wallet_auth_token():
            print("❌ Cannot proceed without wallet auth token")
            return
        
        # Step 3: Test backend health
        await self.test_backend_health()
        
        # Step 4: Test wallet balance management
        await self.test_wallet_balance_management()
        
        # Step 5: Test different game types
        print("\n🎮 TESTING GAME BETTING FUNCTIONALITY")
        print("=" * 50)
        
        game_types = [
            "Slot Machine",
            "Dice", 
            "Roulette",
            "Plinko",
            "Keno",
            "Mines"
        ]
        
        for game_type in game_types:
            await self.test_game_betting(game_type, bet_amount=5.0, currency="CRT")
            await asyncio.sleep(0.5)  # Small delay between bets
        
        # Step 6: Test savings tracking
        await self.test_savings_tracking()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 GAME BETTING TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n🚨 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        print(f"\n📄 Detailed results saved to: /app/game_betting_test_results.json")
        
        # Save results to file
        with open("/app/game_betting_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)

async def main():
    async with GameBettingTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())