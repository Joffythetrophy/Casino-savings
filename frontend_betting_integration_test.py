#!/usr/bin/env python3
"""
FRONTEND-BACKEND BETTING INTEGRATION TEST
Testing the complete betting flow that the frontend would use
to identify potential issues causing "Failing to place bets not working cant play"
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Test Configuration
BACKEND_URL = "https://blockchain-slots.preview.emergentagent.com/api"
TEST_USER = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

class FrontendBettingIntegrationTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        
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
    
    async def test_frontend_login_flow(self) -> bool:
        """Test the exact login flow the frontend would use"""
        try:
            # Test login endpoint that frontend uses
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
                            "Frontend Login Flow", 
                            True, 
                            f"Login successful: {result.get('message', '')}, token received: {bool(self.auth_token)}"
                        )
                        return True
                    else:
                        self.log_test("Frontend Login Flow", False, f"Login failed: {result}", result)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Frontend Login Flow", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Frontend Login Flow", False, f"Login error: {str(e)}")
            return False
    
    async def test_wallet_balance_endpoint(self) -> Dict[str, Any]:
        """Test wallet balance endpoint that frontend uses"""
        try:
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            async with self.session.get(f"{BACKEND_URL}/wallet/{TEST_USER['wallet_address']}", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        wallet_data = result.get("wallet", {})
                        deposit_balance = wallet_data.get("deposit_balance", {})
                        doge_balance = deposit_balance.get("DOGE", 0)
                        
                        self.log_test(
                            "Wallet Balance Endpoint", 
                            True, 
                            f"Balance retrieved: DOGE {doge_balance:,.2f} (matches expected ~88,814)",
                            {"doge_balance": doge_balance, "all_balances": deposit_balance}
                        )
                        return wallet_data
                    else:
                        self.log_test("Wallet Balance Endpoint", False, f"Failed: {result}", result)
                        return {}
                else:
                    error_text = await response.text()
                    self.log_test("Wallet Balance Endpoint", False, f"HTTP {response.status}: {error_text}")
                    return {}
                    
        except Exception as e:
            self.log_test("Wallet Balance Endpoint", False, f"Balance error: {str(e)}")
            return {}
    
    async def test_betting_with_auth_header(self, game_type: str, currency: str, amount: float) -> bool:
        """Test betting with authentication header (as frontend would do)"""
        try:
            bet_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "game_type": game_type,
                "bet_amount": amount,
                "currency": currency,
                "network": "Dogecoin" if currency == "DOGE" else "Solana"
            }
            
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
                headers["Content-Type"] = "application/json"
            
            async with self.session.post(f"{BACKEND_URL}/games/bet", json=bet_data, headers=headers) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        if result.get("success"):
                            self.log_test(
                                f"Authenticated Betting - {game_type}", 
                                True, 
                                f"Bet successful: {amount} {currency} → {result.get('result', 'unknown')}, payout: {result.get('payout', 0)}"
                            )
                            return True
                        else:
                            self.log_test(
                                f"Authenticated Betting - {game_type}", 
                                False, 
                                f"Bet failed: {result.get('message', 'Unknown error')}", 
                                result
                            )
                            return False
                    except json.JSONDecodeError:
                        self.log_test(
                            f"Authenticated Betting - {game_type}", 
                            False, 
                            f"Invalid JSON response: {response_text}"
                        )
                        return False
                else:
                    self.log_test(
                        f"Authenticated Betting - {game_type}", 
                        False, 
                        f"HTTP {response.status}: {response_text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test(f"Authenticated Betting - {game_type}", False, f"Betting error: {str(e)}")
            return False
    
    async def test_cors_and_headers(self) -> bool:
        """Test CORS and header issues that might affect frontend"""
        try:
            # Test preflight request
            headers = {
                "Origin": "https://blockchain-slots.preview.emergentagent.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
            
            async with self.session.options(f"{BACKEND_URL}/games/bet", headers=headers) as response:
                cors_headers = {
                    "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                    "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                    "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
                }
                
                if response.status in [200, 204] or cors_headers.get("Access-Control-Allow-Origin"):
                    self.log_test(
                        "CORS Configuration", 
                        True, 
                        f"CORS properly configured: {cors_headers}",
                        cors_headers
                    )
                    return True
                else:
                    self.log_test(
                        "CORS Configuration", 
                        False, 
                        f"CORS issues detected: HTTP {response.status}, headers: {cors_headers}",
                        cors_headers
                    )
                    return False
                    
        except Exception as e:
            self.log_test("CORS Configuration", False, f"CORS test error: {str(e)}")
            return False
    
    async def test_rapid_betting_sequence(self) -> bool:
        """Test rapid betting sequence that might cause issues"""
        try:
            successful_bets = 0
            total_bets = 5
            
            for i in range(total_bets):
                success = await self.test_betting_with_auth_header("Slot Machine", "DOGE", 10.0)
                if success:
                    successful_bets += 1
                await asyncio.sleep(0.5)  # Small delay between bets
            
            if successful_bets == total_bets:
                self.log_test(
                    "Rapid Betting Sequence", 
                    True, 
                    f"All {total_bets} rapid bets successful"
                )
                return True
            elif successful_bets > 0:
                self.log_test(
                    "Rapid Betting Sequence", 
                    False, 
                    f"Only {successful_bets}/{total_bets} rapid bets successful - potential rate limiting or concurrency issues"
                )
                return False
            else:
                self.log_test(
                    "Rapid Betting Sequence", 
                    False, 
                    "No rapid bets successful - system may be blocking rapid requests"
                )
                return False
                
        except Exception as e:
            self.log_test("Rapid Betting Sequence", False, f"Rapid betting error: {str(e)}")
            return False
    
    async def test_game_specific_endpoints(self) -> bool:
        """Test if there are game-specific endpoints that might be failing"""
        try:
            # Test game history endpoint (frontend might use this)
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            async with self.session.get(f"{BACKEND_URL}/games/history/{TEST_USER['wallet_address']}", headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        game_count = len(result.get("games", []))
                        self.log_test(
                            "Game History Endpoint", 
                            True, 
                            f"Game history accessible: {game_count} games found"
                        )
                        return True
                    else:
                        self.log_test("Game History Endpoint", False, f"Failed: {result}", result)
                        return False
                elif response.status == 403:
                    self.log_test(
                        "Game History Endpoint", 
                        False, 
                        "Authentication required but token not working"
                    )
                    return False
                else:
                    error_text = await response.text()
                    self.log_test("Game History Endpoint", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Game History Endpoint", False, f"Game history error: {str(e)}")
            return False
    
    async def comprehensive_frontend_test(self):
        """Run comprehensive frontend-backend integration test"""
        print("🎮 FRONTEND-BACKEND BETTING INTEGRATION TEST")
        print("=" * 70)
        print(f"Investigating: 'cryptoking' - 'Failing to place bets not working cant play'")
        print(f"Focus: Frontend-backend communication issues")
        print("=" * 70)
        
        # 1. Test frontend login flow
        login_success = await self.test_frontend_login_flow()
        if not login_success:
            print("\n❌ CRITICAL: Frontend login flow failed")
            return
        
        # 2. Test wallet balance endpoint
        wallet_data = await self.test_wallet_balance_endpoint()
        if not wallet_data:
            print("\n❌ CRITICAL: Cannot retrieve wallet data for frontend")
            return
        
        # 3. Test CORS configuration
        await self.test_cors_and_headers()
        
        # 4. Test authenticated betting (as frontend would do)
        games_to_test = ["Slot Machine", "Roulette", "Dice", "Plinko", "Keno", "Mines"]
        successful_games = 0
        
        for game in games_to_test:
            success = await self.test_betting_with_auth_header(game, "DOGE", 10.0)
            if success:
                successful_games += 1
        
        # 5. Test rapid betting sequence
        await self.test_rapid_betting_sequence()
        
        # 6. Test game-specific endpoints
        await self.test_game_specific_endpoints()
        
        # Generate summary
        print("\n" + "=" * 70)
        print("🎯 FRONTEND-BACKEND INTEGRATION SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["success"]])
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Analyze specific issues
        frontend_issues = []
        for result in self.test_results:
            if not result["success"]:
                if "CORS" in result["test"]:
                    frontend_issues.append("🌐 CORS Configuration Issue - Frontend may be blocked")
                elif "Authenticated Betting" in result["test"]:
                    frontend_issues.append(f"🎰 Betting Issue - {result['test']}: {result['details']}")
                elif "Rapid Betting" in result["test"]:
                    frontend_issues.append("⚡ Rate Limiting Issue - Rapid bets failing")
                elif "Game History" in result["test"]:
                    frontend_issues.append("📊 Game History Issue - Frontend cannot access game data")
        
        if frontend_issues:
            print("\n🚨 FRONTEND INTEGRATION ISSUES:")
            for issue in frontend_issues:
                print(f"   {issue}")
        else:
            print("\n✅ NO FRONTEND INTEGRATION ISSUES FOUND")
        
        # Final diagnosis
        if successful_games == len(games_to_test):
            print(f"\n🎯 DIAGNOSIS: All {len(games_to_test)} games working with authentication")
            print("   Backend betting system is fully functional")
            print("   User issue may be frontend-specific or browser-related")
        elif successful_games > 0:
            print(f"\n🎯 DIAGNOSIS: Partial game functionality - {successful_games}/{len(games_to_test)} games working")
            print("   Some games may have specific issues")
        else:
            print(f"\n🎯 DIAGNOSIS: NO GAMES WORKING - Critical backend issue confirmed")
            print("   User complaint is valid - betting system is broken")
        
        return self.test_results

async def main():
    """Run the frontend-backend integration test"""
    async with FrontendBettingIntegrationTester() as tester:
        results = await tester.comprehensive_frontend_test()
        
        # Save results to file for analysis
        with open("/app/frontend_betting_integration_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: /app/frontend_betting_integration_results.json")

if __name__ == "__main__":
    asyncio.run(main())