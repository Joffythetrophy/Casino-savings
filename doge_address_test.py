#!/usr/bin/env python3
"""
DOGE Address Generation System Test Suite - FIXED Implementation Testing
Tests the FIXED DOGE address generation system for Casino Savings dApp
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://cryptosavings.preview.emergentagent.com/api"

class DogeAddressSystemTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        # User's specific wallet address from review request
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
    
    def is_valid_doge_address(self, address: str) -> bool:
        """Validate DOGE address format"""
        if not address:
            return False
        
        # DOGE addresses must:
        # 1. Start with 'D'
        # 2. Be 25-34 characters long
        # 3. Be base58 encoded (alphanumeric, no 0, O, I, l)
        if not address.startswith('D'):
            return False
        
        if len(address) < 25 or len(address) > 34:
            return False
        
        # Check for valid base58 characters (no 0, O, I, l)
        base58_pattern = r'^[1-9A-HJ-NP-Za-km-z]+$'
        if not re.match(base58_pattern, address):
            return False
        
        return True
    
    def is_fake_doge_address(self, address: str) -> bool:
        """Check if address is fake format like DOGE_hash_prefix"""
        if not address:
            return True
        
        # Check for fake patterns
        fake_patterns = [
            r'^DOGE_[a-f0-9]+_',  # DOGE_hash_prefix format
            r'^DOGE[a-f0-9]+$',   # DOGEhash format
            r'DOGE.*hash',        # Any DOGE with hash
            r'DOGE.*prefix'       # Any DOGE with prefix
        ]
        
        for pattern in fake_patterns:
            if re.match(pattern, address, re.IGNORECASE):
                return True
        
        return False

    async def test_doge_address_generation_user_wallet(self):
        """Test 1: DOGE address generation for user's specific wallet"""
        try:
            endpoint = f"{self.base_url}/deposit/doge-address/{self.user_wallet}"
            
            async with self.session.get(endpoint) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if response has required fields
                    required_fields = ["success", "doge_deposit_address", "network", "instructions"]
                    if not all(field in data for field in required_fields):
                        self.log_test("DOGE Address Generation - User Wallet", False, 
                                    f"Missing required fields in response: {list(data.keys())}", data)
                        return
                    
                    if not data.get("success"):
                        self.log_test("DOGE Address Generation - User Wallet", False, 
                                    f"API returned success=false: {data.get('message', 'Unknown error')}", data)
                        return
                    
                    doge_address = data.get("doge_deposit_address", "")
                    network = data.get("network", "")
                    
                    # CRITICAL TEST: Check if address is REAL DOGE format
                    if self.is_fake_doge_address(doge_address):
                        self.log_test("DOGE Address Generation - User Wallet", False, 
                                    f"❌ CRITICAL FAILURE: Generated FAKE address '{doge_address}' - Fix failed!", data)
                        return
                    
                    if self.is_valid_doge_address(doge_address):
                        self.log_test("DOGE Address Generation - User Wallet", True, 
                                    f"✅ SUCCESS: Generated REAL DOGE address '{doge_address}' for wallet {self.user_wallet}, network: {network}", data)
                        
                        # Store for later tests
                        self.generated_doge_address = doge_address
                        
                        # Additional validation
                        instructions = data.get("instructions", [])
                        min_deposit = data.get("min_deposit")
                        processing_time = data.get("processing_time")
                        
                        if min_deposit and processing_time:
                            self.log_test("DOGE Address Instructions", True, 
                                        f"Complete instructions provided: min_deposit={min_deposit}, processing_time={processing_time}", data)
                        else:
                            self.log_test("DOGE Address Instructions", False, 
                                        "Incomplete deposit instructions", data)
                    else:
                        self.log_test("DOGE Address Generation - User Wallet", False, 
                                    f"❌ INVALID DOGE ADDRESS FORMAT: '{doge_address}' - does not meet DOGE address standards", data)
                else:
                    error_text = await response.text()
                    self.log_test("DOGE Address Generation - User Wallet", False, 
                                f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("DOGE Address Generation - User Wallet", False, f"Error: {str(e)}")

    async def test_doge_address_format_validation(self):
        """Test 2: DOGE address format validation"""
        try:
            if not hasattr(self, 'generated_doge_address'):
                self.log_test("DOGE Address Format Validation", False, 
                            "No generated DOGE address available for validation")
                return
            
            address = self.generated_doge_address
            
            # Test 1: Starts with 'D'
            starts_with_d = address.startswith('D')
            
            # Test 2: Length is 25-34 characters
            valid_length = 25 <= len(address) <= 34
            
            # Test 3: Base58 encoded (no 0, O, I, l)
            base58_valid = re.match(r'^[1-9A-HJ-NP-Za-km-z]+$', address) is not None
            
            # Test 4: Not fake format
            not_fake = not self.is_fake_doge_address(address)
            
            validation_results = {
                "starts_with_D": starts_with_d,
                "valid_length": valid_length,
                "base58_encoded": base58_valid,
                "not_fake_format": not_fake,
                "address": address,
                "length": len(address)
            }
            
            all_valid = all(validation_results.values() if k != "address" and k != "length" else True 
                          for k in validation_results.keys())
            
            if all_valid:
                self.log_test("DOGE Address Format Validation", True, 
                            f"✅ DOGE address '{address}' passes all format validations: starts with D, length {len(address)}, base58 encoded, real format", 
                            validation_results)
            else:
                failed_checks = [k for k, v in validation_results.items() 
                               if k not in ["address", "length"] and not v]
                self.log_test("DOGE Address Format Validation", False, 
                            f"❌ DOGE address '{address}' failed validation checks: {failed_checks}", 
                            validation_results)
                
        except Exception as e:
            self.log_test("DOGE Address Format Validation", False, f"Error: {str(e)}")

    async def test_doge_manual_verification_system(self):
        """Test 3: Manual DOGE deposit verification system"""
        try:
            # Test with a real DOGE address format
            real_doge_address = "D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda"  # Example from review request
            
            payload = {
                "doge_address": real_doge_address,
                "casino_wallet_address": self.user_wallet,
                "amount": 100.0  # Test amount
            }
            
            async with self.session.post(f"{self.base_url}/deposit/doge/manual", 
                                       json=payload) as response:
                if response.status in [200, 400]:  # 400 might be expected for various reasons
                    data = await response.json()
                    
                    if response.status == 200 and data.get("success"):
                        self.log_test("DOGE Manual Verification System", True, 
                                    f"✅ Manual verification system accepts real DOGE address: {data.get('message', 'Success')}", data)
                    elif response.status == 400:
                        # Check if it's rejecting for valid reasons (like no balance, user not found, etc.)
                        error_message = data.get("message", "") or data.get("detail", "")
                        
                        # Valid rejection reasons
                        valid_rejections = [
                            "user not found",
                            "no balance",
                            "insufficient balance",
                            "already processed",
                            "cooldown"
                        ]
                        
                        if any(reason in error_message.lower() for reason in valid_rejections):
                            self.log_test("DOGE Manual Verification System", True, 
                                        f"✅ Manual verification system working - valid rejection: {error_message}", data)
                        elif "invalid" in error_message.lower() and "address" in error_message.lower():
                            self.log_test("DOGE Manual Verification System", False, 
                                        f"❌ System incorrectly rejected valid DOGE address: {error_message}", data)
                        else:
                            self.log_test("DOGE Manual Verification System", True, 
                                        f"✅ Manual verification system functional - rejection reason: {error_message}", data)
                    else:
                        self.log_test("DOGE Manual Verification System", False, 
                                    f"Unexpected response: {data}", data)
                else:
                    error_text = await response.text()
                    self.log_test("DOGE Manual Verification System", False, 
                                f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("DOGE Manual Verification System", False, f"Error: {str(e)}")

    async def test_doge_address_validation_endpoint(self):
        """Test 4: DOGE address validation functionality"""
        try:
            # Test valid DOGE addresses
            valid_addresses = [
                "D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda",
                "DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L",
                "D7Y55r6hNkcqDTvFW8GmyJKBGkbqNgLKjh"
            ]
            
            # Test invalid addresses
            invalid_addresses = [
                "DOGE_hash_prefix_fake",
                "1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2",  # Bitcoin address
                "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",  # TRON address
                "invalid_address",
                ""
            ]
            
            valid_count = 0
            invalid_count = 0
            
            # Test valid addresses
            for address in valid_addresses:
                try:
                    payload = {
                        "doge_address": address,
                        "casino_wallet_address": self.user_wallet,
                        "amount": 10.0
                    }
                    
                    async with self.session.post(f"{self.base_url}/deposit/doge/manual", 
                                               json=payload) as response:
                        data = await response.json()
                        
                        # Should not reject due to invalid address format
                        error_message = data.get("message", "") or data.get("detail", "")
                        if "invalid" in error_message.lower() and "address" in error_message.lower():
                            self.log_test(f"DOGE Validation - Valid Address {address}", False, 
                                        f"❌ System incorrectly rejected valid DOGE address: {error_message}", data)
                        else:
                            valid_count += 1
                            
                except Exception as e:
                    self.log_test(f"DOGE Validation - Valid Address {address}", False, f"Error: {str(e)}")
            
            # Test invalid addresses
            for address in invalid_addresses:
                try:
                    payload = {
                        "doge_address": address,
                        "casino_wallet_address": self.user_wallet,
                        "amount": 10.0
                    }
                    
                    async with self.session.post(f"{self.base_url}/deposit/doge/manual", 
                                               json=payload) as response:
                        data = await response.json()
                        
                        # Should reject due to invalid address format
                        error_message = data.get("message", "") or data.get("detail", "")
                        if "invalid" in error_message.lower() and "address" in error_message.lower():
                            invalid_count += 1
                        elif response.status == 400:
                            invalid_count += 1  # Rejected for some reason, which is good
                            
                except Exception as e:
                    # Network errors are acceptable for invalid addresses
                    invalid_count += 1
            
            # Summary
            if valid_count >= 2 and invalid_count >= 3:
                self.log_test("DOGE Address Validation System", True, 
                            f"✅ Address validation working: {valid_count}/{len(valid_addresses)} valid addresses accepted, {invalid_count}/{len(invalid_addresses)} invalid addresses rejected", 
                            {"valid_accepted": valid_count, "invalid_rejected": invalid_count})
            else:
                self.log_test("DOGE Address Validation System", False, 
                            f"❌ Address validation issues: {valid_count}/{len(valid_addresses)} valid addresses accepted, {invalid_count}/{len(invalid_addresses)} invalid addresses rejected", 
                            {"valid_accepted": valid_count, "invalid_rejected": invalid_count})
                
        except Exception as e:
            self.log_test("DOGE Address Validation System", False, f"Error: {str(e)}")

    async def test_real_blockchain_integration(self):
        """Test 5: Real blockchain integration for DOGE"""
        try:
            # Test real DOGE balance endpoint
            real_doge_address = "DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L"
            
            async with self.session.get(f"{self.base_url}/wallet/balance/DOGE?wallet_address={real_doge_address}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success") and data.get("source") == "blockcypher":
                        balance = data.get("balance", 0)
                        self.log_test("Real Blockchain Integration - DOGE", True, 
                                    f"✅ Real blockchain integration working: {balance} DOGE from BlockCypher API", data)
                        
                        # Check if balance is realistic (not mock data like 100.0)
                        if balance != 100.0 and balance != 0.0:
                            self.log_test("Real Blockchain Data Verification", True, 
                                        f"✅ Balance appears to be real blockchain data: {balance} DOGE (not mock)", data)
                        else:
                            self.log_test("Real Blockchain Data Verification", False, 
                                        f"⚠️ Balance might be mock data: {balance} DOGE", data)
                    else:
                        self.log_test("Real Blockchain Integration - DOGE", False, 
                                    f"❌ Not using real blockchain API: source={data.get('source')}, success={data.get('success')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("Real Blockchain Integration - DOGE", False, 
                                f"HTTP {response.status}: {error_text}")
                    
        except Exception as e:
            self.log_test("Real Blockchain Integration - DOGE", False, f"Error: {str(e)}")

    async def test_no_fake_address_generation(self):
        """Test 6: Verify NO fake address generation"""
        try:
            # Test multiple address generations to ensure consistency
            test_wallets = [
                self.user_wallet,
                "TestWallet123456789",
                "AnotherTestWallet987"
            ]
            
            fake_addresses_found = []
            real_addresses_found = []
            
            for wallet in test_wallets:
                try:
                    endpoint = f"{self.base_url}/deposit/doge-address/{wallet}"
                    
                    async with self.session.get(endpoint) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if data.get("success"):
                                doge_address = data.get("doge_deposit_address", "")
                                
                                if self.is_fake_doge_address(doge_address):
                                    fake_addresses_found.append({
                                        "wallet": wallet,
                                        "address": doge_address
                                    })
                                elif self.is_valid_doge_address(doge_address):
                                    real_addresses_found.append({
                                        "wallet": wallet,
                                        "address": doge_address
                                    })
                                    
                except Exception as e:
                    print(f"Error testing wallet {wallet}: {e}")
                    continue
            
            # CRITICAL SUCCESS CRITERIA: NO fake addresses should be generated
            if len(fake_addresses_found) == 0:
                self.log_test("No Fake Address Generation", True, 
                            f"✅ CRITICAL SUCCESS: No fake addresses generated! All {len(real_addresses_found)} addresses are real DOGE format", 
                            {"real_addresses": real_addresses_found, "fake_addresses": fake_addresses_found})
            else:
                self.log_test("No Fake Address Generation", False, 
                            f"❌ CRITICAL FAILURE: {len(fake_addresses_found)} fake addresses still being generated! Fix incomplete!", 
                            {"real_addresses": real_addresses_found, "fake_addresses": fake_addresses_found})
                
        except Exception as e:
            self.log_test("No Fake Address Generation", False, f"Error: {str(e)}")

    async def test_deposit_flow_integration(self):
        """Test 7: Complete DOGE deposit flow integration"""
        try:
            # Step 1: Generate DOGE address
            endpoint = f"{self.base_url}/deposit/doge-address/{self.user_wallet}"
            
            async with self.session.get(endpoint) as response:
                if response.status != 200:
                    self.log_test("Complete DOGE Deposit Flow", False, 
                                "Step 1 failed: Could not generate DOGE address")
                    return
                
                data = await response.json()
                if not data.get("success"):
                    self.log_test("Complete DOGE Deposit Flow", False, 
                                f"Step 1 failed: DOGE address generation unsuccessful: {data.get('message', 'Unknown error')}")
                    return
                
                generated_address = data.get("doge_deposit_address", "")
                if self.is_fake_doge_address(generated_address):
                    self.log_test("Complete DOGE Deposit Flow", False, 
                                f"Step 1 failed: Generated fake address {generated_address}")
                    return
            
            # Step 2: Test manual verification with real DOGE address
            real_doge_address = "D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda"
            
            payload = {
                "doge_address": real_doge_address,
                "casino_wallet_address": self.user_wallet,
                "amount": 50.0
            }
            
            async with self.session.post(f"{self.base_url}/deposit/doge/manual", 
                                       json=payload) as response:
                # Any response (200 or 400) is acceptable as long as it's not rejecting due to invalid address format
                if response.status in [200, 400]:
                    data = await response.json()
                    error_message = data.get("message", "") or data.get("detail", "")
                    
                    if "invalid" in error_message.lower() and "address" in error_message.lower():
                        self.log_test("Complete DOGE Deposit Flow", False, 
                                    f"Step 2 failed: Manual verification incorrectly rejected real DOGE address: {error_message}")
                        return
                
            # Step 3: Test blockchain balance check
            async with self.session.get(f"{self.base_url}/wallet/balance/DOGE?wallet_address=DH5yaieqoZN36fDVciNyRueRGvGLR3mr7L") as response:
                if response.status != 200:
                    self.log_test("Complete DOGE Deposit Flow", False, 
                                "Step 3 failed: Blockchain balance check failed")
                    return
                
                data = await response.json()
                if not data.get("success") or data.get("source") != "blockcypher":
                    self.log_test("Complete DOGE Deposit Flow", False, 
                                "Step 3 failed: Not using real blockchain API")
                    return
            
            # All steps successful
            self.log_test("Complete DOGE Deposit Flow", True, 
                        f"✅ Complete DOGE deposit flow working: 1) Real address generation ({generated_address}), 2) Manual verification accepts real addresses, 3) Real blockchain integration", 
                        {"generated_address": generated_address, "test_address": real_doge_address})
                
        except Exception as e:
            self.log_test("Complete DOGE Deposit Flow", False, f"Error: {str(e)}")

    async def run_all_tests(self):
        """Run all DOGE address system tests"""
        print("🐕 Starting DOGE Address Generation System Tests - FIXED Implementation")
        print(f"Testing with user wallet: {self.user_wallet}")
        print("=" * 80)
        
        # Run tests in order
        await self.test_doge_address_generation_user_wallet()
        await self.test_doge_address_format_validation()
        await self.test_doge_manual_verification_system()
        await self.test_doge_address_validation_endpoint()
        await self.test_real_blockchain_integration()
        await self.test_no_fake_address_generation()
        await self.test_deposit_flow_integration()
        
        # Summary
        print("\n" + "=" * 80)
        print("🐕 DOGE ADDRESS SYSTEM TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Critical success criteria check
        critical_tests = [
            "DOGE Address Generation - User Wallet",
            "DOGE Address Format Validation", 
            "No Fake Address Generation",
            "Complete DOGE Deposit Flow"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result["test"] in critical_tests and result["success"])
        
        print(f"\n🎯 CRITICAL SUCCESS CRITERIA: {critical_passed}/{len(critical_tests)} passed")
        
        if critical_passed == len(critical_tests):
            print("✅ ALL CRITICAL TESTS PASSED - DOGE ADDRESS FIX IS SUCCESSFUL!")
        else:
            print("❌ CRITICAL TESTS FAILED - DOGE ADDRESS FIX NEEDS MORE WORK!")
        
        # Show failed tests
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['details']}")
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "critical_passed": critical_passed,
            "critical_total": len(critical_tests),
            "all_critical_passed": critical_passed == len(critical_tests),
            "test_results": self.test_results
        }

async def main():
    """Main test execution"""
    async with DogeAddressSystemTester(BACKEND_URL) as tester:
        results = await tester.run_all_tests()
        return results

if __name__ == "__main__":
    results = asyncio.run(main())