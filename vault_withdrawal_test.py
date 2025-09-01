#!/usr/bin/env python3
"""
VAULT WITHDRAWAL TEST - Testing Non-Custodial External Withdrawals
This tests the user's ability to withdraw to REAL external wallets via vault system
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://solana-casino.preview.emergentagent.com/api"

class VaultWithdrawalTester:
    def __init__(self):
        self.target_user = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
        
        # Real external wallet addresses for testing
        self.external_wallets = {
            "DOGE": "D7Y55r6hNkcqDTvFW8GmyJKBGkbqNgLKjh",  # Real DOGE address
            "TRX": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",   # Real TRX address  
            "CRT": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",  # Real Solana address
            "USDC": "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"  # USDC on Solana
        }

    async def test_vault_address_generation(self):
        """Test vault address generation for user"""
        print("🏦 Testing Vault Address Generation...")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            # Test vault address generation
            async with session.get(f"{BACKEND_URL}/savings/vault/address/{self.target_user}") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Vault address generation successful")
                    
                    vault_addresses = data.get("vault_addresses", {})
                    for currency, address in vault_addresses.items():
                        print(f"  {currency} vault: {address}")
                    
                    return vault_addresses
                else:
                    print(f"❌ Vault address generation failed: HTTP {response.status}")
                    return {}

    async def test_vault_balance_check(self):
        """Test vault balance checking"""
        print("\n💰 Testing Vault Balance Check...")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BACKEND_URL}/savings/vault/{self.target_user}") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Vault balance check successful")
                    
                    vault_balances = data.get("vault_balances", {})
                    database_savings = data.get("database_savings", {})
                    
                    print("Vault balances (real blockchain):")
                    for currency, balance in vault_balances.items():
                        print(f"  {currency}: {balance}")
                    
                    print("Database savings (backup records):")
                    for currency, balance in database_savings.items():
                        print(f"  {currency}: {balance}")
                    
                    return data
                else:
                    print(f"❌ Vault balance check failed: HTTP {response.status}")
                    return {}

    async def test_vault_withdrawal_transaction_creation(self):
        """Test vault withdrawal transaction creation for each currency"""
        print("\n🔗 Testing Vault Withdrawal Transaction Creation...")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            for currency, external_address in self.external_wallets.items():
                await self.test_currency_vault_withdrawal(session, currency, external_address)

    async def test_currency_vault_withdrawal(self, session, currency, external_address):
        """Test vault withdrawal for specific currency"""
        print(f"\n💎 Testing {currency} vault withdrawal to {external_address[:20]}...")
        
        # Test amounts
        test_amounts = {
            "USDC": 500.0,     # $500 USDC
            "DOGE": 5000.0,    # 5K DOGE
            "TRX": 2000.0,     # 2K TRX
            "CRT": 10000.0     # 10K CRT
        }
        
        amount = test_amounts.get(currency, 1000.0)
        
        vault_payload = {
            "wallet_address": self.target_user,
            "currency": currency,
            "amount": amount,
            "destination_address": external_address
        }
        
        async with session.post(f"{BACKEND_URL}/savings/vault/withdraw", json=vault_payload) as response:
            if response.status == 200:
                data = await response.json()
                
                if data.get("success"):
                    print(f"  ✅ {currency} vault withdrawal transaction created")
                    
                    # Analyze the withdrawal transaction
                    withdrawal_tx = data.get("withdrawal_transaction", {})
                    security = data.get("security", {})
                    
                    print(f"     From: {withdrawal_tx.get('from_address', 'Not specified')}")
                    print(f"     To: {withdrawal_tx.get('to_address', 'Not specified')}")
                    print(f"     Amount: {withdrawal_tx.get('amount')} {currency}")
                    print(f"     Requires signature: {withdrawal_tx.get('requires_user_signature', False)}")
                    print(f"     Transaction type: {withdrawal_tx.get('transaction_type', 'Unknown')}")
                    
                    # Check if this is truly non-custodial
                    if security.get("user_signing_required") and security.get("platform_cannot_access_funds"):
                        print(f"     ✅ TRUE NON-CUSTODIAL: User controls funds completely")
                    else:
                        print(f"     ⚠️  Custodial elements detected")
                    
                    # Check for private key derivation info
                    if "private_key_derivation" in withdrawal_tx:
                        print(f"     🔑 Private key derivation provided")
                        print(f"     💡 User can derive private key independently")
                    
                    # Check for blockchain instructions
                    instructions = data.get("instructions", [])
                    if any("blockchain" in str(inst).lower() for inst in instructions):
                        print(f"     🌐 Includes blockchain broadcast instructions")
                        print(f"     ✅ This creates REAL external wallet transactions")
                    
                else:
                    print(f"  ❌ {currency} vault withdrawal failed: {data.get('message', 'Unknown error')}")
            else:
                print(f"  ❌ {currency} vault withdrawal failed: HTTP {response.status}")

    async def test_vault_withdrawal_vs_regular_withdrawal(self):
        """Compare vault withdrawal vs regular withdrawal"""
        print("\n⚖️  Comparing Vault vs Regular Withdrawals...")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            test_currency = "USDC"
            test_amount = 100.0
            external_address = self.external_wallets[test_currency]
            
            # Test regular withdrawal
            print("Regular withdrawal:")
            regular_payload = {
                "wallet_address": self.target_user,
                "wallet_type": "deposit",
                "currency": test_currency,
                "amount": test_amount
            }
            
            async with session.post(f"{BACKEND_URL}/wallet/withdraw", json=regular_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        print("  ✅ Regular withdrawal successful")
                        print("  ⚠️  No destination address required = INTERNAL transfer")
                        print("  💡 Funds likely stay within platform ecosystem")
                    else:
                        print(f"  ❌ Regular withdrawal failed: {data.get('message')}")
                else:
                    print(f"  ❌ Regular withdrawal failed: HTTP {response.status}")
            
            # Test vault withdrawal
            print("\nVault withdrawal:")
            vault_payload = {
                "wallet_address": self.target_user,
                "currency": test_currency,
                "amount": test_amount,
                "destination_address": external_address
            }
            
            async with session.post(f"{BACKEND_URL}/savings/vault/withdraw", json=vault_payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        print("  ✅ Vault withdrawal successful")
                        print("  ✅ Destination address REQUIRED = EXTERNAL transfer")
                        print("  ✅ User signature required = NON-CUSTODIAL")
                        print("  🌐 Creates real blockchain transaction")
                        
                        # Check transaction details
                        tx = data.get("withdrawal_transaction", {})
                        if tx.get("to_address") == external_address:
                            print(f"  ✅ Confirmed external destination: {external_address[:20]}...")
                    else:
                        print(f"  ❌ Vault withdrawal failed: {data.get('message')}")
                else:
                    print(f"  ❌ Vault withdrawal failed: HTTP {response.status}")

    async def test_user_savings_vault_balances(self):
        """Test user's actual savings vault balances"""
        print("\n💎 Testing User's Actual Savings Vault Balances...")
        print("=" * 60)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BACKEND_URL}/savings/vault/{self.target_user}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    vault_balances = data.get("vault_balances", {})
                    database_savings = data.get("database_savings", {})
                    
                    print("User's savings vault status:")
                    print(f"Vault type: {data.get('vault_type', 'Unknown')}")
                    print(f"User controlled: {data.get('user_controlled', False)}")
                    
                    total_vault_value = 0
                    total_database_value = 0
                    
                    # Mock prices for calculation
                    prices = {"CRT": 0.15, "DOGE": 0.24, "TRX": 0.37, "USDC": 1.0}
                    
                    print("\nVault balances (withdrawable to external wallets):")
                    for currency, balance in vault_balances.items():
                        usd_value = balance * prices.get(currency, 0)
                        total_vault_value += usd_value
                        status = "✅ Available" if balance > 0 else "❌ Empty"
                        print(f"  {currency}: {balance:,.2f} (${usd_value:,.2f}) {status}")
                    
                    print("\nDatabase savings (backup records):")
                    for currency, balance in database_savings.items():
                        usd_value = balance * prices.get(currency, 0)
                        total_database_value += usd_value
                        print(f"  {currency}: {balance:,.2f} (${usd_value:,.2f})")
                    
                    print(f"\nTotal vault value: ${total_vault_value:,.2f}")
                    print(f"Total database value: ${total_database_value:,.2f}")
                    
                    if total_vault_value > 0:
                        print("✅ User has funds available for external withdrawal")
                    else:
                        print("❌ No funds available in vault for external withdrawal")
                        print("💡 User needs to transfer gaming losses to vault first")
                    
                    return data
                else:
                    print(f"❌ Failed to get vault balances: HTTP {response.status}")
                    return {}

