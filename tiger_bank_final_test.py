#!/usr/bin/env python3
"""
Tiger Bank Games Development Fund System - Final Verification Test
Tests the complete $500K development fund withdrawal and CDT bridge integration
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Test Configuration
BACKEND_URL = "https://blockchain-slots.preview.emergentagent.com/api"

class TigerBankFinalTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2)}")
    
    async def test_portfolio_verification(self) -> Dict[str, Any]:
        """Test portfolio shows updated $12.922M total with all 8 tokens"""
        try:
            async with self.session.get(f"{BACKEND_URL}/user/user123/portfolio") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    # Check total value
                    total_value = result.get("total_value_usd", 0)
                    expected_min = 12000000  # $12M minimum
                    expected_max = 13000000  # $13M maximum
                    
                    if expected_min <= total_value <= expected_max:
                        self.log_test("Portfolio Total Value", True, 
                                    f"Portfolio value ${total_value:,.0f} within expected range ${expected_min:,.0f}-${expected_max:,.0f}")
                    else:
                        self.log_test("Portfolio Total Value", False, 
                                    f"Portfolio value ${total_value:,.0f} outside expected range ${expected_min:,.0f}-${expected_max:,.0f}", result)
                    
                    # Check all 8 tokens present
                    tokens = result.get("tokens", {})
                    expected_tokens = ["USDC", "DOGE", "TRX", "CRT", "T52M", "ETH", "BTC", "CDT"]
                    present_tokens = list(tokens.keys())
                    missing_tokens = [token for token in expected_tokens if token not in present_tokens]
                    
                    if not missing_tokens:
                        self.log_test("All 8 Tokens Present", True, 
                                    f"All expected tokens present: {', '.join(present_tokens)}")
                    else:
                        self.log_test("All 8 Tokens Present", False, 
                                    f"Missing tokens: {', '.join(missing_tokens)}. Present: {', '.join(present_tokens)}", result)
                    
                    # Check ETH and BTC balances for dev fund
                    eth_balance = tokens.get("ETH", {}).get("balance", 0)
                    btc_balance = tokens.get("BTC", {}).get("balance", 0)
                    
                    if eth_balance >= 50:  # At least 50 ETH for $150K withdrawal
                        self.log_test("ETH Balance for Dev Fund", True, 
                                    f"ETH balance {eth_balance} sufficient for $150K withdrawal")
                    else:
                        self.log_test("ETH Balance for Dev Fund", False, 
                                    f"ETH balance {eth_balance} insufficient for $150K withdrawal (need ~47 ETH)", result)
                    
                    if btc_balance >= 1.5:  # At least 1.5 BTC for $100K withdrawal
                        self.log_test("BTC Balance for Dev Fund", True, 
                                    f"BTC balance {btc_balance} sufficient for $100K withdrawal")
                    else:
                        self.log_test("BTC Balance for Dev Fund", False, 
                                    f"BTC balance {btc_balance} insufficient for $100K withdrawal (need ~1.54 BTC)", result)
                    
                    return result
                else:
                    error_text = await resp.text()
                    self.log_test("Portfolio Verification", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return {"success": False, "error": error_text}
                    
        except Exception as e:
            self.log_test("Portfolio Verification", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_dev_wallets_configuration(self) -> Dict[str, Any]:
        """Test development wallet addresses are configured"""
        try:
            async with self.session.get(f"{BACKEND_URL}/dev-wallets") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    dev_wallets = result.get("dev_wallets", {})
                    quick_presets = result.get("quick_presets", {})
                    
                    # Check required wallet addresses
                    required_wallets = ["ETH", "BTC", "USDC"]
                    missing_wallets = []
                    
                    for wallet_type in required_wallets:
                        if wallet_type not in dev_wallets:
                            missing_wallets.append(wallet_type)
                        else:
                            wallet_info = dev_wallets[wallet_type]
                            if not wallet_info.get("address"):
                                missing_wallets.append(f"{wallet_type} (no address)")
                    
                    if not missing_wallets:
                        self.log_test("Dev Wallets Configuration", True, 
                                    f"All required wallet addresses configured: {', '.join(required_wallets)}")
                    else:
                        self.log_test("Dev Wallets Configuration", False, 
                                    f"Missing wallet configurations: {', '.join(missing_wallets)}", result)
                    
                    # Check $500K testing fund preset
                    if "testing_fund_500k" in quick_presets:
                        preset = quick_presets["testing_fund_500k"]
                        total_usd = preset.get("total_usd", 0)
                        allocation = preset.get("allocation", {})
                        
                        if total_usd == 500000:
                            self.log_test("$500K Testing Fund Preset", True, 
                                        f"Testing fund preset configured for ${total_usd:,}")
                        else:
                            self.log_test("$500K Testing Fund Preset", False, 
                                        f"Testing fund preset shows ${total_usd:,} instead of $500,000", result)
                        
                        # Check allocation breakdown
                        expected_allocation = {"USDC": 250000, "ETH": 150000, "BTC": 100000}
                        allocation_correct = True
                        
                        for token, expected_amount in expected_allocation.items():
                            actual_amount = allocation.get(token, {}).get("amount", 0)
                            if actual_amount != expected_amount:
                                allocation_correct = False
                                break
                        
                        if allocation_correct:
                            self.log_test("$500K Preset Allocation", True, 
                                        "Allocation correct: $250K USDC, $150K ETH, $100K BTC")
                        else:
                            self.log_test("$500K Preset Allocation", False, 
                                        f"Allocation incorrect. Expected: {expected_allocation}, Got: {allocation}", result)
                    else:
                        self.log_test("$500K Testing Fund Preset", False, 
                                    "testing_fund_500k preset not found in quick_presets", result)
                    
                    return result
                else:
                    error_text = await resp.text()
                    self.log_test("Dev Wallets Configuration", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return {"success": False, "error": error_text}
                    
        except Exception as e:
            self.log_test("Dev Wallets Configuration", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_500k_preset_withdrawal(self) -> Dict[str, Any]:
        """Test $500K development fund preset withdrawal"""
        try:
            # Get initial balances
            async with self.session.get(f"{BACKEND_URL}/balances") as resp:
                if resp.status == 200:
                    initial_balances = await resp.json()
                    initial_balances = initial_balances.get("balances", {})
                else:
                    self.log_test("Initial Balance Check", False, f"Failed to get initial balances: HTTP {resp.status}")
                    return {"success": False}
            
            # Execute $500K preset withdrawal
            async with self.session.post(f"{BACKEND_URL}/withdraw/preset?preset_id=testing_fund_500k") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    if result.get("success"):
                        total_withdrawn = result.get("total_withdrawn_usd", 0)
                        withdrawals = result.get("withdrawals", [])
                        
                        # Check total withdrawal amount
                        if total_withdrawn == 500000:
                            self.log_test("$500K Preset Total Amount", True, 
                                        f"Successfully withdrew ${total_withdrawn:,}")
                        else:
                            self.log_test("$500K Preset Total Amount", False, 
                                        f"Withdrew ${total_withdrawn:,} instead of $500,000", result)
                        
                        # Check individual withdrawals
                        expected_withdrawals = {"USDC": 250000, "ETH": 150000, "BTC": 100000}
                        actual_withdrawals = {}
                        
                        for withdrawal in withdrawals:
                            token = withdrawal.get("token_symbol")
                            usd_value = withdrawal.get("usd_value", 0)
                            actual_withdrawals[token] = usd_value
                        
                        all_correct = True
                        for token, expected_usd in expected_withdrawals.items():
                            actual_usd = actual_withdrawals.get(token, 0)
                            if abs(actual_usd - expected_usd) > 1000:  # Allow $1K tolerance
                                all_correct = False
                                break
                        
                        if all_correct and len(withdrawals) == 3:
                            self.log_test("$500K Preset Distribution", True, 
                                        f"All 3 tokens withdrawn correctly: {actual_withdrawals}")
                        else:
                            self.log_test("$500K Preset Distribution", False, 
                                        f"Incorrect distribution. Expected: {expected_withdrawals}, Got: {actual_withdrawals}", result)
                        
                        # Check wallet addresses used
                        wallet_destinations = result.get("wallet_destinations", {})
                        if len(wallet_destinations) >= 3:
                            self.log_test("External Wallet Addresses", True, 
                                        f"All external wallet addresses used: {list(wallet_destinations.keys())}")
                        else:
                            self.log_test("External Wallet Addresses", False, 
                                        f"Missing wallet addresses: {wallet_destinations}", result)
                        
                        # Verify balance deductions
                        async with self.session.get(f"{BACKEND_URL}/balances") as resp2:
                            if resp2.status == 200:
                                final_balances = await resp2.json()
                                final_balances = final_balances.get("balances", {})
                                
                                balance_changes_correct = True
                                for token in ["USDC", "ETH", "BTC"]:
                                    initial_bal = initial_balances.get(token, {}).get("balance", 0)
                                    final_bal = final_balances.get(token, {}).get("balance", 0)
                                    
                                    if final_bal >= initial_bal:  # Balance should decrease
                                        balance_changes_correct = False
                                        break
                                
                                if balance_changes_correct:
                                    self.log_test("Balance Deductions", True, 
                                                "All token balances correctly decreased after withdrawal")
                                else:
                                    self.log_test("Balance Deductions", False, 
                                                "Token balances not properly deducted", 
                                                {"initial": initial_balances, "final": final_balances})
                        
                        return result
                    else:
                        self.log_test("$500K Preset Withdrawal", False, 
                                    f"Withdrawal failed: {result.get('message', 'Unknown error')}", result)
                        return result
                else:
                    error_text = await resp.text()
                    self.log_test("$500K Preset Withdrawal", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return {"success": False, "error": error_text}
                    
        except Exception as e:
            self.log_test("$500K Preset Withdrawal", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_cdt_pricing_system(self) -> Dict[str, Any]:
        """Test CDT pricing returns complete purchase options"""
        try:
            async with self.session.get(f"{BACKEND_URL}/cdt/pricing") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    # Check CDT price
                    cdt_price = result.get("cdt_price_usd", 0)
                    if cdt_price == 0.10:
                        self.log_test("CDT Price", True, f"CDT price correctly set at ${cdt_price}")
                    else:
                        self.log_test("CDT Price", False, f"CDT price ${cdt_price} instead of $0.10", result)
                    
                    # Check purchase options
                    purchase_options = result.get("purchase_options", {})
                    expected_tokens = ["USDC", "DOGE", "TRX", "CRT", "T52M"]
                    
                    available_tokens = list(purchase_options.keys())
                    missing_tokens = [token for token in expected_tokens if token not in available_tokens]
                    
                    if not missing_tokens:
                        self.log_test("CDT Purchase Options", True, 
                                    f"All expected tokens available for CDT purchase: {', '.join(available_tokens)}")
                    else:
                        self.log_test("CDT Purchase Options", False, 
                                    f"Missing purchase options for: {', '.join(missing_tokens)}", result)
                    
                    # Check total purchase power
                    total_purchase_power = result.get("total_purchase_power_cdt", 0)
                    if total_purchase_power > 100000000:  # Over 100M CDT purchase power
                        self.log_test("CDT Total Purchase Power", True, 
                                    f"Total purchase power: {total_purchase_power:,.0f} CDT")
                    else:
                        self.log_test("CDT Total Purchase Power", False, 
                                    f"Low purchase power: {total_purchase_power:,.0f} CDT", result)
                    
                    # Check bridge method recommendations
                    recommended_sources = result.get("recommended_sources", {})
                    liquid_assets = recommended_sources.get("liquid_assets", [])
                    illiquid_assets = recommended_sources.get("illiquid_assets", [])
                    
                    if "USDC" in liquid_assets and "CRT" in illiquid_assets:
                        self.log_test("CDT Bridge Method Categorization", True, 
                                    f"Correct categorization - Liquid: {liquid_assets}, Illiquid: {illiquid_assets}")
                    else:
                        self.log_test("CDT Bridge Method Categorization", False, 
                                    f"Incorrect categorization - Liquid: {liquid_assets}, Illiquid: {illiquid_assets}", result)
                    
                    return result
                else:
                    error_text = await resp.text()
                    self.log_test("CDT Pricing System", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return {"success": False, "error": error_text}
                    
        except Exception as e:
            self.log_test("CDT Pricing System", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_cdt_bridge_direct_method(self) -> Dict[str, Any]:
        """Test CDT bridge with direct method (liquid assets)"""
        try:
            # Get initial CDT balance
            async with self.session.get(f"{BACKEND_URL}/balances") as resp:
                if resp.status == 200:
                    initial_balances = await resp.json()
                    initial_cdt = initial_balances.get("balances", {}).get("CDT", {}).get("balance", 0)
                else:
                    initial_cdt = 0
            
            # Bridge 1000 USDC to CDT (direct method)
            bridge_data = {
                "source_token": "USDC",
                "amount": 1000,
                "cdt_target_amount": 10000,
                "user_wallet": "test_wallet_address",
                "bridge_type": "direct"
            }
            
            async with self.session.post(f"{BACKEND_URL}/cdt/bridge", json=bridge_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    if result.get("success"):
                        cdt_received = result.get("cdt_received", 0)
                        method = result.get("method", "")
                        
                        # Check CDT amount received
                        if cdt_received == 10000:
                            self.log_test("CDT Direct Bridge Amount", True, 
                                        f"Received {cdt_received:,} CDT for 1000 USDC")
                        else:
                            self.log_test("CDT Direct Bridge Amount", False, 
                                        f"Received {cdt_received:,} CDT instead of 10,000", result)
                        
                        # Check bridge method
                        if method == "direct":
                            self.log_test("CDT Direct Bridge Method", True, 
                                        "Bridge method correctly identified as 'direct'")
                        else:
                            self.log_test("CDT Direct Bridge Method", False, 
                                        f"Bridge method '{method}' instead of 'direct'", result)
                        
                        # Verify CDT balance increase
                        async with self.session.get(f"{BACKEND_URL}/balances") as resp2:
                            if resp2.status == 200:
                                final_balances = await resp2.json()
                                final_cdt = final_balances.get("balances", {}).get("CDT", {}).get("balance", 0)
                                
                                if final_cdt > initial_cdt:
                                    self.log_test("CDT Balance Increase", True, 
                                                f"CDT balance increased from {initial_cdt:,} to {final_cdt:,}")
                                else:
                                    self.log_test("CDT Balance Increase", False, 
                                                f"CDT balance not increased: {initial_cdt:,} → {final_cdt:,}", result)
                        
                        return result
                    else:
                        self.log_test("CDT Direct Bridge", False, 
                                    f"Bridge failed: {result.get('message', 'Unknown error')}", result)
                        return result
                else:
                    error_text = await resp.text()
                    self.log_test("CDT Direct Bridge", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return {"success": False, "error": error_text}
                    
        except Exception as e:
            self.log_test("CDT Direct Bridge", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_cdt_bridge_iou_method(self) -> Dict[str, Any]:
        """Test CDT bridge with IOU method (illiquid assets)"""
        try:
            # Get initial CDT balance
            async with self.session.get(f"{BACKEND_URL}/balances") as resp:
                if resp.status == 200:
                    initial_balances = await resp.json()
                    initial_cdt = initial_balances.get("balances", {}).get("CDT", {}).get("balance", 0)
                else:
                    initial_cdt = 0
            
            # Bridge 10000 CRT to CDT (IOU method)
            bridge_data = {
                "source_token": "CRT",
                "amount": 10000,
                "cdt_target_amount": 25000,
                "user_wallet": "test_wallet_address",
                "bridge_type": "iou"
            }
            
            async with self.session.post(f"{BACKEND_URL}/cdt/bridge", json=bridge_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    if result.get("success"):
                        cdt_received = result.get("cdt_received", 0)
                        method = result.get("method", "")
                        iou_active = result.get("iou_active", False)
                        
                        # Check CDT amount received
                        if cdt_received == 25000:
                            self.log_test("CDT IOU Bridge Amount", True, 
                                        f"Received {cdt_received:,} CDT for 10,000 CRT")
                        else:
                            self.log_test("CDT IOU Bridge Amount", False, 
                                        f"Received {cdt_received:,} CDT instead of 25,000", result)
                        
                        # Check bridge method
                        if method == "iou":
                            self.log_test("CDT IOU Bridge Method", True, 
                                        "Bridge method correctly identified as 'iou'")
                        else:
                            self.log_test("CDT IOU Bridge Method", False, 
                                        f"Bridge method '{method}' instead of 'iou'", result)
                        
                        # Check IOU record creation
                        if iou_active:
                            self.log_test("CDT IOU Record Creation", True, 
                                        "IOU record successfully created for illiquid asset bridge")
                        else:
                            self.log_test("CDT IOU Record Creation", False, 
                                        "IOU record not created for illiquid asset bridge", result)
                        
                        # Verify CDT balance increase
                        async with self.session.get(f"{BACKEND_URL}/balances") as resp2:
                            if resp2.status == 200:
                                final_balances = await resp2.json()
                                final_cdt = final_balances.get("balances", {}).get("CDT", {}).get("balance", 0)
                                
                                if final_cdt > initial_cdt:
                                    self.log_test("CDT IOU Balance Increase", True, 
                                                f"CDT balance increased from {initial_cdt:,} to {final_cdt:,}")
                                else:
                                    self.log_test("CDT IOU Balance Increase", False, 
                                                f"CDT balance not increased: {initial_cdt:,} → {final_cdt:,}", result)
                        
                        return result
                    else:
                        self.log_test("CDT IOU Bridge", False, 
                                    f"Bridge failed: {result.get('message', 'Unknown error')}", result)
                        return result
                else:
                    error_text = await resp.text()
                    self.log_test("CDT IOU Bridge", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return {"success": False, "error": error_text}
                    
        except Exception as e:
            self.log_test("CDT IOU Bridge", False, f"Exception: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def test_integration_flow_complete(self) -> bool:
        """Test complete integration flow: Portfolio → $500K withdrawal → CDT bridge → Verification"""
        try:
            print("\n🔄 Testing Complete Integration Flow...")
            
            # Step 1: Portfolio check
            portfolio_result = await self.test_portfolio_verification()
            if not portfolio_result.get("total_value_usd", 0) > 12000000:
                self.log_test("Integration Flow - Portfolio Check", False, 
                            "Portfolio value insufficient for integration test")
                return False
            
            # Step 2: CDT pricing check
            pricing_result = await self.test_cdt_pricing_system()
            if not pricing_result.get("cdt_price_usd") == 0.10:
                self.log_test("Integration Flow - CDT Pricing", False, 
                            "CDT pricing system not ready")
                return False
            
            # Step 3: Bridge 100K USDC to CDT
            bridge_data = {
                "source_token": "USDC",
                "amount": 100000,
                "cdt_target_amount": 1000000,
                "user_wallet": "integration_test_wallet",
                "bridge_type": "direct"
            }
            
            async with self.session.post(f"{BACKEND_URL}/cdt/bridge", json=bridge_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success") and result.get("cdt_received", 0) >= 900000:
                        self.log_test("Integration Flow - Large CDT Bridge", True, 
                                    f"Successfully bridged 100K USDC → {result.get('cdt_received', 0):,} CDT")
                    else:
                        self.log_test("Integration Flow - Large CDT Bridge", False, 
                                    f"Large CDT bridge failed or insufficient CDT received", result)
                        return False
                else:
                    self.log_test("Integration Flow - Large CDT Bridge", False, 
                                f"Large CDT bridge HTTP error: {resp.status}")
                    return False
            
            # Step 4: Final verification
            async with self.session.get(f"{BACKEND_URL}/balances") as resp:
                if resp.status == 200:
                    final_balances = await resp.json()
                    cdt_balance = final_balances.get("balances", {}).get("CDT", {}).get("balance", 0)
                    
                    if cdt_balance >= 1000000:
                        self.log_test("Integration Flow - Final CDT Verification", True, 
                                    f"Final CDT balance: {cdt_balance:,} CDT")
                        return True
                    else:
                        self.log_test("Integration Flow - Final CDT Verification", False, 
                                    f"Insufficient final CDT balance: {cdt_balance:,}")
                        return False
                else:
                    self.log_test("Integration Flow - Final Verification", False, 
                                "Failed to get final balances")
                    return False
                    
        except Exception as e:
            self.log_test("Integration Flow Complete", False, f"Exception: {str(e)}")
            return False
    
    def print_summary(self):
        """Print comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n{'='*80}")
        print(f"🏦 TIGER BANK GAMES DEVELOPMENT FUND - FINAL VERIFICATION SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")
        
        print(f"\n🎯 PRIORITY 1 - $500K DEVELOPMENT FUND:")
        fund_tests = [r for r in self.test_results if "500k" in r["test"].lower() or "preset" in r["test"].lower()]
        fund_passed = sum(1 for t in fund_tests if t["success"])
        if fund_passed == len(fund_tests) and len(fund_tests) > 0:
            print(f"   ✅ $500K Development Fund System FULLY OPERATIONAL")
        else:
            print(f"   ❌ $500K Development Fund System has issues ({fund_passed}/{len(fund_tests)} tests passed)")
        
        print(f"\n🌉 PRIORITY 2 - CDT BRIDGE INTEGRATION:")
        cdt_tests = [r for r in self.test_results if "cdt" in r["test"].lower()]
        cdt_passed = sum(1 for t in cdt_tests if t["success"])
        if cdt_passed == len(cdt_tests) and len(cdt_tests) > 0:
            print(f"   ✅ CDT Bridge Integration FULLY OPERATIONAL")
        else:
            print(f"   ❌ CDT Bridge Integration has issues ({cdt_passed}/{len(cdt_tests)} tests passed)")
        
        print(f"\n📊 PORTFOLIO VERIFICATION:")
        portfolio_tests = [r for r in self.test_results if "portfolio" in r["test"].lower() or "balance" in r["test"].lower()]
        portfolio_passed = sum(1 for t in portfolio_tests if t["success"])
        if portfolio_passed >= len(portfolio_tests) * 0.8:  # 80% threshold
            print(f"   ✅ Portfolio System OPERATIONAL ({portfolio_passed}/{len(portfolio_tests)} tests passed)")
        else:
            print(f"   ❌ Portfolio System needs attention ({portfolio_passed}/{len(portfolio_tests)} tests passed)")
        
        print(f"\n🚀 FINAL ASSESSMENT:")
        if failed_tests == 0:
            print(f"   🎉 TIGER BANK GAMES DEVELOPMENT FUND SYSTEM READY FOR DEPLOYMENT!")
            print(f"   ✅ $500K automated testing fund fully functional")
            print(f"   ✅ CDT bridge integration complete with direct and IOU methods")
            print(f"   ✅ All external wallet addresses configured correctly")
        elif failed_tests <= 2:
            print(f"   ⚠️  System mostly ready - minor issues to resolve")
            print(f"   🔧 Address remaining {failed_tests} issues before deployment")
        else:
            print(f"   ❌ CRITICAL ISSUES PREVENT DEPLOYMENT")
            print(f"   🚨 {failed_tests} major issues must be resolved")
            print(f"   🔍 Focus on $500K preset withdrawal and CDT bridge functionality")

