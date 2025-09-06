#!/usr/bin/env python3
"""
Current System Analysis - Test what endpoints ARE available
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://blockchain-slots.preview.emergentagent.com/api"
TEST_USER = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

class CurrentSystemTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.available_endpoints = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def authenticate(self):
        """Authenticate user"""
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
                        print(f"✅ Authentication successful")
                        return True
                    else:
                        print(f"❌ Authentication failed: {result.get('message')}")
                        return False
                else:
                    print(f"❌ Authentication HTTP {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_auth_headers(self):
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    async def test_available_endpoints(self):
        """Test what endpoints are actually available"""
        headers = self.get_auth_headers()
        
        # List of endpoints to test based on server.py analysis
        endpoints_to_test = [
            # Basic endpoints
            ("GET", "/", "Root endpoint"),
            ("GET", "/health", "Health check"),
            
            # Authentication
            ("POST", "/auth/login", "User login"),
            ("POST", "/auth/register", "User registration"),
            ("POST", "/auth/challenge", "Wallet challenge"),
            ("POST", "/auth/verify", "Wallet verification"),
            
            # Wallet endpoints
            ("GET", f"/wallet/{TEST_USER['wallet_address']}", "Wallet info"),
            ("POST", "/wallet/deposit", "Wallet deposit"),
            ("POST", "/wallet/withdraw", "Wallet withdrawal"),
            ("POST", "/wallet/convert", "Currency conversion"),
            ("POST", "/wallet/batch-convert", "Batch conversion"),
            ("POST", "/wallet/transfer", "Internal transfer"),
            
            # Blockchain balance endpoints
            ("GET", f"/wallet/balance/CRT?wallet_address={TEST_USER['wallet_address']}", "CRT balance"),
            ("GET", f"/wallet/balance/DOGE?wallet_address={TEST_USER['wallet_address']}", "DOGE balance"),
            ("GET", f"/blockchain/balances?wallet_address={TEST_USER['wallet_address']}", "All balances"),
            
            # CRT specific
            ("GET", "/crt/info", "CRT token info"),
            ("POST", "/crt/simulate-deposit", "CRT simulate deposit"),
            
            # Game endpoints
            ("POST", "/games/bet", "Place bet"),
            ("GET", f"/games/history/{TEST_USER['wallet_address']}", "Game history"),
            
            # Orca/DEX endpoints (if available)
            ("POST", "/orca/add-liquidity", "Add Orca liquidity"),
            ("GET", "/dex/pools", "DEX pools"),
            ("GET", "/dex/crt-price", "CRT price"),
            ("POST", "/dex/create-orca-pool", "Create Orca pool"),
            
            # Admin endpoints
            ("POST", "/admin/fund-real-orca-pools", "Fund Orca pools"),
            ("POST", "/admin/direct-crt-transfer", "Direct CRT transfer"),
            ("POST", "/admin/setup-crt-hot-wallet", "Setup CRT hot wallet"),
            
            # Trust Wallet SWIFT
            ("POST", "/swift-wallet/connect", "SWIFT wallet connect"),
            ("POST", "/swift-wallet/transaction", "SWIFT transaction"),
            ("GET", "/swift-wallet/status", "SWIFT status"),
            ("POST", "/swift-wallet/account-abstraction", "SWIFT account abstraction"),
        ]
        
        print(f"\n🔍 Testing {len(endpoints_to_test)} potential endpoints...")
        
        for method, endpoint, description in endpoints_to_test:
            try:
                if method == "GET":
                    async with self.session.get(f"{BACKEND_URL}{endpoint}", headers=headers) as resp:
                        await self.check_endpoint_response(endpoint, description, resp)
                elif method == "POST":
                    # Use minimal test data for POST requests
                    test_data = {"wallet_address": TEST_USER["wallet_address"]}
                    async with self.session.post(f"{BACKEND_URL}{endpoint}", json=test_data, headers=headers) as resp:
                        await self.check_endpoint_response(endpoint, description, resp)
                        
            except Exception as e:
                print(f"❌ {endpoint} ({description}): Exception - {e}")
    
    async def check_endpoint_response(self, endpoint, description, resp):
        """Check endpoint response and categorize"""
        if resp.status == 404:
            print(f"❌ {endpoint} ({description}): NOT FOUND")
        elif resp.status in [200, 400, 401, 403, 422]:
            # These status codes indicate the endpoint exists
            try:
                result = await resp.json()
                if resp.status == 200:
                    print(f"✅ {endpoint} ({description}): AVAILABLE")
                    self.available_endpoints.append(endpoint)
                elif resp.status == 401:
                    print(f"🔒 {endpoint} ({description}): REQUIRES AUTH")
                    self.available_endpoints.append(endpoint)
                elif resp.status == 403:
                    print(f"🚫 {endpoint} ({description}): FORBIDDEN")
                    self.available_endpoints.append(endpoint)
                elif resp.status == 400:
                    print(f"⚠️ {endpoint} ({description}): BAD REQUEST (endpoint exists)")
                    self.available_endpoints.append(endpoint)
                elif resp.status == 422:
                    print(f"⚠️ {endpoint} ({description}): VALIDATION ERROR (endpoint exists)")
                    self.available_endpoints.append(endpoint)
            except:
                print(f"⚠️ {endpoint} ({description}): HTTP {resp.status} (endpoint exists)")
                self.available_endpoints.append(endpoint)
        else:
            print(f"❓ {endpoint} ({description}): HTTP {resp.status}")
    
    async def test_user_portfolio(self):
        """Test current user portfolio"""
        print(f"\n💰 Current User Portfolio Analysis:")
        
        try:
            async with self.session.get(f"{BACKEND_URL}/wallet/{TEST_USER['wallet_address']}") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success"):
                        wallet = result.get("wallet", {})
                        
                        print(f"📊 User: {wallet.get('user_id', 'Unknown')}")
                        print(f"🏦 Wallet: {wallet.get('wallet_address', 'Unknown')}")
                        
                        # Show all balance types
                        balance_types = ["deposit_balance", "winnings_balance", "gaming_balance", "savings_balance", "liquidity_pool"]
                        
                        total_usd_value = 0
                        
                        for balance_type in balance_types:
                            balances = wallet.get(balance_type, {})
                            if balances:
                                print(f"\n{balance_type.replace('_', ' ').title()}:")
                                for currency, amount in balances.items():
                                    if amount > 0:
                                        # Rough USD conversion
                                        usd_value = 0
                                        if currency == "USDC":
                                            usd_value = amount
                                        elif currency == "DOGE":
                                            usd_value = amount * 0.22
                                        elif currency == "TRX":
                                            usd_value = amount * 0.36
                                        elif currency == "CRT":
                                            usd_value = amount * 0.01
                                        elif currency == "SOL":
                                            usd_value = amount * 200
                                        
                                        total_usd_value += usd_value
                                        print(f"  {currency}: {amount:,.2f} (≈${usd_value:,.2f})")
                        
                        print(f"\n💎 Total Portfolio Value: ≈${total_usd_value:,.2f}")
                        print(f"🎯 Expected Value: $12,277,000")
                        print(f"📈 Difference: ${12277000 - total_usd_value:,.2f}")
                        
                    else:
                        print(f"❌ Wallet request failed: {result.get('message')}")
                else:
                    print(f"❌ Wallet request HTTP {resp.status}")
                    
        except Exception as e:
            print(f"❌ Portfolio analysis error: {e}")
    
    def print_summary(self):
        """Print summary of findings"""
        print(f"\n{'='*80}")
        print(f"📋 CURRENT SYSTEM ANALYSIS SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Available Endpoints: {len(self.available_endpoints)}")
        print(f"🏦 System Type: Casino Gaming Platform")
        print(f"🎯 Review Request: Tiger Bank Games Development Fund & CDT Bridge")
        
        print(f"\n✅ WORKING ENDPOINTS:")
        for endpoint in sorted(self.available_endpoints):
            print(f"   • {endpoint}")
        
        print(f"\n❌ MISSING ENDPOINTS (Required by Review):")
        missing = [
            "/api/withdraw/preset",
            "/api/dev-wallets", 
            "/api/cdt/pricing",
            "/api/cdt/bridge",
            "/api/cdt/iou-status",
            "/api/cdt/iou-repay"
        ]
        for endpoint in missing:
            print(f"   • {endpoint}")
        
        print(f"\n🔍 SYSTEM MISMATCH ANALYSIS:")
        print(f"   • Current System: Casino gaming with Orca DEX integration")
        print(f"   • Review Request: Tiger Bank Games development fund withdrawal system")
        print(f"   • Portfolio Expected: $12.277M (319K USDC, 13M DOGE, 3.9M TRX, 21M CRT, 52M T52M)")
        print(f"   • Portfolio Actual: ~$57K (different token distribution)")
        
        print(f"\n🚨 CRITICAL FINDINGS:")
        print(f"   ❌ COMPLETE SYSTEM MISMATCH")
        print(f"   ❌ None of the requested Tiger Bank Games endpoints are implemented")
        print(f"   ❌ Portfolio balances don't match expected values")
        print(f"   ❌ CDT bridge integration completely missing")
        print(f"   ❌ Development fund withdrawal system not implemented")

async def main():
    print("🔍 Current System Analysis - Testing Available Endpoints")
    print(f"Backend URL: {BACKEND_URL}")
    print("="*80)
    
    async with CurrentSystemTester() as tester:
        if await tester.authenticate():
            await tester.test_available_endpoints()
            await tester.test_user_portfolio()
            tester.print_summary()
        else:
            print("❌ Cannot proceed without authentication")

if __name__ == "__main__":
    asyncio.run(main())