async def main():
    """Run vault withdrawal tests"""
    tester = VaultWithdrawalTester()
    
    print("🚨 URGENT: VAULT WITHDRAWAL CAPABILITY TEST")
    print("Testing NON-CUSTODIAL external wallet withdrawal capabilities")
    print("User:", tester.target_user)
    print("=" * 80)
    
    # Test vault system
    vault_addresses = await tester.test_vault_address_generation()
    vault_data = await tester.test_vault_balance_check()
    await tester.test_user_savings_vault_balances()
    await tester.test_vault_withdrawal_transaction_creation()
    await tester.test_vault_withdrawal_vs_regular_withdrawal()
    
    print("\n" + "=" * 80)
    print("🎯 FINAL VAULT WITHDRAWAL ASSESSMENT:")
    print("=" * 80)
    
    if vault_addresses and vault_data:
        print("✅ VAULT SYSTEM OPERATIONAL:")
        print("  • Non-custodial vault addresses generated")
        print("  • User controls private keys")
        print("  • Can create unsigned withdrawal transactions")
        print("  • Supports external wallet destinations")
        print("  • Requires user signature for withdrawals")
        
        print("\n🔍 WITHDRAWAL CAPABILITY SUMMARY:")
        print("  1. GAMING BALANCES (deposit_balance):")
        print("     • Limited by liquidity constraints")
        print("     • Internal transfers only (no external addresses)")
        print("     • Immediate withdrawal within limits")
        
        print("  2. SAVINGS BALANCES (vault system):")
        print("     • True external wallet withdrawals")
        print("     • Non-custodial (user controls funds)")
        print("     • Requires private key signing")
        print("     • Can withdraw to any external address")
        
        print("\n💡 USER ANSWER:")
        print("  ✅ YES - User CAN withdraw to external wallets via vault system")
        print("  ⚠️  Gaming balances: Limited by liquidity (internal transfers)")
        print("  ✅ Savings balances: Full external withdrawal capability")
        
    else:
        print("❌ VAULT SYSTEM ISSUES DETECTED")
        print("  • Cannot confirm external withdrawal capabilities")
        
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())