#!/usr/bin/env python3
"""
🚨 URGENT FIX VERIFICATION: Gaming Balance Transfer Code 405 Bug Fix
Test the newly added `/api/wallet/transfer-to-gaming` endpoint that was causing 
"Gaming balance failed transfer code 405" error for user DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq.
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

class GamingBalanceTransferTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"  # Real user wallet
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
        
    async def test_method_405_fix_verification(self):
        """🚨 CRITICAL TEST 1: Method 405 Fix Verification - POST request should work"""
        try:
            # Test POST request to the endpoint
            test_data = {
                "wallet_address": self.test_wallet,
                "currency": "CRT",
                "amount": 100000
            }
            
            async with self.session.post(
                f"{self.base_url}/wallet/transfer-to-gaming",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_text = await response.text()
                
                if response.status == 405:
                    self.log_test(
                        "Method 405 Fix Verification", 
                        False, 
                        f"❌ CRITICAL: Still getting 405 Method Not Allowed! Response: {response_text}",
                        {"status": response.status, "response": response_text}
                    )
                    return False
                elif response.status == 200:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    self.log_test(
                        "Method 405 Fix Verification", 
                        True, 
                        f"✅ SUCCESS: POST method now works! Status: {response.status}",
                        {"status": response.status, "response": response_data}
                    )
                    return True
                else:
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    self.log_test(
                        "Method 405 Fix Verification", 
                        True, 
                        f"✅ Method works (not 405): Status {response.status}",
                        {"status": response.status, "response": response_data}
                    )
                    return True
                    
        except Exception as e:
            self.log_test(
                "Method 405 Fix Verification", 
                False, 
                f"❌ Exception occurred: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    async def test_gaming_balance_transfer_functionality(self):
        """🚨 CRITICAL TEST 2: Gaming Balance Transfer Functionality"""
        try:
            # Test transferring 100,000 CRT from deposit to gaming balance
            test_data = {
                "wallet_address": self.test_wallet,
                "currency": "CRT", 
                "amount": 100000
            }
            
            async with self.session.post(
                f"{self.base_url}/wallet/transfer-to-gaming",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response.status == 200 and response_data.get("success"):
                    self.log_test(
                        "Gaming Balance Transfer Functionality", 
                        True, 
                        f"✅ Transfer successful: {response_data.get('message', 'No message')}",
                        response_data
                    )
                    return True
                else:
                    self.log_test(
                        "Gaming Balance Transfer Functionality", 
                        False, 
                        f"❌ Transfer failed: {response_data.get('message', 'Unknown error')}",
                        response_data
                    )
                    return False
                    
        except Exception as e:
            self.log_test(
                "Gaming Balance Transfer Functionality", 
                False, 
                f"❌ Exception: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    async def test_input_validation(self):
        """🚨 CRITICAL TEST 3: Input Validation Testing"""
        validation_tests = [
            {
                "name": "Missing wallet_address",
                "data": {"currency": "CRT", "amount": 1000},
                "expected_error": "wallet_address required"
            },
            {
                "name": "Invalid amount (0)",
                "data": {"wallet_address": self.test_wallet, "currency": "CRT", "amount": 0},
                "expected_error": "Invalid amount"
            },
            {
                "name": "Invalid amount (negative)",
                "data": {"wallet_address": self.test_wallet, "currency": "CRT", "amount": -1000},
                "expected_error": "Invalid amount"
            },
            {
                "name": "Insufficient balance",
                "data": {"wallet_address": self.test_wallet, "currency": "CRT", "amount": 999999999999},
                "expected_error": "Insufficient"
            }
        ]
        
        all_passed = True
        
        for test in validation_tests:
            try:
                async with self.session.post(
                    f"{self.base_url}/wallet/transfer-to-gaming",
                    json=test["data"],
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_data = await response.json()
                    
                    if not response_data.get("success") and test["expected_error"].lower() in response_data.get("message", "").lower():
                        self.log_test(
                            f"Input Validation - {test['name']}", 
                            True, 
                            f"✅ Proper validation: {response_data.get('message')}",
                            response_data
                        )
                    else:
                        self.log_test(
                            f"Input Validation - {test['name']}", 
                            False, 
                            f"❌ Validation failed: Expected '{test['expected_error']}', got '{response_data.get('message')}'",
                            response_data
                        )
                        all_passed = False
                        
            except Exception as e:
                self.log_test(
                    f"Input Validation - {test['name']}", 
                    False, 
                    f"❌ Exception: {str(e)}",
                    {"error": str(e)}
                )
                all_passed = False
        
        return all_passed
    
    async def test_transaction_recording(self):
        """🚨 CRITICAL TEST 4: Transaction Recording and Gaming Balance Update"""
        try:
            # First, get current gaming balance
            async with self.session.get(f"{self.base_url}/wallet/{self.test_wallet}") as response:
                if response.status != 200:
                    self.log_test(
                        "Transaction Recording - Get Initial Balance", 
                        False, 
                        f"❌ Could not get wallet info: {response.status}",
                        {"status": response.status}
                    )
                    return False
                
                wallet_data = await response.json()
                if not wallet_data.get("success"):
                    self.log_test(
                        "Transaction Recording - Get Initial Balance", 
                        False, 
                        f"❌ Wallet not found: {wallet_data.get('message')}",
                        wallet_data
                    )
                    return False
                
                initial_gaming_balance = wallet_data.get("wallet", {}).get("gaming_balance", {}).get("CRT", 0)
                
            # Perform transfer
            transfer_amount = 50000
            test_data = {
                "wallet_address": self.test_wallet,
                "currency": "CRT",
                "amount": transfer_amount
            }
            
            async with self.session.post(
                f"{self.base_url}/wallet/transfer-to-gaming",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if not response_data.get("success"):
                    self.log_test(
                        "Transaction Recording - Transfer", 
                        False, 
                        f"❌ Transfer failed: {response_data.get('message')}",
                        response_data
                    )
                    return False
                
                # Verify transaction_id is returned
                transaction_id = response_data.get("transaction_id")
                if not transaction_id:
                    self.log_test(
                        "Transaction Recording - Transaction ID", 
                        False, 
                        "❌ No transaction_id returned",
                        response_data
                    )
                    return False
                
                # Verify gaming balance is updated
                new_gaming_balance = response_data.get("new_gaming_balance")
                expected_balance = initial_gaming_balance + transfer_amount
                
                if new_gaming_balance == expected_balance:
                    self.log_test(
                        "Transaction Recording", 
                        True, 
                        f"✅ Gaming balance updated correctly: {initial_gaming_balance} + {transfer_amount} = {new_gaming_balance}",
                        response_data
                    )
                    return True
                else:
                    self.log_test(
                        "Transaction Recording", 
                        False, 
                        f"❌ Gaming balance incorrect: Expected {expected_balance}, got {new_gaming_balance}",
                        response_data
                    )
                    return False
                    
        except Exception as e:
            self.log_test(
                "Transaction Recording", 
                False, 
                f"❌ Exception: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    async def test_response_format(self):
        """🚨 CRITICAL TEST 5: Response Format Verification"""
        try:
            test_data = {
                "wallet_address": self.test_wallet,
                "currency": "CRT",
                "amount": 25000
            }
            
            async with self.session.post(
                f"{self.base_url}/wallet/transfer-to-gaming",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                # Required fields for successful response
                required_fields = [
                    "success",
                    "message", 
                    "amount_transferred",
                    "currency",
                    "new_gaming_balance",
                    "available_deposit_balance",
                    "transaction_id"
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in response_data:
                        missing_fields.append(field)
                
                if missing_fields:
                    self.log_test(
                        "Response Format", 
                        False, 
                        f"❌ Missing required fields: {missing_fields}",
                        response_data
                    )
                    return False
                else:
                    self.log_test(
                        "Response Format", 
                        True, 
                        f"✅ All required fields present: {required_fields}",
                        response_data
                    )
                    return True
                    
        except Exception as e:
            self.log_test(
                "Response Format", 
                False, 
                f"❌ Exception: {str(e)}",
                {"error": str(e)}
            )
            return False
    
    async def run_all_tests(self):
        """Run all gaming balance transfer tests"""
        print("🚨 URGENT FIX VERIFICATION: Gaming Balance Transfer Code 405 Bug Fix")
        print("=" * 80)
        print(f"Testing endpoint: {self.base_url}/wallet/transfer-to-gaming")
        print(f"Test wallet: {self.test_wallet}")
        print("=" * 80)
        
        # Run all critical tests
        test_results = []
        
        print("\n🔍 CRITICAL TEST 1: Method 405 Fix Verification")
        test_results.append(await self.test_method_405_fix_verification())
        
        print("\n🔍 CRITICAL TEST 2: Gaming Balance Transfer Functionality")  
        test_results.append(await self.test_gaming_balance_transfer_functionality())
        
        print("\n🔍 CRITICAL TEST 3: Input Validation Testing")
        test_results.append(await self.test_input_validation())
        
        print("\n🔍 CRITICAL TEST 4: Transaction Recording")
        test_results.append(await self.test_transaction_recording())
        
        print("\n🔍 CRITICAL TEST 5: Response Format")
        test_results.append(await self.test_response_format())
        
        # Summary
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 80)
        print("🎯 GAMING BALANCE TRANSFER TEST RESULTS")
        print("=" * 80)
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 ALL TESTS PASSED - Gaming balance transfer fix is working!")
            print("✅ POST /api/wallet/transfer-to-gaming returns 200 (not 405)")
            print("✅ Successful fund transfer from deposit to gaming balance")
            print("✅ Proper gaming_balance tracking separate from deposit_balance")
            print("✅ Complete transaction logging")
            print("✅ User-friendly success/error messages")
        else:
            print("❌ SOME TESTS FAILED - Gaming balance transfer needs attention")
            
        print("\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        return success_rate == 100

async def main():
    """Main test execution"""
    async with GamingBalanceTransferTester(BACKEND_URL) as tester:
        success = await tester.run_all_tests()
        return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)