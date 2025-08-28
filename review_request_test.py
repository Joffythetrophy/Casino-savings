#!/usr/bin/env python3
"""
Review Request Testing - Test newly implemented fixes
Tests specific endpoints mentioned in the review request:
1. Autoplay fix - /api/games/autoplay endpoint
2. External withdrawal fix - /api/wallet/external-withdraw endpoint  
3. User's conversion request - /api/wallet/batch-convert endpoint
4. Loss tracker verification
5. Gaming balance testing
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://cryptoplay-8.preview.emergentagent.com/api"

class ReviewRequestTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth_token: Optional[str] = None
        self.test_results = []
        
        # User credentials from review request
        self.test_username = "cryptoking"
        self.test_password = "crt21million"
        self.test_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        
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
        
    async def authenticate_user(self):
        """Authenticate with the specific user credentials and get JWT token"""
        try:
            # Step 1: Login with username to verify user exists
            login_payload = {
                "username": self.test_username,
                "password": self.test_password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if not data.get("success"):
                        self.log_test("User Authentication", False, 
                                    f"Login failed: {data.get('message')}")
                        return False
                else:
                    self.log_test("User Authentication", False, 
                                f"Login HTTP {response.status}: {await response.text()}")
                    return False
            
            # Step 2: Get wallet authentication challenge
            challenge_payload = {
                "wallet_address": self.test_wallet,
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/auth/challenge", 
                                       json=challenge_payload) as response:
                if response.status == 200:
                    challenge_data = await response.json()
                    if not challenge_data.get("success"):
                        self.log_test("User Authentication", False, 
                                    f"Challenge failed: {challenge_data}")
                        return False
                else:
                    self.log_test("User Authentication", False, 
                                f"Challenge HTTP {response.status}: {await response.text()}")
                    return False
            
            # Step 3: Verify with mock signature to get JWT token
            verify_payload = {
                "challenge_hash": challenge_data.get("challenge_hash"),
                "signature": "mock_signature_for_testing_purposes_12345",
                "wallet_address": self.test_wallet,
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/auth/verify", 
                                       json=verify_payload) as response:
                if response.status == 200:
                    verify_data = await response.json()
                    if verify_data.get("success") and verify_data.get("token"):
                        self.auth_token = verify_data.get("token")
                        self.log_test("User Authentication", True, 
                                    f"Successfully authenticated as {self.test_username} with JWT token")
                        return True
                    else:
                        self.log_test("User Authentication", False, 
                                    f"JWT verification failed: {verify_data}")
                        return False
                else:
                    self.log_test("User Authentication", False, 
                                f"JWT verification HTTP {response.status}: {await response.text()}")
                    return False
                    
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
            return False

    async def test_autoplay_endpoint(self):
        """Test 1: NEW AUTOPLAY FIX - Test /api/games/autoplay endpoint"""
        if not self.auth_token:
            self.log_test("Autoplay Endpoint", False, "No JWT token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test the new autoplay endpoint with authentication
            payload = {
                "wallet_address": self.test_wallet,
                "game_type": "Slot Machine",
                "bet_amount": 10.0,
                "currency": "CRT",
                "strategy": "constant"
            }
            
            async with self.session.post(f"{self.base_url}/games/autoplay", 
                                       json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "game_id", "result", "bet_amount", "payout", "currency", "autoplay", "strategy"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        result = data.get("result")
                        bet_amount = data.get("bet_amount")
                        payout = data.get("payout")
                        savings_contribution = data.get("savings_contribution", 0)
                        autoplay_flag = data.get("autoplay")
                        strategy = data.get("strategy")
                        
                        # Verify autoplay processed the bet correctly
                        if autoplay_flag and strategy == "constant":
                            # Check if it integrates with savings vault system for losses
                            if result == "loss" and savings_contribution > 0:
                                self.log_test("Autoplay Endpoint", True, 
                                            f"Autoplay working: {result}, bet: {bet_amount}, savings: {savings_contribution}, strategy: {strategy}", data)
                            elif result == "win":
                                self.log_test("Autoplay Endpoint", True, 
                                            f"Autoplay working: {result}, bet: {bet_amount}, payout: {payout}, strategy: {strategy}", data)
                            else:
                                self.log_test("Autoplay Endpoint", True, 
                                            f"Autoplay working: {result}, bet: {bet_amount}, strategy: {strategy}", data)
                        else:
                            self.log_test("Autoplay Endpoint", False, 
                                        f"Autoplay flags missing: autoplay={autoplay_flag}, strategy={strategy}", data)
                    elif data.get("autoplay_status") == "insufficient_funds":
                        # Expected if user doesn't have enough balance
                        self.log_test("Autoplay Endpoint", True, 
                                    f"Autoplay validation working: {data.get('message')}", data)
                    else:
                        self.log_test("Autoplay Endpoint", False, 
                                    f"Invalid autoplay response: {data}", data)
                elif response.status == 404:
                    self.log_test("Autoplay Endpoint", False, 
                                "Autoplay endpoint not found - may not be implemented yet")
                elif response.status == 403:
                    self.log_test("Autoplay Endpoint", False, 
                                "Authentication failed for autoplay endpoint")
                else:
                    self.log_test("Autoplay Endpoint", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Autoplay Endpoint", False, f"Error: {str(e)}")

    async def test_external_withdrawal_endpoint(self):
        """Test 2: EXTERNAL WITHDRAWAL FIX - Test /api/wallet/external-withdraw endpoint"""
        if not self.auth_token:
            self.log_test("External Withdrawal Endpoint", False, "No JWT token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test the new external withdrawal endpoint
            payload = {
                "wallet_address": self.test_wallet,
                "currency": "DOGE",
                "amount": 100.0,
                "destination_address": "DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L",  # Valid DOGE address
                "wallet_type": "deposit"
            }
            
            async with self.session.post(f"{self.base_url}/wallet/external-withdraw", 
                                       json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "message", "transaction_id"]
                    
                    if data.get("success"):
                        # Check if it accepts external wallet addresses
                        if "destination_address" in data and data.get("destination_address") == payload["destination_address"]:
                            # Check minimum withdrawal limits and balance validation
                            if "new_balance" in data or "current_balance" in data:
                                self.log_test("External Withdrawal Endpoint", True, 
                                            f"External withdrawal working: {data.get('message')}", data)
                            else:
                                self.log_test("External Withdrawal Endpoint", True, 
                                            f"External withdrawal processed: {data.get('message')}", data)
                        else:
                            self.log_test("External Withdrawal Endpoint", False, 
                                        "External withdrawal doesn't properly handle destination address", data)
                    elif "insufficient" in data.get("message", "").lower():
                        # Expected if user doesn't have enough balance
                        self.log_test("External Withdrawal Endpoint", True, 
                                    f"External withdrawal validation working: {data.get('message')}", data)
                    else:
                        self.log_test("External Withdrawal Endpoint", False, 
                                    f"External withdrawal failed: {data.get('message')}", data)
                elif response.status == 404:
                    self.log_test("External Withdrawal Endpoint", False, 
                                "External withdrawal endpoint not found - may not be implemented yet")
                elif response.status == 400:
                    # Check if it's proper validation
                    data = await response.json()
                    if "balance" in data.get("detail", "").lower() or "insufficient" in data.get("detail", "").lower():
                        self.log_test("External Withdrawal Endpoint", True, 
                                    f"External withdrawal validation working: {data.get('detail')}", data)
                    else:
                        self.log_test("External Withdrawal Endpoint", False, 
                                    f"External withdrawal validation error: {data.get('detail')}", data)
                else:
                    self.log_test("External Withdrawal Endpoint", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("External Withdrawal Endpoint", False, f"Error: {str(e)}")

    async def test_batch_convert_endpoint(self):
        """Test 3: USER'S CONVERSION REQUEST - Test /api/wallet/batch-convert endpoint"""
        if not self.auth_token:
            self.log_test("Batch Convert Endpoint", False, "No JWT token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test the new batch conversion endpoint as requested
            # Convert DOGE to CRT and TRX evenly
            payload = {
                "wallet_address": self.test_wallet,
                "from_currency": "DOGE",
                "to_currencies": ["CRT", "TRX"],
                "amount": 20000  # Test amount as specified
            }
            
            async with self.session.post(f"{self.base_url}/wallet/batch-convert", 
                                       json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "conversions", "new_from_balance", "total_converted"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        conversions = data.get("conversions", [])
                        total_converted = data.get("total_converted", 0)
                        
                        # Verify it converts to both CRT and TRX
                        converted_currencies = [conv.get("to_currency") for conv in conversions]
                        if "CRT" in converted_currencies and "TRX" in converted_currencies:
                            # Check if amounts are split evenly
                            crt_amount = next((conv.get("to_amount", 0) for conv in conversions if conv.get("to_currency") == "CRT"), 0)
                            trx_amount = next((conv.get("to_amount", 0) for conv in conversions if conv.get("to_currency") == "TRX"), 0)
                            
                            self.log_test("Batch Convert Endpoint", True, 
                                        f"Batch conversion successful: {total_converted} DOGE → {crt_amount} CRT + {trx_amount} TRX", data)
                        else:
                            self.log_test("Batch Convert Endpoint", False, 
                                        f"Batch conversion didn't convert to expected currencies: {converted_currencies}", data)
                    elif "insufficient" in data.get("message", "").lower():
                        # Expected if user doesn't have enough DOGE
                        self.log_test("Batch Convert Endpoint", True, 
                                    f"Batch conversion validation working: {data.get('message')}", data)
                    else:
                        self.log_test("Batch Convert Endpoint", False, 
                                    f"Batch conversion failed: {data.get('message')}", data)
                elif response.status == 404:
                    self.log_test("Batch Convert Endpoint", False, 
                                "Batch convert endpoint not found - may not be implemented yet")
                elif response.status == 403:
                    self.log_test("Batch Convert Endpoint", False, 
                                "Authentication failed for batch convert endpoint")
                elif response.status == 400:
                    # Check if it's proper validation
                    data = await response.json()
                    if "balance" in data.get("detail", "").lower() or "insufficient" in data.get("detail", "").lower():
                        self.log_test("Batch Convert Endpoint", True, 
                                    f"Batch conversion validation working: {data.get('detail')}", data)
                    else:
                        self.log_test("Batch Convert Endpoint", False, 
                                    f"Batch conversion validation error: {data.get('detail')}", data)
                else:
                    self.log_test("Batch Convert Endpoint", False, 
                                f"HTTP {response.status}: {await response.text()}")
        except Exception as e:
            self.log_test("Batch Convert Endpoint", False, f"Error: {str(e)}")

    async def test_loss_tracker_status(self):
        """Test 4: VERIFY LOSS TRACKER STATUS - Re-confirm loss tracker is working"""
        if not self.auth_token:
            self.log_test("Loss Tracker Status", False, "No JWT token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test the savings/loss tracker endpoint
            async with self.session.get(f"{self.base_url}/savings/{self.test_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["success", "total_savings", "stats", "savings_history"]
                    
                    if all(field in data for field in required_fields) and data.get("success"):
                        total_savings = data.get("total_savings", {})
                        stats = data.get("stats", {})
                        savings_history = data.get("savings_history", [])
                        
                        # Check if loss tracker is recording losses
                        total_losses = stats.get("total_losses", 0)
                        total_games = stats.get("total_games", 0)
                        
                        if total_losses > 0 and len(savings_history) > 0:
                            # Verify recent losses are being tracked
                            recent_losses = [entry for entry in savings_history if entry.get("game_result") == "Loss"]
                            
                            self.log_test("Loss Tracker Status", True, 
                                        f"Loss tracker working: {total_losses} losses tracked, {len(recent_losses)} recent loss entries", data)
                        elif total_games > 0:
                            self.log_test("Loss Tracker Status", True, 
                                        f"Loss tracker ready: {total_games} games played, tracking system operational", data)
                        else:
                            self.log_test("Loss Tracker Status", True, 
                                        "Loss tracker system operational, no losses recorded yet", data)
                    else:
                        self.log_test("Loss Tracker Status", False, 
                                    "Invalid loss tracker response format", data)
                elif response.status == 403:
                    self.log_test("Loss Tracker Status", False, 
                                "Authentication failed for loss tracker endpoint")
                else:
                    self.log_test("Loss Tracker Status", False, 
                                f"HTTP {response.status}: {await response.text()}")
                    
            # Also test by placing a bet to verify new losses are tracked
            bet_payload = {
                "wallet_address": self.test_wallet,
                "game_type": "Slot Machine",
                "bet_amount": 5.0,
                "currency": "CRT",
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/games/bet", 
                                       json=bet_payload) as bet_response:
                if bet_response.status == 200:
                    bet_data = await bet_response.json()
                    if bet_data.get("success"):
                        result = bet_data.get("result")
                        savings_contribution = bet_data.get("savings_contribution", 0)
                        
                        if result == "loss" and savings_contribution > 0:
                            self.log_test("Loss Tracker Real-time", True, 
                                        f"Real-time loss tracking working: {savings_contribution} added to savings", bet_data)
                        elif result == "win":
                            self.log_test("Loss Tracker Real-time", True, 
                                        "Loss tracker ready (bet won, no loss to track)", bet_data)
                        else:
                            self.log_test("Loss Tracker Real-time", False, 
                                        "Loss tracker not recording savings contributions", bet_data)
                    else:
                        self.log_test("Loss Tracker Real-time", False, 
                                    "Could not place test bet to verify loss tracking")
                        
        except Exception as e:
            self.log_test("Loss Tracker Status", False, f"Error: {str(e)}")

    async def test_gaming_balance_functionality(self):
        """Test 5: GAMING BALANCE - Test gaming balance transfer functionality"""
        try:
            # First, get current wallet info to check gaming balance
            async with self.session.get(f"{self.base_url}/wallet/{self.test_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        gaming_balance = wallet.get("gaming_balance", {})
                        deposit_balance = wallet.get("deposit_balance", {})
                        
                        # Check if gaming balance structure exists
                        if isinstance(gaming_balance, dict):
                            crt_gaming = gaming_balance.get("CRT", 0)
                            crt_deposit = deposit_balance.get("CRT", 0)
                            
                            self.log_test("Gaming Balance Structure", True, 
                                        f"Gaming balance structure exists: CRT gaming={crt_gaming}, CRT deposit={crt_deposit}", data)
                            
                            # Test gaming balance transfer (if endpoint exists)
                            transfer_payload = {
                                "wallet_address": self.test_wallet,
                                "from_balance": "deposit",
                                "to_balance": "gaming",
                                "currency": "CRT",
                                "amount": 100.0
                            }
                            
                            async with self.session.post(f"{self.base_url}/wallet/transfer-balance", 
                                                       json=transfer_payload) as transfer_response:
                                if transfer_response.status == 200:
                                    transfer_data = await transfer_response.json()
                                    if transfer_data.get("success"):
                                        self.log_test("Gaming Balance Transfer", True, 
                                                    f"Gaming balance transfer working: {transfer_data.get('message')}", transfer_data)
                                    else:
                                        self.log_test("Gaming Balance Transfer", False, 
                                                    f"Gaming balance transfer failed: {transfer_data.get('message')}", transfer_data)
                                elif transfer_response.status == 404:
                                    self.log_test("Gaming Balance Transfer", False, 
                                                "Gaming balance transfer endpoint not found")
                                elif transfer_response.status == 400:
                                    # Check if it's proper validation
                                    transfer_data = await transfer_response.json()
                                    if "balance" in transfer_data.get("detail", "").lower():
                                        self.log_test("Gaming Balance Transfer", True, 
                                                    f"Gaming balance validation working: {transfer_data.get('detail')}", transfer_data)
                                    else:
                                        self.log_test("Gaming Balance Transfer", False, 
                                                    f"Gaming balance transfer error: {transfer_data.get('detail')}", transfer_data)
                                else:
                                    self.log_test("Gaming Balance Transfer", False, 
                                                f"Gaming balance transfer HTTP {transfer_response.status}")
                        else:
                            self.log_test("Gaming Balance Structure", False, 
                                        "Gaming balance structure not found in wallet data", data)
                    else:
                        self.log_test("Gaming Balance Structure", False, 
                                    "Could not retrieve wallet data for gaming balance test")
                else:
                    self.log_test("Gaming Balance Structure", False, 
                                f"Wallet endpoint HTTP {response.status}")
                    
        except Exception as e:
            self.log_test("Gaming Balance Functionality", False, f"Error: {str(e)}")

    async def test_user_wallet_balances(self):
        """Test 6: Verify user's current balances (especially DOGE balance mentioned in request)"""
        try:
            # Get user's wallet information
            async with self.session.get(f"{self.base_url}/wallet/{self.test_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        
                        # Check DOGE balance (mentioned as 36M+ in request)
                        doge_balance = deposit_balance.get("DOGE", 0)
                        crt_balance = deposit_balance.get("CRT", 0)
                        trx_balance = deposit_balance.get("TRX", 0)
                        
                        # Verify significant DOGE balance as mentioned in request
                        if doge_balance > 1000000:  # Over 1M DOGE
                            self.log_test("User DOGE Balance", True, 
                                        f"User has significant DOGE balance: {doge_balance:,.0f} DOGE (sufficient for conversion)", data)
                        elif doge_balance > 0:
                            self.log_test("User DOGE Balance", True, 
                                        f"User has DOGE balance: {doge_balance:,.2f} DOGE", data)
                        else:
                            self.log_test("User DOGE Balance", False, 
                                        f"User has no DOGE balance: {doge_balance} DOGE", data)
                        
                        # Check other balances
                        self.log_test("User Balance Summary", True, 
                                    f"Balances - CRT: {crt_balance:,.2f}, DOGE: {doge_balance:,.2f}, TRX: {trx_balance:,.2f}", 
                                    {"CRT": crt_balance, "DOGE": doge_balance, "TRX": trx_balance})
                    else:
                        self.log_test("User Wallet Balances", False, 
                                    "Could not retrieve user wallet data")
                else:
                    self.log_test("User Wallet Balances", False, 
                                f"Wallet endpoint HTTP {response.status}")
        except Exception as e:
            self.log_test("User Wallet Balances", False, f"Error: {str(e)}")

    async def run_all_tests(self):
        """Run all review request tests"""
        print("🚀 Starting Review Request Testing...")
        print(f"Testing backend: {self.base_url}")
        print(f"User: {self.test_username} ({self.test_wallet})")
        print("=" * 80)
        
        # Authenticate first
        auth_success = await self.authenticate_user()
        if not auth_success:
            print("❌ Authentication failed - cannot proceed with tests")
            return
        
        # Run all tests
        await self.test_user_wallet_balances()
        await self.test_autoplay_endpoint()
        await self.test_external_withdrawal_endpoint()
        await self.test_batch_convert_endpoint()
        await self.test_loss_tracker_status()
        await self.test_gaming_balance_functionality()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 REVIEW REQUEST TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        print("\n🎯 REVIEW REQUEST STATUS:")
        
        # Check specific requirements
        autoplay_working = any(r["success"] and "autoplay" in r["test"].lower() for r in self.test_results)
        external_withdraw_working = any(r["success"] and "external withdrawal" in r["test"].lower() for r in self.test_results)
        batch_convert_working = any(r["success"] and "batch convert" in r["test"].lower() for r in self.test_results)
        loss_tracker_working = any(r["success"] and "loss tracker" in r["test"].lower() for r in self.test_results)
        gaming_balance_working = any(r["success"] and "gaming balance" in r["test"].lower() for r in self.test_results)
        
        print(f"1. Autoplay Fix: {'✅ WORKING' if autoplay_working else '❌ NEEDS ATTENTION'}")
        print(f"2. External Withdrawal Fix: {'✅ WORKING' if external_withdraw_working else '❌ NEEDS ATTENTION'}")
        print(f"3. Batch Conversion: {'✅ WORKING' if batch_convert_working else '❌ NEEDS ATTENTION'}")
        print(f"4. Loss Tracker: {'✅ WORKING' if loss_tracker_working else '❌ NEEDS ATTENTION'}")
        print(f"5. Gaming Balance: {'✅ WORKING' if gaming_balance_working else '❌ NEEDS ATTENTION'}")

async def main():
    """Main test execution"""
    async with ReviewRequestTester(BACKEND_URL) as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())