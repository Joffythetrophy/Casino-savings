#!/usr/bin/env python3
"""
AUTHENTICATION STATE PERSISTENCE TEST
Testing authentication state issues that might prevent frontend betting
Based on previous test results showing authentication state persistence problems
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Test Configuration
BACKEND_URL = "https://tiger-dex-casino.preview.emergentagent.com/api"
FRONTEND_URL = "https://tiger-dex-casino.preview.emergentagent.com"
TEST_USER = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

class AuthenticationStateTester:
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
    
    async def test_jwt_token_validation(self) -> bool:
        """Test JWT token validation and expiry"""
        try:
            # First login to get token
            login_data = {
                "identifier": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        self.auth_token = result.get("token")
                        expires_in = result.get("expires_in", 0)
                        
                        # Test token validation
                        headers = {"Authorization": f"Bearer {self.auth_token}"}
                        async with self.session.get(f"{BACKEND_URL}/games/history/{TEST_USER['wallet_address']}", headers=headers) as token_test:
                            if token_test.status == 200:
                                self.log_test(
                                    "JWT Token Validation", 
                                    True, 
                                    f"Token valid, expires in {expires_in} seconds"
                                )
                                return True
                            else:
                                self.log_test(
                                    "JWT Token Validation", 
                                    False, 
                                    f"Token validation failed: HTTP {token_test.status}"
                                )
                                return False
                    else:
                        self.log_test("JWT Token Validation", False, f"Login failed: {result}")
                        return False
                else:
                    self.log_test("JWT Token Validation", False, f"Login HTTP error: {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("JWT Token Validation", False, f"Token validation error: {str(e)}")
            return False
    
    async def test_wallet_auth_challenge_flow(self) -> bool:
        """Test wallet authentication challenge flow (alternative auth method)"""
        try:
            # Test challenge generation
            challenge_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "network": "Solana"
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/challenge", json=challenge_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        challenge = result.get("challenge")
                        challenge_hash = result.get("challenge_hash")
                        
                        self.log_test(
                            "Wallet Auth Challenge", 
                            True, 
                            f"Challenge generated successfully: {challenge[:20]}..."
                        )
                        
                        # Note: We can't complete the signature verification without a real wallet
                        # But we can test that the challenge endpoint works
                        return True
                    else:
                        self.log_test("Wallet Auth Challenge", False, f"Challenge failed: {result}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Wallet Auth Challenge", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Wallet Auth Challenge", False, f"Challenge error: {str(e)}")
            return False
    
    async def test_protected_endpoints_without_auth(self) -> bool:
        """Test protected endpoints without authentication to check security"""
        try:
            protected_endpoints = [
                f"/games/history/{TEST_USER['wallet_address']}",
                f"/wallet/convert",
                f"/orca/add-liquidity"
            ]
            
            auth_required_count = 0
            
            for endpoint in protected_endpoints:
                async with self.session.get(f"{BACKEND_URL}{endpoint}") as response:
                    if response.status in [401, 403]:
                        auth_required_count += 1
            
            if auth_required_count == len(protected_endpoints):
                self.log_test(
                    "Protected Endpoints Security", 
                    True, 
                    f"All {len(protected_endpoints)} protected endpoints require authentication"
                )
                return True
            else:
                self.log_test(
                    "Protected Endpoints Security", 
                    False, 
                    f"Only {auth_required_count}/{len(protected_endpoints)} endpoints require auth"
                )
                return False
                
        except Exception as e:
            self.log_test("Protected Endpoints Security", False, f"Security test error: {str(e)}")
            return False
    
    async def test_betting_without_authentication(self) -> bool:
        """Test if betting works without authentication (should work based on previous tests)"""
        try:
            bet_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "game_type": "Slot Machine",
                "bet_amount": 1.0,
                "currency": "DOGE",
                "network": "Dogecoin"
            }
            
            # Test without auth headers
            async with self.session.post(f"{BACKEND_URL}/games/bet", json=bet_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        self.log_test(
                            "Betting Without Authentication", 
                            True, 
                            "Betting works without authentication - no auth state issues"
                        )
                        return True
                    else:
                        self.log_test(
                            "Betting Without Authentication", 
                            False, 
                            f"Betting failed: {result.get('message', 'Unknown error')}"
                        )
                        return False
                else:
                    error_text = await response.text()
                    self.log_test(
                        "Betting Without Authentication", 
                        False, 
                        f"HTTP {response.status}: {error_text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test("Betting Without Authentication", False, f"Betting test error: {str(e)}")
            return False
    
    async def test_session_persistence(self) -> bool:
        """Test session persistence across multiple requests"""
        try:
            # Login and get token
            login_data = {
                "identifier": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        token = result.get("token")
                        
                        # Test multiple requests with same token
                        headers = {"Authorization": f"Bearer {token}"}
                        successful_requests = 0
                        total_requests = 5
                        
                        for i in range(total_requests):
                            async with self.session.get(f"{BACKEND_URL}/wallet/{TEST_USER['wallet_address']}", headers=headers) as test_response:
                                if test_response.status == 200:
                                    successful_requests += 1
                            await asyncio.sleep(0.1)
                        
                        if successful_requests == total_requests:
                            self.log_test(
                                "Session Persistence", 
                                True, 
                                f"Token valid for all {total_requests} consecutive requests"
                            )
                            return True
                        else:
                            self.log_test(
                                "Session Persistence", 
                                False, 
                                f"Token failed after {total_requests - successful_requests} requests"
                            )
                            return False
                    else:
                        self.log_test("Session Persistence", False, f"Login failed: {result}")
                        return False
                else:
                    self.log_test("Session Persistence", False, f"Login HTTP error: {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("Session Persistence", False, f"Session test error: {str(e)}")
            return False
    
    async def test_frontend_specific_headers(self) -> bool:
        """Test with headers that frontend would typically send"""
        try:
            # Login first
            login_data = {
                "identifier": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        token = result.get("token")
                        
                        # Test betting with frontend-like headers
                        bet_data = {
                            "wallet_address": TEST_USER["wallet_address"],
                            "game_type": "Slot Machine",
                            "bet_amount": 5.0,
                            "currency": "DOGE",
                            "network": "Dogecoin"
                        }
                        
                        frontend_headers = {
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json",
                            "Origin": FRONTEND_URL,
                            "Referer": f"{FRONTEND_URL}/",
                            "User-Agent": "Mozilla/5.0 (Frontend Test)"
                        }
                        
                        async with self.session.post(f"{BACKEND_URL}/games/bet", json=bet_data, headers=frontend_headers) as bet_response:
                            if bet_response.status == 200:
                                bet_result = await bet_response.json()
                                if bet_result.get("success"):
                                    self.log_test(
                                        "Frontend Headers Compatibility", 
                                        True, 
                                        "Betting works with frontend-style headers"
                                    )
                                    return True
                                else:
                                    self.log_test(
                                        "Frontend Headers Compatibility", 
                                        False, 
                                        f"Betting failed with frontend headers: {bet_result}"
                                    )
                                    return False
                            else:
                                error_text = await bet_response.text()
                                self.log_test(
                                    "Frontend Headers Compatibility", 
                                    False, 
                                    f"HTTP {bet_response.status}: {error_text}"
                                )
                                return False
                    else:
                        self.log_test("Frontend Headers Compatibility", False, f"Login failed: {result}")
                        return False
                else:
                    self.log_test("Frontend Headers Compatibility", False, f"Login HTTP error: {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("Frontend Headers Compatibility", False, f"Headers test error: {str(e)}")
            return False
    
    async def comprehensive_auth_test(self):
        """Run comprehensive authentication state test"""
        print("🔐 AUTHENTICATION STATE PERSISTENCE TEST")
        print("=" * 70)
        print(f"Investigating authentication issues that might prevent betting")
        print(f"User: {TEST_USER['username']} ({TEST_USER['wallet_address']})")
        print("=" * 70)
        
        # Run all authentication tests
        await self.test_jwt_token_validation()
        await self.test_wallet_auth_challenge_flow()
        await self.test_protected_endpoints_without_auth()
        await self.test_betting_without_authentication()
        await self.test_session_persistence()
        await self.test_frontend_specific_headers()
        
        # Generate summary
        print("\n" + "=" * 70)
        print("🎯 AUTHENTICATION STATE TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r["success"]])
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Analyze authentication issues
        auth_issues = []
        for result in self.test_results:
            if not result["success"]:
                if "JWT" in result["test"]:
                    auth_issues.append("🔑 JWT Token Issue - Authentication tokens not working")
                elif "Session" in result["test"]:
                    auth_issues.append("📱 Session Persistence Issue - Auth state not maintained")
                elif "Headers" in result["test"]:
                    auth_issues.append("🌐 Header Compatibility Issue - Frontend headers causing problems")
                elif "Security" in result["test"]:
                    auth_issues.append("🔒 Security Configuration Issue - Endpoints not properly protected")
        
        if auth_issues:
            print("\n🚨 AUTHENTICATION ISSUES IDENTIFIED:")
            for issue in auth_issues:
                print(f"   {issue}")
        else:
            print("\n✅ NO AUTHENTICATION ISSUES FOUND")
        
        # Final diagnosis for user complaint
        betting_without_auth = any(r["success"] for r in self.test_results if "Betting Without Authentication" in r["test"])
        jwt_working = any(r["success"] for r in self.test_results if "JWT Token Validation" in r["test"])
        
        if betting_without_auth:
            print(f"\n🎯 DIAGNOSIS: Betting system works WITHOUT authentication")
            print("   User complaint is NOT due to authentication issues")
            print("   Problem may be frontend-specific (browser, cache, etc.)")
        elif jwt_working:
            print(f"\n🎯 DIAGNOSIS: Authentication works but betting may require it")
            print("   User may need to ensure they're properly logged in")
        else:
            print(f"\n🎯 DIAGNOSIS: Authentication system has issues")
            print("   This could be causing the user's betting problems")
        
        return self.test_results

async def main():
    """Run the authentication state test"""
    async with AuthenticationStateTester() as tester:
        results = await tester.comprehensive_auth_test()
        
        # Save results to file for analysis
        with open("/app/authentication_state_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: /app/authentication_state_results.json")

if __name__ == "__main__":
    asyncio.run(main())