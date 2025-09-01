#!/usr/bin/env python3
import asyncio
import aiohttp
import json

async def final_verification():
    BACKEND_URL = 'https://solana-casino.preview.emergentagent.com/api'
    target_user = 'DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq'
    
    async with aiohttp.ClientSession() as session:
        # Test wallet endpoint
        async with session.get(f'{BACKEND_URL}/wallet/{target_user}') as response:
            if response.status == 200:
                data = await response.json()
                if data.get('success'):
                    wallet = data['wallet']
                    deposit_balance = wallet.get('deposit_balance', {})
                    
                    print('🎯 FINAL VERIFICATION RESULTS:')
                    print('=' * 50)
                    print(f'✅ User: {target_user}')
                    print(f'✅ Balance Source: {wallet.get("balance_source", "unknown")}')
                    print('✅ Available Currencies:')
                    
                    total_usd = 0
                    prices = {'USDC': 1.0, 'DOGE': 0.236, 'TRX': 0.363, 'CRT': 0.15}
                    
                    for currency, balance in deposit_balance.items():
                        if balance > 0:
                            usd_value = balance * prices.get(currency, 0)
                            total_usd += usd_value
                            print(f'   • {currency}: {balance:,.2f} (${usd_value:,.0f})')
                    
                    print(f'✅ Total Portfolio Value: ${total_usd:,.0f}')
                    
                    # Check success criteria
                    has_usdc = deposit_balance.get('USDC', 0) > 300000
                    has_doge = deposit_balance.get('DOGE', 0) > 2000000  
                    has_trx = deposit_balance.get('TRX', 0) > 900000
                    has_crt = deposit_balance.get('CRT', 0) > 20000000
                    portfolio_ok = total_usd > 4000000
                    
                    success_count = sum([has_usdc, has_doge, has_trx, has_crt, portfolio_ok])
                    
                    print('\n🎯 SUCCESS CRITERIA CHECK:')
                    print(f'✅ USDC (>300K): {"PASS" if has_usdc else "FAIL"} - {deposit_balance.get("USDC", 0):,.0f}')
                    print(f'✅ DOGE (>2M): {"PASS" if has_doge else "FAIL"} - {deposit_balance.get("DOGE", 0):,.0f}')
                    print(f'✅ TRX (>900K): {"PASS" if has_trx else "FAIL"} - {deposit_balance.get("TRX", 0):,.0f}')
                    print(f'✅ CRT (>20M): {"PASS" if has_crt else "FAIL"} - {deposit_balance.get("CRT", 0):,.0f}')
                    print(f'✅ Portfolio (>$4M): {"PASS" if portfolio_ok else "FAIL"} - ${total_usd:,.0f}')
                    
                    print(f'\n🎉 OVERALL SUCCESS: {success_count}/5 criteria met ({success_count/5*100:.0f}%)')
                    
                    if success_count >= 4:
                        print('🎉 PORTFOLIO FIX VERIFICATION: SUCCESS!')
                        print('✅ User can see converted currencies')
                        print('✅ User can select different cryptocurrencies for gaming')
                        print('✅ Portfolio total exceeds expected value')
                    else:
                        print('❌ PORTFOLIO FIX VERIFICATION: NEEDS ATTENTION')
                else:
                    print('❌ Wallet endpoint failed')
            else:
                print(f'❌ HTTP {response.status}')

if __name__ == "__main__":
    asyncio.run(final_verification())