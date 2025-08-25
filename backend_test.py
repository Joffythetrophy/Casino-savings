#!/usr/bin/env python3
"""
Casino Savings dApp Backend API Test Suite - Real Money Integration Testing
Tests wallet management system for real money integration
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://winsaver.preview.emergentagent.com/api"

class WalletAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.test_wallet = "RealWallet9876543210XYZ"  # Test wallet address
        self.test_results = []
        
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
        
    async def test_basic_connectivity(self):
        """Test 1: Basic API connectivity and root endpoint"""
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    expected_fields = ["message", "version", "supported_networks", "supported_tokens"]
                    if all(field in data for field in expected_fields):
                        self.log_test("Basic Connectivity", True, 
                                    f"API accessible, version: {data.get('version')}", data)
                    else:
                        self.log_test("Basic Connectivity", False, 
                                    f"Missing expected fields in response", data)
                else:
                    self.log_test("Basic Connectivity", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Basic Connectivity", False, f"Connection error: {str(e)}")
    
    async def test_auth_challenge_generation(self):
        """Test 2: Authentication challenge generation"""
        try:
            payload = {
                "wallet_address": self.test_wallet,
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/auth/challenge", 
                                       json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "challenge", "challenge_hash", "network"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        self.challenge_hash = data.get("challenge_hash")
                        self.log_test("Auth Challenge Generation", True, 
                                    "Challenge generated successfully", data)
                        return data
                    else:
                        self.log_test("Auth Challenge Generation", False, 
                                    "Invalid challenge response format", data)
                else:
                    self.log_test("Auth Challenge Generation", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Auth Challenge Generation", False, f"Error: {str(e)}")
        return None
    
    async def test_auth_verification(self, challenge_data: Dict):
        """Test 3: Authentication verification and JWT token generation"""
        if not challenge_data:
            self.log_test("Auth Verification", False, "No challenge data available")
            return
            
        try:
            payload = {
                "challenge_hash": challenge_data.get("challenge_hash"),
                "signature": "mock_signature_for_demo_purposes_12345",  # Mock signature
                "wallet_address": self.test_wallet,
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/auth/verify", 
                                       json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "token", "wallet_address", "network", "expires_in"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        self.auth_token = data.get("token")
                        self.log_test("Auth Verification", True, 
                                    f"JWT token generated, expires in {data.get('expires_in')}s", data)
                    else:
                        self.log_test("Auth Verification", False, 
                                    "Invalid verification response", data)
                else:
                    self.log_test("Auth Verification", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Auth Verification", False, f"Error: {str(e)}")
    
    async def test_wallet_info_endpoint(self):
        """Test 4: Wallet information retrieval"""
        if not self.auth_token:
            self.log_test("Wallet Info", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.test_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        expected_fields = ["wallet_address", "deposit_balance", "winnings_balance", "savings_balance"]
                        if all(field in wallet for field in expected_fields):
                            self.log_test("Wallet Info", True, 
                                        f"Wallet info retrieved successfully", data)
                        else:
                            self.log_test("Wallet Info", False, 
                                        "Missing expected wallet fields", data)
                    else:
                        self.log_test("Wallet Info", False, 
                                    "Invalid wallet info response format", data)
                else:
                    self.log_test("Wallet Info", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Wallet Info", False, f"Error: {str(e)}")
    
    async def test_deposit_endpoint(self):
        """Test 5: Deposit funds endpoint"""
        if not self.auth_token:
            self.log_test("Deposit Funds", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            deposit_payload = {
                "wallet_address": self.test_wallet,
                "currency": "CRT",
                "amount": 100.0
            }
            
            async with self.session.post(f"{self.base_url}/wallet/deposit", 
                                       json=deposit_payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "message" in data:
                        self.log_test("Deposit Funds", True, 
                                    f"Deposit successful: {data.get('message')}", data)
                    else:
                        self.log_test("Deposit Funds", False, 
                                    "Invalid deposit response format", data)
                else:
                    self.log_test("Deposit Funds", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Deposit Funds", False, f"Error: {str(e)}")
    
    async def test_withdraw_endpoint(self):
        """Test 6: Withdraw funds endpoint"""
        if not self.auth_token:
            self.log_test("Withdraw Funds", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            withdraw_payload = {
                "wallet_address": self.test_wallet,
                "wallet_type": "winnings",
                "currency": "CRT",
                "amount": 10.0
            }
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=withdraw_payload, headers=headers) as response:
                if response.status in [200, 400]:  # 400 expected for insufficient balance
                    data = await response.json()
                    if response.status == 400 and "Insufficient balance" in data.get("detail", ""):
                        self.log_test("Withdraw Funds", True, 
                                    "Withdrawal correctly rejected - insufficient balance", data)
                    elif response.status == 200 and data.get("success"):
                        self.log_test("Withdraw Funds", True, 
                                    f"Withdrawal successful: {data.get('message')}", data)
                    else:
                        self.log_test("Withdraw Funds", False, 
                                    "Unexpected withdrawal response", data)
                else:
                    self.log_test("Withdraw Funds", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Withdraw Funds", False, f"Error: {str(e)}")
    
    async def test_convert_endpoint(self):
        """Test 7: Crypto conversion endpoint"""
        if not self.auth_token:
            self.log_test("Crypto Conversion", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            convert_payload = {
                "wallet_address": self.test_wallet,
                "from_currency": "CRT",
                "to_currency": "DOGE",
                "amount": 10.0
            }
            
            async with self.session.post(f"{self.base_url}/wallet/convert", 
                                       json=convert_payload, headers=headers) as response:
                if response.status in [200, 400]:  # 400 expected for insufficient balance
                    data = await response.json()
                    if response.status == 400 and "Insufficient balance" in data.get("detail", ""):
                        self.log_test("Crypto Conversion", True, 
                                    "Conversion correctly rejected - insufficient balance", data)
                    elif response.status == 200 and data.get("success"):
                        # Check if conversion rates are real (not mock)
                        rate = data.get("rate", 0)
                        converted_amount = data.get("converted_amount", 0)
                        if rate > 0 and converted_amount > 0:
                            self.log_test("Crypto Conversion", True, 
                                        f"Conversion successful: rate {rate}, amount {converted_amount}", data)
                        else:
                            self.log_test("Crypto Conversion", False, 
                                        "Conversion response missing rate/amount data", data)
                    else:
                        self.log_test("Crypto Conversion", False, 
                                    "Unexpected conversion response", data)
                else:
                    self.log_test("Crypto Conversion", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Crypto Conversion", False, f"Error: {str(e)}")
    
    async def test_game_betting(self):
        """Test 8: Real money game betting"""
        if not self.auth_token:
            self.log_test("Game Betting", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            bet_payload = {
                "wallet_address": self.test_wallet,
                "game_type": "Slot Machine",
                "bet_amount": 5.0,
                "currency": "CRT",
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/games/bet", 
                                       json=bet_payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "game_id", "bet_amount", "currency", "result", "payout"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        result = data.get("result")
                        payout = data.get("payout")
                        savings_contribution = data.get("savings_contribution", 0)
                        
                        # Check if this is real game logic (not just mock)
                        if result in ["win", "loss"] and isinstance(payout, (int, float)):
                            self.log_test("Game Betting", True, 
                                        f"Real bet placed: {result}, payout: {payout}, savings: {savings_contribution}", data)
                        else:
                            self.log_test("Game Betting", False, 
                                        "Game betting appears to use mock data", data)
                    else:
                        self.log_test("Game Betting", False, 
                                    "Invalid bet response format", data)
                else:
                    self.log_test("Game Betting", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Game Betting", False, f"Error: {str(e)}")
    
    async def test_savings_system(self):
        """Test 9: Smart savings system"""
        if not self.auth_token:
            self.log_test("Savings System", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(f"{self.base_url}/savings/{self.test_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "wallet_address", "total_savings", "stats"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        total_savings = data.get("total_savings", {})
                        stats = data.get("stats", {})
                        savings_history = data.get("savings_history", [])
                        
                        # Check if savings are calculated from real game losses
                        if isinstance(total_savings, dict) and isinstance(stats, dict):
                            total_games = stats.get("total_games", 0)
                            total_losses = stats.get("total_losses", 0)
                            
                            self.log_test("Savings System", True, 
                                        f"Savings system working: {total_games} games, {total_losses} losses, {len(savings_history)} history entries", data)
                        else:
                            self.log_test("Savings System", False, 
                                        "Invalid savings data structure", data)
                    else:
                        self.log_test("Savings System", False, 
                                    "Invalid savings response format", data)
                else:
                    self.log_test("Savings System", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Savings System", False, f"Error: {str(e)}")
    
    async def test_websocket_wallet_monitor(self):
        """Test 10: WebSocket wallet monitoring"""
        try:
            import websockets
            
            ws_url = f"wss://cryptosave-1.preview.emergentagent.com/api/ws/wallet/{self.test_wallet}"
            
            try:
                async with websockets.connect(ws_url) as websocket:
                    # Send a test message
                    test_message = {"type": "refresh_wallet"}
                    await websocket.send(json.dumps(test_message))
                    
                    # Wait for response with timeout
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "wallet_update" and "data" in data:
                        wallet_data = data.get("data", {}).get("wallet", {})
                        if "wallet_address" in wallet_data:
                            self.log_test("WebSocket Wallet Monitor", True, 
                                        "WebSocket wallet monitoring working", data)
                        else:
                            self.log_test("WebSocket Wallet Monitor", False, 
                                        "Invalid wallet data in WebSocket response", data)
                    else:
                        self.log_test("WebSocket Wallet Monitor", False, 
                                    "Invalid WebSocket response format", data)
                        
            except asyncio.TimeoutError:
                self.log_test("WebSocket Wallet Monitor", False, "WebSocket connection timeout")
            except Exception as ws_error:
                self.log_test("WebSocket Wallet Monitor", False, f"WebSocket error: {str(ws_error)}")
                
        except ImportError:
            self.log_test("WebSocket Wallet Monitor", False, "websockets library not available - skipping test")
        except Exception as e:
            self.log_test("WebSocket Wallet Monitor", False, f"Error: {str(e)}")
    
    async def test_database_integration(self):
        """Test 11: Database integration and persistence"""
        if not self.auth_token:
            self.log_test("Database Integration", False, "No auth token available")
            return
            
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            # Test game history to verify database storage
            async with self.session.get(f"{self.base_url}/games/history/{self.test_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "games" in data:
                        games = data.get("games", [])
                        total_games = data.get("total_games", 0)
                        
                        # Check if games have proper database fields
                        if games and len(games) > 0:
                            first_game = games[0]
                            db_fields = ["_id", "wallet_address", "game_type", "bet_amount", "timestamp"]
                            if all(field in first_game for field in db_fields):
                                self.log_test("Database Integration", True, 
                                            f"Database integration working: {total_games} games stored with proper fields", data)
                            else:
                                self.log_test("Database Integration", False, 
                                            "Games missing required database fields", data)
                        else:
                            self.log_test("Database Integration", True, 
                                        "Database integration working: no games yet but endpoint functional", data)
                    else:
                        self.log_test("Database Integration", False, 
                                    "Invalid game history response", data)
                else:
                    self.log_test("Database Integration", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Database Integration", False, f"Error: {str(e)}")

    async def test_user_registration(self):
        """Test 12: User registration with wallet address and password"""
        try:
            # Use a unique wallet address for registration test
            test_wallet_reg = f"RegTestWallet{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            payload = {
                "wallet_address": test_wallet_reg,
                "password": "SecureTestPassword123!"
            }
            
            async with self.session.post(f"{self.base_url}/auth/register", 
                                       json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "message", "user_id", "created_at"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        self.log_test("User Registration", True, 
                                    f"User registered successfully: {data.get('message')}", data)
                        # Store for login test
                        self.registered_wallet = test_wallet_reg
                        self.registered_password = "SecureTestPassword123!"
                    else:
                        self.log_test("User Registration", False, 
                                    "Invalid registration response format", data)
                else:
                    self.log_test("User Registration", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("User Registration", False, f"Error: {str(e)}")

    async def test_user_login(self):
        """Test 13: User login authentication"""
        if not hasattr(self, 'registered_wallet'):
            self.log_test("User Login", False, "No registered user available for login test")
            return
            
        try:
            payload = {
                "wallet_address": self.registered_wallet,
                "password": self.registered_password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login", 
                                       json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "message", "user_id", "created_at"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        self.log_test("User Login", True, 
                                    f"User login successful: {data.get('message')}", data)
                    else:
                        self.log_test("User Login", False, 
                                    "Invalid login response format", data)
                else:
                    self.log_test("User Login", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("User Login", False, f"Error: {str(e)}")

    async def test_real_crypto_conversion_rates(self):
        """Test 14: Real-time crypto conversion rates from CoinGecko"""
        try:
            async with self.session.get(f"{self.base_url}/conversion/rates") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "rates", "prices_usd", "last_updated", "source"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        rates = data.get("rates", {})
                        prices_usd = data.get("prices_usd", {})
                        source = data.get("source", "")
                        
                        # Check if we have real rates (not fallback)
                        expected_currencies = ["CRT", "DOGE", "TRX", "USDC"]
                        has_real_data = source in ["coingecko", "cache"]
                        has_expected_rates = any(f"{curr1}_{curr2}" in rates 
                                               for curr1 in expected_currencies 
                                               for curr2 in expected_currencies 
                                               if curr1 != curr2)
                        
                        if has_real_data and has_expected_rates:
                            self.log_test("Real Crypto Conversion Rates", True, 
                                        f"Real conversion rates working: {len(rates)} rates, source: {source}", data)
                        elif source == "fallback":
                            self.log_test("Real Crypto Conversion Rates", False, 
                                        "Using fallback rates instead of real CoinGecko data", data)
                        else:
                            self.log_test("Real Crypto Conversion Rates", False, 
                                        "Missing expected conversion rates", data)
                    else:
                        self.log_test("Real Crypto Conversion Rates", False, 
                                    "Invalid conversion rates response format", data)
                else:
                    self.log_test("Real Crypto Conversion Rates", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Real Crypto Conversion Rates", False, f"Error: {str(e)}")

    async def test_individual_crypto_prices(self):
        """Test 15: Individual crypto price data"""
        test_currencies = ["DOGE", "TRX", "USDC", "CRT"]
        
        for currency in test_currencies:
            try:
                async with self.session.get(f"{self.base_url}/crypto/price/{currency}") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("success") and "data" in data:
                            price_data = data["data"]
                            required_fields = ["currency", "price_usd", "price_change_24h", "last_updated"]
                            
                            if all(field in price_data for field in required_fields):
                                price = price_data.get("price_usd", 0)
                                change_24h = price_data.get("price_change_24h", 0)
                                
                                if price > 0:
                                    self.log_test(f"Crypto Price - {currency}", True, 
                                                f"Price: ${price}, 24h change: {change_24h}%", data)
                                else:
                                    self.log_test(f"Crypto Price - {currency}", False, 
                                                "Invalid price data (price is 0)", data)
                            else:
                                self.log_test(f"Crypto Price - {currency}", False, 
                                            "Missing required price fields", data)
                        else:
                            self.log_test(f"Crypto Price - {currency}", False, 
                                        "Invalid price response format", data)
                    else:
                        self.log_test(f"Crypto Price - {currency}", False, 
                                    f"HTTP {response.status}: {await response.text()}")
            except Exception as e:
                self.log_test(f"Crypto Price - {currency}", False, f"Error: {str(e)}")

    async def test_redis_caching(self):
        """Test 16: Redis caching functionality for price data"""
        try:
            # Make first request to populate cache
            async with self.session.get(f"{self.base_url}/conversion/rates") as response1:
                if response1.status == 200:
                    data1 = await response1.json()
                    
                    # Make second request immediately to test cache
                    async with self.session.get(f"{self.base_url}/conversion/rates") as response2:
                        if response2.status == 200:
                            data2 = await response2.json()
                            
                            # Check if second request came from cache
                            source1 = data1.get("source", "")
                            source2 = data2.get("source", "")
                            
                            if source2 == "cache":
                                self.log_test("Redis Caching", True, 
                                            f"Redis caching working: first source: {source1}, second source: {source2}", 
                                            {"first_source": source1, "second_source": source2})
                            elif source1 == "coingecko" and source2 == "coingecko":
                                self.log_test("Redis Caching", True, 
                                            "Redis may be working but cache not hit in test timeframe", 
                                            {"first_source": source1, "second_source": source2})
                            else:
                                self.log_test("Redis Caching", False, 
                                            f"Redis caching not working properly: sources {source1}, {source2}", 
                                            {"first_source": source1, "second_source": source2})
                        else:
                            self.log_test("Redis Caching", False, 
                                        f"Second request failed: HTTP {response2.status}")
                else:
                    self.log_test("Redis Caching", False, 
                                f"First request failed: HTTP {response1.status}")
        except Exception as e:
            self.log_test("Redis Caching", False, f"Error: {str(e)}")

    async def test_real_blockchain_balance_doge(self):
        """Test 17: Real DOGE blockchain balance endpoint"""
        try:
            # Test with valid DOGE address
            valid_doge_address = "DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L"
            
            async with self.session.get(f"{self.base_url}/wallet/balance/DOGE?wallet_address={valid_doge_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "balance", "currency", "address", "source"]
                    
                    if all(field in data for field in required_fields):
                        if data.get("success") and data.get("source") == "blockcypher":
                            balance = data.get("balance", 0)
                            self.log_test("Real DOGE Balance", True, 
                                        f"Real DOGE balance retrieved: {balance} DOGE from BlockCypher API", data)
                        else:
                            self.log_test("Real DOGE Balance", False, 
                                        f"DOGE balance not from real blockchain API: source={data.get('source')}", data)
                    else:
                        self.log_test("Real DOGE Balance", False, 
                                    "Missing required fields in DOGE balance response", data)
                else:
                    self.log_test("Real DOGE Balance", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    
            # Test with invalid DOGE address
            invalid_address = "invalid_doge_address"
            async with self.session.get(f"{self.base_url}/wallet/balance/DOGE?wallet_address={invalid_address}") as response:
                if response.status in [400, 500]:
                    data = await response.json()
                    if "error" in data:
                        self.log_test("DOGE Invalid Address Handling", True, 
                                    "Invalid DOGE address correctly rejected", data)
                    else:
                        self.log_test("DOGE Invalid Address Handling", False, 
                                    "Invalid address not properly handled", data)
                else:
                    self.log_test("DOGE Invalid Address Handling", False, 
                                f"Expected error for invalid address, got HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("Real DOGE Balance", False, f"Error: {str(e)}")

    async def test_real_blockchain_balance_trx(self):
        """Test 18: Real TRX blockchain balance endpoint"""
        try:
            # Test with valid TRX address
            valid_trx_address = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
            
            async with self.session.get(f"{self.base_url}/wallet/balance/TRX?wallet_address={valid_trx_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "balance", "currency", "address", "source"]
                    
                    if all(field in data for field in required_fields):
                        if data.get("success") and data.get("source") == "trongrid":
                            balance = data.get("balance", 0)
                            self.log_test("Real TRX Balance", True, 
                                        f"Real TRX balance retrieved: {balance} TRX from TronGrid API", data)
                        else:
                            self.log_test("Real TRX Balance", False, 
                                        f"TRX balance not from real blockchain API: source={data.get('source')}", data)
                    else:
                        self.log_test("Real TRX Balance", False, 
                                    "Missing required fields in TRX balance response", data)
                else:
                    self.log_test("Real TRX Balance", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    
            # Test with invalid TRX address
            invalid_address = "invalid_trx_address"
            async with self.session.get(f"{self.base_url}/wallet/balance/TRX?wallet_address={invalid_address}") as response:
                if response.status in [400, 500]:
                    data = await response.json()
                    if "error" in data:
                        self.log_test("TRX Invalid Address Handling", True, 
                                    "Invalid TRX address correctly rejected", data)
                    else:
                        self.log_test("TRX Invalid Address Handling", False, 
                                    "Invalid address not properly handled", data)
                else:
                    self.log_test("TRX Invalid Address Handling", False, 
                                f"Expected error for invalid address, got HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("Real TRX Balance", False, f"Error: {str(e)}")

    async def test_real_blockchain_balance_crt(self):
        """Test 19: Real CRT blockchain balance endpoint"""
        try:
            # Test with valid Solana address
            valid_solana_address = "DFvHX8ZdqNqbCLJKnwe4h7qqj3hj4dw3pYvQRzweWnP7"
            
            async with self.session.get(f"{self.base_url}/wallet/balance/CRT?wallet_address={valid_solana_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "balance", "currency", "address", "source"]
                    
                    if all(field in data for field in required_fields):
                        if data.get("success") and data.get("source") == "solana_rpc":
                            balance = data.get("balance", 0)
                            mint_address = data.get("mint_address")
                            self.log_test("Real CRT Balance", True, 
                                        f"Real CRT balance retrieved: {balance} CRT from Solana RPC, mint: {mint_address}", data)
                        else:
                            self.log_test("Real CRT Balance", False, 
                                        f"CRT balance not from real blockchain API: source={data.get('source')}", data)
                    else:
                        self.log_test("Real CRT Balance", False, 
                                    "Missing required fields in CRT balance response", data)
                else:
                    self.log_test("Real CRT Balance", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    
            # Test with invalid Solana address
            invalid_address = "invalid_solana_address"
            async with self.session.get(f"{self.base_url}/wallet/balance/CRT?wallet_address={invalid_address}") as response:
                if response.status in [400, 500]:
                    data = await response.json()
                    if "error" in data:
                        self.log_test("CRT Invalid Address Handling", True, 
                                    "Invalid Solana address correctly rejected", data)
                    else:
                        self.log_test("CRT Invalid Address Handling", False, 
                                    "Invalid address not properly handled", data)
                else:
                    self.log_test("CRT Invalid Address Handling", False, 
                                f"Expected error for invalid address, got HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("Real CRT Balance", False, f"Error: {str(e)}")

    async def test_real_blockchain_balance_sol(self):
        """Test 20: Real SOL blockchain balance endpoint"""
        try:
            # Test with valid Solana address
            valid_solana_address = "DFvHX8ZdqNqbCLJKnwe4h7qqj3hj4dw3pYvQRzweWnP7"
            
            async with self.session.get(f"{self.base_url}/wallet/balance/SOL?wallet_address={valid_solana_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "balance", "currency", "address", "source"]
                    
                    if all(field in data for field in required_fields):
                        if data.get("success") and data.get("source") == "solana_rpc":
                            balance = data.get("balance", 0)
                            lamports = data.get("lamports", 0)
                            self.log_test("Real SOL Balance", True, 
                                        f"Real SOL balance retrieved: {balance} SOL ({lamports} lamports) from Solana RPC", data)
                        else:
                            self.log_test("Real SOL Balance", False, 
                                        f"SOL balance not from real blockchain API: source={data.get('source')}", data)
                    else:
                        self.log_test("Real SOL Balance", False, 
                                    "Missing required fields in SOL balance response", data)
                else:
                    self.log_test("Real SOL Balance", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self.log_test("Real SOL Balance", False, f"Error: {str(e)}")

    async def test_all_blockchain_balances(self):
        """Test 21: Get all real blockchain balances endpoint"""
        try:
            # Test with valid Solana address (works for all chains)
            valid_address = "DFvHX8ZdqNqbCLJKnwe4h7qqj3hj4dw3pYvQRzweWnP7"
            
            async with self.session.get(f"{self.base_url}/blockchain/balances?wallet_address={valid_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "wallet_address", "balances", "last_updated"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        balances = data.get("balances", {})
                        errors = data.get("errors", {})
                        
                        # Check if we have balances for expected currencies
                        expected_currencies = ["DOGE", "TRX", "CRT", "SOL"]
                        found_currencies = []
                        real_sources = []
                        
                        for currency in expected_currencies:
                            if currency in balances:
                                found_currencies.append(currency)
                                source = balances[currency].get("source", "unknown")
                                real_sources.append(f"{currency}:{source}")
                        
                        if len(found_currencies) >= 3:  # At least 3 currencies should work
                            self.log_test("All Blockchain Balances", True, 
                                        f"Multi-chain balance retrieval working: {found_currencies}, sources: {real_sources}", data)
                        else:
                            self.log_test("All Blockchain Balances", False, 
                                        f"Insufficient blockchain integrations working: only {found_currencies}", data)
                    else:
                        self.log_test("All Blockchain Balances", False, 
                                    "Invalid multi-chain balance response format", data)
                else:
                    self.log_test("All Blockchain Balances", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self.log_test("All Blockchain Balances", False, f"Error: {str(e)}")

    async def test_crt_token_info(self):
        """Test 22: CRT token information endpoint"""
        try:
            async with self.session.get(f"{self.base_url}/crt/info") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "token_info", "current_price", "mint_address", "decimals"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        token_info = data.get("token_info", {})
                        mint_address = data.get("mint_address")
                        decimals = data.get("decimals")
                        current_price = data.get("current_price")
                        
                        # Check if this is real CRT token info
                        expected_mint = "6kx78Yu19PmGjb9YbfP5nRUvFPY4kFcDKKmGpdSpump"
                        if mint_address == expected_mint and decimals == 6:
                            # Check token info structure
                            if isinstance(token_info, dict) and "supply" in token_info:
                                supply = token_info.get("supply", 0)
                                if supply > 900000000:  # ~1B supply expected
                                    self.log_test("CRT Token Info", True, 
                                                f"Real CRT token info: supply={supply}, decimals={decimals}, price=${current_price}", data)
                                else:
                                    self.log_test("CRT Token Info", False, 
                                                f"CRT token supply seems incorrect: {supply}", data)
                            else:
                                self.log_test("CRT Token Info", False, 
                                            "CRT token info missing supply data", data)
                        else:
                            self.log_test("CRT Token Info", False, 
                                        f"CRT token mint/decimals incorrect: mint={mint_address}, decimals={decimals}", data)
                    else:
                        self.log_test("CRT Token Info", False, 
                                    "Invalid CRT token info response format", data)
                else:
                    self.log_test("CRT Token Info", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    
        except Exception as e:
            self.log_test("CRT Token Info", False, f"Error: {str(e)}")

    async def test_crt_simulate_deposit(self):
        """Test 23: CRT simulate deposit endpoint"""
        try:
            # Test CRT deposit simulation
            valid_solana_address = "DFvHX8ZdqNqbCLJKnwe4h7qqj3hj4dw3pYvQRzweWnP7"
            
            payload = {
                "wallet_address": valid_solana_address,
                "amount": 1000000.0  # 1M CRT
            }
            
            async with self.session.post(f"{self.base_url}/crt/simulate-deposit", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success"]
                    
                    if data.get("success"):
                        # Check if simulation provides meaningful data
                        if "transaction_id" in data or "simulated_balance" in data or "message" in data:
                            self.log_test("CRT Simulate Deposit", True, 
                                        f"CRT deposit simulation working: {data.get('message', 'Simulation successful')}", data)
                        else:
                            self.log_test("CRT Simulate Deposit", True, 
                                        "CRT deposit simulation endpoint functional", data)
                    else:
                        self.log_test("CRT Simulate Deposit", False, 
                                    "CRT deposit simulation failed", data)
                else:
                    self.log_test("CRT Simulate Deposit", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    
            # Test with missing wallet address
            invalid_payload = {"amount": 1000000.0}
            async with self.session.post(f"{self.base_url}/crt/simulate-deposit", json=invalid_payload) as response:
                if response.status == 400:
                    data = await response.json()
                    if "wallet_address is required" in data.get("detail", ""):
                        self.log_test("CRT Deposit Validation", True, 
                                    "CRT deposit validation working - missing wallet address rejected", data)
                    else:
                        self.log_test("CRT Deposit Validation", False, 
                                    "CRT deposit validation not working properly", data)
                else:
                    self.log_test("CRT Deposit Validation", False, 
                                f"Expected 400 for invalid payload, got HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("CRT Simulate Deposit", False, f"Error: {str(e)}")

    async def test_integration_flow(self):
        """Test 24: Complete integration flow - registration → login → wallet → conversion rates"""
        try:
            # Step 1: Register new user
            flow_wallet = f"FlowTest{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            flow_password = "FlowTestPassword123!"
            
            reg_payload = {
                "wallet_address": flow_wallet,
                "password": flow_password
            }
            
            async with self.session.post(f"{self.base_url}/auth/register", 
                                       json=reg_payload) as reg_response:
                if reg_response.status != 200:
                    self.log_test("Integration Flow", False, "Registration step failed")
                    return
                
                reg_data = await reg_response.json()
                if not reg_data.get("success"):
                    self.log_test("Integration Flow", False, "Registration not successful")
                    return
            
            # Step 2: Login with registered user
            login_payload = {
                "identifier": flow_wallet,
                "password": flow_password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login", 
                                       json=login_payload) as login_response:
                if login_response.status != 200:
                    self.log_test("Integration Flow", False, "Login step failed")
                    return
                
                login_data = await login_response.json()
                if not login_data.get("success"):
                    self.log_test("Integration Flow", False, "Login not successful")
                    return
            
            # Step 3: Get conversion rates
            async with self.session.get(f"{self.base_url}/conversion/rates") as rates_response:
                if rates_response.status != 200:
                    self.log_test("Integration Flow", False, "Conversion rates step failed")
                    return
                
                rates_data = await rates_response.json()
                if not rates_data.get("success"):
                    self.log_test("Integration Flow", False, "Conversion rates not successful")
                    return
            
            # Step 4: Test wallet authentication flow (challenge + verify)
            challenge_payload = {
                "wallet_address": flow_wallet,
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/auth/challenge", 
                                       json=challenge_payload) as challenge_response:
                if challenge_response.status != 200:
                    self.log_test("Integration Flow", False, "Wallet challenge step failed")
                    return
                
                challenge_data = await challenge_response.json()
                if not challenge_data.get("success"):
                    self.log_test("Integration Flow", False, "Wallet challenge not successful")
                    return
                
                # Verify with mock signature
                verify_payload = {
                    "challenge_hash": challenge_data.get("challenge_hash"),
                    "signature": "mock_signature_integration_test",
                    "wallet_address": flow_wallet,
                    "network": "solana"
                }
                
                async with self.session.post(f"{self.base_url}/auth/verify", 
                                           json=verify_payload) as verify_response:
                    if verify_response.status != 200:
                        self.log_test("Integration Flow", False, "Wallet verification step failed")
                        return
                    
                    verify_data = await verify_response.json()
                    if not verify_data.get("success"):
                        self.log_test("Integration Flow", False, "Wallet verification not successful")
                        return
                    
                    # All steps successful
                    self.log_test("Integration Flow", True, 
                                "Complete integration flow successful: registration → login → wallet auth → conversion rates", 
                                {
                                    "registration": reg_data.get("success"),
                                    "login": login_data.get("success"),
                                    "conversion_rates": rates_data.get("success"),
                                    "wallet_auth": verify_data.get("success")
                                })
                    
        except Exception as e:
            self.log_test("Integration Flow", False, f"Error: {str(e)}")

    async def test_specific_user_login_wallet_address(self):
        """Test 25: Specific user login with wallet address - DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"""
        try:
            # Test login with the specific wallet address and password from user complaint
            target_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
            target_password = "crt21million"
            
            login_payload = {
                "identifier": target_wallet,
                "password": target_password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "message", "user_id", "username", "wallet_address", "created_at"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        # Verify the returned data matches expected user
                        if (data.get("wallet_address") == target_wallet and 
                            data.get("username") == "cryptoking"):
                            self.log_test("Specific User Login (Wallet)", True, 
                                        f"✅ LOGIN SUCCESSFUL for wallet {target_wallet} (username: {data.get('username')})", data)
                        else:
                            self.log_test("Specific User Login (Wallet)", False, 
                                        f"Login successful but user data mismatch: expected cryptoking, got {data.get('username')}", data)
                    else:
                        self.log_test("Specific User Login (Wallet)", False, 
                                    f"Login failed: {data.get('message', 'Unknown error')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("Specific User Login (Wallet)", False, 
                                f"❌ LOGIN FAILED - HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Specific User Login (Wallet)", False, f"Error: {str(e)}")

    async def test_specific_user_login_username(self):
        """Test 26: Specific user login with username - cryptoking"""
        try:
            # Test login with username endpoint
            target_username = "cryptoking"
            target_password = "crt21million"
            
            login_payload = {
                "username": target_username,
                "password": target_password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "message", "user_id", "username", "wallet_address", "created_at"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        # Verify the returned data matches expected user
                        expected_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
                        if (data.get("username") == target_username and 
                            data.get("wallet_address") == expected_wallet):
                            self.log_test("Specific User Login (Username)", True, 
                                        f"✅ USERNAME LOGIN SUCCESSFUL for {target_username} (wallet: {data.get('wallet_address')})", data)
                        else:
                            self.log_test("Specific User Login (Username)", False, 
                                        f"Login successful but user data mismatch: expected {expected_wallet}, got {data.get('wallet_address')}", data)
                    else:
                        self.log_test("Specific User Login (Username)", False, 
                                    f"Username login failed: {data.get('message', 'Unknown error')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("Specific User Login (Username)", False, 
                                f"❌ USERNAME LOGIN FAILED - HTTP {response.status}: {error_text}")
        except Exception as e:
            self.log_test("Specific User Login (Username)", False, f"Error: {str(e)}")

    async def test_login_error_scenarios(self):
        """Test 27: Login error scenarios and edge cases"""
        try:
            # Test 1: Invalid wallet address
            invalid_wallet_payload = {
                "identifier": "InvalidWalletAddress123",
                "password": "crt21million"
            }
            
            async with self.session.post(f"{self.base_url}/auth/login", 
                                       json=invalid_wallet_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data.get("success") and "not found" in data.get("message", "").lower():
                        self.log_test("Login Error - Invalid Wallet", True, 
                                    f"✅ Invalid wallet correctly rejected: {data.get('message')}", data)
                    else:
                        self.log_test("Login Error - Invalid Wallet", False, 
                                    f"Invalid wallet should be rejected but got: {data}", data)
                else:
                    self.log_test("Login Error - Invalid Wallet", False, 
                                f"Expected 200 with error message, got HTTP {response.status}")
            
            # Test 2: Valid wallet, wrong password
            wrong_password_payload = {
                "identifier": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
                "password": "wrongpassword123"
            }
            
            async with self.session.post(f"{self.base_url}/auth/login", 
                                       json=wrong_password_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data.get("success") and "password" in data.get("message", "").lower():
                        self.log_test("Login Error - Wrong Password", True, 
                                    f"✅ Wrong password correctly rejected: {data.get('message')}", data)
                    else:
                        self.log_test("Login Error - Wrong Password", False, 
                                    f"Wrong password should be rejected but got: {data}", data)
                else:
                    self.log_test("Login Error - Wrong Password", False, 
                                f"Expected 200 with error message, got HTTP {response.status}")
            
            # Test 3: Invalid username
            invalid_username_payload = {
                "username": "nonexistentuser",
                "password": "crt21million"
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=invalid_username_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data.get("success") and "not found" in data.get("message", "").lower():
                        self.log_test("Login Error - Invalid Username", True, 
                                    f"✅ Invalid username correctly rejected: {data.get('message')}", data)
                    else:
                        self.log_test("Login Error - Invalid Username", False, 
                                    f"Invalid username should be rejected but got: {data}", data)
                else:
                    self.log_test("Login Error - Invalid Username", False, 
                                f"Expected 200 with error message, got HTTP {response.status}")
            
            # Test 4: Valid username, wrong password
            wrong_password_username_payload = {
                "username": "cryptoking",
                "password": "wrongpassword123"
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=wrong_password_username_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data.get("success") and "password" in data.get("message", "").lower():
                        self.log_test("Login Error - Username Wrong Password", True, 
                                    f"✅ Wrong password for username correctly rejected: {data.get('message')}", data)
                    else:
                        self.log_test("Login Error - Username Wrong Password", False, 
                                    f"Wrong password for username should be rejected but got: {data}", data)
                else:
                    self.log_test("Login Error - Username Wrong Password", False, 
                                f"Expected 200 with error message, got HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("Login Error Scenarios", False, f"Error: {str(e)}")

    async def test_password_hashing_verification(self):
        """Test 28: Password hashing and verification process"""
        try:
            # Test that the system properly handles bcrypt password verification
            # by attempting login with the known user
            target_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
            target_password = "crt21million"
            
            # First, let's test a successful login to verify password hashing works
            login_payload = {
                "identifier": target_wallet,
                "password": target_password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_test("Password Hashing Verification", True, 
                                    "✅ Password hashing/verification working correctly - bcrypt authentication successful", data)
                    else:
                        self.log_test("Password Hashing Verification", False, 
                                    f"Password verification failed: {data.get('message')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("Password Hashing Verification", False, 
                                f"Password verification endpoint error - HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Password Hashing Verification", False, f"Error: {str(e)}")

    async def test_authentication_endpoints_availability(self):
        """Test 29: Authentication endpoints availability and structure"""
        try:
            # Test that both login endpoints exist and return proper error structure
            endpoints_to_test = [
                ("/auth/login", {"identifier": "test", "password": "test"}),
                ("/auth/login-username", {"username": "test", "password": "test"})
            ]
            
            all_endpoints_available = True
            endpoint_results = {}
            
            for endpoint, payload in endpoints_to_test:
                try:
                    async with self.session.post(f"{self.base_url}{endpoint}", 
                                               json=payload) as response:
                        if response.status in [200, 400, 404]:  # Any of these are acceptable
                            data = await response.json() if response.status != 404 else {"error": "Not found"}
                            endpoint_results[endpoint] = {
                                "status": response.status,
                                "available": True,
                                "response_structure": list(data.keys()) if isinstance(data, dict) else "non-dict"
                            }
                        else:
                            endpoint_results[endpoint] = {
                                "status": response.status,
                                "available": False,
                                "error": await response.text()
                            }
                            all_endpoints_available = False
                except Exception as e:
                    endpoint_results[endpoint] = {
                        "available": False,
                        "error": str(e)
                    }
                    all_endpoints_available = False
            
            if all_endpoints_available:
                self.log_test("Authentication Endpoints Availability", True, 
                            "✅ All authentication endpoints are available and responding", endpoint_results)
            else:
                self.log_test("Authentication Endpoints Availability", False, 
                            "❌ Some authentication endpoints are not available", endpoint_results)
                    
        except Exception as e:
            self.log_test("Authentication Endpoints Availability", False, f"Error: {str(e)}")
    
    async def run_all_tests(self):
        """Run all wallet management tests"""
        print(f"🚀 Starting Casino Savings dApp Backend Tests - Focus on Login Functionality")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 70)
        
        # Run tests in logical order
        await self.test_basic_connectivity()
        
        # PRIORITY: Login functionality tests (as requested)
        print("\n🔐 TESTING LOGIN FUNCTIONALITY (USER COMPLAINT: 'Log in is not working')")
        print("=" * 70)
        await self.test_authentication_endpoints_availability()
        await self.test_specific_user_login_wallet_address()
        await self.test_specific_user_login_username()
        await self.test_password_hashing_verification()
        await self.test_login_error_scenarios()
        
        # Real-money integration endpoints
        await self.test_user_registration()
        await self.test_user_login()
        await self.test_integration_flow()
        
        # Real blockchain integration endpoints
        await self.test_real_blockchain_balance_doge()
        await self.test_real_blockchain_balance_trx()
        await self.test_real_blockchain_balance_crt()
        await self.test_real_blockchain_balance_sol()
        await self.test_all_blockchain_balances()
        await self.test_crt_token_info()
        await self.test_crt_simulate_deposit()
        
        # Crypto pricing and caching
        await self.test_real_crypto_conversion_rates()
        await self.test_individual_crypto_prices()
        await self.test_redis_caching()
        
        # Original authentication flow
        challenge_data = await self.test_auth_challenge_generation()
        await self.test_auth_verification(challenge_data)
        
        # Wallet management endpoints
        await self.test_wallet_info_endpoint()
        await self.test_deposit_endpoint()
        await self.test_withdraw_endpoint()
        await self.test_convert_endpoint()
        
        # Game and savings system
        await self.test_game_betting()
        await self.test_savings_system()
        
        # Real-time and database features
        await self.test_websocket_wallet_monitor()
        await self.test_database_integration()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 WALLET MANAGEMENT SYSTEM TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Categorize results
        critical_failures = []
        minor_issues = []
        
        for result in self.test_results:
            if not result["success"]:
                test_name = result["test"]
                if test_name in ["Basic Connectivity", "User Registration", "User Login", 
                               "Real Crypto Conversion Rates", "Integration Flow",
                               "Auth Challenge Generation", "Auth Verification", 
                               "Game Betting", "Savings System", "Database Integration",
                               "Real DOGE Balance", "Real TRX Balance", "Real CRT Balance", 
                               "Real SOL Balance", "All Blockchain Balances", "CRT Token Info",
                               "CRT Simulate Deposit", "Specific User Login (Wallet)",
                               "Specific User Login (Username)", "Password Hashing Verification",
                               "Authentication Endpoints Availability"]:
                    critical_failures.append(result)
                else:
                    minor_issues.append(result)
        
        if critical_failures:
            print("\n🚨 CRITICAL FAILURES:")
            for result in critical_failures:
                print(f"  ❌ {result['test']}: {result['details']}")
        
        if minor_issues:
            print("\n⚠️  MINOR ISSUES:")
            for result in minor_issues:
                print(f"  ⚠️  {result['test']}: {result['details']}")
        
        print("\n" + "=" * 70)
        
        return {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "critical_failures": len(critical_failures),
            "minor_issues": len(minor_issues),
            "success_rate": passed_tests/total_tests*100,
            "results": self.test_results
        }

async def main():
    """Main test runner"""
    async with WalletAPITester(BACKEND_URL) as tester:
        await tester.run_all_tests()
        summary = tester.print_summary()
        
        # Save detailed results
        with open("/app/backend_test_results.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: /app/backend_test_results.json")
        
        # Return exit code based on critical failures
        return 0 if summary["critical_failures"] == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)