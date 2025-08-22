#!/usr/bin/env python3
"""
Casino Savings dApp Backend API Test Suite
Tests all backend endpoints systematically
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

class CasinoAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.test_wallet = "DemoWallet123456789ABC"  # Mock wallet address
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
    
    async def test_health_check(self):
        """Test 2: Health check endpoint"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    required_services = ["solana", "dogecoin", "tron"]
                    services = data.get("services", {})
                    
                    if all(service in services for service in required_services):
                        healthy_services = sum(1 for service in services.values() 
                                             if service.get("success", False))
                        self.log_test("Health Check", True, 
                                    f"All services checked, {healthy_services}/{len(required_services)} healthy", 
                                    data)
                    else:
                        self.log_test("Health Check", False, 
                                    "Missing required services in health check", data)
                else:
                    self.log_test("Health Check", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
    
    async def test_auth_challenge_generation(self):
        """Test 3: Authentication challenge generation"""
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
        """Test 4: Authentication verification and JWT token generation"""
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
    
    async def test_balance_endpoints(self):
        """Test 5: Multi-chain balance checking endpoints"""
        if not self.auth_token:
            self.log_test("Balance Endpoints", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test multi-chain balance
        try:
            async with self.session.get(f"{self.base_url}/balance/{self.test_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    expected_currencies = ["CRT", "DOGE", "TRX"]
                    balances = data.get("balances", {})
                    
                    if all(currency in balances for currency in expected_currencies):
                        self.log_test("Multi-chain Balance", True, 
                                    f"All {len(expected_currencies)} currencies retrieved", data)
                    else:
                        self.log_test("Multi-chain Balance", False, 
                                    "Missing expected currencies", data)
                else:
                    self.log_test("Multi-chain Balance", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Multi-chain Balance", False, f"Error: {str(e)}")
        
        # Test individual balance endpoints
        currencies = [("CRT", "crt"), ("DOGE", "doge"), ("TRX", "trx")]
        
        for currency_name, endpoint in currencies:
            try:
                async with self.session.get(f"{self.base_url}/balance/{endpoint}/{self.test_wallet}") as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success") and "data" in data:
                            self.log_test(f"{currency_name} Balance", True, 
                                        f"Balance retrieved successfully", data)
                        else:
                            self.log_test(f"{currency_name} Balance", False, 
                                        "Invalid balance response format", data)
                    else:
                        self.log_test(f"{currency_name} Balance", False, 
                                    f"HTTP {response.status}: {await response.text()}")
            except Exception as e:
                self.log_test(f"{currency_name} Balance", False, f"Error: {str(e)}")
    
    async def test_game_betting(self):
        """Test 6: Game betting functionality"""
        if not self.auth_token:
            self.log_test("Game Betting", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test placing a bet
        try:
            bet_payload = {
                "wallet_address": self.test_wallet,
                "game_type": "slots",
                "bet_amount": 10.0,
                "currency": "CRT",
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/games/bet", 
                                       json=bet_payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "game_id", "bet_amount", "currency", "result", "payout"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        self.log_test("Game Betting", True, 
                                    f"Bet placed: {data.get('result')}, payout: {data.get('payout')}", data)
                    else:
                        self.log_test("Game Betting", False, 
                                    "Invalid bet response format", data)
                else:
                    self.log_test("Game Betting", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Game Betting", False, f"Error: {str(e)}")
    
    async def test_game_history(self):
        """Test 7: Game history retrieval"""
        if not self.auth_token:
            self.log_test("Game History", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(f"{self.base_url}/games/history/{self.test_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "games", "total_games"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        total_games = data.get("total_games", 0)
                        self.log_test("Game History", True, 
                                    f"Retrieved {total_games} game records", data)
                    else:
                        self.log_test("Game History", False, 
                                    "Invalid game history response", data)
                else:
                    self.log_test("Game History", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Game History", False, f"Error: {str(e)}")
    
    async def test_savings_tracking(self):
        """Test 8: Savings tracking functionality"""
        if not self.auth_token:
            self.log_test("Savings Tracking", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(f"{self.base_url}/savings/{self.test_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "wallet_address", "savings_by_currency", "stats"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        stats = data.get("stats", {})
                        total_games = stats.get("total_games", 0)
                        win_rate = stats.get("win_rate", 0)
                        self.log_test("Savings Tracking", True, 
                                    f"Savings data retrieved: {total_games} games, {win_rate:.1f}% win rate", data)
                    else:
                        self.log_test("Savings Tracking", False, 
                                    "Invalid savings response format", data)
                else:
                    self.log_test("Savings Tracking", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Savings Tracking", False, f"Error: {str(e)}")
    
    async def test_websocket_connection(self):
        """Test 9: WebSocket connection for real-time updates"""
        try:
            import websockets
            
            ws_url = f"wss://blockchain-casino.preview.emergentagent.com/api/ws/balance/{self.test_wallet}"
            
            try:
                async with websockets.connect(ws_url) as websocket:
                    # Send a test message
                    test_message = {"type": "refresh_balance"}
                    await websocket.send(json.dumps(test_message))
                    
                    # Wait for response with timeout
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "balance_update" and "data" in data:
                        self.log_test("WebSocket Connection", True, 
                                    "WebSocket connection and balance update successful", data)
                    else:
                        self.log_test("WebSocket Connection", False, 
                                    "Invalid WebSocket response format", data)
                        
            except asyncio.TimeoutError:
                self.log_test("WebSocket Connection", False, "WebSocket connection timeout")
            except Exception as ws_error:
                self.log_test("WebSocket Connection", False, f"WebSocket error: {str(ws_error)}")
                
        except ImportError:
            self.log_test("WebSocket Connection", False, "websockets library not available - skipping test")
        except Exception as e:
            self.log_test("WebSocket Connection", False, f"Error: {str(e)}")
    
    async def test_legacy_endpoints(self):
        """Test 10: Legacy status endpoints"""
        try:
            # Test creating status check
            payload = {"client_name": "test_client"}
            
            async with self.session.post(f"{self.base_url}/status", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "id" in data and "client_name" in data:
                        self.log_test("Legacy Status Create", True, 
                                    f"Status check created with ID: {data.get('id')}", data)
                    else:
                        self.log_test("Legacy Status Create", False, 
                                    "Invalid status create response", data)
                else:
                    self.log_test("Legacy Status Create", False, 
                                f"HTTP {response.status}: {await response.text()}")
            
            # Test getting status checks
            async with self.session.get(f"{self.base_url}/status") as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        self.log_test("Legacy Status List", True, 
                                    f"Retrieved {len(data)} status records", data)
                    else:
                        self.log_test("Legacy Status List", False, 
                                    "Invalid status list response format", data)
                else:
                    self.log_test("Legacy Status List", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self.log_test("Legacy Endpoints", False, f"Error: {str(e)}")
    
    async def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"🚀 Starting Casino Savings dApp Backend API Tests")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Run tests in logical order
        await self.test_basic_connectivity()
        await self.test_health_check()
        
        # Authentication flow
        challenge_data = await self.test_auth_challenge_generation()
        await self.test_auth_verification(challenge_data)
        
        # Authenticated endpoints
        await self.test_balance_endpoints()
        await self.test_game_betting()
        await self.test_game_history()
        await self.test_savings_tracking()
        
        # Real-time features
        await self.test_websocket_connection()
        
        # Legacy endpoints
        await self.test_legacy_endpoints()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        print("\n" + "=" * 60)
        
        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": passed_tests/total_tests*100,
            "results": self.test_results
        }

async def main():
    """Main test runner"""
    async with CasinoAPITester(BACKEND_URL) as tester:
        await tester.run_all_tests()
        summary = tester.print_summary()
        
        # Save detailed results
        with open("/app/backend_test_results.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: /app/backend_test_results.json")
        
        # Return exit code based on test results
        return 0 if summary["failed"] == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)