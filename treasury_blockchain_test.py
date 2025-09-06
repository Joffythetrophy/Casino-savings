#!/usr/bin/env python3
"""
Treasury Address Validation and Real Blockchain Integration Test
Tests the newly implemented REAL BLOCKCHAIN INTEGRATION system for treasury addresses
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from decimal import Decimal
import sys

class TreasuryBlockchainTester:
    def __init__(self):
        self.base_url = "https://blockchain-slots.preview.emergentagent.com/api"
        self.test_results = []
        self.session = None
        self.auth_token = None
        
        # Test credentials from review request
        self.test_username = "cryptoking"
        self.test_password = "crt21million"
        self.test_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        
        # Treasury addresses from review request
        self.treasury_addresses = {
            "USDC": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",  # Solana network
            "TRON": "TJkna9XCi5noxE7hsEo6jz6et6c3B7zE9o",  # TRON network
            "DOGE": "DNmtdukSPBf1PTqVQ9z8GGSJjpR8JqAimQ"  # Dogecoin network
        }
        
        # Test amounts for small withdrawals
        self.test_amounts = {
            "USDC": 0.01,
            "DOGE": 10.0
        }
        
    def log_test(self, test_name: str, success: bool, message: str, data: dict = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2)}")
    
    async def setup_session(self):
        """Setup HTTP session"""
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
    
    async def cleanup_session(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def authenticate_user(self):
        """Authenticate user and get JWT token"""
        try:
            print(f"🔐 Authenticating user: {self.test_username}")
            
            # Try username/password login
            login_data = {
                "username": self.test_username,
                "password": self.test_password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login-username", 
                                       json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        # Store token if provided
                        self.auth_token = data.get("token")
                        wallet_address = data.get("wallet_address")
                        
                        if wallet_address == self.test_wallet:
                            self.log_test("User Authentication", True, 
                                        f"✅ User authenticated successfully with correct wallet: {wallet_address}")
                            return True
                        else:
                            self.log_test("User Authentication", False, 
                                        f"❌ Wallet mismatch: expected {self.test_wallet}, got {wallet_address}")
                            return False
                    else:
                        return await self.try_alternative_login()
                else:
                    return await self.try_alternative_login()
                    
        except Exception as e:
            self.log_test("User Authentication", False, f"❌ Exception: {str(e)}")
            return False
    
    async def try_alternative_login(self):
        """Try alternative login method"""
        try:
            login_data = {
                "identifier": self.test_username,
                "password": self.test_password
            }
            
            async with self.session.post(f"{self.base_url}/auth/login", 
                                       json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        self.auth_token = data.get("token")
                        wallet_address = data.get("wallet_address")
                        
                        if wallet_address == self.test_wallet:
                            self.log_test("User Authentication", True, 
                                        f"✅ User authenticated successfully (alternative method)")
                            return True
                        else:
                            self.log_test("User Authentication", False, 
                                        f"❌ Wallet mismatch (alternative): expected {self.test_wallet}, got {wallet_address}")
                            return False
                    else:
                        self.log_test("User Authentication", False, 
                                    f"❌ Alternative authentication failed: {data.get('message', 'Unknown error')}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("User Authentication", False, 
                                f"❌ Alternative HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("User Authentication", False, f"❌ Alternative exception: {str(e)}")
            return False
    
    async def test_treasury_address_validation(self):
        """Test 1: Validate treasury addresses for USDC, TRON, and DOGE networks"""
        try:
            print(f"🏛️ Testing Treasury Address Validation")
            
            validation_results = {}
            
            for currency, address in self.treasury_addresses.items():
                try:
                    # Test address validation endpoint
                    validation_data = {
                        "address": address,
                        "currency": currency,
                        "network": currency.lower() if currency != "USDC" else "solana"
                    }
                    
                    headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
                    
                    async with self.session.post(f"{self.base_url}/blockchain/validate-address", 
                                               json=validation_data, 
                                               headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("success"):
                                validation_info = data.get("validation", {})
                                validation_results[currency] = {
                                    "valid": validation_info.get("valid", False),
                                    "network": validation_info.get("network"),
                                    "address_type": validation_info.get("address_type"),
                                    "address": address
                                }
                            else:
                                validation_results[currency] = {
                                    "valid": False,
                                    "error": data.get("message", "Validation failed"),
                                    "address": address
                                }
                        else:
                            error_text = await response.text()
                            validation_results[currency] = {
                                "valid": False,
                                "error": f"HTTP {response.status}: {error_text}",
                                "address": address
                            }
                            
                except Exception as e:
                    validation_results[currency] = {
                        "valid": False,
                        "error": f"Exception: {str(e)}",
                        "address": address
                    }
            
            # Check results
            valid_addresses = [curr for curr, result in validation_results.items() if result.get("valid")]
            
            if len(valid_addresses) == len(self.treasury_addresses):
                self.log_test("Treasury Address Validation", True, 
                            f"✅ All {len(valid_addresses)} treasury addresses validated successfully: {valid_addresses}", 
                            validation_results)
                return True
            else:
                invalid_addresses = [curr for curr, result in validation_results.items() if not result.get("valid")]
                self.log_test("Treasury Address Validation", False, 
                            f"❌ {len(invalid_addresses)} addresses failed validation: {invalid_addresses}", 
                            validation_results)
                return False
                
        except Exception as e:
            self.log_test("Treasury Address Validation", False, f"❌ Exception: {str(e)}")
            return False
    
    async def test_real_blockchain_balances(self):
        """Test 2: Check real blockchain balances for treasury addresses"""
        try:
            print(f"💰 Testing Real Blockchain Balance Checks")
            
            balance_results = {}
            
            for currency, address in self.treasury_addresses.items():
                try:
                    headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
                    
                    # Use the real balance endpoint with path parameters
                    async with self.session.get(f"{self.base_url}/blockchain/real-balance/{currency}/{address}", 
                                              headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get("success"):
                                balance_info = data.get("balance", {})
                                balance_results[currency] = {
                                    "balance": balance_info.get("balance", 0),
                                    "currency": currency,
                                    "address": address,
                                    "network": balance_info.get("network"),
                                    "accessible": balance_info.get("success", False)
                                }
                            else:
                                balance_results[currency] = {
                                    "balance": 0,
                                    "error": data.get("message", "Balance check failed"),
                                    "address": address,
                                    "accessible": False
                                }
                        else:
                            error_text = await response.text()
                            balance_results[currency] = {
                                "balance": 0,
                                "error": f"HTTP {response.status}: {error_text}",
                                "address": address,
                                "accessible": False
                            }
                            
                except Exception as e:
                    balance_results[currency] = {
                        "balance": 0,
                        "error": f"Exception: {str(e)}",
                        "address": address,
                        "accessible": False
                    }
            
            # Check if addresses are accessible on their networks
            accessible_addresses = [curr for curr, result in balance_results.items() if result.get("accessible")]
            
            if len(accessible_addresses) >= 2:  # At least 2 networks should be accessible
                self.log_test("Real Blockchain Balance Checks", True, 
                            f"✅ {len(accessible_addresses)} treasury addresses accessible on blockchain networks: {accessible_addresses}", 
                            balance_results)
                return True
            else:
                self.log_test("Real Blockchain Balance Checks", False, 
                            f"❌ Only {len(accessible_addresses)} addresses accessible, need at least 2", 
                            balance_results)
                return False
                
        except Exception as e:
            self.log_test("Real Blockchain Balance Checks", False, f"❌ Exception: {str(e)}")
            return False
    
    async def test_small_withdrawal_usdc(self):
        """Test 3: Execute small USDC test withdrawal to treasury address"""
        try:
            print(f"💸 Testing Small USDC Withdrawal to Treasury")
            
            # Get user balance first
            user_balance = await self.get_user_balance()
            if not user_balance:
                self.log_test("Small USDC Withdrawal", False, "❌ Could not get user balance")
                return False
            
            usdc_balance = user_balance.get("USDC", 0)
            test_amount = self.test_amounts["USDC"]
            
            if usdc_balance < test_amount:
                self.log_test("Small USDC Withdrawal", False, 
                            f"❌ Insufficient USDC balance: {usdc_balance}, need {test_amount}")
                return False
            
            # Execute withdrawal
            withdrawal_data = {
                "wallet_address": self.test_wallet,
                "wallet_type": "deposit",
                "currency": "USDC",
                "amount": test_amount,
                "destination_address": self.treasury_addresses["USDC"]
            }
            
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=withdrawal_data, 
                                       headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        tx_hash = data.get("blockchain_transaction_hash")
                        verification_url = data.get("verification_url")
                        
                        self.log_test("Small USDC Withdrawal", True, 
                                    f"✅ USDC withdrawal successful! Amount: {test_amount}, TX: {tx_hash}", 
                                    {"transaction_hash": tx_hash, "verification_url": verification_url})
                        return True
                    else:
                        self.log_test("Small USDC Withdrawal", False, 
                                    f"❌ Withdrawal failed: {data.get('message', 'Unknown error')}", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Small USDC Withdrawal", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Small USDC Withdrawal", False, f"❌ Exception: {str(e)}")
            return False
    
    async def test_small_withdrawal_doge(self):
        """Test 4: Execute small DOGE test withdrawal to treasury address"""
        try:
            print(f"🐕 Testing Small DOGE Withdrawal to Treasury")
            
            # Get user balance first
            user_balance = await self.get_user_balance()
            if not user_balance:
                self.log_test("Small DOGE Withdrawal", False, "❌ Could not get user balance")
                return False
            
            doge_balance = user_balance.get("DOGE", 0)
            test_amount = self.test_amounts["DOGE"]
            
            if doge_balance < test_amount:
                self.log_test("Small DOGE Withdrawal", False, 
                            f"❌ Insufficient DOGE balance: {doge_balance}, need {test_amount}")
                return False
            
            # Execute withdrawal
            withdrawal_data = {
                "wallet_address": self.test_wallet,
                "wallet_type": "deposit",
                "currency": "DOGE",
                "amount": test_amount,
                "destination_address": self.treasury_addresses["DOGE"]
            }
            
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            async with self.session.post(f"{self.base_url}/wallet/withdraw", 
                                       json=withdrawal_data, 
                                       headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        tx_hash = data.get("blockchain_transaction_hash")
                        verification_url = data.get("verification_url")
                        
                        self.log_test("Small DOGE Withdrawal", True, 
                                    f"✅ DOGE withdrawal successful! Amount: {test_amount}, TX: {tx_hash}", 
                                    {"transaction_hash": tx_hash, "verification_url": verification_url})
                        return True
                    else:
                        self.log_test("Small DOGE Withdrawal", False, 
                                    f"❌ Withdrawal failed: {data.get('message', 'Unknown error')}", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Small DOGE Withdrawal", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Small DOGE Withdrawal", False, f"❌ Exception: {str(e)}")
            return False
    
    async def test_multi_currency_transaction_flow(self):
        """Test 5: Test complete multi-currency real transaction flow"""
        try:
            print(f"🔄 Testing Multi-Currency Real Transaction Flow")
            
            # Get user balance
            user_balance = await self.get_user_balance()
            if not user_balance:
                self.log_test("Multi-Currency Transaction Flow", False, "❌ Could not get user balance")
                return False
            
            # Test conversion flow (DOGE to USDC)
            doge_balance = user_balance.get("DOGE", 0)
            if doge_balance < 100:  # Need at least 100 DOGE for conversion test
                self.log_test("Multi-Currency Transaction Flow", False, 
                            f"❌ Insufficient DOGE for conversion test: {doge_balance}")
                return False
            
            # Convert 50 DOGE to USDC
            conversion_data = {
                "wallet_address": self.test_wallet,
                "from_currency": "DOGE",
                "to_currency": "USDC",
                "amount": 50.0
            }
            
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            async with self.session.post(f"{self.base_url}/wallet/convert", 
                                       json=conversion_data, 
                                       headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        converted_amount = data.get("converted_amount", 0)
                        
                        self.log_test("Multi-Currency Transaction Flow", True, 
                                    f"✅ Multi-currency flow successful! Converted 50 DOGE to {converted_amount} USDC", 
                                    {"conversion": data})
                        return True
                    else:
                        self.log_test("Multi-Currency Transaction Flow", False, 
                                    f"❌ Conversion failed: {data.get('message', 'Unknown error')}", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Multi-Currency Transaction Flow", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Multi-Currency Transaction Flow", False, f"❌ Exception: {str(e)}")
            return False
    
    async def test_blockchain_network_accessibility(self):
        """Test 6: Verify all blockchain networks are accessible"""
        try:
            print(f"🌐 Testing Blockchain Network Accessibility")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            # Test health endpoint to check network connectivity
            async with self.session.get(f"{self.base_url}/health", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    services = data.get("services", {})
                    
                    # Check which networks are accessible
                    network_status = {
                        "solana": services.get("solana", {}).get("success", False),
                        "dogecoin": services.get("dogecoin", {}).get("success", False),
                        "tron": services.get("tron", {}).get("success", False)
                    }
                    
                    accessible_networks = [net for net, status in network_status.items() if status]
                    
                    if len(accessible_networks) >= 2:  # At least 2 networks should be accessible
                        self.log_test("Blockchain Network Accessibility", True, 
                                    f"✅ {len(accessible_networks)} blockchain networks accessible: {accessible_networks}", 
                                    network_status)
                        return True
                    else:
                        self.log_test("Blockchain Network Accessibility", False, 
                                    f"❌ Only {len(accessible_networks)} networks accessible: {accessible_networks}", 
                                    network_status)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Blockchain Network Accessibility", False, 
                                f"❌ Health check failed HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Blockchain Network Accessibility", False, f"❌ Exception: {str(e)}")
            return False
    
    async def get_user_balance(self):
        """Get user balance for testing"""
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            async with self.session.get(f"{self.base_url}/wallet/{self.test_wallet}", 
                                      headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        wallet_info = data.get("wallet", {})
                        deposit_balance = wallet_info.get("deposit_balance", {})
                        return deposit_balance
                        
        except Exception as e:
            print(f"Error getting balance: {e}")
            return None
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🏛️ TREASURY BLOCKCHAIN INTEGRATION TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if "✅ PASS" in r["status"]])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests*100):.1f}% success rate)")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if "❌ FAIL" in result["status"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        if passed_tests > 0:
            print(f"\n✅ PASSED TESTS ({passed_tests}):")
            for result in self.test_results:
                if "✅ PASS" in result["status"]:
                    print(f"   • {result['test']}: {result['message']}")
        
        # Treasury addresses summary
        print(f"\n🏛️ TREASURY ADDRESSES TESTED:")
        for currency, address in self.treasury_addresses.items():
            print(f"   • {currency}: {address}")
        
        return passed_tests, total_tests
    
    async def run_all_tests(self):
        """Run all treasury blockchain integration tests"""
        print("🚀 STARTING TREASURY BLOCKCHAIN INTEGRATION TESTS")
        print("="*80)
        
        await self.setup_session()
        
        try:
            # Authenticate user first
            auth_success = await self.authenticate_user()
            
            if auth_success:
                # Get user balance for reference
                user_balance = await self.get_user_balance()
                if user_balance:
                    print(f"💰 User balances: {user_balance}")
                
                # Test 1: Treasury Address Validation
                await self.test_treasury_address_validation()
                
                # Test 2: Real Blockchain Balance Checks
                await self.test_real_blockchain_balances()
                
                # Test 3: Small USDC Withdrawal
                await self.test_small_withdrawal_usdc()
                
                # Test 4: Small DOGE Withdrawal
                await self.test_small_withdrawal_doge()
                
                # Test 5: Multi-Currency Transaction Flow
                await self.test_multi_currency_transaction_flow()
                
                # Test 6: Blockchain Network Accessibility
                await self.test_blockchain_network_accessibility()
            else:
                print("❌ Cannot proceed with treasury tests - authentication failed")
        
        finally:
            await self.cleanup_session()
        
        # Print summary
        passed, total = self.print_summary()
        return passed, total

async def main():
    """Main test execution"""
    tester = TreasuryBlockchainTester()
    passed, total = await tester.run_all_tests()
    
    # Exit with appropriate code
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! Treasury blockchain integration is working correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️ {total - passed} tests failed. Treasury blockchain integration needs attention.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())