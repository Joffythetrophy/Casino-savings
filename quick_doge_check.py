#!/usr/bin/env python3
import asyncio
import aiohttp
import json

async def check_doge_deposit_status():
    BACKEND_URL = 'https://cryptosavings.preview.emergentagent.com/api'
    user_wallet = 'DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq'
    doge_address = 'DLZccCAopg8SJYdmUWdjEkGq9t7boXMKMe'
    
    async with aiohttp.ClientSession() as session:
        print('🔍 CHECKING DOGE DEPOSIT STATUS...')
        print(f'User Wallet: {user_wallet}')
        print(f'DOGE Address: {doge_address}')
        print('=' * 60)
        
        # Check DOGE balance at deposit address
        async with session.get(f'{BACKEND_URL}/wallet/balance/DOGE?wallet_address={doge_address}') as response:
            if response.status == 200:
                data = await response.json()
                if data.get('success'):
                    balance = data.get('balance', 0)
                    unconfirmed = data.get('unconfirmed', 0)
                    total = data.get('total', 0)
                    print(f'✅ DOGE BALANCE: {total} DOGE total ({balance} confirmed, {unconfirmed} unconfirmed)')
                else:
                    print(f'❌ Balance check failed: {data.get("error")}')
            else:
                print(f'❌ HTTP {response.status}: {await response.text()}')
        
        # Check user wallet balances
        async with session.get(f'{BACKEND_URL}/wallet/{user_wallet}') as response:
            if response.status == 200:
                data = await response.json()
                if data.get('success'):
                    wallet = data['wallet']
                    deposit_balance = wallet.get('deposit_balance', {})
                    print(f'\n💰 USER WALLET BALANCES:')
                    for currency, amount in deposit_balance.items():
                        if amount > 0:
                            print(f'  {currency}: {amount:,.2f}')
                    
                    total_value = (
                        deposit_balance.get('CRT', 0) * 0.15 +
                        deposit_balance.get('DOGE', 0) * 0.24 +
                        deposit_balance.get('TRX', 0) * 0.36 +
                        deposit_balance.get('USDC', 0) * 1.0
                    )
                    print(f'  Total Portfolio Value: ${total_value:,.2f}')
                else:
                    print(f'❌ Wallet check failed')
            else:
                print(f'❌ HTTP {response.status}: {await response.text()}')
        
        # Test manual deposit (will show cooldown status)
        payload = {'wallet_address': user_wallet, 'doge_address': doge_address}
        async with session.post(f'{BACKEND_URL}/deposit/doge/manual', json=payload) as response:
            if response.status == 200:
                data = await response.json()
                print(f'\n🔄 DEPOSIT STATUS: {data.get("message", "Unknown")}')
                if data.get('success'):
                    print(f'✅ Credited: {data.get("credited_amount", 0)} DOGE')
                else:
                    print(f'⏳ Status: {data.get("message")}')
            else:
                print(f'❌ HTTP {response.status}: {await response.text()}')

if __name__ == "__main__":
    asyncio.run(check_doge_deposit_status())