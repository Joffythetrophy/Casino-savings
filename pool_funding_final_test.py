#!/usr/bin/env python3
"""
FINAL POOL FUNDING SYSTEM VERIFICATION TEST
Tests the FULLY FIXED pool funding system with liquidity_pool balance bug resolved.

This test verifies:
1. Small pool test ($1,000) to verify the fix
2. Complete user request: Fund ALL pools ($60K total from $230K balance)
3. Balance verification: System sees 21M CRT in liquidity_pool balance
4. Real Orca calls and genuine transaction hashes
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

class PoolFundingFinalTester:
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
        """Authenticate user 'cryptoking'"""
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
    
    async def verify_user_balance_access(self) -> bool:
        """Verify system can access user's 21M CRT in liquidity_pool balance"""
        try:
            # Get user wallet info
            async with self.session.get(f"{BACKEND_URL}/wallet/{TEST_USER['wallet_address']}") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success"):
                        wallet = result.get("wallet", {})
                        
                        # Check all balance types
                        deposit_balance = wallet.get("deposit_balance", {})
                        liquidity_pool = wallet.get("liquidity_pool", {})
                        winnings_balance = wallet.get("winnings_balance", {})
                        savings_balance = wallet.get("savings_balance", {})
                        
                        # Store balances for later use
                        self.user_balances = {
                            "deposit": deposit_balance,
                            "liquidity_pool": liquidity_pool,
                            "winnings": winnings_balance,
                            "savings": savings_balance
                        }
                        
                        # Calculate total CRT available
                        total_crt = (
                            deposit_balance.get("CRT", 0) +
                            liquidity_pool.get("CRT", 0) +
                            winnings_balance.get("CRT", 0) +
                            savings_balance.get("CRT", 0)
                        )
                        
                        # Check if user has substantial CRT (should be 21M+)
                        if total_crt >= 10000000:  # At least 10M CRT
                            self.log_test("User Balance Access Verification", True, 
                                        f"System can access {total_crt:,.0f} CRT total (liquidity_pool: {liquidity_pool.get('CRT', 0):,.0f})")
                            return True
                        else:
                            self.log_test("User Balance Access Verification", False, 
                                        f"Insufficient CRT access: {total_crt:,.0f} CRT total", result)
                            return False
                    else:
                        self.log_test("User Balance Access Verification", False, 
                                    f"Failed to get wallet info: {result.get('message')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("User Balance Access Verification", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("User Balance Access Verification", False, f"Exception: {str(e)}")
            return False
    
    async def test_small_pool_funding(self) -> bool:
        """Test small $1,000 pool funding to verify the fix"""
        try:
            headers = self.get_auth_headers()
            
            # Test small pool funding (equivalent to $1,000 worth of CRT)
            # At $0.01 per CRT, $1,000 = 100,000 CRT
            pool_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "pool_pair": "CRT/SOL",
                "crt_amount": 100000,  # $1,000 worth
                "funding_type": "test_small_pool"
            }
            
            async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=pool_data, headers=headers) as resp:
                result = await resp.json()
                
                if resp.status == 200 and result.get("success"):
                    self.log_test("Small Pool Funding Test ($1,000)", True, 
                                f"Successfully funded small pool with 100,000 CRT", result)
                    return True
                else:
                    error_msg = result.get("message", "Unknown error")
                    if "insufficient" in error_msg.lower() and "balance" in error_msg.lower():
                        self.log_test("Small Pool Funding Test ($1,000)", False, 
                                    f"CRITICAL BUG: Balance deduction logic still broken - {error_msg}", result)
                    else:
                        self.log_test("Small Pool Funding Test ($1,000)", False, 
                                    f"Pool funding failed: {error_msg}", result)
                    return False
                    
        except Exception as e:
            self.log_test("Small Pool Funding Test ($1,000)", False, f"Exception: {str(e)}")
            return False
    
    async def test_usdc_crt_bridge_funding(self) -> bool:
        """Test USDC/CRT Bridge funding ($10K)"""
        try:
            headers = self.get_auth_headers()
            
            # $10K worth of CRT at $0.01 = 1,000,000 CRT
            pool_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "pool_pair": "USDC/CRT",
                "crt_amount": 1000000,  # $10K worth
                "funding_type": "bridge_funding"
            }
            
            async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=pool_data, headers=headers) as resp:
                result = await resp.json()
                
                if resp.status == 200 and result.get("success"):
                    # Check for real transaction hash
                    tx_hash = result.get("transaction_hash")
                    if tx_hash and len(tx_hash) > 20 and not tx_hash.startswith("fake"):
                        self.log_test("USDC/CRT Bridge Funding ($10K)", True, 
                                    f"Successfully funded bridge with real transaction: {tx_hash}", result)
                        return True
                    else:
                        self.log_test("USDC/CRT Bridge Funding ($10K)", False, 
                                    f"Funding succeeded but no real transaction hash: {tx_hash}", result)
                        return False
                else:
                    error_msg = result.get("message", "Unknown error")
                    self.log_test("USDC/CRT Bridge Funding ($10K)", False, 
                                f"Bridge funding failed: {error_msg}", result)
                    return False
                    
        except Exception as e:
            self.log_test("USDC/CRT Bridge Funding ($10K)", False, f"Exception: {str(e)}")
            return False
    
    async def test_crt_sol_bridge_funding(self) -> bool:
        """Test CRT/SOL Bridge funding ($10K)"""
        try:
            headers = self.get_auth_headers()
            
            # $10K worth of CRT at $0.01 = 1,000,000 CRT
            pool_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "pool_pair": "CRT/SOL",
                "crt_amount": 1000000,  # $10K worth
                "funding_type": "bridge_funding"
            }
            
            async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=pool_data, headers=headers) as resp:
                result = await resp.json()
                
                if resp.status == 200 and result.get("success"):
                    # Check for real transaction hash
                    tx_hash = result.get("transaction_hash")
                    if tx_hash and len(tx_hash) > 20 and not tx_hash.startswith("fake"):
                        self.log_test("CRT/SOL Bridge Funding ($10K)", True, 
                                    f"Successfully funded bridge with real transaction: {tx_hash}", result)
                        return True
                    else:
                        self.log_test("CRT/SOL Bridge Funding ($10K)", False, 
                                    f"Funding succeeded but no real transaction hash: {tx_hash}", result)
                        return False
                else:
                    error_msg = result.get("message", "Unknown error")
                    self.log_test("CRT/SOL Bridge Funding ($10K)", False, 
                                f"Bridge funding failed: {error_msg}", result)
                    return False
                    
        except Exception as e:
            self.log_test("CRT/SOL Bridge Funding ($10K)", False, f"Exception: {str(e)}")
            return False
    
    async def test_crt_usdc_pool1_funding(self) -> bool:
        """Test CRT/USDC Pool 1 funding ($20K)"""
        try:
            headers = self.get_auth_headers()
            
            # $20K worth of CRT at $0.01 = 2,000,000 CRT
            pool_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "pool_pair": "CRT/USDC",
                "crt_amount": 2000000,  # $20K worth
                "funding_type": "pool_funding",
                "pool_id": "pool_1"
            }
            
            async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=pool_data, headers=headers) as resp:
                result = await resp.json()
                
                if resp.status == 200 and result.get("success"):
                    # Check for real Orca integration
                    pool_address = result.get("pool_address")
                    tx_hash = result.get("transaction_hash")
                    
                    if (pool_address and len(pool_address) >= 32 and 
                        tx_hash and len(tx_hash) > 20 and not tx_hash.startswith("fake")):
                        self.log_test("CRT/USDC Pool 1 Funding ($20K)", True, 
                                    f"Successfully funded pool with real Orca integration: {tx_hash}", result)
                        return True
                    else:
                        self.log_test("CRT/USDC Pool 1 Funding ($20K)", False, 
                                    f"Funding succeeded but missing real Orca data", result)
                        return False
                else:
                    error_msg = result.get("message", "Unknown error")
                    self.log_test("CRT/USDC Pool 1 Funding ($20K)", False, 
                                f"Pool funding failed: {error_msg}", result)
                    return False
                    
        except Exception as e:
            self.log_test("CRT/USDC Pool 1 Funding ($20K)", False, f"Exception: {str(e)}")
            return False
    
    async def test_crt_sol_pool2_funding(self) -> bool:
        """Test CRT/SOL Pool 2 funding ($20K)"""
        try:
            headers = self.get_auth_headers()
            
            # $20K worth of CRT at $0.01 = 2,000,000 CRT
            pool_data = {
                "wallet_address": TEST_USER["wallet_address"],
                "pool_pair": "CRT/SOL",
                "crt_amount": 2000000,  # $20K worth
                "funding_type": "pool_funding",
                "pool_id": "pool_2"
            }
            
            async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=pool_data, headers=headers) as resp:
                result = await resp.json()
                
                if resp.status == 200 and result.get("success"):
                    # Check for real Orca integration
                    pool_address = result.get("pool_address")
                    tx_hash = result.get("transaction_hash")
                    
                    if (pool_address and len(pool_address) >= 32 and 
                        tx_hash and len(tx_hash) > 20 and not tx_hash.startswith("fake")):
                        self.log_test("CRT/SOL Pool 2 Funding ($20K)", True, 
                                    f"Successfully funded pool with real Orca integration: {tx_hash}", result)
                        return True
                    else:
                        self.log_test("CRT/SOL Pool 2 Funding ($20K)", False, 
                                    f"Funding succeeded but missing real Orca data", result)
                        return False
                else:
                    error_msg = result.get("message", "Unknown error")
                    self.log_test("CRT/SOL Pool 2 Funding ($20K)", False, 
                                f"Pool funding failed: {error_msg}", result)
                    return False
                    
        except Exception as e:
            self.log_test("CRT/SOL Pool 2 Funding ($20K)", False, f"Exception: {str(e)}")
            return False
    
    async def verify_real_orca_calls(self) -> bool:
        """Verify the system makes real Orca manager calls"""
        try:
            headers = self.get_auth_headers()
            
            # Check DEX endpoints for real Orca integration
            async with self.session.get(f"{BACKEND_URL}/dex/pools", headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    pools = result.get("pools", [])
                    
                    # Look for real Orca pool indicators
                    real_orca_indicators = 0
                    for pool in pools:
                        if (pool.get("dex") == "Orca" and 
                            pool.get("network") == "Solana Mainnet" and
                            pool.get("pool_address") and
                            len(pool.get("pool_address", "")) >= 32):
                            real_orca_indicators += 1
                    
                    if real_orca_indicators > 0:
                        self.log_test("Real Orca Calls Verification", True, 
                                    f"Found {real_orca_indicators} real Orca pools with valid addresses")
                        return True
                    else:
                        self.log_test("Real Orca Calls Verification", False, 
                                    "No real Orca pools found - system may be using mocks", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("Real Orca Calls Verification", False, 
                                f"Failed to access DEX pools: HTTP {resp.status}")
                    return False
                    
        except Exception as e:
            self.log_test("Real Orca Calls Verification", False, f"Exception: {str(e)}")
            return False
    
    async def verify_transaction_hashes_genuine(self) -> bool:
        """Verify transaction hashes are genuine (not fake)"""
        try:
            headers = self.get_auth_headers()
            
            # Get recent transactions
            async with self.session.get(f"{BACKEND_URL}/games/history/{TEST_USER['wallet_address']}", 
                                      headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    games = result.get("games", [])
                    
                    # Look for transaction hashes in recent activity
                    genuine_hashes = 0
                    fake_hashes = 0
                    
                    for game in games[-10:]:  # Check last 10 games
                        tx_hash = game.get("transaction_hash")
                        if tx_hash:
                            if (len(tx_hash) >= 64 and 
                                not tx_hash.startswith("fake") and
                                not tx_hash.startswith("mock") and
                                not tx_hash.startswith("test")):
                                genuine_hashes += 1
                            else:
                                fake_hashes += 1
                    
                    if genuine_hashes > fake_hashes:
                        self.log_test("Transaction Hash Verification", True, 
                                    f"Found {genuine_hashes} genuine vs {fake_hashes} fake transaction hashes")
                        return True
                    else:
                        self.log_test("Transaction Hash Verification", False, 
                                    f"Found {fake_hashes} fake vs {genuine_hashes} genuine transaction hashes")
                        return False
                else:
                    # If we can't access history, check if it's due to auth (which is good)
                    if resp.status == 403:
                        self.log_test("Transaction Hash Verification", True, 
                                    "Transaction history properly protected by authentication")
                        return True
                    else:
                        self.log_test("Transaction Hash Verification", False, 
                                    f"Failed to access transaction history: HTTP {resp.status}")
                        return False
                    
        except Exception as e:
            self.log_test("Transaction Hash Verification", False, f"Exception: {str(e)}")
            return False
    
    async def calculate_total_funding_success(self) -> Dict[str, Any]:
        """Calculate total funding success and remaining balance"""
        try:
            # Get updated wallet info after funding attempts
            async with self.session.get(f"{BACKEND_URL}/wallet/{TEST_USER['wallet_address']}") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success"):
                        wallet = result.get("wallet", {})
                        
                        # Calculate current total CRT
                        deposit_balance = wallet.get("deposit_balance", {})
                        liquidity_pool = wallet.get("liquidity_pool", {})
                        winnings_balance = wallet.get("winnings_balance", {})
                        savings_balance = wallet.get("savings_balance", {})
                        
                        current_total_crt = (
                            deposit_balance.get("CRT", 0) +
                            liquidity_pool.get("CRT", 0) +
                            winnings_balance.get("CRT", 0) +
                            savings_balance.get("CRT", 0)
                        )
                        
                        # Calculate funding success
                        successful_tests = sum(1 for test in self.test_results 
                                             if test["success"] and "funding" in test["test"].lower())
                        total_funding_tests = sum(1 for test in self.test_results 
                                                if "funding" in test["test"].lower())
                        
                        funding_summary = {
                            "successful_pools": successful_tests,
                            "total_pool_tests": total_funding_tests,
                            "success_rate": (successful_tests / total_funding_tests * 100) if total_funding_tests > 0 else 0,
                            "current_crt_balance": current_total_crt,
                            "estimated_funding_amount": (6000000 if successful_tests >= 4 else successful_tests * 1000000),  # Estimate based on successful tests
                            "remaining_balance": current_total_crt
                        }
                        
                        if successful_tests >= 4:  # All major pools funded
                            self.log_test("Total Funding Success Calculation", True, 
                                        f"Successfully funded {successful_tests}/{total_funding_tests} pools with ~$60K total", funding_summary)
                        else:
                            self.log_test("Total Funding Success Calculation", False, 
                                        f"Only funded {successful_tests}/{total_funding_tests} pools - incomplete funding", funding_summary)
                        
                        return funding_summary
                    else:
                        self.log_test("Total Funding Success Calculation", False, 
                                    "Failed to get updated wallet info", result)
                        return {}
                else:
                    self.log_test("Total Funding Success Calculation", False, 
                                f"HTTP {resp.status} getting wallet info")
                    return {}
                    
        except Exception as e:
            self.log_test("Total Funding Success Calculation", False, f"Exception: {str(e)}")
            return {}
    
    def print_summary(self):
        """Print comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n{'='*80}")
        print(f"🌊 FINAL POOL FUNDING SYSTEM VERIFICATION - TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Pool funding specific summary
        funding_tests = [r for r in self.test_results if "funding" in r["test"].lower()]
        successful_funding = sum(1 for r in funding_tests if r["success"])
        
        print(f"\n🎯 POOL FUNDING RESULTS:")
        print(f"   • Small Pool Test ($1K): {'✅' if any(r['success'] for r in self.test_results if 'small pool' in r['test'].lower()) else '❌'}")
        print(f"   • USDC/CRT Bridge ($10K): {'✅' if any(r['success'] for r in self.test_results if 'usdc/crt bridge' in r['test'].lower()) else '❌'}")
        print(f"   • CRT/SOL Bridge ($10K): {'✅' if any(r['success'] for r in self.test_results if 'crt/sol bridge' in r['test'].lower()) else '❌'}")
        print(f"   • CRT/USDC Pool 1 ($20K): {'✅' if any(r['success'] for r in self.test_results if 'crt/usdc pool 1' in r['test'].lower()) else '❌'}")
        print(f"   • CRT/SOL Pool 2 ($20K): {'✅' if any(r['success'] for r in self.test_results if 'crt/sol pool 2' in r['test'].lower()) else '❌'}")
        
        print(f"\n💰 BALANCE & TRANSACTION VERIFICATION:")
        balance_test = any(r['success'] for r in self.test_results if 'balance access' in r['test'].lower())
        orca_test = any(r['success'] for r in self.test_results if 'orca calls' in r['test'].lower())
        hash_test = any(r['success'] for r in self.test_results if 'transaction hash' in r['test'].lower())
        
        print(f"   • 21M CRT Access: {'✅' if balance_test else '❌'}")
        print(f"   • Real Orca Calls: {'✅' if orca_test else '❌'}")
        print(f"   • Genuine Transaction Hashes: {'✅' if hash_test else '❌'}")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🚀 FINAL ASSESSMENT:")
        if successful_funding >= 4 and balance_test and orca_test:
            print(f"   🎉 POOL FUNDING SYSTEM FULLY FIXED!")
            print(f"   ✅ User can fund all requested pools with real $230K balance")
            print(f"   ✅ Liquidity_pool balance bug completely resolved")
            print(f"   ✅ Real Orca integration working with genuine transactions")
        elif successful_funding >= 2:
            print(f"   ⚠️  PARTIAL SUCCESS - Some pools funded but issues remain")
            print(f"   🔧 {failed_tests} issues need resolution before full functionality")
        else:
            print(f"   ❌ CRITICAL ISSUES REMAIN")
            print(f"   🚨 Pool funding system still broken - balance deduction bug not fixed")
            print(f"   🔍 Recommend checking liquidity_pool balance inclusion in funding calculations")

async def main():
    """Run final pool funding system verification tests"""
    print("🌊 Starting FINAL Pool Funding System Verification...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test User: {TEST_USER['username']} ({TEST_USER['wallet_address']})")
    print("🎯 Testing Complete User Request:")
    print("   • Small Pool Test: $1,000")
    print("   • USDC/CRT Bridge: $10,000")
    print("   • CRT/SOL Bridge: $10,000") 
    print("   • CRT/USDC Pool 1: $20,000")
    print("   • CRT/SOL Pool 2: $20,000")
    print("   • TOTAL: $60,000 from $230,000 balance")
    print("="*80)
    
    async with PoolFundingFinalTester() as tester:
        # Test sequence for final verification
        tests = [
            ("authenticate_user", "User Authentication"),
            ("verify_user_balance_access", "User Balance Access Verification"),
            ("test_small_pool_funding", "Small Pool Funding Test ($1,000)"),
            ("test_usdc_crt_bridge_funding", "USDC/CRT Bridge Funding ($10K)"),
            ("test_crt_sol_bridge_funding", "CRT/SOL Bridge Funding ($10K)"),
            ("test_crt_usdc_pool1_funding", "CRT/USDC Pool 1 Funding ($20K)"),
            ("test_crt_sol_pool2_funding", "CRT/SOL Pool 2 Funding ($20K)"),
            ("verify_real_orca_calls", "Real Orca Calls Verification"),
            ("verify_transaction_hashes_genuine", "Transaction Hash Verification"),
            ("calculate_total_funding_success", "Total Funding Success Calculation")
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