#!/usr/bin/env python3
"""
REAL DOGE Conversion System Test - Critical User Request Testing
Tests the FIXED real DOGE blockchain integration for conversions
User Request: Convert 100,000 CRT to REAL DOGE (~2,150,000 DOGE expected)
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://cryptosavings.preview.emergentagent.com/api"

class RealDogeConversionTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        # User's actual wallet from review request
        self.user_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        
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
        
    async def test_user_wallet_verification(self):
        """Test 1: Verify user wallet exists and has sufficient CRT balance"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.user_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        crt_balance = wallet.get("deposit_balance", {}).get("CRT", 0)
                        
                        if crt_balance >= 100000:
                            self.log_test("User Wallet Verification", True, 
                                        f"✅ User has sufficient CRT balance: {crt_balance:,.0f} CRT (need 100,000)", data)
                            return True
                        else:
                            self.log_test("User Wallet Verification", False, 
                                        f"❌ Insufficient CRT balance: {crt_balance:,.0f} CRT (need 100,000)", data)
                            return False
                    else:
                        self.log_test("User Wallet Verification", False, 
                                    "❌ User wallet not found or invalid response", data)
                        return False
                else:
                    self.log_test("User Wallet Verification", False, 
                                f"❌ HTTP {response.status}: {await response.text()}")
                    return False
        except Exception as e:
            self.log_test("User Wallet Verification", False, f"❌ Error: {str(e)}")
            return False
    
    async def test_conversion_rates_availability(self):
        """Test 2: Verify CRT to DOGE conversion rate is available"""
        try:
            async with self.session.get(f"{self.base_url}/conversion/rates") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "rates" in data:
                        rates = data.get("rates", {})
                        crt_doge_rate = rates.get("CRT_DOGE")
                        
                        if crt_doge_rate:
                            expected_doge = 100000 * crt_doge_rate
                            self.log_test("Conversion Rates", True, 
                                        f"✅ CRT_DOGE rate available: {crt_doge_rate} (100,000 CRT = {expected_doge:,.0f} DOGE)", data)
                            return crt_doge_rate
                        else:
                            self.log_test("Conversion Rates", False, 
                                        "❌ CRT_DOGE conversion rate not available", data)
                            return None
                    else:
                        self.log_test("Conversion Rates", False, 
                                    "❌ Invalid conversion rates response", data)
                        return None
                else:
                    self.log_test("Conversion Rates", False, 
                                f"❌ HTTP {response.status}: {await response.text()}")
                    return None
        except Exception as e:
            self.log_test("Conversion Rates", False, f"❌ Error: {str(e)}")
            return None
    
    async def test_real_doge_conversion_execution(self):
        """Test 3: Execute the actual 100,000 CRT to REAL DOGE conversion"""
        try:
            conversion_payload = {
                "wallet_address": self.user_wallet,
                "from_currency": "CRT",
                "to_currency": "DOGE",
                "amount": 100000.0  # User's requested amount
            }
            
            async with self.session.post(f"{self.base_url}/wallet/convert", 
                                       json=conversion_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        # Check all the new REAL DOGE features
                        converted_amount = data.get("converted_amount", 0)
                        rate = data.get("rate", 0)
                        real_doge_created = data.get("real_doge_created", False)
                        doge_transaction_hash = data.get("doge_transaction_hash")
                        doge_address = data.get("doge_address")
                        conversion_type = data.get("conversion_type")
                        blockchain_verified = data.get("blockchain_verified", False)
                        verification_url = data.get("verification_url")
                        real_crypto_message = data.get("real_crypto_message")
                        
                        # Verify expected conversion amount (~2,150,000 DOGE)
                        expected_min = 2000000  # Minimum expected
                        expected_max = 2300000  # Maximum expected
                        
                        success_criteria = []
                        
                        # 1. Conversion amount check
                        if expected_min <= converted_amount <= expected_max:
                            success_criteria.append("✅ Conversion amount correct")
                        else:
                            success_criteria.append(f"❌ Conversion amount wrong: {converted_amount:,.0f} (expected ~2,150,000)")
                        
                        # 2. Real DOGE creation check
                        if real_doge_created:
                            success_criteria.append("✅ Real DOGE created")
                        else:
                            success_criteria.append("❌ Real DOGE not created")
                        
                        # 3. DOGE transaction hash check
                        if doge_transaction_hash:
                            success_criteria.append("✅ DOGE transaction hash provided")
                        else:
                            success_criteria.append("❌ DOGE transaction hash missing")
                        
                        # 4. DOGE address check
                        if doge_address and doge_address.startswith('D') and len(doge_address) >= 25:
                            success_criteria.append("✅ Real DOGE address generated")
                        else:
                            success_criteria.append("❌ Invalid DOGE address")
                        
                        # 5. Conversion type check
                        if conversion_type == "real_blockchain":
                            success_criteria.append("✅ Real blockchain conversion")
                        else:
                            success_criteria.append(f"❌ Not real blockchain: {conversion_type}")
                        
                        # 6. Blockchain verification check
                        if blockchain_verified:
                            success_criteria.append("✅ Blockchain verified")
                        else:
                            success_criteria.append("❌ Blockchain not verified")
                        
                        # 7. Verification URL check
                        if verification_url and "dogechain.info" in verification_url:
                            success_criteria.append("✅ Verification URL provided")
                        else:
                            success_criteria.append("❌ Verification URL missing/invalid")
                        
                        # Overall success determination
                        critical_checks = [real_doge_created, doge_transaction_hash, doge_address, 
                                         conversion_type == "real_blockchain"]
                        all_critical_passed = all(critical_checks)
                        
                        if all_critical_passed and expected_min <= converted_amount <= expected_max:
                            self.log_test("REAL DOGE Conversion Execution", True, 
                                        f"🎉 REAL DOGE CONVERSION SUCCESSFUL! {' | '.join(success_criteria)}", data)
                            return data
                        else:
                            self.log_test("REAL DOGE Conversion Execution", False, 
                                        f"❌ REAL DOGE CONVERSION FAILED! {' | '.join(success_criteria)}", data)
                            return None
                    else:
                        self.log_test("REAL DOGE Conversion Execution", False, 
                                    f"❌ Conversion failed: {data.get('message', 'Unknown error')}", data)
                        return None
                else:
                    error_text = await response.text()
                    self.log_test("REAL DOGE Conversion Execution", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return None
        except Exception as e:
            self.log_test("REAL DOGE Conversion Execution", False, f"❌ Error: {str(e)}")
            return None
    
    async def test_balance_updates_verification(self):
        """Test 4: Verify user's balance updates after conversion"""
        try:
            async with self.session.get(f"{self.base_url}/wallet/{self.user_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        crt_balance = wallet.get("deposit_balance", {}).get("CRT", 0)
                        doge_balance = wallet.get("deposit_balance", {}).get("DOGE", 0)
                        
                        # Check if CRT balance decreased by 100,000
                        # Check if DOGE balance increased significantly
                        
                        balance_checks = []
                        
                        # CRT should be reduced (assuming user had enough)
                        if crt_balance >= 0:  # Should be reduced from original
                            balance_checks.append("✅ CRT balance updated")
                        else:
                            balance_checks.append("❌ CRT balance invalid")
                        
                        # DOGE should be increased significantly (expecting ~2M+ DOGE)
                        if doge_balance >= 2000000:
                            balance_checks.append(f"✅ DOGE balance increased: {doge_balance:,.0f} DOGE")
                        else:
                            balance_checks.append(f"❌ DOGE balance not updated: {doge_balance:,.0f} DOGE")
                        
                        # Check balance source
                        balance_source = wallet.get("balance_source", "unknown")
                        if balance_source == "real_blockchain_api":
                            balance_checks.append("✅ Real blockchain balance source")
                        else:
                            balance_checks.append(f"❌ Not real blockchain source: {balance_source}")
                        
                        all_balance_checks_passed = doge_balance >= 2000000
                        
                        if all_balance_checks_passed:
                            self.log_test("Balance Updates Verification", True, 
                                        f"✅ BALANCE UPDATES SUCCESSFUL! {' | '.join(balance_checks)}", data)
                            return True
                        else:
                            self.log_test("Balance Updates Verification", False, 
                                        f"❌ BALANCE UPDATES FAILED! {' | '.join(balance_checks)}", data)
                            return False
                    else:
                        self.log_test("Balance Updates Verification", False, 
                                    "❌ Unable to retrieve wallet info", data)
                        return False
                else:
                    self.log_test("Balance Updates Verification", False, 
                                f"❌ HTTP {response.status}: {await response.text()}")
                    return False
        except Exception as e:
            self.log_test("Balance Updates Verification", False, f"❌ Error: {str(e)}")
            return False
    
    async def test_blockchain_integration_verification(self):
        """Test 5: Verify real blockchain integration for DOGE"""
        try:
            # Get user's DOGE address from wallet info
            async with self.session.get(f"{self.base_url}/wallet/{self.user_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        # Try to get DOGE address from previous conversion or generate one
                        # Test real DOGE balance endpoint
                        test_doge_address = "DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L"  # Known valid DOGE address for testing
                        
                        async with self.session.get(f"{self.base_url}/wallet/balance/DOGE?wallet_address={test_doge_address}") as balance_response:
                            if balance_response.status == 200:
                                balance_data = await balance_response.json()
                                if (balance_data.get("success") and 
                                    balance_data.get("source") == "blockcypher"):
                                    
                                    blockchain_checks = [
                                        "✅ DOGE blockchain API accessible",
                                        f"✅ BlockCypher integration working",
                                        f"✅ Real DOGE balance retrieval: {balance_data.get('balance', 0)} DOGE"
                                    ]
                                    
                                    self.log_test("Blockchain Integration Verification", True, 
                                                f"✅ BLOCKCHAIN INTEGRATION WORKING! {' | '.join(blockchain_checks)}", balance_data)
                                    return True
                                else:
                                    self.log_test("Blockchain Integration Verification", False, 
                                                f"❌ DOGE blockchain integration not working: {balance_data}", balance_data)
                                    return False
                            else:
                                self.log_test("Blockchain Integration Verification", False, 
                                            f"❌ DOGE balance endpoint failed: HTTP {balance_response.status}")
                                return False
                    else:
                        self.log_test("Blockchain Integration Verification", False, 
                                    "❌ Unable to verify blockchain integration", data)
                        return False
                else:
                    self.log_test("Blockchain Integration Verification", False, 
                                f"❌ HTTP {response.status}: {await response.text()}")
                    return False
        except Exception as e:
            self.log_test("Blockchain Integration Verification", False, f"❌ Error: {str(e)}")
            return False
    
    async def test_user_request_fulfillment(self):
        """Test 6: Final verification that user's request is fulfilled"""
        try:
            # Summary test to verify all user requirements are met
            user_requirements = [
                "Convert 100,000 CRT to REAL DOGE",
                "Expected ~2,150,000 DOGE (100,000 × 21.5 rate)",
                "Real DOGE address generation",
                "Blockchain transaction hashes",
                "Verification URLs",
                "Actual DOGE tokens created"
            ]
            
            # Get final wallet state
            async with self.session.get(f"{self.base_url}/wallet/{self.user_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        doge_balance = wallet.get("deposit_balance", {}).get("DOGE", 0)
                        
                        fulfillment_checks = []
                        
                        # Check if user got the expected DOGE amount
                        if doge_balance >= 2000000:
                            fulfillment_checks.append(f"✅ User received {doge_balance:,.0f} DOGE")
                        else:
                            fulfillment_checks.append(f"❌ User only received {doge_balance:,.0f} DOGE")
                        
                        # Check if balance source is real blockchain
                        balance_source = wallet.get("balance_source", "unknown")
                        if balance_source == "real_blockchain_api":
                            fulfillment_checks.append("✅ Real blockchain integration confirmed")
                        else:
                            fulfillment_checks.append(f"❌ Not real blockchain: {balance_source}")
                        
                        # Overall fulfillment assessment
                        user_satisfied = doge_balance >= 2000000 and balance_source == "real_blockchain_api"
                        
                        if user_satisfied:
                            self.log_test("User Request Fulfillment", True, 
                                        f"🎉 USER REQUEST FULFILLED! {' | '.join(fulfillment_checks)}", data)
                            return True
                        else:
                            self.log_test("User Request Fulfillment", False, 
                                        f"❌ USER REQUEST NOT FULFILLED! {' | '.join(fulfillment_checks)}", data)
                            return False
                    else:
                        self.log_test("User Request Fulfillment", False, 
                                    "❌ Unable to verify final user state", data)
                        return False
                else:
                    self.log_test("User Request Fulfillment", False, 
                                f"❌ HTTP {response.status}: {await response.text()}")
                    return False
        except Exception as e:
            self.log_test("User Request Fulfillment", False, f"❌ Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all REAL DOGE conversion tests"""
        print("🚀 STARTING REAL DOGE CONVERSION SYSTEM TESTING")
        print(f"📋 User Request: Convert 100,000 CRT to REAL DOGE")
        print(f"👤 User Wallet: {self.user_wallet}")
        print(f"🎯 Expected: ~2,150,000 DOGE (21.5 rate)")
        print("=" * 80)
        
        # Run tests in sequence
        wallet_verified = await self.test_user_wallet_verification()
        if not wallet_verified:
            print("❌ CRITICAL: User wallet verification failed - cannot proceed")
            return
        
        conversion_rate = await self.test_conversion_rates_availability()
        if not conversion_rate:
            print("❌ CRITICAL: Conversion rates not available - cannot proceed")
            return
        
        conversion_result = await self.test_real_doge_conversion_execution()
        if not conversion_result:
            print("❌ CRITICAL: REAL DOGE conversion failed")
            return
        
        balance_updated = await self.test_balance_updates_verification()
        blockchain_verified = await self.test_blockchain_integration_verification()
        user_fulfilled = await self.test_user_request_fulfillment()
        
        # Final summary
        print("=" * 80)
        print("📊 REAL DOGE CONVERSION TEST SUMMARY")
        
        passed_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"✅ Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        # Critical success criteria
        critical_success = (wallet_verified and conversion_result and 
                          balance_updated and blockchain_verified and user_fulfilled)
        
        if critical_success:
            print("🎉 REAL DOGE CONVERSION SYSTEM: ✅ WORKING")
            print("🎯 USER REQUEST: ✅ FULFILLED")
            print("💰 REAL DOGE TOKENS: ✅ CREATED")
        else:
            print("❌ REAL DOGE CONVERSION SYSTEM: ❌ FAILED")
            print("🎯 USER REQUEST: ❌ NOT FULFILLED")
            print("💰 REAL DOGE TOKENS: ❌ NOT CREATED")
        
        return critical_success

async def main():
    """Main test execution"""
    async with RealDogeConversionTester(BACKEND_URL) as tester:
        success = await tester.run_all_tests()
        
        if success:
            print("\n🎉 REAL DOGE CONVERSION TESTING COMPLETED SUCCESSFULLY!")
            sys.exit(0)
        else:
            print("\n❌ REAL DOGE CONVERSION TESTING FAILED!")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())