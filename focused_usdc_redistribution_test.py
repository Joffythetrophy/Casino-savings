#!/usr/bin/env python3
"""
Focused USDC Treasury Redistribution Test
Test redistributing user 'cryptoking's 7.9M USDC across 3 wallet types using the new internal transfer endpoint
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Get backend URL from frontend env
BACKEND_URL = "https://smart-savings-dapp.preview.emergentagent.com/api"

class FocusedUSDCTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.test_results = []
        self.auth_token = None
        
        # Test credentials from review request
        self.test_username = "cryptoking"
        self.test_password = "crt21million"
        self.test_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        
        # Adjusted target distribution for actual 7.9M USDC (maintaining same percentages)
        total_usdc = 7900694.90
        self.target_distribution = {
            "savings": 3634319.65,    # 46% - long-term treasury storage
            "winnings": 2686236.27,   # 34% - active treasury operations  
            "deposit": 1580139.00     # 20% - remaining balance for liquidity
        }
        
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
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
        """Authenticate user cryptoking"""
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
                        wallet_address = data.get("wallet_address")
                        
                        if wallet_address == self.test_wallet:
                            self.log_test("User Authentication", True, 
                                        f"✅ User authenticated successfully with wallet: {wallet_address}")
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
                        wallet_address = data.get("wallet_address")
                        
                        if wallet_address == self.test_wallet:
                            self.log_test("User Authentication", True, 
                                        f"✅ User authenticated (alternative method) with wallet: {wallet_address}")
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

    async def get_current_usdc_balances(self):
        """Get current USDC balances across all wallet types"""
        try:
            print(f"💰 Checking current USDC balances for user {self.test_username}")
            
            async with self.session.get(f"{self.base_url}/wallet/{self.test_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        wallet_info = data.get("wallet", {})
                        
                        # Extract USDC balances from each wallet type
                        deposit_usdc = wallet_info.get("deposit_balance", {}).get("USDC", 0)
                        winnings_usdc = wallet_info.get("winnings_balance", {}).get("USDC", 0)
                        savings_usdc = wallet_info.get("savings_balance", {}).get("USDC", 0)
                        
                        total_usdc = deposit_usdc + winnings_usdc + savings_usdc
                        
                        current_balances = {
                            "deposit": deposit_usdc,
                            "winnings": winnings_usdc,
                            "savings": savings_usdc,
                            "total": total_usdc
                        }
                        
                        self.log_test("Current USDC Balance Check", True, 
                                    f"✅ Total USDC: {total_usdc:,.2f} (Deposit: {deposit_usdc:,.2f}, Winnings: {winnings_usdc:,.2f}, Savings: {savings_usdc:,.2f})", 
                                    current_balances)
                        
                        return current_balances
                    else:
                        self.log_test("Current USDC Balance Check", False, 
                                    f"❌ Wallet info failed: {data.get('message', 'Unknown error')}", data)
                        return None
                else:
                    error_text = await response.text()
                    self.log_test("Current USDC Balance Check", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            self.log_test("Current USDC Balance Check", False, f"❌ Exception: {str(e)}")
            return None

    async def test_internal_transfer_endpoint(self):
        """Test the new internal wallet transfer endpoint"""
        try:
            print(f"🔄 Testing internal wallet transfer endpoint with small amount")
            
            # Test with a small amount first (1 USDC)
            test_transfer_data = {
                "wallet_address": self.test_wallet,
                "from_wallet_type": "deposit",
                "to_wallet_type": "savings",
                "currency": "USDC",
                "amount": 1.0
            }
            
            async with self.session.post(f"{self.base_url}/wallet/transfer", 
                                       json=test_transfer_data) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        transfer_info = data.get("transfer", {})
                        self.log_test("Internal Transfer Endpoint Test", True, 
                                    f"✅ Transfer endpoint working: {data.get('message', '')}", data)
                        return True
                    else:
                        self.log_test("Internal Transfer Endpoint Test", False, 
                                    f"❌ Transfer failed: {data.get('message', 'Unknown error')}", data)
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Internal Transfer Endpoint Test", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Internal Transfer Endpoint Test", False, f"❌ Exception: {str(e)}")
            return False

    async def execute_usdc_redistribution(self, current_balances: Dict[str, float]):
        """Execute the USDC redistribution plan"""
        try:
            print(f"🚀 Executing USDC redistribution plan")
            
            current = current_balances
            target = self.target_distribution
            
            print(f"📊 Current vs Target Distribution:")
            print(f"  Savings: {current['savings']:,.2f} → {target['savings']:,.2f}")
            print(f"  Winnings: {current['winnings']:,.2f} → {target['winnings']:,.2f}")
            print(f"  Deposit: {current['deposit']:,.2f} → {target['deposit']:,.2f}")
            
            # Calculate transfers needed
            transfers = []
            
            # Transfer 1: Move USDC from deposit to savings to reach target
            savings_needed = target["savings"] - current["savings"]
            if savings_needed > 0:
                transfers.append({
                    "from": "deposit",
                    "to": "savings",
                    "amount": savings_needed,
                    "description": f"Transfer {savings_needed:,.2f} USDC from deposit to savings"
                })
            
            # Transfer 2: Move USDC from deposit to winnings to reach target
            winnings_needed = target["winnings"] - current["winnings"]
            if winnings_needed > 0:
                transfers.append({
                    "from": "deposit", 
                    "to": "winnings",
                    "amount": winnings_needed,
                    "description": f"Transfer {winnings_needed:,.2f} USDC from deposit to winnings"
                })
            
            print(f"\n🎯 Executing {len(transfers)} transfers:")
            
            successful_transfers = 0
            
            for i, transfer in enumerate(transfers, 1):
                print(f"\n📋 Transfer {i}/{len(transfers)}: {transfer['description']}")
                
                transfer_data = {
                    "wallet_address": self.test_wallet,
                    "from_wallet_type": transfer["from"],
                    "to_wallet_type": transfer["to"],
                    "currency": "USDC",
                    "amount": transfer["amount"]
                }
                
                async with self.session.post(f"{self.base_url}/wallet/transfer", 
                                           json=transfer_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            transfer_info = data.get("transfer", {})
                            transaction_id = transfer_info.get("transaction_id", "")
                            
                            self.log_test(f"Transfer {i} Execution", True, 
                                        f"✅ {transfer['description']} - Transaction: {transaction_id}", data)
                            successful_transfers += 1
                        else:
                            self.log_test(f"Transfer {i} Execution", False, 
                                        f"❌ Transfer failed: {data.get('message', 'Unknown error')}", data)
                    else:
                        error_text = await response.text()
                        self.log_test(f"Transfer {i} Execution", False, 
                                    f"❌ HTTP {response.status}: {error_text}")
            
            # Summary
            if successful_transfers == len(transfers):
                self.log_test("USDC Redistribution Execution", True, 
                            f"✅ All {successful_transfers}/{len(transfers)} transfers completed successfully")
                return True
            else:
                self.log_test("USDC Redistribution Execution", False, 
                            f"❌ Only {successful_transfers}/{len(transfers)} transfers completed")
                return False
                
        except Exception as e:
            self.log_test("USDC Redistribution Execution", False, f"❌ Exception: {str(e)}")
            return False

    async def verify_final_distribution(self):
        """Verify the final USDC distribution matches the target"""
        try:
            print(f"🔍 Verifying final USDC distribution")
            
            # Get updated balances
            final_balances = await self.get_current_usdc_balances()
            
            if not final_balances:
                self.log_test("Final Distribution Verification", False, "❌ Could not retrieve final balances")
                return False
            
            target = self.target_distribution
            
            # Check if each wallet type is close to target (allow 5% variance for testing)
            tolerance = 0.05  # 5%
            
            verification_results = {}
            
            for wallet_type in ["deposit", "winnings", "savings"]:
                current_amount = final_balances[wallet_type]
                target_amount = target[wallet_type]
                
                if target_amount > 0:
                    variance = abs(current_amount - target_amount) / target_amount
                    is_within_tolerance = variance <= tolerance
                else:
                    is_within_tolerance = current_amount == 0
                
                verification_results[wallet_type] = {
                    "current": current_amount,
                    "target": target_amount,
                    "variance_pct": variance * 100 if target_amount > 0 else 0,
                    "within_tolerance": is_within_tolerance
                }
            
            # Overall verification
            all_within_tolerance = all(result["within_tolerance"] for result in verification_results.values())
            
            if all_within_tolerance:
                self.log_test("Final Distribution Verification", True, 
                            f"✅ All wallet types within 5% of target distribution", verification_results)
            else:
                failed_wallets = [wallet for wallet, result in verification_results.items() if not result["within_tolerance"]]
                self.log_test("Final Distribution Verification", False, 
                            f"❌ Wallets outside tolerance: {failed_wallets}", verification_results)
            
            # Print detailed comparison
            print(f"\n📊 Final Distribution Comparison:")
            print(f"{'Wallet Type':<12} {'Current':<15} {'Target':<15} {'Variance':<10} {'Status'}")
            print("-" * 70)
            
            for wallet_type, result in verification_results.items():
                status = "✅ OK" if result["within_tolerance"] else "❌ OFF"
                print(f"{wallet_type.capitalize():<12} {result['current']:>14,.2f} {result['target']:>14,.2f} {result['variance_pct']:>8.1f}% {status}")
            
            return all_within_tolerance
            
        except Exception as e:
            self.log_test("Final Distribution Verification", False, f"❌ Exception: {str(e)}")
            return False

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("🎯 FOCUSED USDC REDISTRIBUTION TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["success"]])
        failed_tests = total_tests - passed_tests
        
        print(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed ({(passed_tests/total_tests*100):.1f}% success rate)")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        if passed_tests > 0:
            print(f"\n✅ PASSED TESTS ({passed_tests}):")
            for result in self.test_results:
                if result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        # Key findings
        print(f"\n🔍 KEY FINDINGS:")
        
        auth_success = any("auth" in r["test"].lower() and r["success"] for r in self.test_results)
        transfer_endpoint_working = any("endpoint" in r["test"].lower() and r["success"] for r in self.test_results)
        redistribution_success = any("redistribution" in r["test"].lower() and r["success"] for r in self.test_results)
        verification_success = any("verification" in r["test"].lower() and r["success"] for r in self.test_results)
        
        if auth_success and transfer_endpoint_working and redistribution_success and verification_success:
            print(f"   🎉 SUCCESS: Complete USDC redistribution achieved!")
        elif auth_success and transfer_endpoint_working and redistribution_success:
            print(f"   ✅ PARTIAL SUCCESS: Redistribution completed, verification needs review")
        elif auth_success and transfer_endpoint_working:
            print(f"   ⚠️ PROGRESS: Transfer system working, redistribution needs completion")
        else:
            print(f"   ❌ ISSUES: Core functionality needs attention")
        
        return passed_tests, total_tests

    async def run_focused_test(self):
        """Run focused USDC redistribution test"""
        print("🚀 STARTING FOCUSED USDC REDISTRIBUTION TEST")
        print(f"🎯 Target: Redistribute 7.9M USDC optimally across 3 wallet types")
        print(f"👤 User: {self.test_username} ({self.test_wallet})")
        print(f"📋 Distribution Plan:")
        print(f"   • Savings: {self.target_distribution['savings']:,.2f} USDC (46%)")
        print(f"   • Winnings: {self.target_distribution['winnings']:,.2f} USDC (34%)")
        print(f"   • Deposit: {self.target_distribution['deposit']:,.2f} USDC (20%)")
        print("="*80)
        
        try:
            # Step 1: Authenticate user
            auth_success = await self.authenticate_user()
            if not auth_success:
                print("❌ Cannot proceed without authentication")
                return 0, 1
            
            # Step 2: Get current USDC balances
            current_balances = await self.get_current_usdc_balances()
            if not current_balances:
                print("❌ Cannot proceed without balance information")
                return 0, 1
            
            # Step 3: Test internal transfer endpoint
            transfer_endpoint_working = await self.test_internal_transfer_endpoint()
            if not transfer_endpoint_working:
                print("❌ Cannot proceed without working transfer endpoint")
                return 0, 1
            
            # Step 4: Execute redistribution
            redistribution_success = await self.execute_usdc_redistribution(current_balances)
            
            # Step 5: Verify final distribution
            verification_success = await self.verify_final_distribution()
            
            # Print summary
            passed, total = self.print_summary()
            
            return passed, total
            
        except Exception as e:
            print(f"❌ Test execution failed: {str(e)}")
            return 0, 1

async def main():
    """Main test execution"""
    async with FocusedUSDCTester(BACKEND_URL) as tester:
        passed, total = await tester.run_focused_test()
        
        # Exit with appropriate code
        if passed == total:
            print(f"\n🎉 ALL TESTS PASSED! USDC redistribution completed successfully.")
            sys.exit(0)
        else:
            print(f"\n⚠️ {total - passed} tests failed. Review results above.")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())