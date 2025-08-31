#!/usr/bin/env python3
"""
URGENT BUG INVESTIGATION for user cryptoking (DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq)
Testing 5 critical issues reported by the user:
1. Autoplay System Not Working
2. Loss Tracker Not Working  
3. Gaming Balance Not Functioning
4. Missing Withdrawal Button
5. Currency Conversion Issues
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://crypto-treasury.preview.emergentagent.com/api"

class UrgentBugTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
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
        
    async def authenticate_user(self):
        """Authenticate the specific user for testing"""
        try:
            # Test login with username
            login_payload = {
                "username": self.username,
                "password": self.password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_test("User Authentication", True, 
                                    f"Successfully authenticated user {self.username}", data)
                        return True
                    else:
                        self.log_test("User Authentication", False, 
                                    f"Authentication failed: {data.get('message')}", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
            return False

    async def test_autoplay_system_bug(self):
        """BUG 1: Test AI auto-play functionality across all casino games"""
        print("\n🔍 TESTING BUG 1: AUTOPLAY SYSTEM NOT WORKING")
        
        # Test all game types with autoplay parameters
        game_types = ["Slot Machine", "Dice", "Roulette", "Plinko", "Keno", "Mines"]
        autoplay_results = []
        
        for game_type in game_types:
            try:
                # Test regular bet first
                bet_payload = {
                    "wallet_address": self.user_wallet,
                    "game_type": game_type,
                    "bet_amount": 10.0,
                    "currency": "CRT",
                    "network": "solana"
                }
                
                async with self.session.post(f"{self.base_url}/games/bet", 
                                           json=bet_payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            autoplay_results.append({
                                "game": game_type,
                                "bet_success": True,
                                "game_id": data.get("game_id"),
                                "result": data.get("result"),
                                "payout": data.get("payout"),
                                "savings_contribution": data.get("savings_contribution", 0)
                            })
                            self.log_test(f"Autoplay - {game_type} Bet", True, 
                                        f"Game bet successful: {data.get('result')}, payout: {data.get('payout')}")
                        else:
                            autoplay_results.append({
                                "game": game_type,
                                "bet_success": False,
                                "error": "Bet failed"
                            })
                            self.log_test(f"Autoplay - {game_type} Bet", False, 
                                        f"Game bet failed: {data}")
                    elif response.status == 403:
                        # Authentication required - this is expected for /api/games/bet
                        autoplay_results.append({
                            "game": game_type,
                            "bet_success": False,
                            "error": "Authentication required",
                            "status_code": 403
                        })
                        self.log_test(f"Autoplay - {game_type} Bet", False, 
                                    f"Authentication required for game betting (HTTP 403)")
                    else:
                        error_text = await response.text()
                        autoplay_results.append({
                            "game": game_type,
                            "bet_success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        })
                        self.log_test(f"Autoplay - {game_type} Bet", False, 
                                    f"HTTP {response.status}: {error_text}")
                        
            except Exception as e:
                autoplay_results.append({
                    "game": game_type,
                    "bet_success": False,
                    "error": str(e)
                })
                self.log_test(f"Autoplay - {game_type} Bet", False, f"Error: {str(e)}")
        
        # Test autoplay-specific endpoints if they exist
        try:
            # Check if there's an autoplay endpoint
            autoplay_payload = {
                "wallet_address": self.user_wallet,
                "game_type": "Slot Machine",
                "bet_amount": 10.0,
                "currency": "CRT",
                "autoplay": True,
                "autoplay_count": 5,
                "stop_on_win": True,
                "stop_on_loss_limit": 100.0
            }
            
            async with self.session.post(f"{self.base_url}/games/autoplay", 
                                       json=autoplay_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Autoplay Endpoint", True, 
                                f"Autoplay endpoint exists and working: {data}")
                elif response.status == 404:
                    self.log_test("Autoplay Endpoint", False, 
                                "❌ CRITICAL: No dedicated autoplay endpoint found")
                else:
                    error_text = await response.text()
                    self.log_test("Autoplay Endpoint", False, 
                                f"Autoplay endpoint error: HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Autoplay Endpoint", False, f"Error testing autoplay endpoint: {str(e)}")
        
        # Summary for Bug 1
        successful_games = sum(1 for result in autoplay_results if result.get("bet_success"))
        total_games = len(autoplay_results)
        
        if successful_games == 0:
            self.log_test("BUG 1 - Autoplay System", False, 
                        f"❌ CRITICAL: Autoplay system completely broken - 0/{total_games} games working")
        elif successful_games < total_games:
            self.log_test("BUG 1 - Autoplay System", False, 
                        f"⚠️ PARTIAL: Autoplay system partially working - {successful_games}/{total_games} games working")
        else:
            self.log_test("BUG 1 - Autoplay System", True, 
                        f"✅ Autoplay backend ready - {successful_games}/{total_games} games working")

    async def test_loss_tracker_bug(self):
        """BUG 2: Test the savings tracking system for game losses"""
        print("\n🔍 TESTING BUG 2: LOSS TRACKER NOT WORKING")
        
        try:
            # Test savings history endpoint
            async with self.session.get(f"{self.base_url}/savings/{self.user_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        total_savings = data.get("total_savings", {})
                        savings_history = data.get("savings_history", [])
                        stats = data.get("stats", {})
                        
                        # Check if loss tracking is working
                        total_losses = stats.get("total_losses", 0)
                        total_games = stats.get("total_games", 0)
                        
                        if total_losses > 0 and len(savings_history) > 0:
                            self.log_test("Loss Tracker - Savings History", True, 
                                        f"Loss tracking working: {total_losses} losses tracked, {len(savings_history)} history entries")
                        elif total_games > 0 and total_losses == 0:
                            self.log_test("Loss Tracker - Savings History", False, 
                                        f"❌ CRITICAL: {total_games} games played but 0 losses tracked")
                        else:
                            self.log_test("Loss Tracker - Savings History", False, 
                                        f"❌ CRITICAL: No game history or loss tracking data found")
                        
                        # Check savings amounts
                        total_saved_amount = sum(total_savings.values()) if isinstance(total_savings, dict) else 0
                        if total_saved_amount > 0:
                            self.log_test("Loss Tracker - Savings Amounts", True, 
                                        f"Savings amounts tracked: {total_savings}")
                        else:
                            self.log_test("Loss Tracker - Savings Amounts", False, 
                                        f"❌ CRITICAL: No savings amounts tracked despite losses")
                            
                    else:
                        self.log_test("Loss Tracker - Savings History", False, 
                                    f"Savings endpoint failed: {data}")
                elif response.status == 403:
                    self.log_test("Loss Tracker - Savings History", False, 
                                "❌ CRITICAL: Authentication required for savings endpoint")
                else:
                    error_text = await response.text()
                    self.log_test("Loss Tracker - Savings History", False, 
                                f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Loss Tracker - Savings History", False, f"Error: {str(e)}")
        
        # Test if losses are being recorded in real-time
        try:
            # Place a losing bet and check if it's tracked
            bet_payload = {
                "wallet_address": self.user_wallet,
                "game_type": "Slot Machine",
                "bet_amount": 5.0,
                "currency": "CRT",
                "network": "solana"
            }
            
            async with self.session.post(f"{self.base_url}/games/bet", 
                                       json=bet_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        result = data.get("result")
                        savings_contribution = data.get("savings_contribution", 0)
                        
                        if result == "loss" and savings_contribution > 0:
                            self.log_test("Loss Tracker - Real-time Tracking", True, 
                                        f"Real-time loss tracking working: {savings_contribution} added to savings")
                        elif result == "loss" and savings_contribution == 0:
                            self.log_test("Loss Tracker - Real-time Tracking", False, 
                                        f"❌ CRITICAL: Loss occurred but no savings contribution recorded")
                        else:
                            self.log_test("Loss Tracker - Real-time Tracking", True, 
                                        f"Game result: {result} (not a loss, so no savings expected)")
                    else:
                        self.log_test("Loss Tracker - Real-time Tracking", False, 
                                    f"Test bet failed: {data}")
                else:
                    self.log_test("Loss Tracker - Real-time Tracking", False, 
                                f"Cannot test real-time tracking - bet endpoint failed")
                    
        except Exception as e:
            self.log_test("Loss Tracker - Real-time Tracking", False, f"Error: {str(e)}")

    async def test_gaming_balance_bug(self):
        """BUG 3: Test gaming balance transfers and management"""
        print("\n🔍 TESTING BUG 3: GAMING BALANCE NOT FUNCTIONING")
        
        # Test wallet info to check gaming balance
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.user_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        gaming_balance = wallet.get("gaming_balance", {})
                        deposit_balance = wallet.get("deposit_balance", {})
                        
                        # Check if gaming balance exists and has structure
                        if isinstance(gaming_balance, dict):
                            total_gaming = sum(gaming_balance.values()) if gaming_balance else 0
                            total_deposit = sum(deposit_balance.values()) if deposit_balance else 0
                            
                            self.log_test("Gaming Balance - Structure", True, 
                                        f"Gaming balance structure exists: {gaming_balance}")
                            
                            if total_gaming > 0:
                                self.log_test("Gaming Balance - Has Funds", True, 
                                            f"Gaming balance has funds: {total_gaming}")
                            else:
                                self.log_test("Gaming Balance - Has Funds", False, 
                                            f"❌ Gaming balance is empty: {gaming_balance}")
                                
                            if total_deposit > 0:
                                self.log_test("Gaming Balance - Deposit Available", True, 
                                            f"Deposit balance available for transfer: {total_deposit}")
                            else:
                                self.log_test("Gaming Balance - Deposit Available", False, 
                                            f"❌ No deposit balance available for gaming: {deposit_balance}")
                        else:
                            self.log_test("Gaming Balance - Structure", False, 
                                        f"❌ CRITICAL: Gaming balance structure missing or invalid")
                    else:
                        self.log_test("Gaming Balance - Wallet Info", False, 
                                    f"Failed to get wallet info: {data}")
                else:
                    error_text = await response.text()
                    self.log_test("Gaming Balance - Wallet Info", False, 
                                f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Gaming Balance - Wallet Info", False, f"Error: {str(e)}")
        
        # Test transfer to gaming balance endpoint
        try:
            transfer_payload = {
                "wallet_address": self.user_wallet,
                "currency": "CRT",
                "amount": 100.0,
                "from_wallet": "deposit",
                "to_wallet": "gaming"
            }
            
            async with self.session.post(f"{self.base_url}/wallet/transfer-to-gaming", 
                                       json=transfer_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_test("Gaming Balance - Transfer Endpoint", True, 
                                    f"Transfer to gaming successful: {data}")
                    else:
                        self.log_test("Gaming Balance - Transfer Endpoint", False, 
                                    f"Transfer failed: {data}")
                elif response.status == 404:
                    self.log_test("Gaming Balance - Transfer Endpoint", False, 
                                "❌ CRITICAL: Transfer-to-gaming endpoint not found")
                elif response.status == 403:
                    self.log_test("Gaming Balance - Transfer Endpoint", False, 
                                "❌ CRITICAL: Authentication required for gaming transfers")
                else:
                    error_text = await response.text()
                    self.log_test("Gaming Balance - Transfer Endpoint", False, 
                                f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Gaming Balance - Transfer Endpoint", False, f"Error: {str(e)}")
        
        # Test alternative transfer methods
        try:
            # Test general wallet transfer
            transfer_payload = {
                "wallet_address": self.user_wallet,
                "currency": "CRT",
                "amount": 50.0,
                "wallet_type": "gaming"
            }
            
            async with self.session.post(f"{self.base_url}/wallet/transfer", 
                                       json=transfer_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Gaming Balance - General Transfer", True, 
                                f"General transfer working: {data}")
                elif response.status == 404:
                    self.log_test("Gaming Balance - General Transfer", False, 
                                "General transfer endpoint not found")
                else:
                    error_text = await response.text()
                    self.log_test("Gaming Balance - General Transfer", False, 
                                f"General transfer error: HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Gaming Balance - General Transfer", False, f"Error: {str(e)}")

    async def test_withdrawal_button_bug(self):
        """BUG 4: Test external wallet withdrawal functionality"""
        print("\n🔍 TESTING BUG 4: MISSING WITHDRAWAL BUTTON")
        
        # Test standard withdrawal endpoint
        try:
            withdraw_payload = {
                "wallet_address": self.user_wallet,
                "wallet_type": "deposit",
                "currency": "CRT",
                "amount": 10.0,
                "destination_address": "DFvHX8ZdqNqbCLJKnwe4h7qqj3hj4dw3pYvQRzweWnP7"  # External Solana address
            }
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=withdraw_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        blockchain_hash = data.get("blockchain_transaction_hash")
                        if blockchain_hash:
                            self.log_test("Withdrawal - Standard Endpoint", True, 
                                        f"External withdrawal working: {blockchain_hash}")
                        else:
                            self.log_test("Withdrawal - Standard Endpoint", False, 
                                        f"Withdrawal succeeded but no blockchain transaction: {data}")
                    else:
                        message = data.get("message", "")
                        if "insufficient" in message.lower():
                            self.log_test("Withdrawal - Standard Endpoint", True, 
                                        f"Withdrawal endpoint working (insufficient balance): {message}")
                        else:
                            self.log_test("Withdrawal - Standard Endpoint", False, 
                                        f"Withdrawal failed: {data}")
                elif response.status == 403:
                    self.log_test("Withdrawal - Standard Endpoint", False, 
                                "❌ CRITICAL: Authentication required for withdrawals")
                else:
                    error_text = await response.text()
                    self.log_test("Withdrawal - Standard Endpoint", False, 
                                f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Withdrawal - Standard Endpoint", False, f"Error: {str(e)}")
        
        # Test CoinPayments withdrawal endpoint
        try:
            coinpayments_payload = {
                "wallet_address": self.user_wallet,
                "currency": "DOGE",
                "amount": 100.0,
                "destination_address": "DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L"  # DOGE address
            }
            
            async with self.session.post(f"{self.base_url}/coinpayments/withdraw", 
                                       json=coinpayments_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_test("Withdrawal - CoinPayments", True, 
                                    f"CoinPayments withdrawal working: {data}")
                    else:
                        self.log_test("Withdrawal - CoinPayments", False, 
                                    f"CoinPayments withdrawal failed: {data}")
                elif response.status == 404:
                    self.log_test("Withdrawal - CoinPayments", False, 
                                "❌ CRITICAL: CoinPayments withdrawal endpoint not found")
                elif response.status == 403:
                    self.log_test("Withdrawal - CoinPayments", False, 
                                "❌ CRITICAL: Authentication required for CoinPayments withdrawals")
                else:
                    error_text = await response.text()
                    self.log_test("Withdrawal - CoinPayments", False, 
                                f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Withdrawal - CoinPayments", False, f"Error: {str(e)}")
        
        # Test savings vault withdrawal
        try:
            vault_payload = {
                "wallet_address": self.user_wallet,
                "currency": "CRT",
                "amount": 50.0,
                "destination_address": "DFvHX8ZdqNqbCLJKnwe4h7qqj3hj4dw3pYvQRzweWnP7"
            }
            
            async with self.session.post(f"{self.base_url}/savings/vault/withdraw", 
                                       json=vault_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.log_test("Withdrawal - Savings Vault", True, 
                                    f"Savings vault withdrawal working: {data}")
                    else:
                        self.log_test("Withdrawal - Savings Vault", False, 
                                    f"Savings vault withdrawal failed: {data}")
                elif response.status == 404:
                    self.log_test("Withdrawal - Savings Vault", False, 
                                "❌ CRITICAL: Savings vault withdrawal endpoint not found")
                else:
                    error_text = await response.text()
                    self.log_test("Withdrawal - Savings Vault", False, 
                                f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Withdrawal - Savings Vault", False, f"Error: {str(e)}")

    async def test_currency_conversion_bug(self):
        """BUG 5: Test DOGE to CRT and DOGE to TRX conversion functionality"""
        print("\n🔍 TESTING BUG 5: CURRENCY CONVERSION ISSUES")
        
        # Test DOGE to CRT conversion
        try:
            doge_to_crt_payload = {
                "wallet_address": self.user_wallet,
                "from_currency": "DOGE",
                "to_currency": "CRT",
                "amount": 100.0
            }
            
            async with self.session.post(f"{self.base_url}/wallet/convert", 
                                       json=doge_to_crt_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        converted_amount = data.get("converted_amount", 0)
                        rate = data.get("rate", 0)
                        self.log_test("Conversion - DOGE to CRT", True, 
                                    f"DOGE→CRT conversion working: rate={rate}, converted={converted_amount}")
                    else:
                        message = data.get("message", "")
                        if "insufficient" in message.lower():
                            self.log_test("Conversion - DOGE to CRT", True, 
                                        f"DOGE→CRT endpoint working (insufficient balance): {message}")
                        else:
                            self.log_test("Conversion - DOGE to CRT", False, 
                                        f"DOGE→CRT conversion failed: {data}")
                elif response.status == 403:
                    self.log_test("Conversion - DOGE to CRT", False, 
                                "❌ CRITICAL: Authentication required for conversions")
                else:
                    error_text = await response.text()
                    self.log_test("Conversion - DOGE to CRT", False, 
                                f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Conversion - DOGE to CRT", False, f"Error: {str(e)}")
        
        # Test DOGE to TRX conversion
        try:
            doge_to_trx_payload = {
                "wallet_address": self.user_wallet,
                "from_currency": "DOGE",
                "to_currency": "TRX",
                "amount": 100.0
            }
            
            async with self.session.post(f"{self.base_url}/wallet/convert", 
                                       json=doge_to_trx_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        converted_amount = data.get("converted_amount", 0)
                        rate = data.get("rate", 0)
                        self.log_test("Conversion - DOGE to TRX", True, 
                                    f"DOGE→TRX conversion working: rate={rate}, converted={converted_amount}")
                    else:
                        message = data.get("message", "")
                        if "insufficient" in message.lower():
                            self.log_test("Conversion - DOGE to TRX", True, 
                                        f"DOGE→TRX endpoint working (insufficient balance): {message}")
                        else:
                            self.log_test("Conversion - DOGE to TRX", False, 
                                        f"DOGE→TRX conversion failed: {data}")
                else:
                    error_text = await response.text()
                    self.log_test("Conversion - DOGE to TRX", False, 
                                f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Conversion - DOGE to TRX", False, f"Error: {str(e)}")
        
        # Test conversion rates endpoint
        try:
            async with self.session.get(f"{self.base_url}/conversion/rates") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        rates = data.get("rates", {})
                        doge_crt_rate = rates.get("DOGE_CRT", 0)
                        doge_trx_rate = rates.get("DOGE_TRX", 0)
                        
                        if doge_crt_rate > 0 and doge_trx_rate > 0:
                            self.log_test("Conversion - Rates Available", True, 
                                        f"Conversion rates available: DOGE→CRT={doge_crt_rate}, DOGE→TRX={doge_trx_rate}")
                        else:
                            self.log_test("Conversion - Rates Available", False, 
                                        f"❌ CRITICAL: Missing DOGE conversion rates: {rates}")
                    else:
                        self.log_test("Conversion - Rates Available", False, 
                                    f"Conversion rates endpoint failed: {data}")
                else:
                    error_text = await response.text()
                    self.log_test("Conversion - Rates Available", False, 
                                f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Conversion - Rates Available", False, f"Error: {str(e)}")

    async def run_all_tests(self):
        """Run all urgent bug investigation tests"""
        print("🚨 STARTING URGENT BUG INVESTIGATION")
        print(f"User: {self.username} ({self.user_wallet})")
        print("=" * 80)
        
        # Authenticate user first
        auth_success = await self.authenticate_user()
        if not auth_success:
            print("❌ CRITICAL: Cannot authenticate user - stopping investigation")
            return
        
        # Run all bug tests
        await self.test_autoplay_system_bug()
        await self.test_loss_tracker_bug()
        await self.test_gaming_balance_bug()
        await self.test_withdrawal_button_bug()
        await self.test_currency_conversion_bug()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate investigation summary"""
        print("\n" + "=" * 80)
        print("🚨 URGENT BUG INVESTIGATION SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed ({failed_tests} failed)")
        
        # Categorize results by bug
        bug_categories = {
            "BUG 1 - Autoplay System": [],
            "BUG 2 - Loss Tracker": [],
            "BUG 3 - Gaming Balance": [],
            "BUG 4 - Withdrawal Button": [],
            "BUG 5 - Currency Conversion": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if "Autoplay" in test_name or "BUG 1" in test_name:
                bug_categories["BUG 1 - Autoplay System"].append(result)
            elif "Loss Tracker" in test_name or "Savings" in test_name or "BUG 2" in test_name:
                bug_categories["BUG 2 - Loss Tracker"].append(result)
            elif "Gaming Balance" in test_name or "BUG 3" in test_name:
                bug_categories["BUG 3 - Gaming Balance"].append(result)
            elif "Withdrawal" in test_name or "BUG 4" in test_name:
                bug_categories["BUG 4 - Withdrawal Button"].append(result)
            elif "Conversion" in test_name or "BUG 5" in test_name:
                bug_categories["BUG 5 - Currency Conversion"].append(result)
        
        print("\n🔍 BUG-BY-BUG ANALYSIS:")
        for bug_name, results in bug_categories.items():
            if results:
                passed = sum(1 for r in results if r["success"])
                total = len(results)
                status = "✅ WORKING" if passed == total else "❌ BROKEN" if passed == 0 else "⚠️ PARTIAL"
                print(f"{status} {bug_name}: {passed}/{total} tests passed")
                
                # Show critical failures
                for result in results:
                    if not result["success"] and "CRITICAL" in result["details"]:
                        print(f"  🚨 {result['details']}")
        
        print("\n📋 RECOMMENDATIONS:")
        
        # Check for authentication issues
        auth_failures = [r for r in self.test_results if not r["success"] and "Authentication required" in r["details"]]
        if auth_failures:
            print("🔐 AUTHENTICATION: Multiple endpoints require authentication - implement proper JWT token handling")
        
        # Check for missing endpoints
        missing_endpoints = [r for r in self.test_results if not r["success"] and "not found" in r["details"]]
        if missing_endpoints:
            print("🔗 MISSING ENDPOINTS: Several critical endpoints are missing - implement missing functionality")
        
        # Check for critical system failures
        critical_failures = [r for r in self.test_results if not r["success"] and "CRITICAL" in r["details"]]
        if critical_failures:
            print(f"🚨 CRITICAL ISSUES: {len(critical_failures)} critical system failures detected - immediate attention required")
        
        print("\n" + "=" * 80)

async def main():
    """Main function to run urgent bug investigation"""
    async with UrgentBugTester(BACKEND_URL) as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())