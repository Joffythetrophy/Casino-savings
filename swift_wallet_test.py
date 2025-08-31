#!/usr/bin/env python3
"""
Trust Wallet SWIFT Account Abstraction Integration Testing
Tests all SWIFT endpoints and multi-chain support as requested in the review
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Test Configuration
BACKEND_URL = "https://crypto-treasury.preview.emergentagent.com/api"

# Sample Ethereum addresses for testing (as requested in review)
TEST_ADDRESSES = [
    "0x742D35cc6634C0532925a3b8d8ef3455fa99333d",  # Primary test address from review
    "0x1234567890123456789012345678901234567890",  # Secondary test address
    "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd"   # Third test address
]

# Supported chains for multi-chain testing
SUPPORTED_CHAINS = {
    1: "Ethereum",
    137: "Polygon", 
    56: "BSC",
    42161: "Arbitrum",
    10: "Optimism",
    8453: "Base",
    43114: "Avalanche"
}

class TrustWalletSWIFTTester:
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
    
    async def test_swift_wallet_connect(self) -> bool:
        """Test /api/swift-wallet/connect endpoint with various wallet addresses and SWIFT features"""
        try:
            success_count = 0
            total_tests = 0
            
            for wallet_address in TEST_ADDRESSES:
                for chain_id, chain_name in SUPPORTED_CHAINS.items():
                    for is_swift in [True, False]:
                        total_tests += 1
                        
                        connect_data = {
                            "wallet_address": wallet_address,
                            "chain_id": chain_id,
                            "is_swift": is_swift
                        }
                        
                        async with self.session.post(f"{BACKEND_URL}/swift-wallet/connect", 
                                                   json=connect_data) as resp:
                            result = await resp.json()
                            
                            if resp.status == 200 and result.get("success"):
                                # Validate response structure
                                required_fields = [
                                    "wallet_address", "is_swift", "chain_id", "token",
                                    "account_abstraction", "swift_features", "supported_chains",
                                    "gas_abstraction_enabled"
                                ]
                                
                                missing_fields = [field for field in required_fields if field not in result]
                                
                                if not missing_fields:
                                    # Validate SWIFT features
                                    swift_features = result.get("swift_features", {})
                                    expected_swift_features = [
                                        "gas_abstraction", "biometric_auth", 
                                        "one_click_transactions", "paymaster_enabled"
                                    ]
                                    
                                    swift_features_present = all(
                                        feature in swift_features for feature in expected_swift_features
                                    )
                                    
                                    # Validate supported chains
                                    supported_chains = result.get("supported_chains", [])
                                    expected_chains = [1, 137, 56, 42161, 10, 8453, 43114]
                                    chains_match = set(supported_chains) == set(expected_chains)
                                    
                                    if swift_features_present and chains_match:
                                        success_count += 1
                                        if total_tests <= 3:  # Log first few successes
                                            self.log_test(f"SWIFT Connect ({chain_name}, SWIFT={is_swift})", True,
                                                        f"Connected {wallet_address[-6:]} with all features")
                                    else:
                                        self.log_test(f"SWIFT Connect ({chain_name}, SWIFT={is_swift})", False,
                                                    f"Missing features or chains: swift_features={swift_features_present}, chains={chains_match}", result)
                                else:
                                    self.log_test(f"SWIFT Connect ({chain_name}, SWIFT={is_swift})", False,
                                                f"Missing fields: {missing_fields}", result)
                            else:
                                self.log_test(f"SWIFT Connect ({chain_name}, SWIFT={is_swift})", False,
                                            f"Connection failed: {result.get('message', 'Unknown error')}", result)
            
            # Overall success assessment
            success_rate = (success_count / total_tests) * 100
            if success_rate >= 90:
                self.log_test("SWIFT Connection Endpoint", True,
                            f"Excellent success rate: {success_count}/{total_tests} ({success_rate:.1f}%)")
                return True
            elif success_rate >= 70:
                self.log_test("SWIFT Connection Endpoint", True,
                            f"Good success rate: {success_count}/{total_tests} ({success_rate:.1f}%)")
                return True
            else:
                self.log_test("SWIFT Connection Endpoint", False,
                            f"Poor success rate: {success_count}/{total_tests} ({success_rate:.1f}%)")
                return False
                
        except Exception as e:
            self.log_test("SWIFT Connection Endpoint", False, f"Exception: {str(e)}")
            return False
    
    async def test_swift_wallet_status(self) -> bool:
        """Test /api/swift-wallet/status endpoint to verify SWIFT wallet feature detection"""
        try:
            success_count = 0
            total_tests = 0
            
            # First connect wallets with different SWIFT settings
            test_wallets = []
            for i, wallet_address in enumerate(TEST_ADDRESSES[:2]):  # Test with 2 addresses
                is_swift = i == 0  # First wallet SWIFT, second regular
                
                # Connect wallet first
                connect_data = {
                    "wallet_address": wallet_address,
                    "chain_id": 1,  # Ethereum
                    "is_swift": is_swift
                }
                
                async with self.session.post(f"{BACKEND_URL}/swift-wallet/connect", 
                                           json=connect_data) as resp:
                    if resp.status == 200:
                        test_wallets.append((wallet_address, is_swift))
            
            # Now test status endpoint for each wallet
            for wallet_address, expected_swift in test_wallets:
                total_tests += 1
                
                async with self.session.get(f"{BACKEND_URL}/swift-wallet/status?wallet_address={wallet_address}") as resp:
                    result = await resp.json()
                    
                    if resp.status == 200 and result.get("success"):
                        # Validate status response
                        required_fields = [
                            "wallet_address", "is_swift", "wallet_type", "chain_id",
                            "swift_features", "account_abstraction", "gas_abstraction",
                            "biometric_auth", "one_click_transactions", "supported_features"
                        ]
                        
                        missing_fields = [field for field in required_fields if field not in result]
                        
                        if not missing_fields:
                            # Validate SWIFT detection accuracy
                            detected_swift = result.get("is_swift", False)
                            account_abstraction = result.get("account_abstraction", False)
                            
                            if detected_swift == expected_swift and account_abstraction == expected_swift:
                                # Validate supported features
                                supported_features = result.get("supported_features", [])
                                expected_features = [
                                    "Gas fee abstraction",
                                    "Biometric authentication", 
                                    "One-click transactions",
                                    "Multi-token fee payments",
                                    "Account recovery without seed phrase"
                                ] if expected_swift else ["Standard wallet features"]
                                
                                features_match = len(supported_features) == len(expected_features)
                                
                                if features_match:
                                    success_count += 1
                                    self.log_test(f"SWIFT Status Detection ({wallet_address[-6:]})", True,
                                                f"Correctly detected SWIFT={expected_swift} with proper features")
                                else:
                                    self.log_test(f"SWIFT Status Detection ({wallet_address[-6:]})", False,
                                                f"Feature mismatch: got {len(supported_features)}, expected {len(expected_features)}", result)
                            else:
                                self.log_test(f"SWIFT Status Detection ({wallet_address[-6:]})", False,
                                            f"SWIFT detection mismatch: expected {expected_swift}, got {detected_swift}", result)
                        else:
                            self.log_test(f"SWIFT Status Detection ({wallet_address[-6:]})", False,
                                        f"Missing fields: {missing_fields}", result)
                    else:
                        self.log_test(f"SWIFT Status Detection ({wallet_address[-6:]})", False,
                                    f"Status check failed: {result.get('message', 'Unknown error')}", result)
            
            # Overall assessment
            if success_count == total_tests and total_tests > 0:
                self.log_test("SWIFT Status Endpoint", True,
                            f"Perfect SWIFT feature detection: {success_count}/{total_tests}")
                return True
            elif success_count >= total_tests * 0.8:
                self.log_test("SWIFT Status Endpoint", True,
                            f"Good SWIFT feature detection: {success_count}/{total_tests}")
                return True
            else:
                self.log_test("SWIFT Status Endpoint", False,
                            f"Poor SWIFT feature detection: {success_count}/{total_tests}")
                return False
                
        except Exception as e:
            self.log_test("SWIFT Status Endpoint", False, f"Exception: {str(e)}")
            return False
    
    async def test_swift_wallet_transaction(self) -> bool:
        """Test /api/swift-wallet/transaction endpoint to verify Account Abstraction transaction processing"""
        try:
            success_count = 0
            total_tests = 0
            
            # Connect a SWIFT wallet first
            swift_wallet = TEST_ADDRESSES[0]
            connect_data = {
                "wallet_address": swift_wallet,
                "chain_id": 1,
                "is_swift": True
            }
            
            async with self.session.post(f"{BACKEND_URL}/swift-wallet/connect", 
                                       json=connect_data) as resp:
                if resp.status != 200:
                    self.log_test("SWIFT Transaction Endpoint", False, "Failed to connect SWIFT wallet for testing")
                    return False
            
            # Test various transaction scenarios
            test_scenarios = [
                {
                    "name": "ETH Transaction with Gas Abstraction",
                    "data": {
                        "wallet_address": swift_wallet,
                        "to_address": TEST_ADDRESSES[1],
                        "amount": 0.1,
                        "currency": "ETH",
                        "use_gas_abstraction": True
                    }
                },
                {
                    "name": "USDC Transaction with Gas Abstraction",
                    "data": {
                        "wallet_address": swift_wallet,
                        "to_address": TEST_ADDRESSES[1],
                        "amount": 100,
                        "currency": "USDC",
                        "use_gas_abstraction": True
                    }
                },
                {
                    "name": "Transaction without Gas Abstraction",
                    "data": {
                        "wallet_address": swift_wallet,
                        "to_address": TEST_ADDRESSES[1],
                        "amount": 50,
                        "currency": "USDC",
                        "use_gas_abstraction": False
                    }
                }
            ]
            
            for scenario in test_scenarios:
                total_tests += 1
                
                async with self.session.post(f"{BACKEND_URL}/swift-wallet/transaction", 
                                           json=scenario["data"]) as resp:
                    result = await resp.json()
                    
                    if resp.status == 200 and result.get("success"):
                        # Validate transaction response
                        required_fields = [
                            "transaction_id", "wallet_address", "amount", "currency",
                            "gas_abstraction", "account_abstraction", "swift_features"
                        ]
                        
                        missing_fields = [field for field in required_fields if field not in result]
                        
                        if not missing_fields:
                            # Validate SWIFT features in transaction
                            swift_features = result.get("swift_features", {})
                            expected_swift_features = [
                                "enabled", "gas_abstraction", "one_click_transaction", "biometric_verification"
                            ]
                            
                            swift_features_present = all(
                                feature in swift_features for feature in expected_swift_features
                            )
                            
                            # Validate gas abstraction setting
                            expected_gas_abstraction = scenario["data"].get("use_gas_abstraction", True)
                            actual_gas_abstraction = result.get("gas_abstraction", False)
                            
                            if swift_features_present and (actual_gas_abstraction == expected_gas_abstraction):
                                success_count += 1
                                self.log_test(f"SWIFT Transaction ({scenario['name']})", True,
                                            f"Transaction prepared with correct SWIFT features")
                            else:
                                self.log_test(f"SWIFT Transaction ({scenario['name']})", False,
                                            f"SWIFT features mismatch: features={swift_features_present}, gas={actual_gas_abstraction}", result)
                        else:
                            self.log_test(f"SWIFT Transaction ({scenario['name']})", False,
                                        f"Missing fields: {missing_fields}", result)
                    else:
                        self.log_test(f"SWIFT Transaction ({scenario['name']})", False,
                                    f"Transaction failed: {result.get('message', 'Unknown error')}", result)
            
            # Overall assessment
            if success_count == total_tests:
                self.log_test("SWIFT Transaction Endpoint", True,
                            f"All Account Abstraction transactions working: {success_count}/{total_tests}")
                return True
            elif success_count >= total_tests * 0.8:
                self.log_test("SWIFT Transaction Endpoint", True,
                            f"Most Account Abstraction transactions working: {success_count}/{total_tests}")
                return True
            else:
                self.log_test("SWIFT Transaction Endpoint", False,
                            f"Account Abstraction transaction issues: {success_count}/{total_tests}")
                return False
                
        except Exception as e:
            self.log_test("SWIFT Transaction Endpoint", False, f"Exception: {str(e)}")
            return False
    
    async def test_account_abstraction_configuration(self) -> bool:
        """Test /api/swift-wallet/account-abstraction endpoint to configure SWIFT features"""
        try:
            success_count = 0
            total_tests = 0
            
            # Connect a wallet first
            test_wallet = TEST_ADDRESSES[0]
            connect_data = {
                "wallet_address": test_wallet,
                "chain_id": 1,
                "is_swift": True
            }
            
            async with self.session.post(f"{BACKEND_URL}/swift-wallet/connect", 
                                       json=connect_data) as resp:
                if resp.status != 200:
                    self.log_test("Account Abstraction Configuration", False, "Failed to connect wallet for testing")
                    return False
            
            # Test different feature configurations
            test_configurations = [
                {
                    "name": "Enable All Features",
                    "features": {
                        "gas_abstraction": True,
                        "biometric_auth": True,
                        "one_click_transactions": True,
                        "paymaster_enabled": True,
                        "multi_token_fees": True
                    }
                },
                {
                    "name": "Selective Features",
                    "features": {
                        "gas_abstraction": True,
                        "biometric_auth": False,
                        "one_click_transactions": True,
                        "paymaster_enabled": True,
                        "multi_token_fees": False
                    }
                },
                {
                    "name": "Minimal Features",
                    "features": {
                        "gas_abstraction": False,
                        "biometric_auth": False,
                        "one_click_transactions": False,
                        "paymaster_enabled": False,
                        "multi_token_fees": False
                    }
                }
            ]
            
            for config in test_configurations:
                total_tests += 1
                
                config_data = {
                    "wallet_address": test_wallet,
                    "enable_features": config["features"]
                }
                
                async with self.session.post(f"{BACKEND_URL}/swift-wallet/account-abstraction", 
                                           json=config_data) as resp:
                    result = await resp.json()
                    
                    if resp.status == 200 and result.get("success"):
                        # Validate configuration response
                        required_fields = [
                            "wallet_address", "swift_features", "account_abstraction", "enabled_features"
                        ]
                        
                        missing_fields = [field for field in required_fields if field not in result]
                        
                        if not missing_fields:
                            # Validate feature configuration
                            returned_features = result.get("swift_features", {})
                            expected_features = config["features"]
                            
                            features_match = all(
                                returned_features.get(key) == expected_features[key]
                                for key in expected_features
                            )
                            
                            # Validate enabled_features list
                            enabled_features = result.get("enabled_features", [])
                            has_feature_status = len(enabled_features) == 5  # Should have 5 feature status lines
                            
                            if features_match and has_feature_status:
                                success_count += 1
                                self.log_test(f"AA Configuration ({config['name']})", True,
                                            f"Features configured correctly: {sum(expected_features.values())}/5 enabled")
                            else:
                                self.log_test(f"AA Configuration ({config['name']})", False,
                                            f"Feature mismatch: match={features_match}, status={has_feature_status}", result)
                        else:
                            self.log_test(f"AA Configuration ({config['name']})", False,
                                        f"Missing fields: {missing_fields}", result)
                    else:
                        self.log_test(f"AA Configuration ({config['name']})", False,
                                    f"Configuration failed: {result.get('message', 'Unknown error')}", result)
            
            # Overall assessment
            if success_count == total_tests:
                self.log_test("Account Abstraction Configuration", True,
                            f"All AA configurations working: {success_count}/{total_tests}")
                return True
            elif success_count >= total_tests * 0.8:
                self.log_test("Account Abstraction Configuration", True,
                            f"Most AA configurations working: {success_count}/{total_tests}")
                return True
            else:
                self.log_test("Account Abstraction Configuration", False,
                            f"AA configuration issues: {success_count}/{total_tests}")
                return False
                
        except Exception as e:
            self.log_test("Account Abstraction Configuration", False, f"Exception: {str(e)}")
            return False
    
    async def test_multi_chain_support(self) -> bool:
        """Verify support for Ethereum, Polygon, BSC, Arbitrum, Optimism, Base, and Avalanche"""
        try:
            success_count = 0
            total_tests = len(SUPPORTED_CHAINS)
            
            test_wallet = TEST_ADDRESSES[0]
            
            for chain_id, chain_name in SUPPORTED_CHAINS.items():
                connect_data = {
                    "wallet_address": test_wallet,
                    "chain_id": chain_id,
                    "is_swift": True
                }
                
                async with self.session.post(f"{BACKEND_URL}/swift-wallet/connect", 
                                           json=connect_data) as resp:
                    result = await resp.json()
                    
                    if resp.status == 200 and result.get("success"):
                        # Validate chain support
                        returned_chain_id = result.get("chain_id")
                        supported_chains = result.get("supported_chains", [])
                        
                        if (returned_chain_id == chain_id and 
                            chain_id in supported_chains and 
                            len(supported_chains) == 7):  # Should support all 7 chains
                            
                            success_count += 1
                            self.log_test(f"Multi-Chain Support ({chain_name})", True,
                                        f"Chain {chain_id} supported with all 7 chains listed")
                        else:
                            self.log_test(f"Multi-Chain Support ({chain_name})", False,
                                        f"Chain support issue: returned_id={returned_chain_id}, in_list={chain_id in supported_chains}", result)
                    else:
                        self.log_test(f"Multi-Chain Support ({chain_name})", False,
                                    f"Chain {chain_id} connection failed: {result.get('message', 'Unknown error')}", result)
            
            # Overall assessment
            if success_count == total_tests:
                self.log_test("Multi-Chain Support", True,
                            f"All {total_tests} chains supported perfectly")
                return True
            elif success_count >= total_tests * 0.9:
                self.log_test("Multi-Chain Support", True,
                            f"Excellent chain support: {success_count}/{total_tests}")
                return True
            else:
                self.log_test("Multi-Chain Support", False,
                            f"Insufficient chain support: {success_count}/{total_tests}")
                return False
                
        except Exception as e:
            self.log_test("Multi-Chain Support", False, f"Exception: {str(e)}")
            return False
    
    async def test_gas_abstraction_features(self) -> bool:
        """Test that gas abstraction features are properly enabled for SWIFT wallets"""
        try:
            success_count = 0
            total_tests = 0
            
            # Test with both SWIFT and non-SWIFT wallets
            test_scenarios = [
                {"wallet": TEST_ADDRESSES[0], "is_swift": True, "expected_gas_abstraction": True},
                {"wallet": TEST_ADDRESSES[1], "is_swift": False, "expected_gas_abstraction": False}
            ]
            
            for scenario in test_scenarios:
                total_tests += 1
                
                # Connect wallet
                connect_data = {
                    "wallet_address": scenario["wallet"],
                    "chain_id": 1,
                    "is_swift": scenario["is_swift"]
                }
                
                async with self.session.post(f"{BACKEND_URL}/swift-wallet/connect", 
                                           json=connect_data) as resp:
                    connect_result = await resp.json()
                    
                    if resp.status == 200 and connect_result.get("success"):
                        # Check gas abstraction in connect response
                        gas_abstraction_enabled = connect_result.get("gas_abstraction_enabled", False)
                        
                        # Also check status endpoint
                        async with self.session.get(f"{BACKEND_URL}/swift-wallet/status?wallet_address={scenario['wallet']}") as status_resp:
                            status_result = await status_resp.json()
                            
                            if status_resp.status == 200 and status_result.get("success"):
                                status_gas_abstraction = status_result.get("gas_abstraction", False)
                                
                                # Validate gas abstraction settings
                                expected = scenario["expected_gas_abstraction"]
                                
                                if (gas_abstraction_enabled == expected and 
                                    status_gas_abstraction == expected):
                                    
                                    success_count += 1
                                    wallet_type = "SWIFT" if scenario["is_swift"] else "Regular"
                                    self.log_test(f"Gas Abstraction ({wallet_type} Wallet)", True,
                                                f"Gas abstraction correctly {'enabled' if expected else 'disabled'}")
                                else:
                                    self.log_test(f"Gas Abstraction ({wallet_type} Wallet)", False,
                                                f"Gas abstraction mismatch: connect={gas_abstraction_enabled}, status={status_gas_abstraction}, expected={expected}")
                            else:
                                self.log_test(f"Gas Abstraction (Status Check)", False,
                                            f"Status check failed for {scenario['wallet'][-6:]}")
                    else:
                        self.log_test(f"Gas Abstraction (Connect)", False,
                                    f"Connection failed for {scenario['wallet'][-6:]}")
            
            # Test gas abstraction in transactions
            if success_count > 0:  # Only test if we have at least one working wallet
                total_tests += 1
                
                # Test transaction with gas abstraction
                swift_wallet = TEST_ADDRESSES[0]
                tx_data = {
                    "wallet_address": swift_wallet,
                    "to_address": TEST_ADDRESSES[1],
                    "amount": 10,
                    "currency": "USDC",
                    "use_gas_abstraction": True
                }
                
                async with self.session.post(f"{BACKEND_URL}/swift-wallet/transaction", 
                                           json=tx_data) as resp:
                    result = await resp.json()
                    
                    if resp.status == 200 and result.get("success"):
                        tx_gas_abstraction = result.get("gas_abstraction", False)
                        swift_features = result.get("swift_features", {})
                        
                        if (tx_gas_abstraction and 
                            swift_features.get("gas_abstraction", False) and
                            swift_features.get("enabled", False)):
                            
                            success_count += 1
                            self.log_test("Gas Abstraction (Transaction)", True,
                                        "Gas abstraction working in transactions")
                        else:
                            self.log_test("Gas Abstraction (Transaction)", False,
                                        f"Transaction gas abstraction failed: tx={tx_gas_abstraction}, features={swift_features}")
                    else:
                        self.log_test("Gas Abstraction (Transaction)", False,
                                    f"Transaction test failed: {result.get('message', 'Unknown error')}")
            
            # Overall assessment
            if success_count == total_tests:
                self.log_test("Gas Abstraction Features", True,
                            f"All gas abstraction features working: {success_count}/{total_tests}")
                return True
            elif success_count >= total_tests * 0.8:
                self.log_test("Gas Abstraction Features", True,
                            f"Most gas abstraction features working: {success_count}/{total_tests}")
                return True
            else:
                self.log_test("Gas Abstraction Features", False,
                            f"Gas abstraction issues: {success_count}/{total_tests}")
                return False
                
        except Exception as e:
            self.log_test("Gas Abstraction Features", False, f"Exception: {str(e)}")
            return False
    
    def print_summary(self):
        """Print comprehensive test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n{'='*80}")
        print(f"🚀 TRUST WALLET SWIFT ACCOUNT ABSTRACTION INTEGRATION TEST SUMMARY")
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
        
        print(f"\n🎯 SWIFT INTEGRATION ASSESSMENT:")
        
        # Check each major component
        components = {
            "SWIFT Connection": ["swift connection", "swift connect"],
            "SWIFT Status": ["swift status"],
            "SWIFT Transaction": ["swift transaction"],
            "Account Abstraction": ["account abstraction", "aa configuration"],
            "Multi-Chain Support": ["multi-chain"],
            "Gas Abstraction": ["gas abstraction"]
        }
        
        for component, keywords in components.items():
            component_tests = [
                r for r in self.test_results 
                if any(keyword in r["test"].lower() for keyword in keywords)
            ]
            
            if component_tests:
                component_success = sum(1 for t in component_tests if t["success"])
                component_total = len(component_tests)
                
                if component_success == component_total:
                    print(f"   ✅ {component}: Perfect ({component_success}/{component_total})")
                elif component_success >= component_total * 0.8:
                    print(f"   ✅ {component}: Good ({component_success}/{component_total})")
                else:
                    print(f"   ❌ {component}: Issues ({component_success}/{component_total})")
            else:
                print(f"   ⚠️  {component}: Not tested")
        
        print(f"\n🚀 FINAL ASSESSMENT:")
        if failed_tests == 0:
            print(f"   🎉 TRUST WALLET SWIFT INTEGRATION FULLY WORKING!")
            print(f"   ✅ All Account Abstraction features operational")
            print(f"   ✅ Multi-chain support confirmed (7 chains)")
            print(f"   ✅ Gas abstraction, biometric auth, one-click transactions ready")
            print(f"   ✅ Multi-token fee payments and account recovery supported")
        elif failed_tests <= 2:
            print(f"   ⚠️  SWIFT integration mostly working - minor issues")
            print(f"   🔧 Check {failed_tests} remaining issues")
        else:
            print(f"   ❌ MAJOR SWIFT INTEGRATION ISSUES")
            print(f"   🚨 {failed_tests} critical problems need resolution")
            print(f"   🔍 Review implementation and dependencies")

async def main():
    """Run all Trust Wallet SWIFT Account Abstraction tests"""
    print("🚀 Starting Trust Wallet SWIFT Account Abstraction Integration Tests...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Addresses: {[addr[-6:] for addr in TEST_ADDRESSES]}")
    print(f"Supported Chains: {list(SUPPORTED_CHAINS.values())}")
    print("="*80)
    
    async with TrustWalletSWIFTTester() as tester:
        # Test sequence as requested in review
        tests = [
            ("test_swift_wallet_connect", "SWIFT Connection Endpoint"),
            ("test_swift_wallet_status", "SWIFT Status Endpoint"),
            ("test_swift_wallet_transaction", "SWIFT Transaction Endpoint"),
            ("test_account_abstraction_configuration", "Account Abstraction Configuration"),
            ("test_multi_chain_support", "Multi-Chain Support Verification"),
            ("test_gas_abstraction_features", "Gas Abstraction Features")
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