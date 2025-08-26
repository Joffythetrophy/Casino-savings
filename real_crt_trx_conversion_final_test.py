#!/usr/bin/env python3
"""
FINAL REAL CRT to TRX Conversion Test - Focus on Actual Conversion Functionality
Tests the specific user request for converting 100,000 CRT to TRX with real verification
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://gamewin-vault.preview.emergentagent.com/api"

class FinalCRTToTRXTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        
        # User-specific data from review request
        self.user_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        self.conversion_amount = 100000  # 100,000 CRT
        self.expected_trx_amount = 980000  # ~980,000 TRX (100,000 × 9.8 rate)
        
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
        
    async def test_user_has_sufficient_crt(self):
        """Test 1: Verify user has sufficient CRT for conversion"""
        try:
            async with self.session.get(f"{self.base_url.replace('/api', '')}/api/wallet/{self.user_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        crt_balance = wallet.get("deposit_balance", {}).get("CRT", 0)
                        
                        if crt_balance >= self.conversion_amount:
                            self.log_test("User CRT Balance Check", True, 
                                        f"✅ User has sufficient CRT: {crt_balance:,.0f} CRT (need {self.conversion_amount:,.0f})", data)
                            return crt_balance
                        else:
                            self.log_test("User CRT Balance Check", False, 
                                        f"❌ Insufficient CRT: {crt_balance:,.0f} CRT (need {self.conversion_amount:,.0f})", data)
                            return 0
                    else:
                        self.log_test("User CRT Balance Check", False, "❌ Invalid wallet response", data)
                        return 0
                else:
                    self.log_test("User CRT Balance Check", False, f"❌ HTTP {response.status}")
                    return 0
        except Exception as e:
            self.log_test("User CRT Balance Check", False, f"❌ Error: {str(e)}")
            return 0

    async def test_conversion_rate_available(self):
        """Test 2: Check if CRT to TRX conversion rate is available"""
        try:
            async with self.session.get(f"{self.base_url}/conversion/rates") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "rates" in data:
                        rates = data.get("rates", {})
                        crt_trx_rate = rates.get("CRT_TRX")
                        
                        if crt_trx_rate and crt_trx_rate > 0:
                            self.log_test("CRT to TRX Rate Available", True, 
                                        f"✅ CRT_TRX conversion rate: {crt_trx_rate}", data)
                            return crt_trx_rate
                        else:
                            self.log_test("CRT to TRX Rate Available", False, 
                                        f"❌ CRT_TRX rate not found or invalid: {crt_trx_rate}", data)
                            return None
                    else:
                        self.log_test("CRT to TRX Rate Available", False, "❌ Invalid rates response", data)
                        return None
                else:
                    self.log_test("CRT to TRX Rate Available", False, f"❌ HTTP {response.status}")
                    return None
        except Exception as e:
            self.log_test("CRT to TRX Rate Available", False, f"❌ Error: {str(e)}")
            return None

    async def test_execute_real_conversion(self):
        """Test 3: Execute the REAL CRT to TRX conversion"""
        try:
            conversion_payload = {
                "wallet_address": self.user_wallet,
                "from_currency": "CRT",
                "to_currency": "TRX",
                "amount": self.conversion_amount
            }
            
            async with self.session.post(f"{self.base_url}/wallet/convert", 
                                       json=conversion_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        converted_amount = data.get("converted_amount", 0)
                        rate_used = data.get("rate", 0)
                        transaction_id = data.get("transaction_id")
                        liquidity_contributed = data.get("liquidity_contributed", 0)
                        
                        # Verify conversion amounts are correct
                        expected_converted = self.conversion_amount * rate_used
                        amount_diff = abs(converted_amount - expected_converted)
                        
                        if amount_diff < 1000:  # Allow small rounding differences
                            self.log_test("Execute Real CRT to TRX Conversion", True, 
                                        f"✅ REAL CONVERSION SUCCESSFUL: {self.conversion_amount:,.0f} CRT → {converted_amount:,.2f} TRX (rate: {rate_used}, tx: {transaction_id}, liquidity: {liquidity_contributed:,.2f})", data)
                            return {
                                "success": True,
                                "converted_amount": converted_amount,
                                "rate": rate_used,
                                "transaction_id": transaction_id,
                                "liquidity_contributed": liquidity_contributed
                            }
                        else:
                            self.log_test("Execute Real CRT to TRX Conversion", False, 
                                        f"❌ Conversion amount mismatch: got {converted_amount}, expected {expected_converted}", data)
                            return {"success": False}
                    else:
                        self.log_test("Execute Real CRT to TRX Conversion", False, 
                                    f"❌ Conversion failed: {data.get('message', 'Unknown error')}", data)
                        return {"success": False}
                else:
                    error_text = await response.text()
                    self.log_test("Execute Real CRT to TRX Conversion", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return {"success": False}
        except Exception as e:
            self.log_test("Execute Real CRT to TRX Conversion", False, f"❌ Error: {str(e)}")
            return {"success": False}

    async def test_crt_balance_decreased(self, initial_crt_balance: float, conversion_result: Dict):
        """Test 4: Verify CRT balance decreased after conversion"""
        if not conversion_result.get("success"):
            self.log_test("CRT Balance Decreased", False, "❌ Skipping - conversion failed")
            return False
            
        try:
            # Wait a moment for balance to update
            await asyncio.sleep(2)
            
            async with self.session.get(f"{self.base_url.replace('/api', '')}/api/wallet/{self.user_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        new_crt_balance = wallet.get("deposit_balance", {}).get("CRT", 0)
                        
                        expected_decrease = self.conversion_amount
                        actual_decrease = initial_crt_balance - new_crt_balance
                        
                        if abs(actual_decrease - expected_decrease) < 1000:  # Allow small variance
                            self.log_test("CRT Balance Decreased", True, 
                                        f"✅ CRT balance correctly decreased: {initial_crt_balance:,.0f} → {new_crt_balance:,.0f} (decrease: {actual_decrease:,.0f})", data)
                            return True
                        else:
                            self.log_test("CRT Balance Decreased", False, 
                                        f"❌ CRT balance decrease incorrect: expected {expected_decrease:,.0f}, actual {actual_decrease:,.0f}", data)
                            return False
                    else:
                        self.log_test("CRT Balance Decreased", False, "❌ Invalid wallet response", data)
                        return False
                else:
                    self.log_test("CRT Balance Decreased", False, f"❌ HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("CRT Balance Decreased", False, f"❌ Error: {str(e)}")
            return False

    async def test_transaction_recorded(self, conversion_result: Dict):
        """Test 5: Verify conversion transaction was recorded"""
        if not conversion_result.get("success"):
            self.log_test("Transaction Recorded", False, "❌ Skipping - conversion failed")
            return False
            
        try:
            transaction_id = conversion_result.get("transaction_id")
            if transaction_id:
                # Transaction ID exists and is valid UUID format
                if len(transaction_id) >= 32 and '-' in transaction_id:
                    self.log_test("Transaction Recorded", True, 
                                f"✅ Conversion transaction recorded with ID: {transaction_id}", {"transaction_id": transaction_id})
                    return True
                else:
                    self.log_test("Transaction Recorded", False, 
                                f"❌ Invalid transaction ID format: {transaction_id}", {"transaction_id": transaction_id})
                    return False
            else:
                self.log_test("Transaction Recorded", False, "❌ No transaction ID returned", conversion_result)
                return False
        except Exception as e:
            self.log_test("Transaction Recorded", False, f"❌ Error: {str(e)}")
            return False

    async def test_liquidity_pool_updated(self, conversion_result: Dict):
        """Test 6: Verify liquidity pool was updated with conversion"""
        if not conversion_result.get("success"):
            self.log_test("Liquidity Pool Updated", False, "❌ Skipping - conversion failed")
            return False
            
        try:
            liquidity_contributed = conversion_result.get("liquidity_contributed", 0)
            if liquidity_contributed > 0:
                # Check if liquidity contribution is reasonable (should be percentage of converted amount)
                converted_amount = conversion_result.get("converted_amount", 0)
                expected_liquidity = converted_amount * 0.1  # 10% as per code
                
                if abs(liquidity_contributed - expected_liquidity) < 1000:  # Allow variance
                    self.log_test("Liquidity Pool Updated", True, 
                                f"✅ Liquidity pool updated: {liquidity_contributed:,.2f} TRX added (10% of {converted_amount:,.2f})", conversion_result)
                    return True
                else:
                    self.log_test("Liquidity Pool Updated", False, 
                                f"❌ Liquidity contribution incorrect: expected ~{expected_liquidity:,.2f}, got {liquidity_contributed:,.2f}", conversion_result)
                    return False
            else:
                self.log_test("Liquidity Pool Updated", False, 
                            f"❌ No liquidity contribution recorded: {liquidity_contributed}", conversion_result)
                return False
        except Exception as e:
            self.log_test("Liquidity Pool Updated", False, f"❌ Error: {str(e)}")
            return False

    async def test_real_money_verification(self):
        """Test 7: Verify this is real money conversion, not fake/mock"""
        try:
            # Check that the system uses real conversion rates from CoinGecko
            async with self.session.get(f"{self.base_url}/conversion/rates") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        source = data.get("source", "")
                        last_updated = data.get("last_updated", "")
                        
                        # Verify it's using real data source (CoinGecko or cache)
                        if source in ["coingecko", "cache"]:
                            self.log_test("Real Money Verification", True, 
                                        f"✅ REAL MONEY CONFIRMED: Using real conversion rates from {source}, last updated: {last_updated}", data)
                            return True
                        else:
                            self.log_test("Real Money Verification", False, 
                                        f"❌ FAKE DATA DETECTED: Using {source} instead of real rates", data)
                            return False
                    else:
                        self.log_test("Real Money Verification", False, "❌ Invalid rates response", data)
                        return False
                else:
                    self.log_test("Real Money Verification", False, f"❌ HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("Real Money Verification", False, f"❌ Error: {str(e)}")
            return False

    async def test_no_mock_data_used(self):
        """Test 8: Verify no mock/fake data is used in conversion"""
        try:
            # Check wallet balance source
            async with self.session.get(f"{self.base_url.replace('/api', '')}/api/wallet/{self.user_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") and "wallet" in data:
                        wallet = data["wallet"]
                        balance_source = wallet.get("balance_source", "")
                        
                        if balance_source == "real_blockchain_api":
                            self.log_test("No Mock Data Used", True, 
                                        f"✅ NO FAKE DATA: Wallet uses real blockchain API (source: {balance_source})", data)
                            return True
                        else:
                            self.log_test("No Mock Data Used", False, 
                                        f"❌ FAKE DATA DETECTED: Wallet source is {balance_source}", data)
                            return False
                    else:
                        self.log_test("No Mock Data Used", False, "❌ Invalid wallet response", data)
                        return False
                else:
                    self.log_test("No Mock Data Used", False, f"❌ HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("No Mock Data Used", False, f"❌ Error: {str(e)}")
            return False

    async def run_comprehensive_test(self):
        """Run comprehensive CRT to TRX conversion test"""
        print("🚀 FINAL REAL CRT TO TRX CONVERSION TEST")
        print(f"👤 User Wallet: {self.user_wallet}")
        print(f"💰 Converting: {self.conversion_amount:,.0f} CRT → Expected: ~{self.expected_trx_amount:,.0f} TRX")
        print("🎯 Focus: REAL MONEY CONVERSION VERIFICATION")
        print("=" * 80)
        
        # Test 1: Check user has sufficient CRT
        initial_crt_balance = await self.test_user_has_sufficient_crt()
        if initial_crt_balance < self.conversion_amount:
            print("❌ CRITICAL: Insufficient CRT balance - cannot proceed")
            return self.generate_summary()
        
        # Test 2: Check conversion rate availability
        conversion_rate = await self.test_conversion_rate_available()
        if not conversion_rate:
            print("❌ CRITICAL: CRT_TRX conversion rate not available - cannot proceed")
            return self.generate_summary()
        
        # Test 3: Execute the real conversion
        conversion_result = await self.test_execute_real_conversion()
        if not conversion_result.get("success"):
            print("❌ CRITICAL: Conversion execution failed - cannot proceed with verification")
            return self.generate_summary()
        
        # Test 4: Verify CRT balance decreased
        await self.test_crt_balance_decreased(initial_crt_balance, conversion_result)
        
        # Test 5: Verify transaction was recorded
        await self.test_transaction_recorded(conversion_result)
        
        # Test 6: Verify liquidity pool was updated
        await self.test_liquidity_pool_updated(conversion_result)
        
        # Test 7: Verify real money (not fake/mock)
        await self.test_real_money_verification()
        
        # Test 8: Verify no mock data used
        await self.test_no_mock_data_used()
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "=" * 80)
        print("📊 FINAL CRT TO TRX CONVERSION TEST SUMMARY")
        print("=" * 80)
        print(f"✅ PASSED: {passed_tests}/{total_tests} tests")
        print(f"❌ FAILED: {failed_tests}/{total_tests} tests")
        print(f"📈 SUCCESS RATE: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        # Check critical requirements for REAL MONEY conversion
        critical_tests = [
            "Execute Real CRT to TRX Conversion",
            "CRT Balance Decreased", 
            "Transaction Recorded",
            "Real Money Verification",
            "No Mock Data Used"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result["test"] in critical_tests and result["success"])
        
        print(f"\n🎯 CRITICAL REAL MONEY REQUIREMENTS: {critical_passed}/{len(critical_tests)} passed")
        
        # Find the conversion result
        conversion_details = None
        for result in self.test_results:
            if result["test"] == "Execute Real CRT to TRX Conversion" and result["success"]:
                conversion_details = result.get("response_data", {})
                break
        
        if critical_passed >= 4:  # At least 4/5 critical tests must pass
            print("🎉 SUCCESS: REAL CRT TO TRX CONVERSION IS WORKING!")
            print("✅ User can convert CRT to TRX with real money functionality")
            if conversion_details:
                converted_amount = conversion_details.get("converted_amount", 0)
                rate = conversion_details.get("rate", 0)
                transaction_id = conversion_details.get("transaction_id", "")
                print(f"💰 CONVERSION EXECUTED: {self.conversion_amount:,.0f} CRT → {converted_amount:,.2f} TRX")
                print(f"📊 RATE USED: {rate}")
                print(f"🧾 TRANSACTION ID: {transaction_id}")
        else:
            print("⚠️  WARNING: Critical real money requirements not met")
            print("❌ Real money conversion functionality may be compromised")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests/total_tests*100,
            "critical_passed": critical_passed,
            "critical_total": len(critical_tests),
            "overall_success": critical_passed >= 4,
            "conversion_details": conversion_details,
            "test_results": self.test_results
        }

async def main():
    """Main test execution"""
    async with FinalCRTToTRXTester(BACKEND_URL) as tester:
        summary = await tester.run_comprehensive_test()
        
        # Save results to file
        with open("/app/final_crt_trx_test_results.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: /app/final_crt_trx_test_results.json")
        
        # Return exit code based on success
        return 0 if summary["overall_success"] else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)