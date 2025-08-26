#!/usr/bin/env python3
"""
Fix Vault Withdrawal Test - Test with correct parameters
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BACKEND_URL = "https://cryptosavings.preview.emergentagent.com/api"

async def test_vault_withdrawal_fixed():
    """Test vault withdrawal with correct parameter names"""
    user_wallet = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
    withdrawal_amount = 500.0
    external_address = "0xaA94Fe949f6734e228c13C9Fc25D1eBCd994bffD"
    currency = "USDC"
    
    async with aiohttp.ClientSession() as session:
        print("🏛️ Testing vault withdrawal with corrected parameters...")
        
        # Try different parameter combinations
        test_payloads = [
            {
                "wallet_address": user_wallet,  # Changed from user_wallet
                "currency": currency,
                "amount": withdrawal_amount,
                "destination_address": external_address
            },
            {
                "user_wallet": user_wallet,
                "currency": currency,
                "amount": withdrawal_amount,
                "destination_address": external_address
            },
            {
                "wallet_address": user_wallet,
                "currency": currency,
                "amount": withdrawal_amount,
                "to_address": external_address  # Different parameter name
            }
        ]
        
        for i, payload in enumerate(test_payloads, 1):
            print(f"\n--- Test {i}: {list(payload.keys())} ---")
            
            try:
                async with session.post(f"{BACKEND_URL}/savings/vault/withdraw", 
                                      json=payload) as response:
                    response_text = await response.text()
                    print(f"Status: {response.status}")
                    print(f"Response: {response_text}")
                    
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            print("✅ VAULT WITHDRAWAL SUCCESSFUL!")
                            return True, data
                        else:
                            print(f"❌ Failed: {data.get('message')}")
                    else:
                        print(f"❌ HTTP Error: {response.status}")
                        
            except Exception as e:
                print(f"❌ Exception: {e}")
        
        return False, None

if __name__ == "__main__":
    asyncio.run(test_vault_withdrawal_fixed())