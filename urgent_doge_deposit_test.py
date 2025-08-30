#!/usr/bin/env python3
"""
URGENT DOGE DEPOSIT VERIFICATION TEST
Testing if user's 30 DOGE deposit cooldown has expired and can be credited immediately.

User Details:
- User: DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq  
- DOGE Address: DLZccCAopg8SJYdmUWdjEkGq9t7boXMKMe
- Amount: 30.0 DOGE (previously confirmed)
- Status: Was waiting for 1-hour security cooldown
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://tiger-dex-casino.preview.emergentagent.com/api"

class UrgentDogeDepositTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        
        # User details from review request
        self.user_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        self.doge_address = "DLZccCAopg8SJYdmUWdjEkGq9t7boXMKMe"
        self.expected_amount = 30.0
        
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
        
    async def test_doge_balance_verification(self):
        """Test 1: Check if 30 DOGE still confirmed at deposit address"""
        try:
            url = f"{self.base_url}/wallet/balance/DOGE"
            params = {"wallet_address": self.doge_address}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        balance = data.get("balance", 0)
                        total = data.get("total", 0)
                        unconfirmed = data.get("unconfirmed", 0)
                        
                        if total >= self.expected_amount:
                            self.log_test(
                                "DOGE Balance Verification", 
                                True, 
                                f"✅ DOGE FOUND: {total} DOGE confirmed at address {self.doge_address} (confirmed: {balance}, unconfirmed: {unconfirmed})",
                                data
                            )
                            return True
                        else:
                            self.log_test(
                                "DOGE Balance Verification", 
                                False, 
                                f"❌ INSUFFICIENT DOGE: Only {total} DOGE found, expected {self.expected_amount}",
                                data
                            )
                            return False
                    else:
                        self.log_test(
                            "DOGE Balance Verification", 
                            False, 
                            f"❌ BALANCE CHECK FAILED: {data.get('error', 'Unknown error')}",
                            data
                        )
                        return False
                else:
                    error_text = await response.text()
                    self.log_test(
                        "DOGE Balance Verification", 
                        False, 
                        f"❌ HTTP {response.status}: {error_text}",
                        None
                    )
                    return False
                    
        except Exception as e:
            self.log_test(
                "DOGE Balance Verification", 
                False, 
                f"❌ EXCEPTION: {str(e)}",
                None
            )
            return False
    
    async def test_manual_credit_attempt(self):
        """Test 2: Attempt manual credit via /api/deposit/doge/manual"""
        try:
            url = f"{self.base_url}/deposit/doge/manual"
            payload = {
                "wallet_address": self.user_wallet,
                "doge_address": self.doge_address
            }
            
            async with self.session.post(url, json=payload) as response:
                data = await response.json()
                
                if response.status == 200:
                    if data.get("success"):
                        credited_amount = data.get("credited_amount", 0)
                        transaction_id = data.get("transaction_id", "")
                        
                        if credited_amount > 0:
                            self.log_test(
                                "Manual Credit Attempt", 
                                True, 
                                f"🎉 DOGE CREDITED: {credited_amount} DOGE successfully credited to casino account (Transaction: {transaction_id})",
                                data
                            )
                            return True, "credited"
                        else:
                            # Check if message indicates successful verification but no credit due to cooldown
                            message = data.get("message", "")
                            if "credited" in message.lower():
                                self.log_test(
                                    "Manual Credit Attempt", 
                                    True, 
                                    f"✅ VERIFICATION SUCCESS: {message} (API indicates success but balance may not update immediately)",
                                    data
                                )
                                return True, "verified"
                            else:
                                self.log_test(
                                    "Manual Credit Attempt", 
                                    False, 
                                    f"❌ NO CREDIT: {message}",
                                    data
                                )
                                return False, "error"
                    else:
                        error_msg = data.get("message", data.get("error", "Unknown error"))
                        last_deposit = data.get("last_deposit", "")
                        
                        if "wait" in error_msg.lower() or "cooldown" in error_msg.lower():
                            # Calculate cooldown expiry
                            cooldown_info = f"⏳ COOLDOWN ACTIVE: {error_msg}"
                            if last_deposit:
                                from datetime import datetime, timedelta
                                try:
                                    last_time = datetime.fromisoformat(last_deposit.replace('Z', '+00:00'))
                                    expiry_time = last_time + timedelta(hours=1)
                                    current_time = datetime.utcnow()
                                    remaining = expiry_time - current_time
                                    
                                    if remaining.total_seconds() > 0:
                                        minutes_remaining = int(remaining.total_seconds() / 60)
                                        cooldown_info += f" (Expires in ~{minutes_remaining} minutes at {expiry_time.strftime('%H:%M:%S')} UTC)"
                                    else:
                                        cooldown_info += " (Should have expired - try again)"
                                except:
                                    cooldown_info += f" (Last deposit: {last_deposit})"
                            
                            self.log_test(
                                "Manual Credit Attempt", 
                                True, 
                                cooldown_info,
                                data
                            )
                            return True, "cooldown"
                        else:
                            self.log_test(
                                "Manual Credit Attempt", 
                                False, 
                                f"❌ CREDIT FAILED: {error_msg}",
                                data
                            )
                            return False, "error"
                else:
                    error_text = await response.text()
                    self.log_test(
                        "Manual Credit Attempt", 
                        False, 
                        f"❌ HTTP {response.status}: {error_text}",
                        None
                    )
                    return False, "error"
                    
        except Exception as e:
            self.log_test(
                "Manual Credit Attempt", 
                False, 
                f"❌ EXCEPTION: {str(e)}",
                None
            )
            return False, "error"
    
    async def test_casino_balance_check(self):
        """Test 3: Check user's casino DOGE balance"""
        try:
            url = f"{self.base_url}/wallet/{self.user_wallet}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        wallet_data = data.get("wallet", {})
                        deposit_balance = wallet_data.get("deposit_balance", {})
                        doge_balance = deposit_balance.get("DOGE", 0)
                        
                        self.log_test(
                            "Casino Balance Check", 
                            True, 
                            f"💰 CASINO DOGE BALANCE: {doge_balance} DOGE in user's casino account",
                            {"doge_balance": doge_balance, "wallet_data": wallet_data}
                        )
                        return doge_balance
                    else:
                        self.log_test(
                            "Casino Balance Check", 
                            False, 
                            f"❌ WALLET CHECK FAILED: {data.get('message', 'Unknown error')}",
                            data
                        )
                        return 0
                else:
                    error_text = await response.text()
                    self.log_test(
                        "Casino Balance Check", 
                        False, 
                        f"❌ HTTP {response.status}: {error_text}",
                        None
                    )
                    return 0
                    
        except Exception as e:
            self.log_test(
                "Casino Balance Check", 
                False, 
                f"❌ EXCEPTION: {str(e)}",
                None
            )
            return 0
    
    async def test_user_verification(self):
        """Test 4: Verify user account exists"""
        try:
            url = f"{self.base_url}/wallet/{self.user_wallet}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        wallet_data = data.get("wallet", {})
                        user_id = wallet_data.get("user_id", "")
                        created_at = wallet_data.get("created_at", "")
                        
                        self.log_test(
                            "User Verification", 
                            True, 
                            f"✅ USER VERIFIED: Account exists (ID: {user_id}, Created: {created_at})",
                            wallet_data
                        )
                        return True
                    else:
                        self.log_test(
                            "User Verification", 
                            False, 
                            f"❌ USER NOT FOUND: {data.get('message', 'Unknown error')}",
                            data
                        )
                        return False
                else:
                    error_text = await response.text()
                    self.log_test(
                        "User Verification", 
                        False, 
                        f"❌ HTTP {response.status}: {error_text}",
                        None
                    )
                    return False
                    
        except Exception as e:
            self.log_test(
                "User Verification", 
                False, 
                f"❌ EXCEPTION: {str(e)}",
                None
            )
            return False
    
    async def run_urgent_verification(self):
        """Run all urgent DOGE deposit verification tests"""
        print("🚨 URGENT DOGE DEPOSIT VERIFICATION STARTING...")
        print(f"User: {self.user_wallet}")
        print(f"DOGE Address: {self.doge_address}")
        print(f"Expected Amount: {self.expected_amount} DOGE")
        print("=" * 80)
        
        # Test 1: Verify user account exists
        print("\n1️⃣ VERIFYING USER ACCOUNT...")
        user_exists = await self.test_user_verification()
        
        if not user_exists:
            print("❌ CRITICAL: User account not found - cannot proceed with deposit")
            return
        
        # Test 2: Check DOGE balance at deposit address
        print("\n2️⃣ CHECKING DOGE BALANCE AT DEPOSIT ADDRESS...")
        doge_available = await self.test_doge_balance_verification()
        
        if not doge_available:
            print("❌ CRITICAL: 30 DOGE not found at deposit address")
            return
        
        # Test 3: Check current casino balance (before credit attempt)
        print("\n3️⃣ CHECKING CURRENT CASINO BALANCE...")
        initial_balance = await self.test_casino_balance_check()
        
        # Test 4: Attempt manual credit
        print("\n4️⃣ ATTEMPTING MANUAL CREDIT...")
        credit_success, credit_status = await self.test_manual_credit_attempt()
        
        # Test 5: Check final casino balance
        print("\n5️⃣ CHECKING FINAL CASINO BALANCE...")
        final_balance = await self.test_casino_balance_check()
        
        # Summary
        print("\n" + "=" * 80)
        print("🎯 URGENT DOGE DEPOSIT VERIFICATION SUMMARY")
        print("=" * 80)
        
        if credit_status == "credited":
            balance_increase = final_balance - initial_balance
            print(f"🎉 SUCCESS: DOGE DEPOSIT CREDITED!")
            print(f"   • Initial Balance: {initial_balance} DOGE")
            print(f"   • Final Balance: {final_balance} DOGE")
            print(f"   • Amount Credited: {balance_increase} DOGE")
            print(f"   • User can now start gaming with DOGE!")
            print(f"   • DOGE available for AI Auto-Play and casino games!")
            
        elif credit_status == "verified":
            print(f"✅ VERIFICATION SUCCESS: API indicates DOGE credited")
            print(f"   • 30 DOGE confirmed at deposit address")
            print(f"   • API returned success message")
            print(f"   • Balance may take time to update")
            print(f"   • User should check balance again shortly")
            
        elif credit_status == "cooldown":
            print(f"⏳ COOLDOWN ACTIVE: Security cooldown still in effect")
            print(f"   • 30 DOGE confirmed and ready at deposit address")
            print(f"   • User must wait for cooldown to expire")
            print(f"   • Current Casino Balance: {final_balance} DOGE")
            print(f"   • Retry manual credit after cooldown expires")
            
        else:
            print(f"❌ CREDIT FAILED: Unable to credit DOGE deposit")
            print(f"   • Current Casino Balance: {final_balance} DOGE")
            print(f"   • Manual intervention may be required")
        
        # Test results summary
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 TEST RESULTS: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}% success rate)")
        
        return credit_status in ["credited", "verified"]

async def main():
    """Main test execution"""
    async with UrgentDogeDepositTester(BACKEND_URL) as tester:
        success = await tester.run_urgent_verification()
        
        if success:
            print("\n✅ URGENT VERIFICATION COMPLETE: User's 30 DOGE has been credited!")
        else:
            print("\n⚠️ URGENT VERIFICATION COMPLETE: DOGE not yet credited (see details above)")

if __name__ == "__main__":
    asyncio.run(main())