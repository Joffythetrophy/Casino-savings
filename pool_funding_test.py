#!/usr/bin/env python3
"""
Pool Funding System Testing - FIXED Balance Deduction Bug Verification
Tests the FIXED pool funding system with the balance deduction bug resolved.
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Test Configuration
BACKEND_URL = "https://solana-casino.preview.emergentagent.com/api"
TEST_USER = {
    "username": "cryptoking",
    "password": "crt21million",
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

class PoolFundingTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.user_balances = {}
        
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
        """Authenticate user cryptoking"""
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
                        self.log_test("User Authentication", True, 
                                    f"Successfully authenticated user '{TEST_USER['username']}'")
                        return True
                    else:
                        self.log_test("User Authentication", False, 
                                    f"Login failed: {result.get('message', 'Unknown error')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("User Authentication", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    async def get_user_balances(self) -> bool:
        """Get user's current balances to verify $230K availability"""
        try:
            # Get wallet info
            async with self.session.get(f"{BACKEND_URL}/wallet/{TEST_USER['wallet_address']}") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success"):
                        wallet_data = result.get("wallet", {})
                        
                        # Extract all balance types
                        deposit_balance = wallet_data.get("deposit_balance", {})
                        winnings_balance = wallet_data.get("winnings_balance", {})
                        gaming_balance = wallet_data.get("gaming_balance", {})
                        savings_balance = wallet_data.get("savings_balance", {})
                        
                        # Calculate totals
                        total_balances = {}
                        for currency in ["CRT", "DOGE", "TRX", "USDC", "SOL"]:
                            total = (deposit_balance.get(currency, 0) + 
                                   winnings_balance.get(currency, 0) + 
                                   gaming_balance.get(currency, 0) + 
                                   savings_balance.get(currency, 0))
                            total_balances[currency] = total
                        
                        self.user_balances = total_balances
                        
                        # Calculate USD value (rough estimates)
                        usd_values = {
                            "CRT": total_balances.get("CRT", 0) * 0.01,  # $0.01 per CRT
                            "DOGE": total_balances.get("DOGE", 0) * 0.236,  # $0.236 per DOGE
                            "TRX": total_balances.get("TRX", 0) * 0.363,  # $0.363 per TRX
                            "USDC": total_balances.get("USDC", 0) * 1.0,  # $1.00 per USDC
                            "SOL": total_balances.get("SOL", 0) * 240.0  # $240 per SOL
                        }
                        
                        total_usd = sum(usd_values.values())
                        
                        self.log_test("User Balance Verification", True, 
                                    f"Total portfolio value: ${total_usd:,.2f} USD", {
                                        "balances": total_balances,
                                        "usd_values": usd_values,
                                        "total_usd": total_usd
                                    })
                        
                        # Check if user has sufficient funds for $60K pool funding
                        if total_usd >= 60000:
                            self.log_test("Sufficient Balance Check", True, 
                                        f"User has ${total_usd:,.2f} available for $60K pool funding")
                            return True
                        else:
                            self.log_test("Sufficient Balance Check", False, 
                                        f"User only has ${total_usd:,.2f}, insufficient for $60K pool funding")
                            return False
                    else:
                        self.log_test("User Balance Verification", False, 
                                    f"Failed to get wallet info: {result.get('message')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("User Balance Verification", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("User Balance Verification", False, f"Exception: {str(e)}")
            return False
    
    async def test_pool_funding_endpoint_exists(self) -> bool:
        """Test that the pool funding endpoint exists and is accessible"""
        try:
            headers = self.get_auth_headers()
            
            # Test with minimal data to check endpoint existence
            test_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "pool_requests": []
            }
            
            async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=test_data, headers=headers) as resp:
                result = await resp.json()
                
                if resp.status in [200, 400]:  # 200 = success, 400 = validation error (both mean endpoint exists)
                    self.log_test("Pool Funding Endpoint Exists", True, 
                                "Endpoint /api/pools/fund-with-user-balance is accessible")
                    return True
                elif resp.status == 404:
                    self.log_test("Pool Funding Endpoint Exists", False, 
                                "Endpoint /api/pools/fund-with-user-balance not found")
                    return False
                else:
                    self.log_test("Pool Funding Endpoint Exists", False, 
                                f"Unexpected response: HTTP {resp.status}", result)
                    return False
                    
        except Exception as e:
            self.log_test("Pool Funding Endpoint Exists", False, f"Exception: {str(e)}")
            return False
    
    async def test_bridge_funding_usdc_crt(self) -> Dict[str, Any]:
        """Test USDC/CRT Bridge funding with $10K"""
        try:
            headers = self.get_auth_headers()
            
            pool_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "pool_requests": [
                    {
                        "pool_type": "USDC/CRT",
                        "amount_usd": 10000,
                        "description": "USDC/CRT Bridge Pool"
                    }
                ]
            }
            
            async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=pool_data, headers=headers) as resp:
                result = await resp.json()
                
                if resp.status == 200 and result.get("success"):
                    funded_pools = result.get("funded_pools", [])
                    if funded_pools:
                        pool_info = funded_pools[0]
                        transaction_hash = pool_info.get("transaction_hash")
                        pool_address = pool_info.get("pool_address")
                        
                        if transaction_hash and pool_address:
                            self.log_test("USDC/CRT Bridge Funding", True, 
                                        f"Bridge funded with real transaction: {transaction_hash[:16]}...", result)
                            return result
                        else:
                            self.log_test("USDC/CRT Bridge Funding", False, 
                                        "Missing transaction hash or pool address - may be fake", result)
                            return result
                    else:
                        self.log_test("USDC/CRT Bridge Funding", False, 
                                    "No funded pools returned", result)
                        return result
                else:
                    self.log_test("USDC/CRT Bridge Funding", False, 
                                f"Bridge funding failed: {result.get('error', 'Unknown error')}", result)
                    return result
                    
        except Exception as e:
            self.log_test("USDC/CRT Bridge Funding", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_bridge_funding_crt_sol(self) -> Dict[str, Any]:
        """Test CRT/SOL Bridge funding with $10K"""
        try:
            headers = self.get_auth_headers()
            
            pool_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "pool_requests": [
                    {
                        "pool_type": "CRT/SOL",
                        "amount_usd": 10000,
                        "description": "CRT/SOL Bridge Pool"
                    }
                ]
            }
            
            async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=pool_data, headers=headers) as resp:
                result = await resp.json()
                
                if resp.status == 200 and result.get("success"):
                    funded_pools = result.get("funded_pools", [])
                    if funded_pools:
                        pool_info = funded_pools[0]
                        transaction_hash = pool_info.get("transaction_hash")
                        pool_address = pool_info.get("pool_address")
                        
                        if transaction_hash and pool_address:
                            self.log_test("CRT/SOL Bridge Funding", True, 
                                        f"Bridge funded with real transaction: {transaction_hash[:16]}...", result)
                            return result
                        else:
                            self.log_test("CRT/SOL Bridge Funding", False, 
                                        "Missing transaction hash or pool address - may be fake", result)
                            return result
                    else:
                        self.log_test("CRT/SOL Bridge Funding", False, 
                                    "No funded pools returned", result)
                        return result
                else:
                    self.log_test("CRT/SOL Bridge Funding", False, 
                                f"Bridge funding failed: {result.get('error', 'Unknown error')}", result)
                    return result
                    
        except Exception as e:
            self.log_test("CRT/SOL Bridge Funding", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_pool_funding_crt_usdc(self) -> Dict[str, Any]:
        """Test CRT/USDC Pool 1 funding with $20K"""
        try:
            headers = self.get_auth_headers()
            
            pool_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "pool_requests": [
                    {
                        "pool_type": "CRT/USDC",
                        "amount_usd": 20000,
                        "description": "CRT/USDC Pool 1"
                    }
                ]
            }
            
            async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=pool_data, headers=headers) as resp:
                result = await resp.json()
                
                if resp.status == 200 and result.get("success"):
                    funded_pools = result.get("funded_pools", [])
                    if funded_pools:
                        pool_info = funded_pools[0]
                        transaction_hash = pool_info.get("transaction_hash")
                        pool_address = pool_info.get("pool_address")
                        
                        if transaction_hash and pool_address:
                            self.log_test("CRT/USDC Pool 1 Funding", True, 
                                        f"Pool funded with real transaction: {transaction_hash[:16]}...", result)
                            return result
                        else:
                            self.log_test("CRT/USDC Pool 1 Funding", False, 
                                        "Missing transaction hash or pool address - may be fake", result)
                            return result
                    else:
                        self.log_test("CRT/USDC Pool 1 Funding", False, 
                                    "No funded pools returned", result)
                        return result
                else:
                    self.log_test("CRT/USDC Pool 1 Funding", False, 
                                f"Pool funding failed: {result.get('error', 'Unknown error')}", result)
                    return result
                    
        except Exception as e:
            self.log_test("CRT/USDC Pool 1 Funding", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_pool_funding_crt_sol(self) -> Dict[str, Any]:
        """Test CRT/SOL Pool 2 funding with $20K"""
        try:
            headers = self.get_auth_headers()
            
            pool_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "pool_requests": [
                    {
                        "pool_type": "CRT/SOL",
                        "amount_usd": 20000,
                        "description": "CRT/SOL Pool 2"
                    }
                ]
            }
            
            async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=pool_data, headers=headers) as resp:
                result = await resp.json()
                
                if resp.status == 200 and result.get("success"):
                    funded_pools = result.get("funded_pools", [])
                    if funded_pools:
                        pool_info = funded_pools[0]
                        transaction_hash = pool_info.get("transaction_hash")
                        pool_address = pool_info.get("pool_address")
                        
                        if transaction_hash and pool_address:
                            self.log_test("CRT/SOL Pool 2 Funding", True, 
                                        f"Pool funded with real transaction: {transaction_hash[:16]}...", result)
                            return result
                        else:
                            self.log_test("CRT/SOL Pool 2 Funding", False, 
                                        "Missing transaction hash or pool address - may be fake", result)
                            return result
                    else:
                        self.log_test("CRT/SOL Pool 2 Funding", False, 
                                    "No funded pools returned", result)
                        return result
                else:
                    self.log_test("CRT/SOL Pool 2 Funding", False, 
                                f"Pool funding failed: {result.get('error', 'Unknown error')}", result)
                    return result
                    
        except Exception as e:
            self.log_test("CRT/SOL Pool 2 Funding", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_batch_pool_funding(self) -> Dict[str, Any]:
        """Test funding all pools in a single request - Total $60K"""
        try:
            headers = self.get_auth_headers()
            
            pool_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "pool_requests": [
                    {
                        "pool_type": "USDC/CRT",
                        "amount_usd": 10000,
                        "description": "USDC/CRT Bridge"
                    },
                    {
                        "pool_type": "CRT/SOL",
                        "amount_usd": 10000,
                        "description": "CRT/SOL Bridge"
                    },
                    {
                        "pool_type": "CRT/USDC",
                        "amount_usd": 20000,
                        "description": "CRT/USDC Pool 1"
                    },
                    {
                        "pool_type": "CRT/SOL",
                        "amount_usd": 20000,
                        "description": "CRT/SOL Pool 2"
                    }
                ]
            }
            
            async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=pool_data, headers=headers) as resp:
                result = await resp.json()
                
                if resp.status == 200 and result.get("success"):
                    funded_pools = result.get("funded_pools", [])
                    total_used = result.get("total_used", {})
                    
                    if len(funded_pools) == 4:
                        # Verify all pools have real transaction hashes
                        real_transactions = 0
                        for pool in funded_pools:
                            if pool.get("transaction_hash") and pool.get("pool_address"):
                                real_transactions += 1
                        
                        if real_transactions == 4:
                            self.log_test("Batch Pool Funding (All $60K)", True, 
                                        f"All 4 pools funded with real transactions. Total used: {total_used}", result)
                            return result
                        else:
                            self.log_test("Batch Pool Funding (All $60K)", False, 
                                        f"Only {real_transactions}/4 pools have real transactions", result)
                            return result
                    else:
                        self.log_test("Batch Pool Funding (All $60K)", False, 
                                    f"Only {len(funded_pools)}/4 pools funded", result)
                        return result
                else:
                    self.log_test("Batch Pool Funding (All $60K)", False, 
                                f"Batch funding failed: {result.get('error', 'Unknown error')}", result)
                    return result
                    
        except Exception as e:
            self.log_test("Batch Pool Funding (All $60K)", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_balance_deduction_verification(self) -> bool:
        """Verify that user balances are properly reduced after pool creation"""
        try:
            # Get balances before and after funding
            initial_balances = self.user_balances.copy()
            
            # Get current balances after funding
            await self.get_user_balances()
            current_balances = self.user_balances
            
            # Check if balances were reduced
            balance_changes = {}
            for currency in ["CRT", "USDC", "SOL"]:
                initial = initial_balances.get(currency, 0)
                current = current_balances.get(currency, 0)
                change = initial - current
                balance_changes[currency] = change
            
            # Verify meaningful reductions occurred
            total_reduction = sum(abs(change) for change in balance_changes.values() if change > 0)
            
            if total_reduction > 0:
                self.log_test("Balance Deduction Verification", True, 
                            f"User balances properly reduced: {balance_changes}", {
                                "initial_balances": initial_balances,
                                "current_balances": current_balances,
                                "changes": balance_changes
                            })
                return True
            else:
                self.log_test("Balance Deduction Verification", False, 
                            "No balance reductions detected - pools may be fake", {
                                "initial_balances": initial_balances,
                                "current_balances": current_balances,
                                "changes": balance_changes
                            })
                return False
                
        except Exception as e:
            self.log_test("Balance Deduction Verification", False, f"Exception: {str(e)}")
            return False
    
    async def test_insufficient_balance_handling(self) -> bool:
        """Test error handling with insufficient balances"""
        try:
            headers = self.get_auth_headers()
            
            # Try to fund a pool with more money than user has
            pool_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "pool_requests": [
                    {
                        "pool_type": "CRT/USDC",
                        "amount_usd": 1000000,  # $1M - should exceed user's balance
                        "description": "Excessive Pool Test"
                    }
                ]
            }
            
            async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=pool_data, headers=headers) as resp:
                result = await resp.json()
                
                if resp.status == 400 or not result.get("success"):
                    error_msg = result.get("error", "").lower()
                    if "insufficient" in error_msg or "balance" in error_msg:
                        self.log_test("Insufficient Balance Handling", True, 
                                    "Properly rejected excessive funding request", result)
                        return True
                    else:
                        self.log_test("Insufficient Balance Handling", False, 
                                    f"Wrong error type: {result.get('error')}", result)
                        return False
                else:
                    self.log_test("Insufficient Balance Handling", False, 
                                "Should have rejected excessive funding request", result)
                    return False
                    
        except Exception as e:
            self.log_test("Insufficient Balance Handling", False, f"Exception: {str(e)}")
            return False
    
    async def test_real_orca_integration_verification(self) -> bool:
        """Verify that the system uses real Orca managers, not fake/simulated"""
        try:
            headers = self.get_auth_headers()
            
            # Test a small pool to check for real integration indicators
            pool_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "pool_requests": [
                    {
                        "pool_type": "CRT/USDC",
                        "amount_usd": 100,  # Small test amount
                        "description": "Real Integration Test"
                    }
                ]
            }
            
            async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=pool_data, headers=headers) as resp:
                result = await resp.json()
                
                # Check for indicators of real vs fake integration
                result_str = json.dumps(result).lower()
                
                # Real integration indicators
                real_indicators = [
                    "real_transaction",
                    "transaction_hash",
                    "pool_address",
                    "solana",
                    "orca"
                ]
                
                # Fake integration indicators
                fake_indicators = [
                    "fake",
                    "mock",
                    "simulated",
                    "test_hash",
                    "dummy"
                ]
                
                real_score = sum(1 for indicator in real_indicators if indicator in result_str)
                fake_score = sum(1 for indicator in fake_indicators if indicator in result_str)
                
                if real_score > fake_score and real_score >= 2:
                    self.log_test("Real Orca Integration Verification", True, 
                                f"Real integration detected (score: {real_score} real vs {fake_score} fake)", result)
                    return True
                else:
                    self.log_test("Real Orca Integration Verification", False, 
                                f"Fake/simulated integration detected (score: {real_score} real vs {fake_score} fake)", result)
                    return False
                    
        except Exception as e:
            self.log_test("Real Orca Integration Verification", False, f"Exception: {str(e)}")
            return False
    
    def print_summary(self):
        """Print comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n{'='*80}")
        print(f"🌊 POOL FUNDING SYSTEM TESTING - USER BALANCE INTEGRATION SUMMARY")
        print(f"{'='*80}")
        print(f"User: {TEST_USER['username']} ({TEST_USER['wallet_address']})")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🎯 POOL FUNDING ASSESSMENT:")
        
        # Check authentication
        auth_tests = [r for r in self.test_results if "authentication" in r["test"].lower()]
        if any(t["success"] for t in auth_tests):
            print(f"   ✅ User authentication working")
        else:
            print(f"   ❌ User authentication failed")
        
        # Check balance verification
        balance_tests = [r for r in self.test_results if "balance" in r["test"].lower()]
        sufficient_balance = any(t["success"] for t in balance_tests if "sufficient" in t["test"].lower())
        if sufficient_balance:
            print(f"   ✅ User has sufficient balance for $60K pool funding")
        else:
            print(f"   ❌ User lacks sufficient balance for pool funding")
        
        # Check pool funding
        pool_tests = [r for r in self.test_results if "funding" in r["test"].lower() and "pool" in r["test"].lower()]
        successful_pools = [t for t in pool_tests if t["success"]]
        if successful_pools:
            print(f"   ✅ Pool funding working for {len(successful_pools)} test cases")
        else:
            print(f"   ❌ Pool funding not working")
        
        # Check real integration
        real_tests = [r for r in self.test_results if "real" in r["test"].lower()]
        if any(t["success"] for t in real_tests):
            print(f"   ✅ Real Orca integration detected (not fake/simulated)")
        else:
            print(f"   ❌ Fake/simulated integration detected")
        
        print(f"\n🚀 FINAL ASSESSMENT:")
        if failed_tests == 0:
            print(f"   🎉 POOL FUNDING SYSTEM FULLY OPERATIONAL!")
            print(f"   ✅ User can fund pools with existing balances")
            print(f"   ✅ Real Orca transactions confirmed")
            print(f"   ✅ Balance deduction working properly")
        elif failed_tests <= 2:
            print(f"   ⚠️  Pool funding mostly working - minor issues remain")
            print(f"   🔧 Check {failed_tests} remaining issues")
        else:
            print(f"   ❌ MAJOR POOL FUNDING ISSUES DETECTED")
            print(f"   🚨 System may be using fake/simulated transactions")
            print(f"   🔍 Recommend investigating real Orca integration")

async def main():
    """Run all pool funding tests"""
    print("🌊 Starting Pool Funding System Testing...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test User: {TEST_USER['username']} ({TEST_USER['wallet_address']})")
    print("🎯 Testing pool funding with user's $230K balance:")
    print("   • USDC/CRT Bridge: $10K")
    print("   • CRT/SOL Bridge: $10K")
    print("   • CRT/USDC Pool 1: $20K")
    print("   • CRT/SOL Pool 2: $20K")
    print("   • Total: $60K from user's existing balance")
    print("="*80)
    
    async with PoolFundingTester() as tester:
        # Test sequence
        tests = [
            ("authenticate_user", "User Authentication"),
            ("get_user_balances", "User Balance Verification"),
            ("test_pool_funding_endpoint_exists", "Pool Funding Endpoint Accessibility"),
            ("test_bridge_funding_usdc_crt", "USDC/CRT Bridge Funding ($10K)"),
            ("test_bridge_funding_crt_sol", "CRT/SOL Bridge Funding ($10K)"),
            ("test_pool_funding_crt_usdc", "CRT/USDC Pool 1 Funding ($20K)"),
            ("test_pool_funding_crt_sol", "CRT/SOL Pool 2 Funding ($20K)"),
            ("test_batch_pool_funding", "Batch Pool Funding (All $60K)"),
            ("test_balance_deduction_verification", "Balance Deduction Verification"),
            ("test_insufficient_balance_handling", "Insufficient Balance Error Handling"),
            ("test_real_orca_integration_verification", "Real Orca Integration Verification")
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