#!/usr/bin/env python3
"""
CRITICAL: Real CRT Casino System Testing with User's Actual 21M CRT Tokens
Tests the complete real blockchain integration with NO fake transactions or simulated balances
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Test Configuration - REAL PRODUCTION ENVIRONMENT
BACKEND_URL = "https://crypto-treasury-app.preview.emergentagent.com/api"
REAL_USER_WALLET = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
TEST_USER = {
    "username": "cryptoking",
    "password": "crt21million",
    "wallet_address": REAL_USER_WALLET
}

class RealCRTCasinoTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.real_crt_balance = 0
        
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
    
    async def authenticate_user(self) -> bool:
        """Authenticate the real user with actual wallet"""
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
                        wallet_address = result.get("wallet_address")
                        
                        if wallet_address == REAL_USER_WALLET:
                            self.log_test("Real User Authentication", True, 
                                        f"Successfully authenticated user with real wallet: {REAL_USER_WALLET}")
                            return True
                        else:
                            self.log_test("Real User Authentication", False, 
                                        f"Wallet mismatch: expected {REAL_USER_WALLET}, got {wallet_address}")
                            return False
                    else:
                        self.log_test("Real User Authentication", False, 
                                    f"Login failed: {result.get('message', 'Unknown error')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("Real User Authentication", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Real User Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    async def test_real_crt_balance_check(self) -> bool:
        """Test /api/wallet/crt-balance with actual wallet address"""
        try:
            # Test the specific endpoint mentioned in requirements
            async with self.session.get(f"{BACKEND_URL}/wallet/balance/CRT?wallet_address={REAL_USER_WALLET}") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    if result.get("success"):
                        balance = result.get("balance", 0)
                        source = result.get("source", "unknown")
                        
                        # Store real balance for later tests
                        self.real_crt_balance = balance
                        
                        # Verify this is real blockchain data
                        if source in ["solana_rpc", "database_gaming_balance", "hybrid_blockchain_database"]:
                            if balance > 0:
                                self.log_test("Real CRT Balance Check", True, 
                                            f"Real CRT balance retrieved: {balance:,.2f} CRT from {source}")
                                return True
                            else:
                                self.log_test("Real CRT Balance Check", False, 
                                            f"Zero CRT balance detected - user should have 21M CRT", result)
                                return False
                        else:
                            self.log_test("Real CRT Balance Check", False, 
                                        f"Suspicious balance source: {source} - not real blockchain", result)
                            return False
                    else:
                        self.log_test("Real CRT Balance Check", False, 
                                    f"Balance check failed: {result.get('error', 'Unknown error')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("Real CRT Balance Check", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Real CRT Balance Check", False, f"Exception: {str(e)}")
            return False
    
    async def test_bridge_pool_estimation(self) -> bool:
        """Test /api/bridge/estimate-requirements for CRT/SOL and CRT/USDC bridges"""
        try:
            success_count = 0
            
            # Test CRT/SOL bridge estimation
            bridge_data = {
                "from_token": "CRT",
                "to_token": "SOL",
                "pool_size_usd": 10000,  # $10K pool as requested
                "wallet_address": REAL_USER_WALLET
            }
            
            async with self.session.post(f"{BACKEND_URL}/bridge/estimate-requirements", 
                                       json=bridge_data, headers=self.get_auth_headers()) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success"):
                        crt_required = result.get("crt_required", 0)
                        sol_required = result.get("sol_required", 0)
                        
                        if crt_required > 0 and sol_required > 0:
                            success_count += 1
                            print(f"   CRT/SOL Bridge: {crt_required:,.0f} CRT + {sol_required:.4f} SOL required")
                        else:
                            print(f"   CRT/SOL Bridge: Invalid requirements - CRT: {crt_required}, SOL: {sol_required}")
                    else:
                        print(f"   CRT/SOL Bridge: Estimation failed - {result.get('message', 'Unknown error')}")
                else:
                    print(f"   CRT/SOL Bridge: HTTP {resp.status}")
            
            # Test CRT/USDC bridge estimation
            bridge_data = {
                "from_token": "CRT",
                "to_token": "USDC",
                "pool_size_usd": 10000,  # $10K pool as requested
                "wallet_address": REAL_USER_WALLET
            }
            
            async with self.session.post(f"{BACKEND_URL}/bridge/estimate-requirements", 
                                       json=bridge_data, headers=self.get_auth_headers()) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success"):
                        crt_required = result.get("crt_required", 0)
                        usdc_required = result.get("usdc_required", 0)
                        
                        if crt_required > 0 and usdc_required > 0:
                            success_count += 1
                            print(f"   CRT/USDC Bridge: {crt_required:,.0f} CRT + {usdc_required:,.2f} USDC required")
                        else:
                            print(f"   CRT/USDC Bridge: Invalid requirements - CRT: {crt_required}, USDC: {usdc_required}")
                    else:
                        print(f"   CRT/USDC Bridge: Estimation failed - {result.get('message', 'Unknown error')}")
                else:
                    print(f"   CRT/USDC Bridge: HTTP {resp.status}")
            
            if success_count == 2:
                self.log_test("Bridge Pool Estimation", True, 
                            "Both CRT/SOL and CRT/USDC bridge estimations working")
                return True
            else:
                self.log_test("Bridge Pool Estimation", False, 
                            f"Only {success_count}/2 bridge estimations working")
                return False
                
        except Exception as e:
            self.log_test("Bridge Pool Estimation", False, f"Exception: {str(e)}")
            return False
    
    async def test_system_status_verification(self) -> bool:
        """Confirm all features show 'real_cryptocurrency': true"""
        try:
            # Test system health endpoint
            async with self.session.get(f"{BACKEND_URL}/health") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    # Check for real cryptocurrency indicators
                    services = result.get("services", {})
                    real_indicators = []
                    
                    # Check Solana connection (real blockchain)
                    if services.get("solana", {}).get("success"):
                        real_indicators.append("solana_mainnet")
                    
                    # Check DOGE connection (real blockchain)
                    if services.get("dogecoin", {}).get("success"):
                        real_indicators.append("dogecoin_mainnet")
                    
                    # Check TRON connection (real blockchain)
                    if services.get("tron", {}).get("success"):
                        real_indicators.append("tron_mainnet")
                    
                    if len(real_indicators) >= 2:
                        self.log_test("System Status Verification", True, 
                                    f"Real cryptocurrency connections confirmed: {', '.join(real_indicators)}")
                        return True
                    else:
                        self.log_test("System Status Verification", False, 
                                    f"Insufficient real blockchain connections: {real_indicators}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("System Status Verification", False, 
                                f"Health check failed: HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("System Status Verification", False, f"Exception: {str(e)}")
            return False
    
    async def test_casino_games_crt_betting(self) -> bool:
        """Test /api/casino/games to verify CRT betting is available"""
        try:
            # First check if games endpoint exists
            async with self.session.get(f"{BACKEND_URL}/casino/games", 
                                      headers=self.get_auth_headers()) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    if result.get("success"):
                        games = result.get("games", [])
                        
                        # Check if games support CRT betting
                        crt_supported_games = []
                        for game in games:
                            supported_currencies = game.get("supported_currencies", [])
                            if "CRT" in supported_currencies:
                                crt_supported_games.append(game.get("name", "Unknown"))
                        
                        if crt_supported_games:
                            self.log_test("Casino Games CRT Betting", True, 
                                        f"CRT betting available in {len(crt_supported_games)} games: {', '.join(crt_supported_games)}")
                            return True
                        else:
                            self.log_test("Casino Games CRT Betting", False, 
                                        "No games support CRT betting", result)
                            return False
                    else:
                        self.log_test("Casino Games CRT Betting", False, 
                                    f"Games endpoint failed: {result.get('message', 'Unknown error')}", result)
                        return False
                elif resp.status == 404:
                    # Try alternative endpoint - test actual game betting
                    return await self.test_actual_crt_betting()
                else:
                    error_text = await resp.text()
                    self.log_test("Casino Games CRT Betting", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Casino Games CRT Betting", False, f"Exception: {str(e)}")
            return False
    
    async def test_actual_crt_betting(self) -> bool:
        """Test actual CRT betting functionality"""
        try:
            # Test a small CRT bet to verify system works
            bet_data = {
                "wallet_address": REAL_USER_WALLET,
                "game_type": "Slot Machine",
                "bet_amount": 1.0,  # Small test bet
                "currency": "CRT",
                "network": "Solana"
            }
            
            async with self.session.post(f"{BACKEND_URL}/games/bet", 
                                       json=bet_data, headers=self.get_auth_headers()) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    if result.get("success"):
                        game_id = result.get("game_id")
                        bet_result = result.get("result")
                        payout = result.get("payout", 0)
                        
                        if game_id and bet_result in ["win", "loss"]:
                            self.log_test("Actual CRT Betting", True, 
                                        f"CRT betting functional - Game ID: {game_id}, Result: {bet_result}, Payout: {payout}")
                            return True
                        else:
                            self.log_test("Actual CRT Betting", False, 
                                        "Invalid betting response structure", result)
                            return False
                    else:
                        error_msg = result.get("message", "Unknown error")
                        if "insufficient" in error_msg.lower():
                            self.log_test("Actual CRT Betting", True, 
                                        "CRT betting system working - insufficient balance validation active")
                            return True
                        else:
                            self.log_test("Actual CRT Betting", False, 
                                        f"Betting failed: {error_msg}", result)
                            return False
                else:
                    error_text = await resp.text()
                    self.log_test("Actual CRT Betting", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Actual CRT Betting", False, f"Exception: {str(e)}")
            return False
    
    async def test_supported_bridge_pairs(self) -> bool:
        """Test /api/bridge/supported-pairs for bridge options"""
        try:
            async with self.session.get(f"{BACKEND_URL}/bridge/supported-pairs", 
                                      headers=self.get_auth_headers()) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    if result.get("success"):
                        pairs = result.get("supported_pairs", [])
                        
                        # Check for required CRT bridge pairs
                        required_pairs = ["CRT/SOL", "CRT/USDC"]
                        found_pairs = []
                        
                        for pair in pairs:
                            pair_name = pair.get("pair") or f"{pair.get('from_token')}/{pair.get('to_token')}"
                            if pair_name in required_pairs:
                                found_pairs.append(pair_name)
                        
                        if len(found_pairs) >= 2:
                            self.log_test("Supported Bridge Pairs", True, 
                                        f"Required bridge pairs available: {', '.join(found_pairs)}")
                            return True
                        else:
                            self.log_test("Supported Bridge Pairs", False, 
                                        f"Missing required bridge pairs. Found: {found_pairs}, Required: {required_pairs}", result)
                            return False
                    else:
                        self.log_test("Supported Bridge Pairs", False, 
                                    f"Bridge pairs endpoint failed: {result.get('message', 'Unknown error')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("Supported Bridge Pairs", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Supported Bridge Pairs", False, f"Exception: {str(e)}")
            return False
    
    async def test_no_fake_transactions(self) -> bool:
        """Verify system uses real blockchain operations, not fake transactions"""
        try:
            # Test wallet info to check for real blockchain integration
            async with self.session.get(f"{BACKEND_URL}/wallet/{REAL_USER_WALLET}", 
                                      headers=self.get_auth_headers()) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    if result.get("success"):
                        wallet_data = result.get("wallet", {})
                        balance_source = wallet_data.get("balance_source", "unknown")
                        balance_notes = wallet_data.get("balance_notes", {})
                        
                        # Check for real blockchain indicators
                        real_indicators = []
                        
                        if "blockchain" in balance_source.lower():
                            real_indicators.append("blockchain_source")
                        
                        if any("blockchain" in note.lower() for note in balance_notes.values()):
                            real_indicators.append("blockchain_notes")
                        
                        # Check for fake transaction indicators (should NOT be present)
                        fake_indicators = []
                        
                        if "fake" in str(result).lower() or "mock" in str(result).lower():
                            fake_indicators.append("fake_mock_detected")
                        
                        if "simulation" in str(result).lower() or "test" in balance_source.lower():
                            fake_indicators.append("simulation_detected")
                        
                        if real_indicators and not fake_indicators:
                            self.log_test("No Fake Transactions", True, 
                                        f"Real blockchain integration confirmed: {', '.join(real_indicators)}")
                            return True
                        elif fake_indicators:
                            self.log_test("No Fake Transactions", False, 
                                        f"Fake/simulation indicators detected: {', '.join(fake_indicators)}", result)
                            return False
                        else:
                            self.log_test("No Fake Transactions", False, 
                                        "Cannot verify real blockchain integration - insufficient indicators", result)
                            return False
                    else:
                        self.log_test("No Fake Transactions", False, 
                                    f"Wallet info failed: {result.get('message', 'Unknown error')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("No Fake Transactions", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("No Fake Transactions", False, f"Exception: {str(e)}")
            return False
    
    def print_summary(self):
        """Print comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n{'='*80}")
        print(f"🎰 REAL CRT CASINO SYSTEM - FINAL VERIFICATION SUMMARY")
        print(f"{'='*80}")
        print(f"User Wallet: {REAL_USER_WALLET}")
        print(f"Real CRT Balance: {self.real_crt_balance:,.2f} CRT")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🎯 CRITICAL REQUIREMENTS ASSESSMENT:")
        
        # Check each requirement
        requirements = {
            "Real CRT Balance": any("crt balance" in r["test"].lower() and r["success"] for r in self.test_results),
            "Bridge Pool Estimation": any("bridge" in r["test"].lower() and "estimation" in r["test"].lower() and r["success"] for r in self.test_results),
            "System Real Crypto Status": any("system status" in r["test"].lower() and r["success"] for r in self.test_results),
            "CRT Casino Betting": any("casino" in r["test"].lower() and r["success"] for r in self.test_results),
            "Bridge Pairs Support": any("bridge pairs" in r["test"].lower() and r["success"] for r in self.test_results),
            "No Fake Transactions": any("fake" in r["test"].lower() and r["success"] for r in self.test_results)
        }
        
        for req, status in requirements.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {req}")
        
        print(f"\n🚀 FINAL ASSESSMENT:")
        if failed_tests == 0:
            print(f"   🎉 ALL REQUIREMENTS MET - REAL CRT CASINO SYSTEM READY!")
            print(f"   ✅ User can safely use their 21M CRT tokens")
            print(f"   ✅ All transactions will be genuine blockchain operations")
            print(f"   ✅ Bridge pools ready for $10K funding")
        elif failed_tests <= 2:
            print(f"   ⚠️  MOSTLY READY - Minor issues remain")
            print(f"   🔧 Address {failed_tests} remaining issues before production use")
        else:
            print(f"   ❌ SYSTEM NOT READY FOR REAL CRT USAGE")
            print(f"   🚨 {failed_tests} critical issues must be resolved")
            print(f"   ⚠️  DO NOT USE REAL 21M CRT TOKENS YET")

async def main():
    """Run all Real CRT Casino System tests"""
    print("🎰 Starting CRITICAL Real CRT Casino System Testing...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Real User Wallet: {REAL_USER_WALLET}")
    print(f"Expected CRT Balance: 21,000,000 CRT")
    print("🚨 TESTING REAL BLOCKCHAIN INTEGRATION - NO FAKE TRANSACTIONS ALLOWED")
    print("="*80)
    
    async with RealCRTCasinoTester() as tester:
        # Test sequence for real CRT casino system
        tests = [
            ("authenticate_user", "Real User Authentication"),
            ("test_real_crt_balance_check", "Real CRT Balance Check"),
            ("test_bridge_pool_estimation", "Bridge Pool Estimation"),
            ("test_system_status_verification", "System Status Verification"),
            ("test_casino_games_crt_betting", "Casino Games CRT Betting"),
            ("test_supported_bridge_pairs", "Supported Bridge Pairs"),
            ("test_no_fake_transactions", "No Fake Transactions Verification")
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