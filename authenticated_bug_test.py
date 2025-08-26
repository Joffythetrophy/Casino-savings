#!/usr/bin/env python3
"""
AUTHENTICATED BUG INVESTIGATION for user cryptoking
Testing with proper JWT authentication
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

class AuthenticatedBugTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.jwt_token: Optional[str] = None
        self.test_results = []
        
        # User credentials from review request
        self.user_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        self.username = "cryptoking"
        self.password = "crt21million"
        
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
        
    async def get_jwt_token(self):
        """Get JWT token through wallet authentication flow"""
        try:
            # Step 1: Generate challenge
            challenge_payload = {
                "wallet_address": self.user_wallet,
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/auth/challenge", 
                                       json=challenge_payload) as response:
                if response.status == 200:
                    challenge_data = await response.json()
                    if challenge_data.get("success"):
                        challenge_hash = challenge_data.get("challenge_hash")
                        
                        # Step 2: Verify with mock signature (demo purposes)
                        verify_payload = {
                            "challenge_hash": challenge_hash,
                            "signature": "mock_signature_for_testing_purposes",
                            "wallet_address": self.user_wallet,
                            "network": "solana"
                        }
                        
                        async with self.session.post(f"{self.base_url}/auth/verify", 
                                                   json=verify_payload) as verify_response:
                            if verify_response.status == 200:
                                verify_data = await verify_response.json()
                                if verify_data.get("success"):
                                    self.jwt_token = verify_data.get("token")
                                    self.log_test("JWT Authentication", True, 
                                                f"JWT token obtained successfully")
                                    return True
                                else:
                                    self.log_test("JWT Authentication", False, 
                                                f"JWT verification failed: {verify_data}")
                                    return False
                            else:
                                error_text = await verify_response.text()
                                self.log_test("JWT Authentication", False, 
                                            f"JWT verify HTTP {verify_response.status}: {error_text}")
                                return False
                    else:
                        self.log_test("JWT Authentication", False, 
                                    f"Challenge generation failed: {challenge_data}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("JWT Authentication", False, 
                                f"Challenge HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("JWT Authentication", False, f"Error: {str(e)}")
            return False

    async def test_authenticated_savings_endpoint(self):
        """Test savings endpoint with authentication"""
        if not self.jwt_token:
            self.log_test("Authenticated Savings", False, "No JWT token available")
            return
            
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        
        try:
            async with self.session.get(f"{self.base_url}/savings/{self.user_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        total_savings = data.get("total_savings", {})
                        savings_history = data.get("savings_history", [])
                        stats = data.get("stats", {})
                        
                        total_losses = stats.get("total_losses", 0)
                        total_games = stats.get("total_games", 0)
                        
                        if total_losses > 0 and len(savings_history) > 0:
                            self.log_test("Authenticated Savings - Loss Tracking", True, 
                                        f"✅ LOSS TRACKER WORKING: {total_losses} losses tracked, {len(savings_history)} history entries")
                        elif total_games > 0:
                            self.log_test("Authenticated Savings - Loss Tracking", False, 
                                        f"❌ LOSS TRACKER BROKEN: {total_games} games but {total_losses} losses tracked")
                        else:
                            self.log_test("Authenticated Savings - Loss Tracking", True, 
                                        f"No games played yet - loss tracker ready")
                        
                        # Check savings amounts
                        total_saved = sum(total_savings.values()) if isinstance(total_savings, dict) else 0
                        self.log_test("Authenticated Savings - Amounts", True, 
                                    f"Savings amounts: {total_savings} (total: {total_saved})")
                    else:
                        self.log_test("Authenticated Savings", False, 
                                    f"Savings endpoint failed: {data}")
                else:
                    error_text = await response.text()
                    self.log_test("Authenticated Savings", False, 
                                f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Authenticated Savings", False, f"Error: {str(e)}")

    async def test_authenticated_game_betting(self):
        """Test game betting with authentication for autoplay testing"""
        if not self.jwt_token:
            self.log_test("Authenticated Game Betting", False, "No JWT token available")
            return
            
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        
        # Test multiple rapid bets to simulate autoplay
        game_results = []
        
        for i in range(5):  # Test 5 rapid bets
            try:
                bet_payload = {
                    "wallet_address": self.user_wallet,
                    "game_type": "Slot Machine",
                    "bet_amount": 10.0,
                    "currency": "CRT",
                    "network": "solana"
                }
                
                async with self.session.post(f"{self.base_url}/games/bet", 
                                           json=bet_payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            game_results.append({
                                "bet": i+1,
                                "result": data.get("result"),
                                "payout": data.get("payout"),
                                "savings_contribution": data.get("savings_contribution", 0)
                            })
                        else:
                            game_results.append({
                                "bet": i+1,
                                "error": data.get("message", "Unknown error")
                            })
                    else:
                        error_text = await response.text()
                        game_results.append({
                            "bet": i+1,
                            "error": f"HTTP {response.status}: {error_text}"
                        })
                        
            except Exception as e:
                game_results.append({
                    "bet": i+1,
                    "error": str(e)
                })
        
        # Analyze results
        successful_bets = [r for r in game_results if "result" in r]
        failed_bets = [r for r in game_results if "error" in r]
        
        if len(successful_bets) == 5:
            self.log_test("Authenticated Game Betting - Autoplay Simulation", True, 
                        f"✅ AUTOPLAY BACKEND READY: 5/5 rapid bets successful")
            
            # Check loss tracking
            losses = [r for r in successful_bets if r["result"] == "loss"]
            total_savings = sum(r["savings_contribution"] for r in losses)
            
            if losses and total_savings > 0:
                self.log_test("Authenticated Game Betting - Loss Tracking", True, 
                            f"✅ LOSS TRACKING WORKING: {len(losses)} losses, {total_savings} saved")
            elif losses and total_savings == 0:
                self.log_test("Authenticated Game Betting - Loss Tracking", False, 
                            f"❌ LOSS TRACKING BROKEN: {len(losses)} losses but 0 saved")
            else:
                self.log_test("Authenticated Game Betting - Loss Tracking", True, 
                            f"No losses in test - loss tracking ready")
                
        elif len(successful_bets) > 0:
            self.log_test("Authenticated Game Betting - Autoplay Simulation", False, 
                        f"⚠️ AUTOPLAY PARTIAL: {len(successful_bets)}/5 bets successful")
        else:
            self.log_test("Authenticated Game Betting - Autoplay Simulation", False, 
                        f"❌ AUTOPLAY BROKEN: 0/5 bets successful")

    async def test_authenticated_coinpayments_withdrawal(self):
        """Test CoinPayments withdrawal with authentication"""
        if not self.jwt_token:
            self.log_test("Authenticated CoinPayments", False, "No JWT token available")
            return
            
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        
        try:
            coinpayments_payload = {
                "wallet_address": self.user_wallet,
                "currency": "DOGE",
                "amount": 10.0,
                "destination_address": "DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L"
            }
            
            async with self.session.post(f"{self.base_url}/coinpayments/withdraw", 
                                       json=coinpayments_payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_test("Authenticated CoinPayments - Withdrawal", True, 
                                    f"✅ COINPAYMENTS WITHDRAWAL WORKING: {data}")
                    else:
                        message = data.get("message", "")
                        if "insufficient" in message.lower():
                            self.log_test("Authenticated CoinPayments - Withdrawal", True, 
                                        f"✅ COINPAYMENTS ENDPOINT WORKING (insufficient balance): {message}")
                        else:
                            self.log_test("Authenticated CoinPayments - Withdrawal", False, 
                                        f"❌ COINPAYMENTS WITHDRAWAL FAILED: {data}")
                elif response.status == 404:
                    self.log_test("Authenticated CoinPayments - Withdrawal", False, 
                                "❌ CRITICAL: CoinPayments withdrawal endpoint missing")
                else:
                    error_text = await response.text()
                    self.log_test("Authenticated CoinPayments - Withdrawal", False, 
                                f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Authenticated CoinPayments - Withdrawal", False, f"Error: {str(e)}")

    async def test_gaming_balance_transfer(self):
        """Test gaming balance transfer functionality"""
        try:
            # First check current balances
            async with self.session.get(f"{self.base_url}/wallet/{self.user_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        gaming_balance = wallet.get("gaming_balance", {})
                        
                        crt_deposit = deposit_balance.get("CRT", 0)
                        crt_gaming = gaming_balance.get("CRT", 0)
                        
                        self.log_test("Gaming Balance - Current Balances", True, 
                                    f"Deposit CRT: {crt_deposit}, Gaming CRT: {crt_gaming}")
                        
                        # Test if user has sufficient balance for gaming
                        if crt_deposit > 100 or crt_gaming > 100:
                            self.log_test("Gaming Balance - Sufficient Funds", True, 
                                        f"✅ GAMING BALANCE FUNCTIONAL: User has funds for gaming")
                        else:
                            self.log_test("Gaming Balance - Sufficient Funds", False, 
                                        f"❌ GAMING BALANCE ISSUE: Insufficient funds (Deposit: {crt_deposit}, Gaming: {crt_gaming})")
                    else:
                        self.log_test("Gaming Balance - Current Balances", False, 
                                    f"Failed to get wallet info: {data}")
                else:
                    self.log_test("Gaming Balance - Current Balances", False, 
                                f"HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("Gaming Balance - Current Balances", False, f"Error: {str(e)}")

    async def run_authenticated_tests(self):
        """Run all authenticated bug tests"""
        print("🔐 STARTING AUTHENTICATED BUG INVESTIGATION")
        print(f"User: {self.username} ({self.user_wallet})")
        print("=" * 80)
        
        # Get JWT token first
        jwt_success = await self.get_jwt_token()
        if not jwt_success:
            print("❌ CRITICAL: Cannot obtain JWT token - some tests will be limited")
        
        # Run authenticated tests
        await self.test_authenticated_savings_endpoint()
        await self.test_authenticated_game_betting()
        await self.test_authenticated_coinpayments_withdrawal()
        await self.test_gaming_balance_transfer()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate investigation summary"""
        print("\n" + "=" * 80)
        print("🔐 AUTHENTICATED BUG INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({failed_tests} failed)")
        
        # Key findings
        print("\n🔍 KEY FINDINGS:")
        
        for result in self.test_results:
            if "✅" in result["details"] or "❌" in result["details"]:
                print(f"  {result['details']}")
        
        print("\n📋 FINAL ASSESSMENT:")
        
        # Determine which bugs are actually broken
        critical_issues = []
        working_systems = []
        
        for result in self.test_results:
            if not result["success"] and "CRITICAL" in result["details"]:
                critical_issues.append(result["test"])
            elif result["success"] and ("WORKING" in result["details"] or "READY" in result["details"]):
                working_systems.append(result["test"])
        
        if critical_issues:
            print(f"🚨 CRITICAL ISSUES CONFIRMED: {len(critical_issues)} systems broken")
            for issue in critical_issues:
                print(f"  - {issue}")
        
        if working_systems:
            print(f"✅ WORKING SYSTEMS: {len(working_systems)} systems functional")
            for system in working_systems:
                print(f"  - {system}")
        
        print("\n" + "=" * 80)

async def main():
    """Main function to run authenticated bug investigation"""
    async with AuthenticatedBugTester(BACKEND_URL) as tester:
        await tester.run_authenticated_tests()

if __name__ == "__main__":
    asyncio.run(main())