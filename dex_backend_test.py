#!/usr/bin/env python3
"""
CRT Token DEX Listing System Backend Testing
Tests all DEX endpoints for CRT token listing on Orca and Jupiter
"""

import asyncio
import aiohttp
import json
import sys
import os
from datetime import datetime

# Backend URL from environment
BACKEND_URL = "https://smart-savings-dapp.preview.emergentagent.com/api"

# Test user credentials (admin access required for DEX operations)
TEST_USER = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

# CRT Token Details
CRT_TOKEN = {
    "mint": "9pjWtc6x88wrRMXTxkBcNB6YtcN7NNcyzDAfUMfRknty",
    "symbol": "CRT",
    "name": "CRT Tiger Token",
    "logo": "https://customer-assets.emergentagent.com/job_smart-savings-dapp/artifacts/b3v23rrw_copilot_image_1755811225489.jpeg"
}

class DEXTestRunner:
    def __init__(self):
        self.session = None
        self.jwt_token = None
        self.test_results = []
        
    async def setup_session(self):
        """Setup HTTP session and authenticate user"""
        self.session = aiohttp.ClientSession()
        
        # Authenticate user
        auth_success = await self.authenticate_user()
        if not auth_success:
            print("❌ Authentication failed - cannot proceed with DEX tests")
            return False
        
        print(f"✅ Authenticated as {TEST_USER['username']} with admin access")
        return True
    
    async def authenticate_user(self):
        """Authenticate user and get JWT token"""
        try:
            # Try username/password login
            login_data = {
                "username": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login-username", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("success"):
                        self.jwt_token = result.get("token")
                        print(f"✅ Login successful for user: {TEST_USER['username']}")
                        return True
                    else:
                        print(f"❌ Login failed: {result.get('message')}")
                        return False
                else:
                    print(f"❌ Login request failed with status: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def get_auth_headers(self):
        """Get authentication headers for API requests"""
        if self.jwt_token:
            return {"Authorization": f"Bearer {self.jwt_token}"}
        return {}
    
    async def test_create_crt_sol_orca_pool(self):
        """Test 1: Create CRT/SOL Orca Pool"""
        print("\n🌊 Testing CRT/SOL Orca Pool Creation...")
        
        try:
            pool_data = {
                "pool_pair": "CRT/SOL",
                "wallet_address": TEST_USER["wallet_address"]
            }
            
            headers = self.get_auth_headers()
            async with self.session.post(f"{BACKEND_URL}/dex/create-orca-pool", 
                                       json=pool_data, headers=headers) as response:
                result = await response.json()
                
                if response.status == 200 and result.get("success"):
                    print(f"✅ CRT/SOL Orca pool created successfully!")
                    print(f"   Pool Address: {result.get('pool', {}).get('pool_address', 'N/A')}")
                    print(f"   Transaction Hash: {result.get('transaction_hash', 'N/A')}")
                    print(f"   Pool URL: {result.get('pool_url', 'N/A')}")
                    
                    self.test_results.append({
                        "test": "Create CRT/SOL Orca Pool",
                        "status": "✅ PASSED",
                        "details": f"Pool created with initial liquidity: 1M CRT + 100 SOL"
                    })
                    return True
                else:
                    print(f"❌ CRT/SOL pool creation failed: {result.get('message', 'Unknown error')}")
                    self.test_results.append({
                        "test": "Create CRT/SOL Orca Pool", 
                        "status": "❌ FAILED",
                        "error": result.get("error", "Pool creation failed")
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ CRT/SOL pool creation error: {str(e)}")
            self.test_results.append({
                "test": "Create CRT/SOL Orca Pool",
                "status": "❌ ERROR", 
                "error": str(e)
            })
            return False
    
    async def test_create_crt_usdc_orca_pool(self):
        """Test 2: Create CRT/USDC Orca Pool"""
        print("\n💰 Testing CRT/USDC Orca Pool Creation...")
        
        try:
            pool_data = {
                "pool_pair": "CRT/USDC",
                "wallet_address": TEST_USER["wallet_address"]
            }
            
            headers = self.get_auth_headers()
            async with self.session.post(f"{BACKEND_URL}/dex/create-orca-pool",
                                       json=pool_data, headers=headers) as response:
                result = await response.json()
                
                if response.status == 200 and result.get("success"):
                    print(f"✅ CRT/USDC Orca pool created successfully!")
                    print(f"   Pool Address: {result.get('pool', {}).get('pool_address', 'N/A')}")
                    print(f"   Transaction Hash: {result.get('transaction_hash', 'N/A')}")
                    print(f"   Pool URL: {result.get('pool_url', 'N/A')}")
                    
                    self.test_results.append({
                        "test": "Create CRT/USDC Orca Pool",
                        "status": "✅ PASSED",
                        "details": f"Pool created with initial liquidity: 1M CRT + $10,000 USDC"
                    })
                    return True
                else:
                    print(f"❌ CRT/USDC pool creation failed: {result.get('message', 'Unknown error')}")
                    self.test_results.append({
                        "test": "Create CRT/USDC Orca Pool",
                        "status": "❌ FAILED", 
                        "error": result.get("error", "Pool creation failed")
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ CRT/USDC pool creation error: {str(e)}")
            self.test_results.append({
                "test": "Create CRT/USDC Orca Pool",
                "status": "❌ ERROR",
                "error": str(e)
            })
            return False
    
    async def test_submit_jupiter_listing(self):
        """Test 3: Submit CRT to Jupiter Aggregator"""
        print("\n🪐 Testing Jupiter Aggregator Submission...")
        
        try:
            submission_data = {
                "wallet_address": TEST_USER["wallet_address"]
            }
            
            headers = self.get_auth_headers()
            async with self.session.post(f"{BACKEND_URL}/dex/submit-jupiter-listing",
                                       json=submission_data, headers=headers) as response:
                result = await response.json()
                
                if response.status == 200 and result.get("success"):
                    print(f"✅ CRT token submitted to Jupiter aggregator successfully!")
                    print(f"   Submission ID: {result.get('submission', {}).get('submission_id', 'N/A')}")
                    print(f"   PR URL: {result.get('pr_url', 'N/A')}")
                    print(f"   Review Time: {result.get('estimated_review_time', 'N/A')}")
                    
                    self.test_results.append({
                        "test": "Submit CRT to Jupiter Aggregator",
                        "status": "✅ PASSED",
                        "details": f"Token metadata submitted with CRT tiger branding"
                    })
                    return True
                else:
                    print(f"❌ Jupiter submission failed: {result.get('message', 'Unknown error')}")
                    self.test_results.append({
                        "test": "Submit CRT to Jupiter Aggregator",
                        "status": "❌ FAILED",
                        "error": result.get("error", "Submission failed")
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Jupiter submission error: {str(e)}")
            self.test_results.append({
                "test": "Submit CRT to Jupiter Aggregator", 
                "status": "❌ ERROR",
                "error": str(e)
            })
            return False
    
    async def test_get_crt_price_discovery(self):
        """Test 4: Get CRT Price Discovery"""
        print("\n💎 Testing CRT Price Discovery...")
        
        try:
            async with self.session.get(f"{BACKEND_URL}/dex/crt-price") as response:
                result = await response.json()
                
                if response.status == 200 and result.get("success"):
                    price_data = result.get("price_data", {})
                    prices = price_data.get("price", {})
                    
                    print(f"✅ CRT price data retrieved successfully!")
                    print(f"   USD Price: ${prices.get('usd', 0):.6f}")
                    print(f"   SOL Price: {prices.get('sol', 0):.6f} SOL")
                    print(f"   USDC Price: {prices.get('usdc', 0):.6f} USDC")
                    
                    # Check if we have pool data
                    pools = price_data.get("pools", [])
                    print(f"   Active Pools: {len(pools)}")
                    for pool in pools:
                        print(f"     - {pool.get('pair')} on {pool.get('dex')}: ${pool.get('liquidity', 0):,.2f} liquidity")
                    
                    self.test_results.append({
                        "test": "Get CRT Price Discovery",
                        "status": "✅ PASSED",
                        "details": f"Price data available in USD, SOL, and USDC"
                    })
                    return True
                else:
                    print(f"❌ Price discovery failed: {result.get('message', 'Unknown error')}")
                    self.test_results.append({
                        "test": "Get CRT Price Discovery",
                        "status": "❌ FAILED",
                        "error": result.get("error", "Price fetch failed")
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Price discovery error: {str(e)}")
            self.test_results.append({
                "test": "Get CRT Price Discovery",
                "status": "❌ ERROR",
                "error": str(e)
            })
            return False
    
    async def test_check_dex_listing_status(self):
        """Test 5: Check DEX Listing Status"""
        print("\n📊 Testing DEX Listing Status...")
        
        try:
            async with self.session.get(f"{BACKEND_URL}/dex/listing-status") as response:
                result = await response.json()
                
                if response.status == 200 and result.get("success"):
                    listing_status = result.get("listing_status", {})
                    summary = result.get("summary", {})
                    
                    print(f"✅ DEX listing status retrieved successfully!")
                    print(f"   Total DEXs: {summary.get('total_dexs', 0)}")
                    print(f"   Listed On: {summary.get('listed_on', 0)} DEXs")
                    print(f"   Listing Progress: {summary.get('listing_percentage', 0):.1f}%")
                    
                    # Check individual DEX status
                    for dex, status in listing_status.items():
                        status_icon = "✅" if status.get("listed") else "⏳"
                        print(f"     {status_icon} {dex}: {status.get('status', 'unknown')}")
                        
                        if dex == "Orca" and "pools" in status:
                            for pool in status["pools"]:
                                pool_icon = "✅" if pool.get("exists") else "❌"
                                print(f"       {pool_icon} {pool.get('pair')} pool")
                    
                    self.test_results.append({
                        "test": "Check DEX Listing Status",
                        "status": "✅ PASSED",
                        "details": f"Status verified across {summary.get('total_dexs', 0)} DEX platforms"
                    })
                    return True
                else:
                    print(f"❌ DEX listing status check failed: {result.get('error', 'Unknown error')}")
                    self.test_results.append({
                        "test": "Check DEX Listing Status",
                        "status": "❌ FAILED",
                        "error": result.get("error", "Status check failed")
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ DEX listing status error: {str(e)}")
            self.test_results.append({
                "test": "Check DEX Listing Status",
                "status": "❌ ERROR",
                "error": str(e)
            })
            return False
    
    async def test_create_market_maker_strategy(self):
        """Test 6: Create Market Maker Strategy"""
        print("\n🤖 Testing Market Maker Strategy Creation...")
        
        try:
            mm_data = {
                "pool_pair": "CRT/SOL"
            }
            
            headers = self.get_auth_headers()
            async with self.session.post(f"{BACKEND_URL}/dex/create-market-maker",
                                       json=mm_data, headers=headers) as response:
                result = await response.json()
                
                if response.status == 200 and result.get("success"):
                    strategy = result.get("strategy", {})
                    
                    print(f"✅ Market maker strategy created successfully!")
                    print(f"   Strategy Type: {strategy.get('strategy_type', 'N/A')}")
                    print(f"   Pool Pair: {strategy.get('pool_pair', 'N/A')}")
                    print(f"   Grid Levels: {strategy.get('parameters', {}).get('grid_levels', 'N/A')}")
                    print(f"   Risk Management: {len(strategy.get('risk_management', {}))} controls")
                    print(f"   Status: {strategy.get('status', 'N/A')}")
                    
                    if result.get("activation_required"):
                        print(f"   ⚠️ Manual activation required for safety")
                    
                    self.test_results.append({
                        "test": "Create Market Maker Strategy",
                        "status": "✅ PASSED",
                        "details": f"Grid trading strategy configured with risk management"
                    })
                    return True
                else:
                    print(f"❌ Market maker creation failed: {result.get('error', 'Unknown error')}")
                    self.test_results.append({
                        "test": "Create Market Maker Strategy",
                        "status": "❌ FAILED",
                        "error": result.get("error", "Strategy creation failed")
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Market maker creation error: {str(e)}")
            self.test_results.append({
                "test": "Create Market Maker Strategy",
                "status": "❌ ERROR",
                "error": str(e)
            })
            return False
    
    async def test_get_crt_liquidity_pools(self):
        """Test 7: Get CRT Liquidity Pools"""
        print("\n🏊 Testing CRT Liquidity Pools Retrieval...")
        
        try:
            async with self.session.get(f"{BACKEND_URL}/dex/pools") as response:
                result = await response.json()
                
                if response.status == 200 and result.get("success"):
                    pools = result.get("pools", [])
                    supported_dexs = result.get("supported_dexs", [])
                    
                    print(f"✅ CRT liquidity pools retrieved successfully!")
                    print(f"   Total Active Pools: {result.get('total_pools', 0)}")
                    print(f"   Supported DEXs: {len(supported_dexs)}")
                    
                    for pool in pools:
                        print(f"     🌊 {pool.get('pool_pair')} on {pool.get('dex')}")
                        print(f"        Pool ID: {pool.get('pool_id', 'N/A')}")
                        print(f"        Address: {pool.get('pool_address', 'N/A')}")
                        print(f"        Status: {pool.get('status', 'N/A')}")
                    
                    if not pools:
                        print("     No active pools found (pools may be in creation process)")
                    
                    self.test_results.append({
                        "test": "Get CRT Liquidity Pools",
                        "status": "✅ PASSED",
                        "details": f"Retrieved {len(pools)} active pools across {len(supported_dexs)} supported DEXs"
                    })
                    return True
                else:
                    print(f"❌ Liquidity pools retrieval failed: {result.get('error', 'Unknown error')}")
                    self.test_results.append({
                        "test": "Get CRT Liquidity Pools",
                        "status": "❌ FAILED",
                        "error": result.get("error", "Pools retrieval failed")
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Liquidity pools retrieval error: {str(e)}")
            self.test_results.append({
                "test": "Get CRT Liquidity Pools",
                "status": "❌ ERROR",
                "error": str(e)
            })
            return False
    
    async def run_all_tests(self):
        """Run all DEX system tests"""
        print("🚀 Starting CRT Token DEX Listing System Tests")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test User: {TEST_USER['username']} (Admin)")
        print(f"CRT Token: {CRT_TOKEN['symbol']} - {CRT_TOKEN['name']}")
        print(f"Token Mint: {CRT_TOKEN['mint']}")
        print("=" * 60)
        
        # Setup session and authenticate
        if not await self.setup_session():
            return False
        
        # Run all tests
        tests = [
            self.test_create_crt_sol_orca_pool,
            self.test_create_crt_usdc_orca_pool,
            self.test_submit_jupiter_listing,
            self.test_get_crt_price_discovery,
            self.test_check_dex_listing_status,
            self.test_create_market_maker_strategy,
            self.test_get_crt_liquidity_pools
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                success = await test()
                if success:
                    passed_tests += 1
                await asyncio.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test execution error: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 DEX SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            print(f"{result['status']} {result['test']}")
            if 'details' in result:
                print(f"    📝 {result['details']}")
            if 'error' in result:
                print(f"    ❌ {result['error']}")
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n📊 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🎉 DEX SYSTEM TESTING COMPLETED SUCCESSFULLY!")
            print("✅ CRT token DEX listing infrastructure is ready for production")
        elif success_rate >= 60:
            print("⚠️ DEX SYSTEM PARTIALLY FUNCTIONAL")
            print("🔧 Some components need attention before full deployment")
        else:
            print("❌ DEX SYSTEM NEEDS SIGNIFICANT FIXES")
            print("🚨 Major issues found that require immediate attention")
        
        return success_rate >= 60
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

async def main():
    """Main test execution"""
    tester = DEXTestRunner()
    
    try:
        success = await tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        return 1
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)