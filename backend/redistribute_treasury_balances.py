#!/usr/bin/env python3
"""
Treasury Balance Redistribution Script
Converts DOGE to TRX and USDC and distributes across all 3 treasury wallets
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from decimal import Decimal
import json
from datetime import datetime, timezone
from pycoingecko import CoinGeckoAPI

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Initialize clients
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
cg = CoinGeckoAPI()

# User details
USER_WALLET = "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
USERNAME = "cryptoking"

# Get real-time conversion rates
def get_current_rates():
    """Get current crypto prices from CoinGecko"""
    try:
        prices = cg.get_price(ids=['dogecoin', 'tron', 'usd-coin'], vs_currencies='usd')
        return {
            'DOGE': prices['dogecoin']['usd'],
            'TRX': prices['tron']['usd'], 
            'USDC': prices['usd-coin']['usd']
        }
    except:
        # Fallback prices if API fails
        return {
            'DOGE': 0.24,
            'TRX': 0.37,
            'USDC': 1.00
        }

async def redistribute_treasury_balances():
    """
    Redistribute user's DOGE balance across multiple currencies and treasury wallets
    Current: 34,831,540 DOGE
    Target Distribution:
    - Treasury 1 (Savings): 60% of total value
    - Treasury 2 (Liquidity - MAIN): 30% of total value  
    - Treasury 3 (Winnings): 10% of total value
    
    Currency Split:
    - DOGE: 50% of portfolio
    - TRX: 30% of portfolio
    - USDC: 20% of portfolio
    """
    
    print("🏦 Starting Treasury Balance Redistribution...")
    print(f"👤 User: {USERNAME} ({USER_WALLET})")
    
    # Get current rates
    rates = get_current_rates()
    print(f"💱 Current rates: DOGE=${rates['DOGE']:.3f}, TRX=${rates['TRX']:.3f}, USDC=${rates['USDC']:.3f}")
    
    # Current balance
    current_doge = 34831540
    total_usd_value = current_doge * rates['DOGE']
    print(f"💰 Current balance: {current_doge:,.0f} DOGE (~${total_usd_value:,.0f} USD)")
    
    # Calculate target currency amounts based on USD values
    target_currencies = {
        'DOGE': total_usd_value * 0.50,  # 50% in DOGE
        'TRX': total_usd_value * 0.30,   # 30% in TRX  
        'USDC': total_usd_value * 0.20   # 20% in USDC
    }
    
    # Convert to actual token amounts
    target_amounts = {
        'DOGE': target_currencies['DOGE'] / rates['DOGE'],
        'TRX': target_currencies['TRX'] / rates['TRX'],
        'USDC': target_currencies['USDC'] / rates['USDC']
    }
    
    print(f"\n🎯 Target Portfolio Distribution:")
    for currency, amount in target_amounts.items():
        usd_value = amount * rates[currency]
        print(f"   {currency}: {amount:,.0f} tokens (~${usd_value:,.0f} USD)")
    
    # Treasury distribution (by percentage of each currency)
    treasury_percentages = {
        'treasury_1_savings': 0.60,     # Savings Treasury (60%)
        'treasury_2_liquidity': 0.30,   # Liquidity Treasury - MAIN (30%)
        'treasury_3_winnings': 0.10     # Winnings Treasury (10%)
    }
    
    # Calculate final balances for each treasury and currency
    final_balances = {}
    
    for treasury, percentage in treasury_percentages.items():
        final_balances[treasury] = {}
        treasury_usd_total = 0
        
        for currency, total_amount in target_amounts.items():
            treasury_amount = total_amount * percentage
            final_balances[treasury][currency] = treasury_amount
            treasury_usd_total += treasury_amount * rates[currency]
        
        treasury_name = {
            'treasury_1_savings': 'Savings Treasury',
            'treasury_2_liquidity': 'Liquidity Treasury (MAIN)',
            'treasury_3_winnings': 'Winnings Treasury'
        }[treasury]
        
        print(f"\n🏛️ {treasury_name} ({percentage*100}%):")
        for currency, amount in final_balances[treasury].items():
            usd_value = amount * rates[currency]
            print(f"   {currency}: {amount:,.0f} (~${usd_value:,.0f})")
        print(f"   💵 Treasury Total: ~${treasury_usd_total:,.0f}")
    
    # Update user's database record
    try:
        # Find user by wallet address
        user = await db.users.find_one({"wallet_address": USER_WALLET})
        if not user:
            print(f"❌ User not found with wallet address: {USER_WALLET}")
            return False
        
        print(f"\n📝 Updating database for user: {user.get('username', 'Unknown')}")
        
        # Create new balance structure with 3 treasury wallets
        new_balance_structure = {
            "deposit_balance": {  # Treasury 1 - Savings
                "CRT": final_balances['treasury_1_savings'].get('CRT', 0),
                "DOGE": round(final_balances['treasury_1_savings']['DOGE'], 2),
                "TRX": round(final_balances['treasury_1_savings']['TRX'], 2),
                "USDC": round(final_balances['treasury_1_savings']['USDC'], 2),
                "SOL": 0.0
            },
            "winnings_balance": {  # Treasury 2 - Liquidity (MAIN)
                "CRT": final_balances['treasury_2_liquidity'].get('CRT', 0),
                "DOGE": round(final_balances['treasury_2_liquidity']['DOGE'], 2),
                "TRX": round(final_balances['treasury_2_liquidity']['TRX'], 2), 
                "USDC": round(final_balances['treasury_2_liquidity']['USDC'], 2),
                "SOL": 0.0
            },
            "savings_balance": {   # Treasury 3 - Winnings
                "CRT": final_balances['treasury_3_winnings'].get('CRT', 0),
                "DOGE": round(final_balances['treasury_3_winnings']['DOGE'], 2),
                "TRX": round(final_balances['treasury_3_winnings']['TRX'], 2),
                "USDC": round(final_balances['treasury_3_winnings']['USDC'], 2),
                "SOL": 0.0
            }
        }
        
        # Keep existing CRT balance if present
        if 'balance' in user and isinstance(user['balance'], dict):
            existing_crt = 0
            for balance_type in ['deposit_balance', 'winnings_balance', 'savings_balance']:
                if balance_type in user['balance']:
                    existing_crt += user['balance'][balance_type].get('CRT', 0)
            
            if existing_crt > 0:
                # Distribute existing CRT across treasuries
                new_balance_structure['deposit_balance']['CRT'] = round(existing_crt * 0.60, 2)
                new_balance_structure['winnings_balance']['CRT'] = round(existing_crt * 0.30, 2)
                new_balance_structure['savings_balance']['CRT'] = round(existing_crt * 0.10, 2)
        
        # Update the user's balance
        result = await db.users.update_one(
            {"wallet_address": USER_WALLET},
            {
                "$set": {
                    "balance": new_balance_structure,
                    "last_balance_update": datetime.now(timezone.utc),
                    "treasury_rebalance_timestamp": datetime.now(timezone.utc).isoformat(),
                    "treasury_rebalance_note": "Multi-currency treasury redistribution for UI testing"
                }
            }
        )
        
        if result.modified_count > 0:
            print("✅ Database updated successfully!")
            
            # Log the conversion transaction
            conversion_record = {
                "transaction_id": f"treasury_rebalance_{int(datetime.now().timestamp())}",
                "user_id": user.get('user_id', user['_id']),
                "wallet_address": USER_WALLET,
                "username": user.get('username', 'Unknown'),
                "transaction_type": "treasury_rebalance",
                "source_currency": "DOGE",
                "target_currencies": ["DOGE", "TRX", "USDC"],
                "conversion_rates": rates,
                "final_balances": new_balance_structure,
                "total_usd_value": total_usd_value,
                "treasury_distribution": {
                    "savings": "60%",
                    "liquidity_main": "30%", 
                    "winnings": "10%"
                },
                "created_at": datetime.now(timezone.utc),
                "status": "completed"
            }
            
            await db.transactions.insert_one(conversion_record)
            print("📋 Transaction record created")
            
            print("\n🎉 TREASURY REDISTRIBUTION COMPLETED!")
            print("=" * 60)
            print("📊 FINAL PORTFOLIO SUMMARY:")
            
            grand_total_usd = 0
            for treasury_key, treasury_data in new_balance_structure.items():
                treasury_names = {
                    'deposit_balance': 'Treasury 1 - Savings (60%)',
                    'winnings_balance': 'Treasury 2 - Liquidity Main (30%)',
                    'savings_balance': 'Treasury 3 - Winnings (10%)'
                }
                
                print(f"\n🏛️ {treasury_names[treasury_key]}:")
                treasury_usd = 0
                for currency, amount in treasury_data.items():
                    if amount > 0 and currency in rates:
                        usd_value = amount * rates[currency]
                        treasury_usd += usd_value
                        print(f"   {currency}: {amount:,.2f} (~${usd_value:,.0f})")
                
                print(f"   💵 Treasury Total: ${treasury_usd:,.0f}")
                grand_total_usd += treasury_usd
            
            print(f"\n💰 GRAND TOTAL PORTFOLIO VALUE: ${grand_total_usd:,.0f} USD")
            print("✅ Ready for comprehensive UI testing!")
            
            return True
        else:
            print("❌ Failed to update database")
            return False
            
    except Exception as e:
        print(f"❌ Error updating database: {e}")
        return False

async def main():
    """Main execution function"""
    success = await redistribute_treasury_balances()
    if success:
        print("\n🎯 Next Steps:")
        print("1. Test frontend UI with new multi-currency balances")
        print("2. Verify all 3 treasury wallets display correctly")
        print("3. Test withdrawal interfaces for DOGE, TRX, and USDC")
        print("4. Test currency conversion functionality")
    else:
        print("\n❌ Redistribution failed - please check the logs")

if __name__ == "__main__":
    asyncio.run(main())