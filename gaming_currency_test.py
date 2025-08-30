#!/usr/bin/env python3
import asyncio
import aiohttp
import json

async def test_gaming_currencies():
    BACKEND_URL = 'https://tiger-dex-casino.preview.emergentagent.com/api'
    user_wallet = 'DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq'
    username = 'cryptoking'
    password = 'crt21million'
    
    async with aiohttp.ClientSession() as session:
        print('🎮 TESTING MULTI-CURRENCY GAMING SYSTEM...')
        print(f'User: {username} ({user_wallet})')
        print('=' * 60)
        
        # First authenticate user
        login_payload = {'username': username, 'password': password}
        async with session.post(f'{BACKEND_URL}/auth/login-username', json=login_payload) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('success'):
                    print(f'✅ User authenticated: {data.get("username")}')
                else:
                    print(f'❌ Authentication failed: {data.get("message")}')
                    return
            else:
                print(f'❌ HTTP {response.status}: {await response.text()}')
                return
        
        # Test different currencies for gaming
        test_currencies = ['CRT', 'DOGE', 'TRX', 'USDC']
        games = ['Slot Machine', 'Dice', 'Roulette']
        
        print(f'\n🎯 TESTING CURRENCY SUPPORT IN GAMES:')
        
        for currency in test_currencies:
            print(f'\n💰 Testing {currency}:')
            
            for game in games:
                bet_payload = {
                    'wallet_address': user_wallet,
                    'game_type': game,
                    'bet_amount': 1.0,
                    'currency': currency,
                    'network': 'test'
                }
                
                async with session.post(f'{BACKEND_URL}/games/bet', json=bet_payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('success'):
                            result = data.get('result', 'unknown')
                            payout = data.get('payout', 0)
                            print(f'  ✅ {game}: {result} (payout: {payout} {currency})')
                        else:
                            print(f'  ❌ {game}: {data.get("message", "Failed")}')
                    elif response.status == 403:
                        print(f'  🔒 {game}: Authentication required (currency supported)')
                    else:
                        error_text = await response.text()
                        if 'currency' in error_text.lower():
                            print(f'  ❌ {game}: Currency not supported')
                        else:
                            print(f'  ⚠️ {game}: HTTP {response.status}')
        
        # Test conversion rates for gaming
        print(f'\n💱 CONVERSION RATES FOR GAMING:')
        async with session.get(f'{BACKEND_URL}/conversion/rates') as response:
            if response.status == 200:
                data = await response.json()
                if data.get('success'):
                    rates = data.get('rates', {})
                    prices_usd = data.get('prices_usd', {})
                    
                    print(f'  USD Prices:')
                    for currency in test_currencies:
                        price = prices_usd.get(currency, 0)
                        print(f'    {currency}: ${price:.4f}')
                    
                    print(f'  Key Conversion Rates:')
                    key_pairs = ['CRT_DOGE', 'CRT_TRX', 'CRT_USDC', 'DOGE_USDC', 'TRX_USDC']
                    for pair in key_pairs:
                        if pair in rates:
                            print(f'    {pair}: {rates[pair]:.4f}')
                else:
                    print(f'  ❌ Failed to get rates')
            else:
                print(f'  ❌ HTTP {response.status}')
        
        # Test user's available balances for gaming
        print(f'\n💳 AVAILABLE BALANCES FOR GAMING:')
        async with session.get(f'{BACKEND_URL}/wallet/{user_wallet}') as response:
            if response.status == 200:
                data = await response.json()
                if data.get('success'):
                    wallet = data['wallet']
                    deposit_balance = wallet.get('deposit_balance', {})
                    
                    gaming_ready = {}
                    for currency in test_currencies:
                        balance = deposit_balance.get(currency, 0)
                        if balance > 10:  # Minimum for gaming
                            gaming_ready[currency] = f'✅ {balance:,.2f} (Ready)'
                        elif balance > 0:
                            gaming_ready[currency] = f'⚠️ {balance:.4f} (Low)'
                        else:
                            gaming_ready[currency] = f'❌ 0.00 (Empty)'
                    
                    for currency, status in gaming_ready.items():
                        print(f'  {currency}: {status}')
                    
                    ready_currencies = [c for c, s in gaming_ready.items() if '✅' in s]
                    print(f'\n🎮 GAMING READY: {len(ready_currencies)}/4 currencies available')
                    print(f'   Ready for gaming: {", ".join(ready_currencies)}')
                else:
                    print(f'  ❌ Failed to get wallet info')
            else:
                print(f'  ❌ HTTP {response.status}')

if __name__ == "__main__":
    asyncio.run(test_gaming_currencies())