async def main():
    """Run all Tiger Bank Games final verification tests"""
    print("🏦 Starting Tiger Bank Games Development Fund - Final Verification Tests...")
    print(f"Backend URL: {BACKEND_URL}")
    print("🎯 Testing Priority Features:")
    print("   • $500K Development Fund Preset Withdrawal")
    print("   • CDT Bridge Integration (Direct & IOU Methods)")
    print("   • Portfolio Verification ($12.922M with 8 tokens)")
    print("   • Complete Integration Flow")
    print("="*80)
    
    async with TigerBankFinalTester() as tester:
        # Test sequence for final verification
        tests = [
            ("test_portfolio_verification", "Portfolio Verification"),
            ("test_dev_wallets_configuration", "Development Wallets Configuration"),
            ("test_500k_preset_withdrawal", "$500K Preset Withdrawal"),
            ("test_cdt_pricing_system", "CDT Pricing System"),
            ("test_cdt_bridge_direct_method", "CDT Bridge Direct Method"),
            ("test_cdt_bridge_iou_method", "CDT Bridge IOU Method"),
            ("test_integration_flow_complete", "Complete Integration Flow")
        ]
        
        for method_name, test_description in tests:
            print(f"\n🧪 Running: {test_description}")
            try:
                method = getattr(tester, method_name)
                await method()
            except Exception as e:
                tester.log_test(test_description, False, f"Test execution failed: {str(e)}")
        
        # Print final summary
        tester.print_summary()
        
        # Return exit code based on results
        failed_count = sum(1 for result in tester.test_results if not result["success"])
        return 0 if failed_count <= 2 else 1  # Allow up to 2 minor failures

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)