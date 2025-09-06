#!/usr/bin/env python3
"""
Tiger Bank Games Development Fund Withdrawal System & CDT Bridge Integration Testing
Tests the complete system as requested in the review: $500K testing fund and CDT bridge functionality
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Test Configuration
BACKEND_URL = "https://blockchain-slots.preview.emergentagent.com/api"

class TigerBankDevFundTester:
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
    
    # PHASE 1 - Development Fund Withdrawals Testing
    
    async def test_500k_testing_fund_preset(self) -> bool:
        """Test $500K testing fund preset endpoint"""
        try:
            async with self.session.post(f"{BACKEND_URL}/withdraw/preset?preset_id=testing_fund_500k") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success"):
                        # Verify the preset details
                        preset_name = result.get("preset_name", "")
                        total_withdrawn = result.get("total_withdrawn_usd", 0)
                        withdrawals = result.get("withdrawals", [])
                        
                        # Check if it's the correct $500K preset
                        if total_withdrawn == 500000 and "Testing Fund" in preset_name:
                            # Verify allocation: $250k USDC, $150k ETH, $100k BTC
                            usdc_found = eth_found = btc_found = False
                            
                            for withdrawal in withdrawals:
                                token = withdrawal.get("token_symbol", "")
                                usd_value = withdrawal.get("usd_value", 0)
                                
                                if token == "USDC" and usd_value == 250000:
                                    usdc_found = True
                                elif token == "ETH" and usd_value == 150000:
                                    eth_found = True
                                elif token == "BTC" and usd_value == 100000:
                                    btc_found = True
                            
                            if usdc_found and eth_found and btc_found:
                                self.log_test("$500K Testing Fund Preset", True, 
                                            f"✅ SUCCESS: Preset executed correctly - $250k USDC, $150k ETH, $100k BTC allocated to external addresses", result)
                                return True
                            else:
                                self.log_test("$500K Testing Fund Preset", False, 
                                            f"❌ ALLOCATION ERROR: Expected $250k USDC, $150k ETH, $100k BTC but got different allocation", result)
                                return False
                        else:
                            self.log_test("$500K Testing Fund Preset", False, 
                                        f"❌ AMOUNT ERROR: Expected $500K testing fund but got ${total_withdrawn:,}", result)
                            return False
                    else:
                        self.log_test("$500K Testing Fund Preset", False, 
                                    f"❌ PRESET FAILED: {result.get('message', 'Unknown error')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("$500K Testing Fund Preset", False, 
                                f"❌ HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("$500K Testing Fund Preset", False, f"❌ Exception: {str(e)}")
            return False
    
    async def test_dev_wallets_endpoint(self) -> bool:
        """Test /api/dev-wallets endpoint returns configured addresses"""
        try:
            async with self.session.get(f"{BACKEND_URL}/dev-wallets") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    dev_wallets = result.get("dev_wallets", {})
                    quick_presets = result.get("quick_presets", {})
                    
                    # Verify required wallet addresses are present
                    required_wallets = ["ETH", "BTC", "USDC"]
                    missing_wallets = []
                    
                    for wallet_type in required_wallets:
                        if wallet_type not in dev_wallets:
                            missing_wallets.append(wallet_type)
                        else:
                            wallet_info = dev_wallets[wallet_type]
                            if not wallet_info.get("address") or not wallet_info.get("network"):
                                missing_wallets.append(f"{wallet_type} (incomplete)")
                    
                    # Verify testing_fund_500k preset exists
                    if "testing_fund_500k" not in quick_presets:
                        missing_wallets.append("testing_fund_500k preset")
                    
                    if not missing_wallets:
                        self.log_test("Dev Wallets Configuration", True, 
                                    f"✅ SUCCESS: All required wallet addresses configured (ETH, BTC, USDC) and $500K preset available", result)
                        return True
                    else:
                        self.log_test("Dev Wallets Configuration", False, 
                                    f"❌ MISSING: {', '.join(missing_wallets)}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("Dev Wallets Configuration", False, 
                                f"❌ HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Dev Wallets Configuration", False, f"❌ Exception: {str(e)}")
            return False
    
    async def test_portfolio_balance_verification(self) -> bool:
        """Test portfolio shows expected $12.277M total value"""
        try:
            async with self.session.get(f"{BACKEND_URL}/user/user123/portfolio") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    total_value = result.get("total_value_usd", 0)
                    tokens = result.get("tokens", {})
                    
                    # Expected values from review request
                    expected_total = 12277000  # $12.277M
                    expected_tokens = {
                        "USDC": 319000,    # 319K USDC
                        "DOGE": 13000000,  # 13M DOGE  
                        "TRX": 3900000,    # 3.9M TRX
                        "CRT": 21000000,   # 21M CRT
                        "T52M": 52000000   # 52M T52M
                    }
                    
                    # Check total value (allow 5% variance)
                    value_diff = abs(total_value - expected_total)
                    value_variance = (value_diff / expected_total) * 100
                    
                    if value_variance <= 5:
                        # Check individual token balances
                        balance_issues = []
                        for token, expected_balance in expected_tokens.items():
                            if token in tokens:
                                actual_balance = tokens[token].get("balance", 0)
                                balance_diff = abs(actual_balance - expected_balance)
                                balance_variance = (balance_diff / expected_balance) * 100 if expected_balance > 0 else 100
                                
                                if balance_variance > 10:  # Allow 10% variance for individual tokens
                                    balance_issues.append(f"{token}: expected {expected_balance:,}, got {actual_balance:,}")
                            else:
                                balance_issues.append(f"{token}: missing from portfolio")
                        
                        if not balance_issues:
                            self.log_test("Portfolio Balance Verification", True, 
                                        f"✅ SUCCESS: Portfolio shows ${total_value:,.0f} total value with correct token distribution", result)
                            return True
                        else:
                            self.log_test("Portfolio Balance Verification", False, 
                                        f"❌ BALANCE ISSUES: {'; '.join(balance_issues)}", result)
                            return False
                    else:
                        self.log_test("Portfolio Balance Verification", False, 
                                    f"❌ VALUE MISMATCH: Expected $12.277M but got ${total_value:,.0f} ({value_variance:.1f}% variance)", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("Portfolio Balance Verification", False, 
                                f"❌ HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Portfolio Balance Verification", False, f"❌ Exception: {str(e)}")
            return False
    
    # PHASE 2 - CDT Bridge Integration Testing
    
    async def test_cdt_pricing_endpoint(self) -> bool:
        """Test /api/cdt/pricing endpoint for CDT purchase options"""
        try:
            async with self.session.get(f"{BACKEND_URL}/cdt/pricing") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    # Verify required fields
                    required_fields = ["cdt_price_usd", "purchase_options", "total_purchase_power_cdt"]
                    missing_fields = [field for field in required_fields if field not in result]
                    
                    if not missing_fields:
                        cdt_price = result.get("cdt_price_usd", 0)
                        purchase_options = result.get("purchase_options", {})
                        total_power = result.get("total_purchase_power_cdt", 0)
                        
                        # Verify purchase options include expected tokens
                        expected_tokens = ["USDC", "DOGE", "TRX", "CRT", "T52M"]
                        available_tokens = list(purchase_options.keys())
                        missing_tokens = [token for token in expected_tokens if token not in available_tokens]
                        
                        if not missing_tokens and cdt_price > 0 and total_power > 0:
                            self.log_test("CDT Pricing System", True, 
                                        f"✅ SUCCESS: CDT pricing at ${cdt_price}, {len(available_tokens)} tokens available, ${total_power:,.0f} total purchase power", result)
                            return True
                        else:
                            issues = []
                            if missing_tokens:
                                issues.append(f"Missing tokens: {missing_tokens}")
                            if cdt_price <= 0:
                                issues.append("Invalid CDT price")
                            if total_power <= 0:
                                issues.append("No purchase power")
                            
                            self.log_test("CDT Pricing System", False, 
                                        f"❌ ISSUES: {'; '.join(issues)}", result)
                            return False
                    else:
                        self.log_test("CDT Pricing System", False, 
                                    f"❌ MISSING FIELDS: {missing_fields}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("CDT Pricing System", False, 
                                f"❌ HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("CDT Pricing System", False, f"❌ Exception: {str(e)}")
            return False
    
    async def test_cdt_bridge_direct_method(self) -> bool:
        """Test /api/cdt/bridge endpoint with direct bridge method (liquid assets)"""
        try:
            # Test direct bridge with USDC (liquid asset)
            bridge_data = {
                "source_token": "USDC",
                "amount": 1000,  # 1000 USDC
                "cdt_target_amount": 10000,  # Should get 10000 CDT at $0.10 each
                "user_wallet": "test_wallet_address",
                "bridge_type": "direct"
            }
            
            async with self.session.post(f"{BACKEND_URL}/cdt/bridge", json=bridge_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    if result.get("success"):
                        bridge_id = result.get("bridge_id")
                        method = result.get("method")
                        cdt_received = result.get("cdt_received", 0)
                        
                        # Verify direct bridge worked correctly
                        if method == "direct" and cdt_received > 0 and bridge_id:
                            self.log_test("CDT Bridge Direct Method", True, 
                                        f"✅ SUCCESS: Direct bridge completed - {cdt_received:,.0f} CDT received for 1000 USDC", result)
                            return True
                        else:
                            self.log_test("CDT Bridge Direct Method", False, 
                                        f"❌ BRIDGE ERROR: Expected direct method with CDT received, got method={method}, cdt={cdt_received}", result)
                            return False
                    else:
                        self.log_test("CDT Bridge Direct Method", False, 
                                    f"❌ BRIDGE FAILED: {result.get('message', 'Unknown error')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("CDT Bridge Direct Method", False, 
                                f"❌ HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("CDT Bridge Direct Method", False, f"❌ Exception: {str(e)}")
            return False
    
    async def test_cdt_bridge_iou_method(self) -> bool:
        """Test /api/cdt/bridge endpoint with IOU bridge method (illiquid assets)"""
        try:
            # Test IOU bridge with CRT (illiquid asset)
            bridge_data = {
                "source_token": "CRT",
                "amount": 10000,  # 10000 CRT
                "cdt_target_amount": 25000,  # Should get 25000 CDT (CRT at $0.25 each)
                "user_wallet": "test_wallet_address",
                "bridge_type": "iou"
            }
            
            async with self.session.post(f"{BACKEND_URL}/cdt/bridge", json=bridge_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    if result.get("success"):
                        bridge_id = result.get("bridge_id")
                        method = result.get("method")
                        cdt_received = result.get("cdt_received", 0)
                        iou_active = result.get("iou_active", False)
                        
                        # Verify IOU bridge worked correctly
                        if method == "iou" and cdt_received > 0 and iou_active and bridge_id:
                            self.log_test("CDT Bridge IOU Method", True, 
                                        f"✅ SUCCESS: IOU bridge completed - {cdt_received:,.0f} CDT received for 10000 CRT with IOU record created", result)
                            return True
                        else:
                            self.log_test("CDT Bridge IOU Method", False, 
                                        f"❌ IOU ERROR: Expected IOU method with CDT and IOU record, got method={method}, cdt={cdt_received}, iou={iou_active}", result)
                            return False
                    else:
                        self.log_test("CDT Bridge IOU Method", False, 
                                    f"❌ IOU BRIDGE FAILED: {result.get('message', 'Unknown error')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("CDT Bridge IOU Method", False, 
                                f"❌ HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("CDT Bridge IOU Method", False, f"❌ Exception: {str(e)}")
            return False
    
    async def test_tokens_summary_categorization(self) -> bool:
        """Test /api/tokens/summary categorizes tokens correctly by source"""
        try:
            async with self.session.get(f"{BACKEND_URL}/tokens/summary") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    # Verify required categories
                    required_categories = ["converted_portfolio", "current_holdings", "purchase_targets"]
                    missing_categories = [cat for cat in required_categories if cat not in result]
                    
                    if not missing_categories:
                        converted = result.get("converted_portfolio", {})
                        current = result.get("current_holdings", {})
                        targets = result.get("purchase_targets", {})
                        
                        # Verify token categorization
                        converted_tokens = converted.get("tokens", {})
                        current_tokens = current.get("tokens", {})
                        target_tokens = targets.get("tokens", {})
                        
                        # Expected categorization
                        expected_converted = ["USDC", "DOGE", "TRX", "CRT"]  # converted_from_previous_portfolio
                        expected_current = ["T52M"]  # current_holding
                        expected_targets = ["CDT"]  # target_purchase
                        
                        categorization_issues = []
                        
                        # Check converted tokens
                        for token in expected_converted:
                            if token not in converted_tokens:
                                categorization_issues.append(f"{token} not in converted_portfolio")
                        
                        # Check current holdings
                        for token in expected_current:
                            if token not in current_tokens:
                                categorization_issues.append(f"{token} not in current_holdings")
                        
                        # Check targets
                        for token in expected_targets:
                            if token not in target_tokens:
                                categorization_issues.append(f"{token} not in purchase_targets")
                        
                        if not categorization_issues:
                            total_value = result.get("grand_total_usd", 0)
                            self.log_test("Token Summary Categorization", True, 
                                        f"✅ SUCCESS: Tokens correctly categorized by source - ${total_value:,.0f} total value", result)
                            return True
                        else:
                            self.log_test("Token Summary Categorization", False, 
                                        f"❌ CATEGORIZATION ISSUES: {'; '.join(categorization_issues)}", result)
                            return False
                    else:
                        self.log_test("Token Summary Categorization", False, 
                                    f"❌ MISSING CATEGORIES: {missing_categories}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("Token Summary Categorization", False, 
                                f"❌ HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Token Summary Categorization", False, f"❌ Exception: {str(e)}")
            return False
    
    # Integration Testing
    
    async def test_full_dev_fund_flow(self) -> bool:
        """Test full flow: Check portfolio → Execute $500K dev fund → Verify balance changes"""
        try:
            # Step 1: Get initial portfolio
            async with self.session.get(f"{BACKEND_URL}/user/user123/portfolio") as resp:
                if resp.status != 200:
                    self.log_test("Full Dev Fund Flow", False, "❌ Failed to get initial portfolio")
                    return False
                
                initial_portfolio = await resp.json()
                initial_total = initial_portfolio.get("total_value_usd", 0)
            
            # Step 2: Execute $500K dev fund withdrawal
            async with self.session.post(f"{BACKEND_URL}/withdraw/preset?preset_id=testing_fund_500k") as resp:
                if resp.status != 200:
                    self.log_test("Full Dev Fund Flow", False, "❌ Failed to execute $500K dev fund withdrawal")
                    return False
                
                withdrawal_result = await resp.json()
                if not withdrawal_result.get("success"):
                    self.log_test("Full Dev Fund Flow", False, f"❌ Dev fund withdrawal failed: {withdrawal_result.get('message')}")
                    return False
                
                withdrawn_amount = withdrawal_result.get("total_withdrawn_usd", 0)
            
            # Step 3: Check portfolio after withdrawal
            async with self.session.get(f"{BACKEND_URL}/user/user123/portfolio") as resp:
                if resp.status != 200:
                    self.log_test("Full Dev Fund Flow", False, "❌ Failed to get portfolio after withdrawal")
                    return False
                
                final_portfolio = await resp.json()
                final_total = final_portfolio.get("total_value_usd", 0)
            
            # Step 4: Verify balance change
            expected_decrease = withdrawn_amount
            actual_decrease = initial_total - final_total
            decrease_variance = abs(actual_decrease - expected_decrease) / expected_decrease * 100 if expected_decrease > 0 else 100
            
            if decrease_variance <= 5:  # Allow 5% variance
                self.log_test("Full Dev Fund Flow", True, 
                            f"✅ SUCCESS: Portfolio decreased by ${actual_decrease:,.0f} after ${withdrawn_amount:,.0f} withdrawal (${initial_total:,.0f} → ${final_total:,.0f})")
                return True
            else:
                self.log_test("Full Dev Fund Flow", False, 
                            f"❌ BALANCE MISMATCH: Expected ${expected_decrease:,.0f} decrease but got ${actual_decrease:,.0f} ({decrease_variance:.1f}% variance)")
                return False
                
        except Exception as e:
            self.log_test("Full Dev Fund Flow", False, f"❌ Exception: {str(e)}")
            return False
    
    async def test_cdt_bridge_flow(self) -> bool:
        """Test CDT bridge flow: Check pricing → Bridge tokens → Verify CDT received"""
        try:
            # Step 1: Get CDT pricing
            async with self.session.get(f"{BACKEND_URL}/cdt/pricing") as resp:
                if resp.status != 200:
                    self.log_test("CDT Bridge Flow", False, "❌ Failed to get CDT pricing")
                    return False
                
                pricing_result = await resp.json()
                cdt_price = pricing_result.get("cdt_price_usd", 0)
                if cdt_price <= 0:
                    self.log_test("CDT Bridge Flow", False, "❌ Invalid CDT price")
                    return False
            
            # Step 2: Get initial CDT balance
            async with self.session.get(f"{BACKEND_URL}/user/user123/portfolio") as resp:
                if resp.status != 200:
                    self.log_test("CDT Bridge Flow", False, "❌ Failed to get initial portfolio")
                    return False
                
                initial_portfolio = await resp.json()
                initial_cdt = initial_portfolio.get("tokens", {}).get("CDT", {}).get("balance", 0)
            
            # Step 3: Bridge USDC to CDT
            bridge_amount = 500  # $500 USDC
            expected_cdt = bridge_amount / cdt_price
            
            bridge_data = {
                "source_token": "USDC",
                "amount": bridge_amount,
                "cdt_target_amount": expected_cdt,
                "user_wallet": "test_wallet_address",
                "bridge_type": "direct"
            }
            
            async with self.session.post(f"{BACKEND_URL}/cdt/bridge", json=bridge_data) as resp:
                if resp.status != 200:
                    self.log_test("CDT Bridge Flow", False, "❌ Failed to execute CDT bridge")
                    return False
                
                bridge_result = await resp.json()
                if not bridge_result.get("success"):
                    self.log_test("CDT Bridge Flow", False, f"❌ CDT bridge failed: {bridge_result.get('message')}")
                    return False
                
                cdt_received = bridge_result.get("cdt_received", 0)
            
            # Step 4: Verify CDT balance increased
            async with self.session.get(f"{BACKEND_URL}/user/user123/portfolio") as resp:
                if resp.status != 200:
                    self.log_test("CDT Bridge Flow", False, "❌ Failed to get final portfolio")
                    return False
                
                final_portfolio = await resp.json()
                final_cdt = final_portfolio.get("tokens", {}).get("CDT", {}).get("balance", 0)
            
            # Verify CDT increase
            cdt_increase = final_cdt - initial_cdt
            increase_variance = abs(cdt_increase - cdt_received) / cdt_received * 100 if cdt_received > 0 else 100
            
            if increase_variance <= 5:  # Allow 5% variance
                self.log_test("CDT Bridge Flow", True, 
                            f"✅ SUCCESS: CDT balance increased by {cdt_increase:,.2f} after bridging ${bridge_amount} USDC ({initial_cdt:,.2f} → {final_cdt:,.2f})")
                return True
            else:
                self.log_test("CDT Bridge Flow", False, 
                            f"❌ CDT MISMATCH: Expected {cdt_received:,.2f} CDT increase but got {cdt_increase:,.2f} ({increase_variance:.1f}% variance)")
                return False
                
        except Exception as e:
            self.log_test("CDT Bridge Flow", False, f"❌ Exception: {str(e)}")
            return False
    
    def print_summary(self):
        """Print comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n{'='*80}")
        print(f"🏦 TIGER BANK GAMES - DEVELOPMENT FUND & CDT BRIDGE TEST SUMMARY")
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
        
        print(f"\n🎯 PHASE 1 - DEVELOPMENT FUND WITHDRAWALS:")
        phase1_tests = [r for r in self.test_results if any(keyword in r["test"].lower() 
                       for keyword in ["500k", "dev fund", "wallet", "portfolio balance"])]
        phase1_passed = sum(1 for t in phase1_tests if t["success"])
        
        if phase1_passed == len(phase1_tests) and len(phase1_tests) > 0:
            print(f"   ✅ ALL PHASE 1 TESTS PASSED ({phase1_passed}/{len(phase1_tests)})")
            print(f"   ✅ $500K testing fund preset working correctly")
            print(f"   ✅ Development wallet addresses configured")
            print(f"   ✅ Portfolio balance verification successful")
        else:
            print(f"   ❌ PHASE 1 ISSUES: {phase1_passed}/{len(phase1_tests)} tests passed")
        
        print(f"\n🌉 PHASE 2 - CDT BRIDGE INTEGRATION:")
        phase2_tests = [r for r in self.test_results if any(keyword in r["test"].lower() 
                       for keyword in ["cdt", "bridge", "pricing", "iou"])]
        phase2_passed = sum(1 for t in phase2_tests if t["success"])
        
        if phase2_passed == len(phase2_tests) and len(phase2_tests) > 0:
            print(f"   ✅ ALL PHASE 2 TESTS PASSED ({phase2_passed}/{len(phase2_tests)})")
            print(f"   ✅ CDT pricing system working")
            print(f"   ✅ Direct bridge method (liquid assets) working")
            print(f"   ✅ IOU bridge method (illiquid assets) working")
        else:
            print(f"   ❌ PHASE 2 ISSUES: {phase2_passed}/{len(phase2_tests)} tests passed")
        
        print(f"\n🔄 INTEGRATION TESTING:")
        integration_tests = [r for r in self.test_results if "flow" in r["test"].lower()]
        integration_passed = sum(1 for t in integration_tests if t["success"])
        
        if integration_passed == len(integration_tests) and len(integration_tests) > 0:
            print(f"   ✅ ALL INTEGRATION TESTS PASSED ({integration_passed}/{len(integration_tests)})")
            print(f"   ✅ Full development fund withdrawal flow working")
            print(f"   ✅ Complete CDT bridge flow working")
        else:
            print(f"   ❌ INTEGRATION ISSUES: {integration_passed}/{len(integration_tests)} tests passed")
        
        print(f"\n🚀 FINAL ASSESSMENT:")
        if failed_tests == 0:
            print(f"   🎉 ALL TESTS PASSED - TIGER BANK GAMES SYSTEM READY!")
            print(f"   ✅ $500K automated testing fund working immediately")
            print(f"   ✅ CDT bridge integration fully functional")
            print(f"   ✅ Portfolio verification and balance tracking working")
        elif failed_tests <= 2:
            print(f"   ⚠️  Minor issues remain - mostly functional")
            print(f"   🔧 Address remaining {failed_tests} issues for full functionality")
        else:
            print(f"   ❌ MAJOR ISSUES DETECTED")
            print(f"   🚨 {failed_tests} critical failures need immediate attention")
            print(f"   🔍 Review failed tests and implement missing functionality")

