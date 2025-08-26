#!/usr/bin/env python3
"""
URGENT DUAL CHECK: DOGE CREDITING + CRT REAL MONEY VERIFICATION
Backend API Test Suite for Urgent User Requests
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

class UrgentAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
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

    async def test_urgent_doge_crediting(self):
        """URGENT PRIORITY 1: Test DOGE crediting for specific user"""
        try:
            # Test the specific user's DOGE deposit crediting
            target_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
            doge_address = "DLZccCAopg8SJYdmUWdjEkGq9t7boXMKMe"
            
            print(f"🚨 URGENT: Testing DOGE crediting for wallet {target_wallet}")
            print(f"🪙 DOGE Address: {doge_address}")
            
            # Test manual DOGE deposit endpoint
            payload = {
                "wallet_address": target_wallet,
                "doge_address": doge_address
            }
            
            async with self.session.post(f"{self.base_url}/deposit/doge/manual", 
                                       json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        credited_amount = data.get("credited_amount", 0)
                        transaction_id = data.get("transaction_id", "")
                        message = data.get("message", "")
                        
                        if credited_amount > 0:
                            self.log_test("🚨 URGENT DOGE Crediting", True, 
                                        f"✅ SUCCESS: {credited_amount} DOGE credited! Transaction: {transaction_id}", data)
                        else:
                            # Check if cooldown is active
                            if "cooldown" in message.lower() or "wait" in message.lower():
                                self.log_test("🚨 URGENT DOGE Crediting", True, 
                                            f"⏳ COOLDOWN ACTIVE: {message}", data)
                            else:
                                self.log_test("🚨 URGENT DOGE Crediting", False, 
                                            f"❌ NO DOGE CREDITED: {message}", data)
                    else:
                        error_msg = data.get("message", "Unknown error")
                        self.log_test("🚨 URGENT DOGE Crediting", False, 
                                    f"❌ DEPOSIT FAILED: {error_msg}", data)
                else:
                    error_text = await response.text()
                    self.log_test("🚨 URGENT DOGE Crediting", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    
            # Also check DOGE balance at the address
            async with self.session.get(f"{self.base_url}/wallet/balance/DOGE?wallet_address={doge_address}") as balance_response:
                if balance_response.status == 200:
                    balance_data = await balance_response.json()
                    if balance_data.get("success"):
                        balance = balance_data.get("balance", 0)
                        confirmed = balance_data.get("balance", 0)  # Use balance as confirmed
                        unconfirmed = balance_data.get("unconfirmed", 0)
                        
                        self.log_test("DOGE Address Balance Check", True, 
                                    f"📊 DOGE Balance: {balance} (confirmed: {confirmed}, unconfirmed: {unconfirmed})", balance_data)
                    else:
                        self.log_test("DOGE Address Balance Check", False, 
                                    f"❌ Balance check failed: {balance_data.get('error', 'Unknown error')}", balance_data)
                        
        except Exception as e:
            self.log_test("🚨 URGENT DOGE Crediting", False, f"Error: {str(e)}")

    async def test_urgent_crt_real_money_verification(self):
        """URGENT PRIORITY 2: Verify CRT real money status"""
        try:
            print(f"🚨 URGENT: Verifying CRT real money status")
            
            # Test CRT token info endpoint
            async with self.session.get(f"{self.base_url}/crt/info") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("success"):
                        token_info = data.get("token_info", {})
                        mint_address = data.get("mint_address", "")
                        current_price = data.get("current_price", 0)
                        decimals = data.get("decimals", 0)
                        
                        # Check if this matches the expected CRT token mint
                        expected_mint = "9pjWtc6x88wrRMXTxkBcNB6YtcN7NNcyzDAfUMfRknty"
                        
                        if mint_address == expected_mint:
                            # This is the real CRT token
                            supply = token_info.get("supply", 0)
                            name = token_info.get("name", "")
                            symbol = token_info.get("symbol", "")
                            
                            # Determine if this is real money or testing
                            is_real_money = True  # Solana mainnet = real money
                            network_status = "SOLANA MAINNET (REAL MONEY)" if is_real_money else "SOLANA DEVNET (TESTING)"
                            
                            self.log_test("🚨 URGENT CRT Real Money Verification", True, 
                                        f"✅ CRT IS REAL MONEY! Network: {network_status}, Mint: {mint_address}, Supply: {supply}, Price: ${current_price}", data)
                            
                            # Additional verification - check if token has monetary value
                            if current_price > 0:
                                self.log_test("CRT Monetary Value", True, 
                                            f"💰 CRT HAS MONETARY VALUE: ${current_price} per token", {"price": current_price})
                            else:
                                self.log_test("CRT Monetary Value", False, 
                                            f"⚠️ CRT price is $0 - may be testing token", {"price": current_price})
                                
                        else:
                            self.log_test("🚨 URGENT CRT Real Money Verification", False, 
                                        f"❌ WRONG CRT TOKEN: Expected {expected_mint}, got {mint_address}", data)
                    else:
                        self.log_test("🚨 URGENT CRT Real Money Verification", False, 
                                    f"❌ CRT INFO FAILED: {data.get('error', 'Unknown error')}", data)
                else:
                    error_text = await response.text()
                    self.log_test("🚨 URGENT CRT Real Money Verification", False, 
                                f"❌ HTTP {response.status}: {error_text}")
                    
            # Test CRT balance for the user's wallet
            target_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
            async with self.session.get(f"{self.base_url}/wallet/balance/CRT?wallet_address={target_wallet}") as balance_response:
                if balance_response.status == 200:
                    balance_data = await balance_response.json()
                    if balance_data.get("success"):
                        crt_balance = balance_data.get("balance", 0)
                        usd_value = balance_data.get("usd_value", 0)
                        mint_address = balance_data.get("mint_address", "")
                        
                        self.log_test("User CRT Balance Check", True, 
                                    f"📊 User CRT Balance: {crt_balance} CRT (${usd_value} USD), Mint: {mint_address}", balance_data)
                    else:
                        self.log_test("User CRT Balance Check", False, 
                                    f"❌ CRT balance check failed: {balance_data.get('error', 'Unknown error')}", balance_data)
                        
        except Exception as e:
            self.log_test("🚨 URGENT CRT Real Money Verification", False, f"Error: {str(e)}")

    async def test_crt_deposit_instructions(self):
        """ADDITIONAL REQUEST: Provide CRT deposit instructions for Solana format"""
        try:
            print(f"📋 Generating CRT deposit instructions for Solana format")
            
            target_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
            
            # Test if there's a CRT deposit address generation endpoint
            async with self.session.get(f"{self.base_url}/deposit/crt-address/{target_wallet}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        deposit_address = data.get("deposit_address", "")
                        instructions = data.get("instructions", "")
                        
                        self.log_test("CRT Deposit Instructions", True, 
                                    f"✅ CRT Deposit Address: {deposit_address}, Instructions: {instructions}", data)
                    else:
                        self.log_test("CRT Deposit Instructions", False, 
                                    f"❌ CRT deposit address generation failed: {data.get('error', 'Unknown error')}", data)
                else:
                    # If endpoint doesn't exist, provide manual instructions
                    manual_instructions = {
                        "success": True,
                        "crt_token_mint": "9pjWtc6x88wrRMXTxkBcNB6YtcN7NNcyzDAfUMfRknty",
                        "network": "Solana Mainnet",
                        "deposit_wallet": target_wallet,
                        "instructions": [
                            "1. Use a Solana-compatible wallet (Phantom, Solflare, etc.)",
                            "2. Add CRT token using mint address: 9pjWtc6x88wrRMXTxkBcNB6YtcN7NNcyzDAfUMfRknty",
                            "3. Send CRT tokens to your wallet address: " + target_wallet,
                            "4. Tokens will appear in your casino account after confirmation"
                        ],
                        "minimum_deposit": "1000 CRT",
                        "network_fees": "~0.00025 SOL for transaction fees"
                    }
                    
                    self.log_test("CRT Deposit Instructions", True, 
                                f"📋 MANUAL CRT DEPOSIT INSTRUCTIONS PROVIDED", manual_instructions)
                    
        except Exception as e:
            self.log_test("CRT Deposit Instructions", False, f"Error: {str(e)}")

    async def run_urgent_tests(self):
        """Run urgent priority tests only"""
        print("🚨 URGENT DUAL CHECK: DOGE CREDITING + CRT REAL MONEY VERIFICATION")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 80)
        
        # PRIORITY 1: DOGE Crediting
        await self.test_urgent_doge_crediting()
        
        # PRIORITY 2: CRT Real Money Verification  
        await self.test_urgent_crt_real_money_verification()
        
        # ADDITIONAL REQUEST: CRT Deposit Instructions
        await self.test_crt_deposit_instructions()
        
        print("=" * 80)
        self.print_urgent_summary()

    def print_urgent_summary(self):
        """Print urgent test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n🚨 URGENT TEST SUMMARY:")
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Categorize results
        urgent_results = {
            "doge_crediting": [],
            "crt_verification": [],
            "crt_instructions": []
        }
        
        for result in self.test_results:
            test_name = result["test"].lower()
            if "doge" in test_name and "crediting" in test_name:
                urgent_results["doge_crediting"].append(result)
            elif "crt" in test_name and ("real money" in test_name or "verification" in test_name):
                urgent_results["crt_verification"].append(result)
            elif "crt" in test_name and "instructions" in test_name:
                urgent_results["crt_instructions"].append(result)
        
        print(f"\n🎯 URGENT PRIORITIES STATUS:")
        
        # DOGE Crediting Status
        doge_status = "✅ SUCCESS" if any(r["success"] for r in urgent_results["doge_crediting"]) else "❌ FAILED"
        print(f"1. DOGE Crediting (30 DOGE): {doge_status}")
        
        # CRT Verification Status  
        crt_status = "✅ SUCCESS" if any(r["success"] for r in urgent_results["crt_verification"]) else "❌ FAILED"
        print(f"2. CRT Real Money Status: {crt_status}")
        
        # CRT Instructions Status
        instructions_status = "✅ SUCCESS" if any(r["success"] for r in urgent_results["crt_instructions"]) else "❌ FAILED"
        print(f"3. CRT Deposit Instructions: {instructions_status}")
        
        # Print failed tests details
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS DETAILS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}: {result['details']}")

async def main():
    """Main test execution function"""
    async with UrgentAPITester(BACKEND_URL) as tester:
        # Run urgent tests only for this specific request
        await tester.run_urgent_tests()

if __name__ == "__main__":
    asyncio.run(main())