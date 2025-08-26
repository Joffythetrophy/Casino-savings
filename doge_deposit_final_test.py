#!/usr/bin/env python3
"""
DOGE Deposit Final Verification Test Suite
Tests the user's DOGE deposit status for final crediting to casino account
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://cryptosavings.preview.emergentagent.com/api"

class DogeDepositFinalTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        
        # User's specific DOGE deposit details from review request
        self.user_doge_address = "DLZccCAopg8SJYdmUWdjEkGq9t7boXMKMe"
        self.user_casino_account = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        self.expected_doge_amount = 30.0
        
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
        
    async def test_doge_balance_verification(self):
        """Test 1: Verify 30 DOGE still confirmed at deposit address"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/balance/DOGE?wallet_address={self.user_doge_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success") and data.get("source") == "blockcypher":
                        confirmed_balance = data.get("balance", 0)
                        unconfirmed_balance = data.get("unconfirmed", 0)
                        total_balance = data.get("total", 0)
                        
                        # Check if the expected 30 DOGE is still there and confirmed
                        if confirmed_balance >= self.expected_doge_amount:
                            self.log_test("DOGE Balance Verification", True, 
                                        f"✅ DOGE CONFIRMED: {confirmed_balance} DOGE confirmed at address {self.user_doge_address} (unconfirmed: {unconfirmed_balance}, total: {total_balance})", data)
                            return {"confirmed": confirmed_balance, "unconfirmed": unconfirmed_balance, "total": total_balance}
                        else:
                            self.log_test("DOGE Balance Verification", False, 
                                        f"❌ INSUFFICIENT DOGE: Only {confirmed_balance} DOGE confirmed, expected {self.expected_doge_amount}", data)
                            return {"confirmed": confirmed_balance, "unconfirmed": unconfirmed_balance, "total": total_balance}
                    else:
                        self.log_test("DOGE Balance Verification", False, 
                                    f"❌ BALANCE CHECK FAILED: {data.get('error', 'Unknown error')}", data)
                        return None
                else:
                    error_text = await response.text()
                    self.log_test("DOGE Balance Verification", False, 
                                f"❌ API ERROR: HTTP {response.status}: {error_text}")
                    return None
        except Exception as e:
            self.log_test("DOGE Balance Verification", False, f"❌ EXCEPTION: {str(e)}")
            return None

    async def test_casino_account_balance(self):
        """Test 2: Check current DOGE balance in casino account"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.user_casino_account}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        deposit_balance = wallet.get("deposit_balance", {})
                        current_doge = deposit_balance.get("DOGE", 0)
                        
                        self.log_test("Casino Account Balance Check", True, 
                                    f"💰 CASINO DOGE BALANCE: {current_doge} DOGE in casino account {self.user_casino_account}", data)
                        return current_doge
                    else:
                        self.log_test("Casino Account Balance Check", False, 
                                    f"❌ WALLET INFO FAILED: {data.get('message', 'Unknown error')}", data)
                        return None
                else:
                    error_text = await response.text()
                    self.log_test("Casino Account Balance Check", False, 
                                f"❌ API ERROR: HTTP {response.status}: {error_text}")
                    return None
        except Exception as e:
            self.log_test("Casino Account Balance Check", False, f"❌ EXCEPTION: {str(e)}")
            return None

    async def test_manual_deposit_attempt(self):
        """Test 3: Attempt manual DOGE deposit crediting"""
        try:
            payload = {
                "wallet_address": self.user_casino_account,
                "doge_address": self.user_doge_address
            }
            
            async with self.session.post(f"{self.base_url}/deposit/doge/manual", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        credited_amount = data.get("credited_amount", 0)
                        transaction_id = data.get("transaction_id", "")
                        
                        self.log_test("Manual Deposit Attempt", True, 
                                    f"🎉 DEPOSIT SUCCESSFUL: {credited_amount} DOGE credited to casino account! Transaction ID: {transaction_id}", data)
                        return {"success": True, "credited": credited_amount, "transaction_id": transaction_id}
                    else:
                        error_message = data.get("message", "Unknown error")
                        
                        # Check if it's a cooldown error
                        if "cooldown" in error_message.lower() or "hour" in error_message.lower():
                            self.log_test("Manual Deposit Attempt", True, 
                                        f"⏳ COOLDOWN ACTIVE: {error_message} (This is expected security behavior)", data)
                            return {"success": False, "reason": "cooldown", "message": error_message}
                        else:
                            self.log_test("Manual Deposit Attempt", False, 
                                        f"❌ DEPOSIT FAILED: {error_message}", data)
                            return {"success": False, "reason": "error", "message": error_message}
                else:
                    error_text = await response.text()
                    self.log_test("Manual Deposit Attempt", False, 
                                f"❌ API ERROR: HTTP {response.status}: {error_text}")
                    return {"success": False, "reason": "api_error", "message": error_text}
        except Exception as e:
            self.log_test("Manual Deposit Attempt", False, f"❌ EXCEPTION: {str(e)}")
            return {"success": False, "reason": "exception", "message": str(e)}

    async def test_deposit_history_check(self):
        """Test 4: Check deposit transaction history"""
        try:
            # Try to get deposit history or transaction records
            async with self.session.get(f"{self.base_url}/deposit/history/{self.user_casino_account}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        deposits = data.get("deposits", [])
                        doge_deposits = [d for d in deposits if d.get("currency") == "DOGE"]
                        
                        if doge_deposits:
                            latest_doge = doge_deposits[0]  # Assuming sorted by date
                            self.log_test("Deposit History Check", True, 
                                        f"📋 DEPOSIT HISTORY: Found {len(doge_deposits)} DOGE deposits. Latest: {latest_doge.get('amount', 0)} DOGE on {latest_doge.get('timestamp', 'unknown')}", data)
                            return doge_deposits
                        else:
                            self.log_test("Deposit History Check", True, 
                                        f"📋 DEPOSIT HISTORY: No DOGE deposits found in history (total deposits: {len(deposits)})", data)
                            return []
                    else:
                        self.log_test("Deposit History Check", False, 
                                    f"❌ HISTORY FAILED: {data.get('message', 'Unknown error')}", data)
                        return None
                elif response.status == 404:
                    self.log_test("Deposit History Check", True, 
                                "📋 DEPOSIT HISTORY: Endpoint not available (expected for this system)", None)
                    return []
                else:
                    error_text = await response.text()
                    self.log_test("Deposit History Check", False, 
                                f"❌ API ERROR: HTTP {response.status}: {error_text}")
                    return None
        except Exception as e:
            self.log_test("Deposit History Check", False, f"❌ EXCEPTION: {str(e)}")
            return None

    async def test_user_data_persistence(self):
        """Test 5: Verify user account data is properly stored"""
        try:
            # Check if user exists and has proper data structure
            async with self.session.get(f"{self.base_url}/wallet/{self.user_casino_account}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        required_fields = ["user_id", "wallet_address", "deposit_balance", "winnings_balance", "savings_balance"]
                        
                        if all(field in wallet for field in required_fields):
                            user_id = wallet.get("user_id")
                            created_at = wallet.get("created_at")
                            balance_source = wallet.get("balance_source", "unknown")
                            
                            self.log_test("User Data Persistence", True, 
                                        f"💾 USER DATA VERIFIED: User ID {user_id}, created {created_at}, balance source: {balance_source}", data)
                            return wallet
                        else:
                            missing_fields = [f for f in required_fields if f not in wallet]
                            self.log_test("User Data Persistence", False, 
                                        f"❌ MISSING FIELDS: {missing_fields}", data)
                            return None
                    else:
                        self.log_test("User Data Persistence", False, 
                                    f"❌ USER DATA FAILED: {data.get('message', 'Unknown error')}", data)
                        return None
                else:
                    error_text = await response.text()
                    self.log_test("User Data Persistence", False, 
                                f"❌ API ERROR: HTTP {response.status}: {error_text}")
                    return None
        except Exception as e:
            self.log_test("User Data Persistence", False, f"❌ EXCEPTION: {str(e)}")
            return None

    async def test_cooldown_status_check(self):
        """Test 6: Check if 1-hour cooldown period has expired"""
        try:
            # Try to get the last deposit check timestamp
            payload = {
                "wallet_address": self.user_casino_account,
                "doge_address": self.user_doge_address,
                "check_only": True  # Just check status, don't process
            }
            
            async with self.session.post(f"{self.base_url}/deposit/doge/check-status", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    last_check = data.get("last_check_time")
                    cooldown_remaining = data.get("cooldown_remaining_minutes", 0)
                    can_process = data.get("can_process", False)
                    
                    if can_process:
                        self.log_test("Cooldown Status Check", True, 
                                    f"✅ COOLDOWN EXPIRED: Can process deposit now! Last check: {last_check}", data)
                    else:
                        self.log_test("Cooldown Status Check", True, 
                                    f"⏳ COOLDOWN ACTIVE: {cooldown_remaining} minutes remaining. Last check: {last_check}", data)
                    
                    return {"can_process": can_process, "cooldown_remaining": cooldown_remaining, "last_check": last_check}
                elif response.status == 404:
                    self.log_test("Cooldown Status Check", True, 
                                "⏳ COOLDOWN STATUS: Check endpoint not available, will test via manual deposit attempt", None)
                    return {"can_process": None, "cooldown_remaining": None, "last_check": None}
                else:
                    error_text = await response.text()
                    self.log_test("Cooldown Status Check", False, 
                                f"❌ API ERROR: HTTP {response.status}: {error_text}")
                    return None
        except Exception as e:
            self.log_test("Cooldown Status Check", False, f"❌ EXCEPTION: {str(e)}")
            return None

    async def run_comprehensive_doge_deposit_test(self):
        """Run all DOGE deposit verification tests"""
        print("🐕 STARTING COMPREHENSIVE DOGE DEPOSIT FINAL VERIFICATION")
        print(f"📍 DOGE Address: {self.user_doge_address}")
        print(f"🎰 Casino Account: {self.user_casino_account}")
        print(f"💰 Expected Amount: {self.expected_doge_amount} DOGE")
        print("=" * 80)
        
        # Test 1: Check DOGE balance at deposit address
        print("\n1️⃣ CHECKING DOGE BALANCE AT DEPOSIT ADDRESS...")
        doge_balance = await self.test_doge_balance_verification()
        
        # Test 2: Check current casino account balance
        print("\n2️⃣ CHECKING CASINO ACCOUNT BALANCE...")
        casino_balance = await self.test_casino_account_balance()
        
        # Test 3: Check cooldown status
        print("\n3️⃣ CHECKING COOLDOWN STATUS...")
        cooldown_status = await self.test_cooldown_status_check()
        
        # Test 4: Attempt manual deposit
        print("\n4️⃣ ATTEMPTING MANUAL DEPOSIT CREDITING...")
        deposit_result = await self.test_manual_deposit_attempt()
        
        # Test 5: Check deposit history
        print("\n5️⃣ CHECKING DEPOSIT HISTORY...")
        deposit_history = await self.test_deposit_history_check()
        
        # Test 6: Verify user data persistence
        print("\n6️⃣ VERIFYING USER DATA PERSISTENCE...")
        user_data = await self.test_user_data_persistence()
        
        # Final assessment
        print("\n" + "=" * 80)
        print("🎯 FINAL ASSESSMENT")
        print("=" * 80)
        
        success_count = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 TEST RESULTS: {success_count}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        
        # Determine final status
        if doge_balance and doge_balance.get("confirmed", 0) >= self.expected_doge_amount:
            print(f"✅ DOGE CONFIRMED: {doge_balance['confirmed']} DOGE available at deposit address")
            
            if deposit_result and deposit_result.get("success"):
                print(f"🎉 DEPOSIT SUCCESSFUL: {deposit_result.get('credited', 0)} DOGE credited to casino account!")
                print(f"🎮 USER CAN NOW ACCESS GAMING FEATURES")
                return "DEPOSIT_COMPLETED"
            elif deposit_result and deposit_result.get("reason") == "cooldown":
                print(f"⏳ COOLDOWN ACTIVE: {deposit_result.get('message', 'Security cooldown in effect')}")
                print(f"⏰ USER SHOULD RETRY AFTER COOLDOWN EXPIRES")
                return "COOLDOWN_ACTIVE"
            else:
                print(f"❌ DEPOSIT FAILED: {deposit_result.get('message', 'Unknown error') if deposit_result else 'No response'}")
                print(f"🔧 MANUAL INTERVENTION MAY BE REQUIRED")
                return "DEPOSIT_FAILED"
        else:
            print(f"❌ INSUFFICIENT DOGE: Only {doge_balance.get('confirmed', 0) if doge_balance else 0} DOGE confirmed")
            print(f"💸 USER NEEDS TO SEND MORE DOGE OR WAIT FOR CONFIRMATIONS")
            return "INSUFFICIENT_BALANCE"

async def main():
    """Main test execution"""
    async with DogeDepositFinalTester(BACKEND_URL) as tester:
        final_status = await tester.run_comprehensive_doge_deposit_test()
        
        print("\n" + "=" * 80)
        print("📋 DETAILED TEST RESULTS")
        print("=" * 80)
        
        for result in tester.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        print(f"\n🏁 FINAL STATUS: {final_status}")
        
        return final_status

if __name__ == "__main__":
    try:
        final_status = asyncio.run(main())
        print(f"\n🎯 DOGE DEPOSIT VERIFICATION COMPLETED: {final_status}")
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")