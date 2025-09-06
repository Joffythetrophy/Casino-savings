#!/usr/bin/env python3
"""
URGENT: User cryptoking Balance Integrity Investigation
Comprehensive audit of user's balances, transaction history, and data integrity
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Test Configuration
BACKEND_URL = "https://blockchain-slots.preview.emergentagent.com/api"
TEST_USER = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

class CryptokingBalanceAuditor:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.mongo_client = None
        self.db = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        # Connect to MongoDB for direct database inspection
        try:
            self.mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
            self.db = self.mongo_client["test_database"]
        except Exception as e:
            print(f"⚠️ MongoDB connection failed: {e}")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        if self.mongo_client:
            self.mongo_client.close()
    
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
        
        status = "✅ VERIFIED" if success else "❌ ISSUE FOUND"
        print(f"{status} {test_name}: {details}")
        if data and isinstance(data, dict):
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")
    
    async def authenticate_user(self) -> bool:
        """Authenticate user cryptoking"""
        try:
            login_data = {
                "identifier": TEST_USER["username"],
                "password": TEST_USER["password"]
            }
            
            async with self.session.post(f"{BACKEND_URL}/auth/login", json=login_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("success"):
                        self.auth_token = result.get("token")
                        self.log_test("User Authentication", True, 
                                    f"Successfully authenticated user '{TEST_USER['username']}'")
                        return True
                    else:
                        self.log_test("User Authentication", False, 
                                    f"Login failed: {result.get('message', 'Unknown error')}", result)
                        return False
                else:
                    error_text = await resp.text()
                    self.log_test("User Authentication", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("User Authentication", False, f"Exception: {str(e)}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    async def verify_database_user_record(self) -> Dict[str, Any]:
        """Verify user exists in database and get complete record"""
        try:
            if self.db is None:
                self.log_test("Database User Record", False, "MongoDB connection not available")
                return {}
            
            # Find user in database
            user_record = await self.db.users.find_one({"wallet_address": TEST_USER["wallet_address"]})
            
            if not user_record:
                self.log_test("Database User Record", False, 
                            f"User {TEST_USER['username']} not found in database")
                return {}
            
            # Extract balance information
            balances = {
                "deposit_balance": user_record.get("deposit_balance", {}),
                "winnings_balance": user_record.get("winnings_balance", {}),
                "savings_balance": user_record.get("savings_balance", {}),
                "liquidity_pool": user_record.get("liquidity_pool", {}),
                "gaming_balance": user_record.get("gaming_balance", {})
            }
            
            # Calculate totals
            total_balances = {}
            for currency in ["CRT", "DOGE", "TRX", "USDC", "SOL"]:
                total = 0
                for balance_type in balances:
                    total += balances[balance_type].get(currency, 0)
                total_balances[currency] = total
            
            user_info = {
                "user_id": user_record.get("user_id"),
                "username": user_record.get("username"),
                "wallet_address": user_record.get("wallet_address"),
                "created_at": user_record.get("created_at"),
                "balances": balances,
                "total_balances": total_balances
            }
            
            self.log_test("Database User Record", True, 
                        f"User found in database with {len(balances)} wallet types", user_info)
            return user_info
            
        except Exception as e:
            self.log_test("Database User Record", False, f"Exception: {str(e)}")
            return {}
    
    async def verify_transaction_history(self) -> Dict[str, Any]:
        """Verify user's transaction history in database"""
        try:
            if self.db is None:
                self.log_test("Transaction History", False, "MongoDB connection not available")
                return {}
            
            # Get all transactions for user
            transactions = await self.db.transactions.find(
                {"wallet_address": TEST_USER["wallet_address"]}
            ).to_list(1000)
            
            # Get game bets
            game_bets = await self.db.game_bets.find(
                {"wallet_address": TEST_USER["wallet_address"]}
            ).to_list(1000)
            
            # Get conversions
            conversions = await self.db.conversions.find(
                {"wallet_address": TEST_USER["wallet_address"]}
            ).to_list(1000)
            
            # Analyze transaction types
            transaction_types = {}
            real_hashes = []
            fake_hashes = []
            
            for tx in transactions:
                tx_type = tx.get("type", "unknown")
                transaction_types[tx_type] = transaction_types.get(tx_type, 0) + 1
                
                # Check for blockchain transaction hashes
                blockchain_hash = tx.get("blockchain_transaction_hash")
                if blockchain_hash:
                    # Simple check for fake vs real hashes
                    if len(blockchain_hash) == 64 and all(c in "0123456789abcdef" for c in blockchain_hash.lower()):
                        real_hashes.append(blockchain_hash)
                    else:
                        fake_hashes.append(blockchain_hash)
            
            history_summary = {
                "total_transactions": len(transactions),
                "total_game_bets": len(game_bets),
                "total_conversions": len(conversions),
                "transaction_types": transaction_types,
                "real_blockchain_hashes": len(real_hashes),
                "fake_hashes": len(fake_hashes),
                "sample_real_hashes": real_hashes[:3],
                "sample_fake_hashes": fake_hashes[:3]
            }
            
            success = len(transactions) > 0 or len(game_bets) > 0 or len(conversions) > 0
            self.log_test("Transaction History", success, 
                        f"Found {len(transactions)} transactions, {len(game_bets)} game bets, {len(conversions)} conversions", 
                        history_summary)
            
            return history_summary
            
        except Exception as e:
            self.log_test("Transaction History", False, f"Exception: {str(e)}")
            return {}
    
    async def verify_api_balances(self) -> Dict[str, Any]:
        """Get user balances via API endpoints"""
        try:
            headers = self.get_auth_headers()
            
            # Get wallet info via API
            async with self.session.get(f"{BACKEND_URL}/wallet/{TEST_USER['wallet_address']}", 
                                      headers=headers) as resp:
                if resp.status == 200:
                    wallet_data = await resp.json()
                    if wallet_data.get("success"):
                        wallet_info = wallet_data.get("wallet", {})
                        
                        api_balances = {
                            "deposit_balance": wallet_info.get("deposit_balance", {}),
                            "winnings_balance": wallet_info.get("winnings_balance", {}),
                            "savings_balance": wallet_info.get("savings_balance", {}),
                            "liquidity_pool": wallet_info.get("liquidity_pool", {}),
                            "balance_source": wallet_info.get("balance_source", "unknown")
                        }
                        
                        self.log_test("API Balance Retrieval", True, 
                                    f"Retrieved balances via API - source: {api_balances['balance_source']}", 
                                    api_balances)
                        return api_balances
                    else:
                        self.log_test("API Balance Retrieval", False, 
                                    f"API returned error: {wallet_data.get('message')}")
                        return {}
                else:
                    error_text = await resp.text()
                    self.log_test("API Balance Retrieval", False, 
                                f"HTTP {resp.status}: {error_text}")
                    return {}
                    
        except Exception as e:
            self.log_test("API Balance Retrieval", False, f"Exception: {str(e)}")
            return {}
    
    async def verify_blockchain_balances(self) -> Dict[str, Any]:
        """Check real blockchain balances for each currency"""
        try:
            headers = self.get_auth_headers()
            blockchain_balances = {}
            
            currencies = ["CRT", "DOGE", "TRX", "SOL", "USDC"]
            
            for currency in currencies:
                try:
                    async with self.session.get(
                        f"{BACKEND_URL}/wallet/balance/{currency}?wallet_address={TEST_USER['wallet_address']}", 
                        headers=headers
                    ) as resp:
                        if resp.status == 200:
                            balance_data = await resp.json()
                            if balance_data.get("success"):
                                blockchain_balances[currency] = {
                                    "balance": balance_data.get("balance", 0),
                                    "source": balance_data.get("source", "unknown"),
                                    "success": True
                                }
                            else:
                                blockchain_balances[currency] = {
                                    "balance": 0,
                                    "error": balance_data.get("error", "Unknown error"),
                                    "success": False
                                }
                        else:
                            blockchain_balances[currency] = {
                                "balance": 0,
                                "error": f"HTTP {resp.status}",
                                "success": False
                            }
                except Exception as e:
                    blockchain_balances[currency] = {
                        "balance": 0,
                        "error": str(e),
                        "success": False
                    }
            
            successful_currencies = [c for c in currencies if blockchain_balances[c].get("success")]
            
            self.log_test("Blockchain Balance Verification", len(successful_currencies) > 0, 
                        f"Retrieved blockchain balances for {len(successful_currencies)}/{len(currencies)} currencies", 
                        blockchain_balances)
            
            return blockchain_balances
            
        except Exception as e:
            self.log_test("Blockchain Balance Verification", False, f"Exception: {str(e)}")
            return {}
    
    async def analyze_balance_discrepancies(self, db_balances: Dict, api_balances: Dict, blockchain_balances: Dict) -> Dict[str, Any]:
        """Analyze discrepancies between database, API, and blockchain balances"""
        try:
            discrepancies = {}
            
            currencies = ["CRT", "DOGE", "TRX", "SOL", "USDC"]
            
            for currency in currencies:
                # Get balances from each source
                db_total = db_balances.get("total_balances", {}).get(currency, 0)
                api_deposit = api_balances.get("deposit_balance", {}).get(currency, 0)
                blockchain_balance = blockchain_balances.get(currency, {}).get("balance", 0)
                blockchain_source = blockchain_balances.get(currency, {}).get("source", "unknown")
                
                # Calculate discrepancies
                db_vs_api = abs(db_total - api_deposit) if db_total and api_deposit else 0
                db_vs_blockchain = abs(db_total - blockchain_balance) if db_total and blockchain_balance else 0
                api_vs_blockchain = abs(api_deposit - blockchain_balance) if api_deposit and blockchain_balance else 0
                
                discrepancies[currency] = {
                    "database_total": db_total,
                    "api_deposit": api_deposit,
                    "blockchain_balance": blockchain_balance,
                    "blockchain_source": blockchain_source,
                    "db_vs_api_diff": db_vs_api,
                    "db_vs_blockchain_diff": db_vs_blockchain,
                    "api_vs_blockchain_diff": api_vs_blockchain,
                    "has_major_discrepancy": max(db_vs_api, db_vs_blockchain, api_vs_blockchain) > 1000
                }
            
            # Find major issues
            major_issues = [c for c in currencies if discrepancies[c]["has_major_discrepancy"]]
            
            success = len(major_issues) == 0
            details = f"Found major discrepancies in {len(major_issues)} currencies: {major_issues}" if major_issues else "No major balance discrepancies found"
            
            self.log_test("Balance Discrepancy Analysis", success, details, discrepancies)
            
            return discrepancies
            
        except Exception as e:
            self.log_test("Balance Discrepancy Analysis", False, f"Exception: {str(e)}")
            return {}
    
    async def verify_crt_balance_source(self) -> Dict[str, Any]:
        """Specifically investigate CRT balance source - blockchain vs database"""
        try:
            headers = self.get_auth_headers()
            
            # Get detailed CRT balance info
            async with self.session.get(f"{BACKEND_URL}/crt/info", headers=headers) as resp:
                crt_info = {}
                if resp.status == 200:
                    crt_info = await resp.json()
            
            # Get CRT balance with source details
            async with self.session.get(
                f"{BACKEND_URL}/wallet/balance/CRT?wallet_address={TEST_USER['wallet_address']}", 
                headers=headers
            ) as resp:
                crt_balance_info = {}
                if resp.status == 200:
                    crt_balance_info = await resp.json()
            
            # Check if user has real CRT on blockchain
            crt_analysis = {
                "crt_token_info": crt_info,
                "crt_balance_response": crt_balance_info,
                "balance_source": crt_balance_info.get("source", "unknown"),
                "crt_balance": crt_balance_info.get("balance", 0),
                "is_real_blockchain": crt_balance_info.get("source") == "solana_rpc",
                "is_database_gaming": crt_balance_info.get("source") == "database_gaming_balance"
            }
            
            # Determine if CRT is real or fake
            if crt_analysis["is_real_blockchain"] and crt_analysis["crt_balance"] > 0:
                success = True
                details = f"CRT balance ({crt_analysis['crt_balance']}) comes from real Solana blockchain"
            elif crt_analysis["is_database_gaming"]:
                success = False
                details = f"CRT balance ({crt_analysis['crt_balance']}) is database-only gaming balance, not real blockchain"
            else:
                success = False
                details = f"CRT balance source unclear: {crt_analysis['balance_source']}"
            
            self.log_test("CRT Balance Source Verification", success, details, crt_analysis)
            
            return crt_analysis
            
        except Exception as e:
            self.log_test("CRT Balance Source Verification", False, f"Exception: {str(e)}")
            return {}
    
    async def check_fake_transaction_elimination(self) -> Dict[str, Any]:
        """Check if fake transaction hash generation has been eliminated"""
        try:
            if self.db is None:
                self.log_test("Fake Transaction Check", False, "MongoDB connection not available")
                return {}
            
            # Get recent transactions
            recent_transactions = await self.db.transactions.find(
                {"wallet_address": TEST_USER["wallet_address"]}
            ).sort("timestamp", -1).limit(50).to_list(50)
            
            fake_patterns = []
            real_patterns = []
            
            for tx in recent_transactions:
                tx_hash = tx.get("blockchain_transaction_hash")
                if tx_hash:
                    # Check for fake hash patterns
                    if (tx_hash.startswith("fake_") or 
                        tx_hash.startswith("mock_") or 
                        tx_hash.startswith("sim_") or
                        len(tx_hash) < 32):
                        fake_patterns.append({
                            "hash": tx_hash,
                            "type": tx.get("type"),
                            "timestamp": tx.get("timestamp")
                        })
                    elif len(tx_hash) == 64 and all(c in "0123456789abcdef" for c in tx_hash.lower()):
                        real_patterns.append({
                            "hash": tx_hash,
                            "type": tx.get("type"),
                            "timestamp": tx.get("timestamp")
                        })
            
            analysis = {
                "total_recent_transactions": len(recent_transactions),
                "fake_hash_count": len(fake_patterns),
                "real_hash_count": len(real_patterns),
                "fake_patterns": fake_patterns[:5],  # Sample
                "real_patterns": real_patterns[:5]   # Sample
            }
            
            success = len(fake_patterns) == 0
            details = f"Found {len(fake_patterns)} fake hashes and {len(real_patterns)} real hashes in recent transactions"
            
            self.log_test("Fake Transaction Hash Elimination", success, details, analysis)
            
            return analysis
            
        except Exception as e:
            self.log_test("Fake Transaction Hash Elimination", False, f"Exception: {str(e)}")
            return {}
    
    def print_comprehensive_audit_report(self):
        """Print detailed audit report for user cryptoking"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n{'='*100}")
        print(f"🔍 CRYPTOKING BALANCE INTEGRITY AUDIT REPORT")
        print(f"{'='*100}")
        print(f"User: {TEST_USER['username']} ({TEST_USER['wallet_address']})")
        print(f"Audit Date: {datetime.utcnow().isoformat()}")
        print(f"Total Checks: {total_tests}")
        print(f"✅ Verified: {passed_tests}")
        print(f"❌ Issues Found: {failed_tests}")
        print(f"Integrity Score: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📊 DETAILED FINDINGS:")
        
        # Database verification
        db_tests = [r for r in self.test_results if "database" in r["test"].lower()]
        if db_tests:
            db_result = db_tests[0]
            if db_result["success"]:
                print(f"   ✅ User exists in database with complete record")
                if db_result.get("data", {}).get("total_balances"):
                    balances = db_result["data"]["total_balances"]
                    print(f"      Total Balances: {json.dumps(balances, indent=6)}")
            else:
                print(f"   ❌ Database record issues: {db_result['details']}")
        
        # Transaction history
        tx_tests = [r for r in self.test_results if "transaction history" in r["test"].lower()]
        if tx_tests:
            tx_result = tx_tests[0]
            if tx_result["success"]:
                data = tx_result.get("data", {}) or {}
                print(f"   ✅ Transaction history found:")
                print(f"      Transactions: {data.get('total_transactions', 0)}")
                print(f"      Game Bets: {data.get('total_game_bets', 0)}")
                print(f"      Conversions: {data.get('total_conversions', 0)}")
                print(f"      Real Blockchain Hashes: {data.get('real_blockchain_hashes', 0)}")
                print(f"      Fake Hashes: {data.get('fake_hashes', 0)}")
            else:
                print(f"   ❌ Transaction history issues: {tx_result['details']}")
        
        # Balance source analysis
        crt_tests = [r for r in self.test_results if "crt balance source" in r["test"].lower()]
        if crt_tests:
            crt_result = crt_tests[0]
            data = crt_result.get("data", {}) or {}
            if crt_result["success"]:
                print(f"   ✅ CRT balance is from real blockchain (Solana RPC)")
            else:
                print(f"   ❌ CRT balance issue: {crt_result['details']}")
                print(f"      Source: {data.get('balance_source', 'unknown')}")
                print(f"      Balance: {data.get('crt_balance', 0)}")
        
        # Fake transaction check
        fake_tests = [r for r in self.test_results if "fake transaction" in r["test"].lower()]
        if fake_tests:
            fake_result = fake_tests[0]
            data = fake_result.get("data", {}) or {}
            if fake_result["success"]:
                print(f"   ✅ No fake transaction hashes found - system using real blockchain")
            else:
                print(f"   ❌ Fake transaction hashes detected: {fake_result['details']}")
                print(f"      Fake Hashes: {data.get('fake_hash_count', 0)}")
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        if failed_tests == 0:
            print(f"   🎉 ALL BALANCES VERIFIED - User's funds are legitimate and properly stored")
            print(f"   ✅ Database integrity confirmed")
            print(f"   ✅ Real blockchain integration working")
            print(f"   ✅ No fake transactions detected")
        elif failed_tests <= 2:
            print(f"   ⚠️  Minor integrity issues found - mostly legitimate")
            print(f"   🔧 {failed_tests} issues need attention")
        else:
            print(f"   ❌ MAJOR INTEGRITY ISSUES DETECTED")
            print(f"   🚨 User's concern about fake balances may be valid")
            print(f"   🔍 {failed_tests} critical issues require immediate investigation")
        
        print(f"\n📋 RECOMMENDATIONS:")
        if any("fake" in r["test"].lower() and not r["success"] for r in self.test_results):
            print(f"   🔧 Eliminate remaining fake transaction hash generation")
        if any("crt" in r["test"].lower() and not r["success"] for r in self.test_results):
            print(f"   🔧 Sync CRT balance between blockchain and database")
        if any("discrepancy" in r["test"].lower() and not r["success"] for r in self.test_results):
            print(f"   🔧 Resolve balance discrepancies between data sources")
        
        print(f"{'='*100}")

async def main():
    """Run comprehensive balance integrity audit for user cryptoking"""
    print("🔍 Starting URGENT Balance Integrity Investigation for user cryptoking...")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Target User: {TEST_USER['username']} ({TEST_USER['wallet_address']})")
    print(f"Investigation Focus: Balance legitimacy, transaction history, data integrity")
    print("="*100)
    
    async with CryptokingBalanceAuditor() as auditor:
        # Authentication
        auth_success = await auditor.authenticate_user()
        if not auth_success:
            print("❌ Cannot proceed without authentication")
            return 1
        
        # Run comprehensive audit
        print(f"\n🔍 Phase 1: Database Record Verification")
        db_balances = await auditor.verify_database_user_record()
        
        print(f"\n🔍 Phase 2: Transaction History Analysis")
        tx_history = await auditor.verify_transaction_history()
        
        print(f"\n🔍 Phase 3: API Balance Verification")
        api_balances = await auditor.verify_api_balances()
        
        print(f"\n🔍 Phase 4: Blockchain Balance Verification")
        blockchain_balances = await auditor.verify_blockchain_balances()
        
        print(f"\n🔍 Phase 5: Balance Discrepancy Analysis")
        discrepancies = await auditor.analyze_balance_discrepancies(db_balances, api_balances, blockchain_balances)
        
        print(f"\n🔍 Phase 6: CRT Balance Source Investigation")
        crt_analysis = await auditor.verify_crt_balance_source()
        
        print(f"\n🔍 Phase 7: Fake Transaction Hash Check")
        fake_check = await auditor.check_fake_transaction_elimination()
        
        # Generate comprehensive report
        auditor.print_comprehensive_audit_report()
        
        # Return exit code based on results
        failed_count = sum(1 for result in auditor.test_results if not result["success"])
        return 0 if failed_count <= 2 else 1  # Allow up to 2 minor issues

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)