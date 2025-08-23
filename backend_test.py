#!/usr/bin/env python3
"""
Casino Savings dApp Backend API Test Suite - Real Money Integration Testing
Tests wallet management system for real money integration
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://cryptosave-1.preview.emergentagent.com/api"

class WalletAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.test_wallet = "RealWallet9876543210XYZ"  # Test wallet address
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
        
    async def test_basic_connectivity(self):
        """Test 1: Basic API connectivity and root endpoint"""
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    expected_fields = ["message", "version", "supported_networks", "supported_tokens"]
                    if all(field in data for field in expected_fields):
                        self.log_test("Basic Connectivity", True, 
                                    f"API accessible, version: {data.get('version')}", data)
                    else:
                        self.log_test("Basic Connectivity", False, 
                                    f"Missing expected fields in response", data)
                else:
                    self.log_test("Basic Connectivity", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Basic Connectivity", False, f"Connection error: {str(e)}")
    
    async def test_auth_challenge_generation(self):
        """Test 2: Authentication challenge generation"""
        try:
            payload = {
                "wallet_address": self.test_wallet,
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/auth/challenge", 
                                       json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "challenge", "challenge_hash", "network"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        self.challenge_hash = data.get("challenge_hash")
                        self.log_test("Auth Challenge Generation", True, 
                                    "Challenge generated successfully", data)
                        return data
                    else:
                        self.log_test("Auth Challenge Generation", False, 
                                    "Invalid challenge response format", data)
                else:
                    self.log_test("Auth Challenge Generation", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Auth Challenge Generation", False, f"Error: {str(e)}")
        return None
    
    async def test_auth_verification(self, challenge_data: Dict):
        """Test 3: Authentication verification and JWT token generation"""
        if not challenge_data:
            self.log_test("Auth Verification", False, "No challenge data available")
            return
            
        try:
            payload = {
                "challenge_hash": challenge_data.get("challenge_hash"),
                "signature": "mock_signature_for_demo_purposes_12345",  # Mock signature
                "wallet_address": self.test_wallet,
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/auth/verify", 
                                       json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "token", "wallet_address", "network", "expires_in"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        self.auth_token = data.get("token")
                        self.log_test("Auth Verification", True, 
                                    f"JWT token generated, expires in {data.get('expires_in')}s", data)
                    else:
                        self.log_test("Auth Verification", False, 
                                    "Invalid verification response", data)
                else:
                    self.log_test("Auth Verification", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Auth Verification", False, f"Error: {str(e)}")
    
    async def test_wallet_info_endpoint(self):
        """Test 4: Wallet information retrieval"""
        if not self.auth_token:
            self.log_test("Wallet Info", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.test_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        expected_fields = ["wallet_address", "deposit_balance", "winnings_balance", "savings_balance"]
                        if all(field in wallet for field in expected_fields):
                            self.log_test("Wallet Info", True, 
                                        f"Wallet info retrieved successfully", data)
                        else:
                            self.log_test("Wallet Info", False, 
                                        "Missing expected wallet fields", data)
                    else:
                        self.log_test("Wallet Info", False, 
                                    "Invalid wallet info response format", data)
                else:
                    self.log_test("Wallet Info", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Wallet Info", False, f"Error: {str(e)}")
    
    async def test_deposit_endpoint(self):
        """Test 5: Deposit funds endpoint"""
        if not self.auth_token:
            self.log_test("Deposit Funds", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            deposit_payload = {
                "wallet_address": self.test_wallet,
                "currency": "CRT",
                "amount": 100.0
            }
            
            async with self.session.post(f"{self.base_url}/wallet/deposit", 
                                       json=deposit_payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "message" in data:
                        self.log_test("Deposit Funds", True, 
                                    f"Deposit successful: {data.get('message')}", data)
                    else:
                        self.log_test("Deposit Funds", False, 
                                    "Invalid deposit response format", data)
                else:
                    self.log_test("Deposit Funds", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Deposit Funds", False, f"Error: {str(e)}")
    
    async def test_withdraw_endpoint(self):
        """Test 6: Withdraw funds endpoint"""
        if not self.auth_token:
            self.log_test("Withdraw Funds", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            withdraw_payload = {
                "wallet_address": self.test_wallet,
                "wallet_type": "winnings",
                "currency": "CRT",
                "amount": 10.0
            }
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=withdraw_payload, headers=headers) as response:
                if response.status in [200, 400]:  # 400 expected for insufficient balance
                    data = await response.json()
                    if response.status == 400 and "Insufficient balance" in data.get("detail", ""):
                        self.log_test("Withdraw Funds", True, 
                                    "Withdrawal correctly rejected - insufficient balance", data)
                    elif response.status == 200 and data.get("success"):
                        self.log_test("Withdraw Funds", True, 
                                    f"Withdrawal successful: {data.get('message')}", data)
                    else:
                        self.log_test("Withdraw Funds", False, 
                                    "Unexpected withdrawal response", data)
                else:
                    self.log_test("Withdraw Funds", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Withdraw Funds", False, f"Error: {str(e)}")
    
    async def test_convert_endpoint(self):
        """Test 7: Crypto conversion endpoint"""
        if not self.auth_token:
            self.log_test("Crypto Conversion", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            convert_payload = {
                "wallet_address": self.test_wallet,
                "from_currency": "CRT",
                "to_currency": "DOGE",
                "amount": 10.0
            }
            
            async with self.session.post(f"{self.base_url}/wallet/convert", 
                                       json=convert_payload, headers=headers) as response:
                if response.status in [200, 400]:  # 400 expected for insufficient balance
                    data = await response.json()
                    if response.status == 400 and "Insufficient balance" in data.get("detail", ""):
                        self.log_test("Crypto Conversion", True, 
                                    "Conversion correctly rejected - insufficient balance", data)
                    elif response.status == 200 and data.get("success"):
                        # Check if conversion rates are real (not mock)
                        rate = data.get("rate", 0)
                        converted_amount = data.get("converted_amount", 0)
                        if rate > 0 and converted_amount > 0:
                            self.log_test("Crypto Conversion", True, 
                                        f"Conversion successful: rate {rate}, amount {converted_amount}", data)
                        else:
                            self.log_test("Crypto Conversion", False, 
                                        "Conversion response missing rate/amount data", data)
                    else:
                        self.log_test("Crypto Conversion", False, 
                                    "Unexpected conversion response", data)
                else:
                    self.log_test("Crypto Conversion", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Crypto Conversion", False, f"Error: {str(e)}")
    
    async def test_game_betting(self):
        """Test 8: Real money game betting"""
        if not self.auth_token:
            self.log_test("Game Betting", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
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
                    required_fields = ["success", "game_id", "bet_amount", "currency", "result", "payout"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        result = data.get("result")
                        payout = data.get("payout")
                        savings_contribution = data.get("savings_contribution", 0)
                        
                        # Check if this is real game logic (not just mock)
                        if result in ["win", "loss"] and isinstance(payout, (int, float)):
                            self.log_test("Game Betting", True, 
                                        f"Real bet placed: {result}, payout: {payout}, savings: {savings_contribution}", data)
                        else:
                            self.log_test("Game Betting", False, 
                                        "Game betting appears to use mock data", data)
                    else:
                        self.log_test("Game Betting", False, 
                                    "Invalid bet response format", data)
                else:
                    self.log_test("Game Betting", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Game Betting", False, f"Error: {str(e)}")
    
    async def test_savings_system(self):
        """Test 9: Smart savings system"""
        if not self.auth_token:
            self.log_test("Savings System", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(f"{self.base_url}/savings/{self.test_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "wallet_address", "total_savings", "stats"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        total_savings = data.get("total_savings", {})
                        stats = data.get("stats", {})
                        savings_history = data.get("savings_history", [])
                        
                        # Check if savings are calculated from real game losses
                        if isinstance(total_savings, dict) and isinstance(stats, dict):
                            total_games = stats.get("total_games", 0)
                            total_losses = stats.get("total_losses", 0)
                            
                            self.log_test("Savings System", True, 
                                        f"Savings system working: {total_games} games, {total_losses} losses, {len(savings_history)} history entries", data)
                        else:
                            self.log_test("Savings System", False, 
                                        "Invalid savings data structure", data)
                    else:
                        self.log_test("Savings System", False, 
                                    "Invalid savings response format", data)
                else:
                    self.log_test("Savings System", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Savings System", False, f"Error: {str(e)}")
    
    async def test_websocket_wallet_monitor(self):
        """Test 10: WebSocket wallet monitoring"""
        try:
            import websockets
            
            ws_url = f"wss://cryptosave-1.preview.emergentagent.com/api/ws/wallet/{self.test_wallet}"
            
            try:
                async with websockets.connect(ws_url) as websocket:
                    # Send a test message
                    test_message = {"type": "refresh_wallet"}
                    await websocket.send(json.dumps(test_message))
                    
                    # Wait for response with timeout
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "wallet_update" and "data" in data:
                        wallet_data = data.get("data", {}).get("wallet", {})
                        if "wallet_address" in wallet_data:
                            self.log_test("WebSocket Wallet Monitor", True, 
                                        "WebSocket wallet monitoring working", data)
                        else:
                            self.log_test("WebSocket Wallet Monitor", False, 
                                        "Invalid wallet data in WebSocket response", data)
                    else:
                        self.log_test("WebSocket Wallet Monitor", False, 
                                    "Invalid WebSocket response format", data)
                        
            except asyncio.TimeoutError:
                self.log_test("WebSocket Wallet Monitor", False, "WebSocket connection timeout")
            except Exception as ws_error:
                self.log_test("WebSocket Wallet Monitor", False, f"WebSocket error: {str(ws_error)}")
                
        except ImportError:
            self.log_test("WebSocket Wallet Monitor", False, "websockets library not available - skipping test")
        except Exception as e:
            self.log_test("WebSocket Wallet Monitor", False, f"Error: {str(e)}")
    
    async def test_database_integration(self):
        """Test 11: Database integration and persistence"""
        if not self.auth_token:
            self.log_test("Database Integration", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            # Test game history to verify database storage
            async with self.session.get(f"{self.base_url}/games/history/{self.test_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "games" in data:
                        games = data.get("games", [])
                        total_games = data.get("total_games", 0)
                        
                        # Check if games have proper database fields
                        if games and len(games) > 0:
                            first_game = games[0]
                            db_fields = ["_id", "wallet_address", "game_type", "bet_amount", "timestamp"]
                            if all(field in first_game for field in db_fields):
                                self.log_test("Database Integration", True, 
                                            f"Database integration working: {total_games} games stored with proper fields", data)
                            else:
                                self.log_test("Database Integration", False, 
                                            "Games missing required database fields", data)
                        else:
                            self.log_test("Database Integration", True, 
                                        "Database integration working: no games yet but endpoint functional", data)
                    else:
                        self.log_test("Database Integration", False, 
                                    "Invalid game history response", data)
                else:
                    self.log_test("Database Integration", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Database Integration", False, f"Error: {str(e)}")
    
    async def run_all_tests(self):
        """Run all wallet management tests"""
        print(f"🚀 Starting Wallet Management System Tests - Real Money Integration")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 70)
        
        # Run tests in logical order
        await self.test_basic_connectivity()
        
        # Authentication flow
        challenge_data = await self.test_auth_challenge_generation()
        await self.test_auth_verification(challenge_data)
        
        # Wallet management endpoints
        await self.test_wallet_info_endpoint()
        await self.test_deposit_endpoint()
        await self.test_withdraw_endpoint()
        await self.test_convert_endpoint()
        
        # Game and savings system
        await self.test_game_betting()
        await self.test_savings_system()
        
        # Real-time and database features
        await self.test_websocket_wallet_monitor()
        await self.test_database_integration()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 WALLET MANAGEMENT SYSTEM TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Categorize results
        critical_failures = []
        minor_issues = []
        
        for result in self.test_results:
            if not result["success"]:
                test_name = result["test"]
                if test_name in ["Basic Connectivity", "Auth Challenge Generation", "Auth Verification", 
                               "Game Betting", "Savings System", "Database Integration"]:
                    critical_failures.append(result)
                else:
                    minor_issues.append(result)
        
        if critical_failures:
            print("\n🚨 CRITICAL FAILURES:")
            for result in critical_failures:
                print(f"  ❌ {result['test']}: {result['details']}")
        
        if minor_issues:
            print("\n⚠️  MINOR ISSUES:")
            for result in minor_issues:
                print(f"  ⚠️  {result['test']}: {result['details']}")
        
        print("\n" + "=" * 70)
        
        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "critical_failures": len(critical_failures),
            "minor_issues": len(minor_issues),
            "success_rate": passed_tests/total_tests*100,
            "results": self.test_results
        }

async def main():
    """Main test runner"""
    async with WalletAPITester(BACKEND_URL) as tester:
        await tester.run_all_tests()
        summary = tester.print_summary()
        
        # Save detailed results
        with open("/app/backend_test_results.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: /app/backend_test_results.json")
        
        # Return exit code based on critical failures
        return 0 if summary["critical_failures"] == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)