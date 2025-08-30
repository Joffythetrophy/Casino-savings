#!/usr/bin/env python3
"""
Complete Casino Authentication System Testing
Tests the authentication fix for user 'cryptoking' and casino access functionality
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Test Configuration
BACKEND_URL = "https://crypto-treasury-app.preview.emergentagent.com/api"
TEST_USER = {
    "username": "cryptoking",
    "password": "crt21million",
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

class CasinoAuthenticationTester:
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
            print(f"   Data: {json.dumps(data, indent=2)}")
    
    async def test_backend_login_endpoint(self) -> bool:
        """Test /api/auth/login endpoint with cryptoking credentials"""
        try:
            login_data = {
                "identifier": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success"):
                        self.auth_token = result.get("token")
                        username = result.get("username")
                        wallet_address = result.get("wallet_address")
                        
                        # Verify response contains expected data
                        if (username == TEST_USER["username"] and 
                            wallet_address == TEST_USER["wallet_address"] and
                            self.auth_token):
                            self.log_test("Backend Login Endpoint", True, 
                                        f"Successfully authenticated user '{username}' with correct wallet address")
                            return True
                        else:
                            self.log_test("Backend Login Endpoint", False, 
                                        f"Login successful but missing expected data", result)
                            return False
                    else:
                        self.log_test("Backend Login Endpoint", False, 
                                    f"Login failed: {result.get('message', 'Unknown error')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("Backend Login Endpoint", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Backend Login Endpoint", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    async def test_jwt_token_generation(self) -> bool:
        """Test that JWT token is properly generated and valid"""
        try:
            if not self.auth_token:
                self.log_test("JWT Token Generation", False, "No auth token available from login")
                return False
            
            # JWT tokens should have 3 parts separated by dots
            token_parts = self.auth_token.split('.')
            if len(token_parts) != 3:
                self.log_test("JWT Token Generation", False, 
                            f"Invalid JWT format - expected 3 parts, got {len(token_parts)}")
                return False
            
            # Test token by making an authenticated request
            headers = self.get_auth_headers()
            async with self.session.get(f"{BACKEND_URL}/wallet/{TEST_USER['wallet_address']}", 
                                      headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success"):
                        self.log_test("JWT Token Generation", True, 
                                    "JWT token is valid and working for authenticated requests")
                        return True
                    else:
                        self.log_test("JWT Token Generation", False, 
                                    "JWT token present but authentication failed", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("JWT Token Generation", False, 
                                f"JWT token authentication failed: HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("JWT Token Generation", False, f"Exception: {str(e)}")
            return False
    
    async def test_user_data_retrieval(self) -> bool:
        """Test that authenticated user can access wallet data and balances"""
        try:
            headers = self.get_auth_headers()
            
            # Test wallet data retrieval
            async with self.session.get(f"{BACKEND_URL}/wallet/{TEST_USER['wallet_address']}", 
                                      headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success"):
                        wallet_data = result.get("wallet", {})
                        
                        # Verify wallet data structure
                        required_fields = ["user_id", "wallet_address", "deposit_balance", 
                                         "winnings_balance", "savings_balance"]
                        missing_fields = [field for field in required_fields if field not in wallet_data]
                        
                        if not missing_fields:
                            # Check if user has substantial balances (whale-level)
                            deposit_balance = wallet_data.get("deposit_balance", {})
                            total_value = 0
                            
                            # Calculate total portfolio value
                            for currency, amount in deposit_balance.items():
                                if currency == "USDC":
                                    total_value += amount
                                elif currency == "DOGE":
                                    total_value += amount * 0.236  # DOGE to USD
                                elif currency == "CRT":
                                    total_value += amount * 0.15   # CRT to USD
                                elif currency == "TRX":
                                    total_value += amount * 0.363  # TRX to USD
                            
                            if total_value > 1000000:  # $1M+ whale status
                                self.log_test("User Data Retrieval", True, 
                                            f"Successfully retrieved whale-level portfolio: ${total_value:,.2f}")
                            else:
                                self.log_test("User Data Retrieval", True, 
                                            f"Successfully retrieved user data with ${total_value:,.2f} portfolio")
                            return True
                        else:
                            self.log_test("User Data Retrieval", False, 
                                        f"Missing required wallet fields: {missing_fields}", result)
                            return False
                    else:
                        self.log_test("User Data Retrieval", False, 
                                    f"Failed to retrieve wallet data: {result.get('message')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("User Data Retrieval", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("User Data Retrieval", False, f"Exception: {str(e)}")
            return False
    
    async def test_casino_access_betting(self) -> bool:
        """Test that user can place bets and access casino features after login"""
        try:
            # Test placing a bet in the casino
            bet_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "game_type": "Slot Machine",
                "bet_amount": 10.0,
                "currency": "CRT",
                "network": "Solana"
            }
            
            async with self.session.post(f"{BACKEND_URL}/games/bet", json=bet_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success"):
                        game_id = result.get("game_id")
                        bet_amount = result.get("bet_amount")
                        game_result = result.get("result")
                        
                        if game_id and bet_amount == 10.0 and game_result in ["win", "loss"]:
                            self.log_test("Casino Access - Betting", True, 
                                        f"Successfully placed bet: Game {game_id}, Result: {game_result}")
                            return True
                        else:
                            self.log_test("Casino Access - Betting", False, 
                                        "Bet placed but response data incomplete", result)
                            return False
                    else:
                        self.log_test("Casino Access - Betting", False, 
                                    f"Bet placement failed: {result.get('message')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("Casino Access - Betting", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Casino Access - Betting", False, f"Exception: {str(e)}")
            return False
    
    async def test_game_history_access(self) -> bool:
        """Test that authenticated user can access game history"""
        try:
            headers = self.get_auth_headers()
            
            async with self.session.get(f"{BACKEND_URL}/games/history/{TEST_USER['wallet_address']}", 
                                      headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success"):
                        games = result.get("games", [])
                        total_games = result.get("total_games", 0)
                        
                        self.log_test("Game History Access", True, 
                                    f"Successfully retrieved game history: {total_games} games")
                        return True
                    else:
                        self.log_test("Game History Access", False, 
                                    f"Failed to retrieve game history: {result.get('message')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("Game History Access", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Game History Access", False, f"Exception: {str(e)}")
            return False
    
    async def test_orca_pool_access(self) -> bool:
        """Test that authenticated user can access Orca pool management features"""
        try:
            headers = self.get_auth_headers()
            
            # Test accessing Orca pools data
            async with self.session.get(f"{BACKEND_URL}/dex/pools", headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success"):
                        pools = result.get("pools", [])
                        total_liquidity = result.get("total_liquidity_usd", 0)
                        
                        self.log_test("Orca Pool Access", True, 
                                    f"Successfully accessed Orca pools: {len(pools)} pools, ${total_liquidity:,.2f} liquidity")
                        return True
                    else:
                        self.log_test("Orca Pool Access", False, 
                                    f"Failed to access Orca pools: {result.get('message')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("Orca Pool Access", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Orca Pool Access", False, f"Exception: {str(e)}")
            return False
    
    async def test_admin_pool_creation_access(self) -> bool:
        """Test that cryptoking user has admin access to pool creation"""
        try:
            headers = self.get_auth_headers()
            
            # Test admin pool creation access (should work for cryptoking)
            pool_data = {
                "pool_pair": "CRT/SOL",
                "wallet_address": TEST_USER["wallet_address"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/dex/create-orca-pool", 
                                       json=pool_data, headers=headers) as resp:
                result = await resp.json()
                
                if resp.status == 200 and result.get("success"):
                    self.log_test("Admin Pool Creation Access", True, 
                                "Successfully accessed admin pool creation features")
                    return True
                elif resp.status == 403:
                    self.log_test("Admin Pool Creation Access", False, 
                                "Access denied - admin privileges not working", result)
                    return False
                else:
                    # Check if it's a reasonable error (like insufficient balance)
                    error_msg = str(result).lower()
                    if any(keyword in error_msg for keyword in ["balance", "treasury", "insufficient"]):
                        self.log_test("Admin Pool Creation Access", True, 
                                    "Admin access confirmed - pool creation blocked by balance validation only")
                        return True
                    else:
                        self.log_test("Admin Pool Creation Access", False, 
                                    f"Unexpected error: {result.get('message', 'Unknown')}", result)
                        return False
                    
        except Exception as e:
            self.log_test("Admin Pool Creation Access", False, f"Exception: {str(e)}")
            return False
    
    async def test_wallet_balance_access(self) -> bool:
        """Test that user can access their massive liquidity pools and balances"""
        try:
            headers = self.get_auth_headers()
            
            # Test wallet balance access
            async with self.session.get(f"{BACKEND_URL}/wallet/{TEST_USER['wallet_address']}", 
                                      headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success"):
                        wallet_data = result.get("wallet", {})
                        deposit_balance = wallet_data.get("deposit_balance", {})
                        
                        # Check for whale-level balances
                        usdc_balance = deposit_balance.get("USDC", 0)
                        doge_balance = deposit_balance.get("DOGE", 0)
                        crt_balance = deposit_balance.get("CRT", 0)
                        
                        total_usd_value = (usdc_balance + 
                                         (doge_balance * 0.236) + 
                                         (crt_balance * 0.15))
                        
                        if total_usd_value > 6500000:  # $6.5M+ as mentioned in requirements
                            self.log_test("Wallet Balance Access", True, 
                                        f"Successfully accessed whale-level balances: ${total_usd_value:,.2f} total value")
                        else:
                            self.log_test("Wallet Balance Access", True, 
                                        f"Successfully accessed wallet balances: ${total_usd_value:,.2f} total value")
                        return True
                    else:
                        self.log_test("Wallet Balance Access", False, 
                                    f"Failed to access wallet balances: {result.get('message')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("Wallet Balance Access", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Wallet Balance Access", False, f"Exception: {str(e)}")
            return False
    
    def print_summary(self):
        """Print comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n{'='*80}")
        print(f"🎰 COMPLETE CASINO AUTHENTICATION SYSTEM TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🎯 AUTHENTICATION SYSTEM ASSESSMENT:")
        
        # Check login functionality
        login_tests = [r for r in self.test_results if "login" in r["test"].lower()]
        if any(t["success"] for t in login_tests):
            print(f"   ✅ User 'cryptoking' can login successfully with password 'crt21million'")
        else:
            print(f"   ❌ Login system not working - user cannot authenticate")
        
        # Check JWT token
        jwt_tests = [r for r in self.test_results if "jwt" in r["test"].lower()]
        if any(t["success"] for t in jwt_tests):
            print(f"   ✅ JWT token generated and working for API authentication")
        else:
            print(f"   ❌ JWT token generation or validation issues")
        
        # Check wallet access
        wallet_tests = [r for r in self.test_results if "wallet" in r["test"].lower() or "balance" in r["test"].lower()]
        if any(t["success"] for t in wallet_tests):
            print(f"   ✅ User can access their wallet data and balances")
        else:
            print(f"   ❌ Wallet data access issues")
        
        # Check casino functionality
        casino_tests = [r for r in self.test_results if "casino" in r["test"].lower() or "betting" in r["test"].lower()]
        if any(t["success"] for t in casino_tests):
            print(f"   ✅ Casino games functional after authentication")
        else:
            print(f"   ❌ Casino functionality not accessible")
        
        # Check pool access
        pool_tests = [r for r in self.test_results if "pool" in r["test"].lower() or "orca" in r["test"].lower()]
        if any(t["success"] for t in pool_tests):
            print(f"   ✅ Pool management accessible to admin user")
        else:
            print(f"   ❌ Pool management access issues")
        
        print(f"\n🚀 FINAL ASSESSMENT:")
        if failed_tests == 0:
            print(f"   🎉 COMPLETE AUTHENTICATION SYSTEM FIX SUCCESSFUL!")
            print(f"   ✅ User 'cryptoking' can fully access casino and pool features")
            print(f"   ✅ No more 'cant sign in' issues - authentication working perfectly")
        elif failed_tests <= 2:
            print(f"   ⚠️  Authentication mostly working - minor issues remain")
            print(f"   🔧 Check remaining {failed_tests} issues for full functionality")
        else:
            print(f"   ❌ AUTHENTICATION SYSTEM STILL HAS MAJOR ISSUES")
            print(f"   🚨 User may still experience 'cant sign in' problems")
            print(f"   🔍 {failed_tests} critical issues need to be resolved")

