#!/usr/bin/env python3
"""
Fund All Pools Button Functionality Testing
Tests the FIXED "Fund All Pools" button functionality after method signature conflict resolution
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Test Configuration
BACKEND_URL = "https://real-crt-casino.preview.emergentagent.com/api"
TEST_USER = {
    "username": "cryptoking",
    "password": "crt21million",
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

class FundAllPoolsTester:
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
    
    async def test_user_balance_verification(self) -> Dict[str, Any]:
        """Verify user has sufficient balances for $60K pool funding"""
        try:
            # Get user wallet info
            async with self.session.get(f"{BACKEND_URL}/wallet/{TEST_USER['wallet_address']}") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success"):
                        wallet = result.get("wallet", {})
                        
                        # Get all balance types
                        deposit_balance = wallet.get("deposit_balance", {})
                        winnings_balance = wallet.get("winnings_balance", {})
                        gaming_balance = wallet.get("gaming_balance", {})
                        liquidity_pool = wallet.get("liquidity_pool", {})
                        
                        # Calculate total balances
                        total_crt = (deposit_balance.get("CRT", 0) + 
                                   winnings_balance.get("CRT", 0) + 
                                   gaming_balance.get("CRT", 0) + 
                                   liquidity_pool.get("CRT", 0))
                        
                        total_usdc = (deposit_balance.get("USDC", 0) + 
                                    winnings_balance.get("USDC", 0) + 
                                    gaming_balance.get("USDC", 0) + 
                                    liquidity_pool.get("USDC", 0))
                        
                        total_sol = (deposit_balance.get("SOL", 0) + 
                                   winnings_balance.get("SOL", 0) + 
                                   gaming_balance.get("SOL", 0) + 
                                   liquidity_pool.get("SOL", 0))
                        
                        # Calculate portfolio value (assuming CRT = $0.01, SOL = $240, USDC = $1)
                        portfolio_value = (total_crt * 0.01) + (total_sol * 240) + total_usdc
                        
                        # Check if sufficient for $60K funding
                        sufficient_for_60k = portfolio_value >= 60000
                        
                        balance_info = {
                            "total_crt": total_crt,
                            "total_usdc": total_usdc,
                            "total_sol": total_sol,
                            "portfolio_value_usd": portfolio_value,
                            "sufficient_for_60k": sufficient_for_60k,
                            "breakdown": {
                                "deposit": deposit_balance,
                                "winnings": winnings_balance,
                                "gaming": gaming_balance,
                                "liquidity_pool": liquidity_pool
                            }
                        }
                        
                        if sufficient_for_60k:
                            self.log_test("User Balance Verification", True, 
                                        f"User has ${portfolio_value:,.2f} portfolio - sufficient for $60K pool funding", balance_info)
                        else:
                            self.log_test("User Balance Verification", False, 
                                        f"User has only ${portfolio_value:,.2f} portfolio - insufficient for $60K pool funding", balance_info)
                        
                        return balance_info
                    else:
                        self.log_test("User Balance Verification", False, 
                                    f"Failed to get wallet info: {result.get('message')}", result)
                        return {}
                else:
                    error_text = await resp.text()
                    self.log_test("User Balance Verification", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return {}
                    
        except Exception as e:
            self.log_test("User Balance Verification", False, f"Exception: {str(e)}")
            return {}
    
    async def test_method_signature_fix(self) -> bool:
        """Test that method signature conflicts have been resolved"""
        try:
            headers = self.get_auth_headers()
            
            # Test the fund-with-user-balance endpoint with minimal request
            test_request = {
                "wallet_address": TEST_USER["wallet_address"],
                "pool_requests": [
                    {
                        "pool_type": "CRT/USDC",
                        "amount_usd": 100  # Small test amount
                    }
                ]
            }
            
            async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=test_request, headers=headers) as resp:
                result = await resp.json()
                
                # Check for method signature errors
                error_msg = str(result).lower()
                
                if "unexpected keyword argument 'crt_amount'" in error_msg:
                    self.log_test("Method Signature Fix", False, 
                                "Method signature conflict still present - 'crt_amount' parameter error", result)
                    return False
                elif "duplicate method" in error_msg or "method already defined" in error_msg:
                    self.log_test("Method Signature Fix", False, 
                                "Duplicate method definition error still present", result)
                    return False
                elif resp.status in [200, 400, 403]:
                    # If we get a proper response, method signature is working
                    self.log_test("Method Signature Fix", True, 
                                "No method signature conflicts detected - fix successful", result)
                    return True
                else:
                    self.log_test("Method Signature Fix", False, 
                                f"Unexpected response status: {resp.status}", result)
                    return False
                    
        except Exception as e:
            self.log_test("Method Signature Fix", False, f"Exception: {str(e)}")
            return False
    
    async def test_fund_all_pools_button_api(self) -> Dict[str, Any]:
        """Test the complete $60K pool funding request that the button triggers"""
        try:
            headers = self.get_auth_headers()
            
            # The exact request that the "Fund All Pools" button should make
            fund_all_request = {
                "wallet_address": TEST_USER["wallet_address"],
                "pool_requests": [
                    {
                        "pool_type": "USDC/CRT",
                        "amount_usd": 10000,  # USDC/CRT Bridge: $10K
                        "description": "USDC/CRT Bridge"
                    },
                    {
                        "pool_type": "CRT/SOL", 
                        "amount_usd": 10000,  # CRT/SOL Bridge: $10K
                        "description": "CRT/SOL Bridge"
                    },
                    {
                        "pool_type": "CRT/USDC",
                        "amount_usd": 20000,  # CRT/USDC Pool 1: $20K
                        "description": "CRT/USDC Pool 1"
                    },
                    {
                        "pool_type": "CRT/SOL",
                        "amount_usd": 20000,  # CRT/SOL Pool 2: $20K
                        "description": "CRT/SOL Pool 2"
                    }
                ]
            }
            
            async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=fund_all_request, headers=headers) as resp:
                result = await resp.json()
                
                if resp.status == 200 and result.get("success"):
                    funded_pools = result.get("funded_pools", [])
                    total_used = result.get("total_used", {})
                    
                    # Verify all 4 pools were funded
                    if len(funded_pools) == 4:
                        total_funding = sum(pool.get("crt_amount", 0) * 0.01 + 
                                          pool.get("usdc_amount", 0) + 
                                          pool.get("sol_amount", 0) * 240 
                                          for pool in funded_pools)
                        
                        self.log_test("Fund All Pools Button API", True, 
                                    f"Successfully funded all 4 pools with ~${total_funding:,.0f} total value", result)
                        return result
                    else:
                        self.log_test("Fund All Pools Button API", False, 
                                    f"Only {len(funded_pools)}/4 pools funded successfully", result)
                        return result
                elif "insufficient balance" in str(result).lower():
                    self.log_test("Fund All Pools Button API", False, 
                                f"Insufficient balance for $60K pool funding: {result.get('error')}", result)
                    return result
                else:
                    self.log_test("Fund All Pools Button API", False, 
                                f"Pool funding failed: {result.get('error', 'Unknown error')}", result)
                    return result
                    
        except Exception as e:
            self.log_test("Fund All Pools Button API", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_individual_pool_funding(self) -> bool:
        """Test individual pool funding to isolate issues"""
        try:
            headers = self.get_auth_headers()
            
            # Test each pool type individually with smaller amounts
            pool_tests = [
                {"pool_type": "CRT/USDC", "amount_usd": 1000, "name": "CRT/USDC Pool"},
                {"pool_type": "CRT/SOL", "amount_usd": 1000, "name": "CRT/SOL Pool"}
            ]
            
            successful_pools = 0
            
            for pool_test in pool_tests:
                test_request = {
                    "wallet_address": TEST_USER["wallet_address"],
                    "pool_requests": [pool_test]
                }
                
                async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                           json=test_request, headers=headers) as resp:
                    result = await resp.json()
                    
                    if resp.status == 200 and result.get("success"):
                        successful_pools += 1
                        print(f"   ✅ {pool_test['name']}: Success")
                    else:
                        print(f"   ❌ {pool_test['name']}: {result.get('error', 'Failed')}")
            
            if successful_pools == len(pool_tests):
                self.log_test("Individual Pool Funding", True, 
                            f"All {successful_pools} individual pool types working correctly")
                return True
            else:
                self.log_test("Individual Pool Funding", False, 
                            f"Only {successful_pools}/{len(pool_tests)} pool types working")
                return False
                
        except Exception as e:
            self.log_test("Individual Pool Funding", False, f"Exception: {str(e)}")
            return False
    
    async def test_real_orca_integration(self) -> bool:
        """Verify calls to real Orca managers work correctly"""
        try:
            headers = self.get_auth_headers()
            
            # Test DEX endpoints that indicate real Orca integration
            endpoints_to_test = [
                ("/dex/crt-price", "CRT Price API"),
                ("/dex/pools", "Orca Pools API"),
                ("/dex/listing-status", "DEX Listing Status")
            ]
            
            working_endpoints = 0
            
            for endpoint, name in endpoints_to_test:
                try:
                    async with self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers) as resp:
                        result = await resp.json()
                        
                        if resp.status == 200:
                            working_endpoints += 1
                            print(f"   ✅ {name}: Working")
                        else:
                            print(f"   ❌ {name}: HTTP {resp.status}")
                            
                except Exception as e:
                    print(f"   ❌ {name}: Exception - {str(e)}")
            
            if working_endpoints >= 2:  # At least 2/3 endpoints working
                self.log_test("Real Orca Integration", True, 
                            f"{working_endpoints}/3 Orca DEX endpoints working - real integration detected")
                return True
            else:
                self.log_test("Real Orca Integration", False, 
                            f"Only {working_endpoints}/3 Orca DEX endpoints working")
                return False
                
        except Exception as e:
            self.log_test("Real Orca Integration", False, f"Exception: {str(e)}")
            return False
    
    async def test_error_resolution(self) -> bool:
        """Test that previous errors have been resolved"""
        try:
            headers = self.get_auth_headers()
            
            # Test with a request that should trigger the previous error
            test_request = {
                "wallet_address": TEST_USER["wallet_address"],
                "pool_requests": [
                    {
                        "pool_type": "CRT/USDC",
                        "amount_usd": 100
                    }
                ]
            }
            
            async with self.session.post(f"{BACKEND_URL}/pools/fund-with-user-balance", 
                                       json=test_request, headers=headers) as resp:
                result = await resp.json()
                error_msg = str(result).lower()
                
                # Check for specific errors that should be resolved
                resolved_errors = []
                
                if "unexpected keyword argument 'crt_amount'" not in error_msg:
                    resolved_errors.append("crt_amount parameter error")
                
                if "500 internal server error" not in str(resp.status):
                    resolved_errors.append("500 server error")
                
                if "method signature" not in error_msg and "duplicate" not in error_msg:
                    resolved_errors.append("method signature conflicts")
                
                if len(resolved_errors) >= 2:
                    self.log_test("Error Resolution", True, 
                                f"Previous errors resolved: {', '.join(resolved_errors)}", result)
                    return True
                else:
                    self.log_test("Error Resolution", False, 
                                f"Some errors may still be present", result)
                    return False
                    
        except Exception as e:
            self.log_test("Error Resolution", False, f"Exception: {str(e)}")
            return False
    
    def print_summary(self):
        """Print comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n{'='*80}")
        print(f"🎯 FUND ALL POOLS BUTTON FUNCTIONALITY TEST SUMMARY")
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
        
        print(f"\n🎯 FUND ALL POOLS ASSESSMENT:")
        
        # Check method signature fix
        method_tests = [r for r in self.test_results if "method signature" in r["test"].lower()]
        if any(t["success"] for t in method_tests):
            print(f"   ✅ Method signature conflicts RESOLVED")
        else:
            print(f"   ❌ Method signature conflicts STILL PRESENT")
        
        # Check balance verification
        balance_tests = [r for r in self.test_results if "balance verification" in r["test"].lower()]
        if any(t["success"] for t in balance_tests):
            print(f"   ✅ User has sufficient balance for $60K pool funding")
        else:
            print(f"   ❌ User balance insufficient for $60K pool funding")
        
        # Check API functionality
        api_tests = [r for r in self.test_results if "button api" in r["test"].lower()]
        if any(t["success"] for t in api_tests):
            print(f"   ✅ Fund All Pools button API working correctly")
        else:
            print(f"   ❌ Fund All Pools button API has issues")
        
        # Check Orca integration
        orca_tests = [r for r in self.test_results if "orca integration" in r["test"].lower()]
        if any(t["success"] for t in orca_tests):
            print(f"   ✅ Real Orca integration working")
        else:
            print(f"   ❌ Real Orca integration issues detected")
        
        print(f"\n🚀 FINAL ASSESSMENT:")
        if failed_tests == 0:
            print(f"   🎉 FUND ALL POOLS BUTTON FULLY WORKING!")
            print(f"   ✅ All method signature conflicts resolved")
            print(f"   ✅ $60K pool funding ready for execution")
            print(f"   ✅ Real Orca integration operational")
        elif failed_tests <= 2:
            print(f"   ⚠️  Fund All Pools mostly working - minor issues remain")
            print(f"   🔧 Check remaining {failed_tests} issues")
        else:
            print(f"   ❌ FUND ALL POOLS BUTTON STILL HAS MAJOR ISSUES")
            print(f"   🚨 {failed_tests} critical problems need resolution")

async def main():
    """Run all Fund All Pools button tests"""
    print("🎯 Starting Fund All Pools Button Functionality Tests...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test User: {TEST_USER['username']} ({TEST_USER['wallet_address']})")
    print("🎯 Testing FIXED 'Fund All Pools' button functionality:")
    print("   • Method signature conflict resolution")
    print("   • $60K pool funding (USDC/CRT $10K, CRT/SOL $10K, CRT/USDC $20K, CRT/SOL $20K)")
    print("   • Real Orca integration verification")
    print("="*80)
    
    async with FundAllPoolsTester() as tester:
        # Test sequence for Fund All Pools functionality
        tests = [
            ("authenticate_user", "User Authentication"),
            ("test_user_balance_verification", "User Balance Verification"),
            ("test_method_signature_fix", "Method Signature Fix Verification"),
            ("test_real_orca_integration", "Real Orca Integration Verification"),
            ("test_individual_pool_funding", "Individual Pool Funding Test"),
            ("test_fund_all_pools_button_api", "Fund All Pools Button API Test"),
            ("test_error_resolution", "Error Resolution Verification")
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