async def main():
    """Run all Tiger Bank Games development fund and CDT bridge tests"""
    print("🏦 Starting Tiger Bank Games - Development Fund & CDT Bridge Integration Tests...")
    print(f"Backend URL: {BACKEND_URL}")
    print("🎯 Testing Focus:")
    print("   PHASE 1: $500K Development Fund Withdrawals")
    print("   PHASE 2: CDT Bridge Integration (Direct & IOU)")
    print("   INTEGRATION: Full workflow testing")
    print("="*80)
    
    async with TigerBankDevFundTester() as tester:
        # Test sequence as requested in review
        tests = [
            # PHASE 1 - Development Fund Withdrawals
            ("test_500k_testing_fund_preset", "$500K Testing Fund Preset"),
            ("test_dev_wallets_endpoint", "Development Wallets Configuration"),
            ("test_portfolio_balance_verification", "Portfolio Balance Verification ($12.277M)"),
            
            # PHASE 2 - CDT Bridge Integration
            ("test_cdt_pricing_endpoint", "CDT Pricing System"),
            ("test_cdt_bridge_direct_method", "CDT Bridge Direct Method (Liquid Assets)"),
            ("test_cdt_bridge_iou_method", "CDT Bridge IOU Method (Illiquid Assets)"),
            ("test_tokens_summary_categorization", "Token Summary Categorization"),
            
            # Integration Testing
            ("test_full_dev_fund_flow", "Full Development Fund Withdrawal Flow"),
            ("test_cdt_bridge_flow", "Complete CDT Bridge Flow")
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
        return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)