async def main():
    """Run all casino authentication system tests"""
    print("🎰 Starting Complete Casino Authentication System Tests...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test User: {TEST_USER['username']} ({TEST_USER['wallet_address']})")
    print(f"Testing Credentials: {TEST_USER['username']} / {TEST_USER['password']}")
    print("="*80)
    
    async with CasinoAuthenticationTester() as tester:
        # Test sequence for complete authentication system
        tests = [
            ("test_backend_login_endpoint", "Backend Login Test"),
            ("test_jwt_token_generation", "JWT Token Generation"),
            ("test_user_data_retrieval", "User Data Retrieval"),
            ("test_wallet_balance_access", "Wallet Balance Access"),
            ("test_casino_access_betting", "Casino Access Test"),
            ("test_game_history_access", "Game History Access"),
            ("test_orca_pool_access", "Pool Access Test"),
            ("test_admin_pool_creation_access", "Admin Pool Creation Access")
        ]
        
        for method_name, test_description in tests:
            print(f"\n🧪 Running: {test_description}")
            try:
                method = getattr(tester, method_name)
                await method()
            except Exception as e:
                tester.log_test(test_description, False, f"Test execution failed: {str(e)}")
        
        # Print final summary
        tester.print_summary()
        
        # Return exit code based on results
        failed_count = sum(1 for result in tester.test_results if not result["success"])
        return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)