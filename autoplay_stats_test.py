#!/usr/bin/env python3
"""
Autoplay and Stats Testing - Test autoplay functionality and real-time stats
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

BACKEND_URL = "https://crypto-treasury.preview.emergentagent.com/api"
TEST_CREDENTIALS = {
    "username": "cryptoking",
    "password": "crt21million", 
    "wallet_address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq"
}

async def test_autoplay_and_stats():
    """Test autoplay functionality and real-time stats"""
    async with aiohttp.ClientSession() as session:
        wallet_address = TEST_CREDENTIALS["wallet_address"]
        
        print("🤖 AUTOPLAY & STATS TESTING")
        print("=" * 50)
        
        # 1. Test all games for autoplay compatibility
        print("\n1. AUTOPLAY COMPATIBILITY TEST:")
        games = ["Slot Machine", "Roulette", "Dice", "Plinko", "Keno", "Mines"]
        autoplay_results = {}
        
        for game in games:
            print(f"\n   Testing {game}:")
            
            # Test multiple rapid bets to simulate autoplay
            rapid_bets = []
            for i in range(3):
                bet_payload = {
                    "wallet_address": wallet_address,
                    "game_type": game,
                    "bet_amount": 1.0,
                    "currency": "CRT",
                    "network": "solana"
                }
                
                start_time = time.time()
                async with session.post(f"{BACKEND_URL}/games/bet", json=bet_payload) as response:
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            rapid_bets.append({
                                "bet": i + 1,
                                "result": data.get("result"),
                                "payout": data.get("payout", 0),
                                "response_time": response_time,
                                "game_id": data.get("game_id"),
                                "success": True
                            })
                            print(f"     Bet {i+1}: {data.get('result')} (payout: {data.get('payout', 0)}, time: {response_time:.2f}s)")
                        else:
                            rapid_bets.append({
                                "bet": i + 1,
                                "error": data.get("message"),
                                "response_time": response_time,
                                "success": False
                            })
                            print(f"     Bet {i+1}: FAILED - {data.get('message')}")
                    else:
                        rapid_bets.append({
                            "bet": i + 1,
                            "http_status": response.status,
                            "response_time": response_time,
                            "success": False
                        })
                        print(f"     Bet {i+1}: HTTP {response.status}")
                
                # Small delay between bets
                await asyncio.sleep(0.1)
            
            successful_bets = [b for b in rapid_bets if b.get("success")]
            avg_response_time = sum(b["response_time"] for b in successful_bets) / len(successful_bets) if successful_bets else 0
            
            autoplay_results[game] = {
                "successful_bets": len(successful_bets),
                "total_bets": len(rapid_bets),
                "success_rate": len(successful_bets) / len(rapid_bets) * 100,
                "avg_response_time": avg_response_time,
                "autoplay_ready": len(successful_bets) >= 2 and avg_response_time < 1.0
            }
            
            if autoplay_results[game]["autoplay_ready"]:
                print(f"   ✅ {game}: AUTOPLAY READY ({len(successful_bets)}/3 bets, {avg_response_time:.2f}s avg)")
            else:
                print(f"   ❌ {game}: NOT AUTOPLAY READY ({len(successful_bets)}/3 bets, {avg_response_time:.2f}s avg)")
        
        # 2. Test high-volume autoplay simulation
        print("\n2. HIGH-VOLUME AUTOPLAY SIMULATION:")
        print("   Testing 10 rapid successive bets...")
        
        high_volume_results = []
        start_total = time.time()
        
        for i in range(10):
            bet_payload = {
                "wallet_address": wallet_address,
                "game_type": "Slot Machine",  # Use slot machine for consistency
                "bet_amount": 1.0,
                "currency": "CRT",
                "network": "solana"
            }
            
            start_time = time.time()
            async with session.post(f"{BACKEND_URL}/games/bet", json=bet_payload) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status == 200:
                    data = await response.json()
                    if data.get("success"):
                        high_volume_results.append({
                            "bet_number": i + 1,
                            "result": data.get("result"),
                            "payout": data.get("payout", 0),
                            "response_time": response_time,
                            "success": True
                        })
                    else:
                        high_volume_results.append({
                            "bet_number": i + 1,
                            "error": data.get("message"),
                            "response_time": response_time,
                            "success": False
                        })
                else:
                    high_volume_results.append({
                        "bet_number": i + 1,
                        "http_status": response.status,
                        "response_time": response_time,
                        "success": False
                    })
        
        end_total = time.time()
        total_time = end_total - start_total
        
        successful_high_volume = [r for r in high_volume_results if r.get("success")]
        wins = [r for r in successful_high_volume if r.get("result") == "win"]
        losses = [r for r in successful_high_volume if r.get("result") == "loss"]
        
        print(f"   📊 Results: {len(successful_high_volume)}/10 successful")
        print(f"   🎰 Wins: {len(wins)}, Losses: {len(losses)}")
        print(f"   ⏱️  Total time: {total_time:.2f}s ({total_time/10:.2f}s per bet)")
        print(f"   🚀 Throughput: {len(successful_high_volume)/total_time:.1f} bets/second")
        
        if len(successful_high_volume) >= 8:  # 80% success rate
            print(f"   ✅ HIGH-VOLUME AUTOPLAY: READY FOR PRODUCTION")
        else:
            print(f"   ❌ HIGH-VOLUME AUTOPLAY: NOT READY ({len(successful_high_volume)}/10 success rate)")
        
        # 3. Test real-time stats tracking
        print("\n3. REAL-TIME STATS TRACKING:")
        
        # Get initial wallet state
        async with session.get(f"{BACKEND_URL}/wallet/{wallet_address}") as response:
            if response.status == 200:
                initial_data = await response.json()
                if initial_data.get("success"):
                    initial_wallet = initial_data["wallet"]
                    initial_crt = initial_wallet.get("deposit_balance", {}).get("CRT", 0)
                    initial_savings = initial_wallet.get("savings_balance", {}).get("CRT", 0)
                    initial_winnings = initial_wallet.get("winnings_balance", {}).get("CRT", 0)
                    
                    print(f"   📊 Initial State:")
                    print(f"     CRT Deposit: {initial_crt:,.2f}")
                    print(f"     CRT Savings: {initial_savings:,.2f}")
                    print(f"     CRT Winnings: {initial_winnings:,.2f}")
                    
                    # Place 3 test bets
                    print(f"\n   🎰 Placing 3 test bets...")
                    test_bet_results = []
                    
                    for i in range(3):
                        bet_payload = {
                            "wallet_address": wallet_address,
                            "game_type": "Dice",
                            "bet_amount": 5.0,
                            "currency": "CRT",
                            "network": "solana"
                        }
                        
                        async with session.post(f"{BACKEND_URL}/games/bet", json=bet_payload) as bet_response:
                            if bet_response.status == 200:
                                bet_data = await bet_response.json()
                                if bet_data.get("success"):
                                    test_bet_results.append({
                                        "bet": i + 1,
                                        "result": bet_data.get("result"),
                                        "payout": bet_data.get("payout", 0),
                                        "savings_contribution": bet_data.get("savings_contribution", 0)
                                    })
                                    print(f"     Bet {i+1}: {bet_data.get('result')} (payout: {bet_data.get('payout', 0)})")
                    
                    # Check updated wallet state
                    async with session.get(f"{BACKEND_URL}/wallet/{wallet_address}") as updated_response:
                        if updated_response.status == 200:
                            updated_data = await updated_response.json()
                            if updated_data.get("success"):
                                updated_wallet = updated_data["wallet"]
                                updated_crt = updated_wallet.get("deposit_balance", {}).get("CRT", 0)
                                updated_savings = updated_wallet.get("savings_balance", {}).get("CRT", 0)
                                updated_winnings = updated_wallet.get("winnings_balance", {}).get("CRT", 0)
                                
                                print(f"\n   📈 Updated State:")
                                print(f"     CRT Deposit: {initial_crt:,.2f} → {updated_crt:,.2f} (Δ {updated_crt - initial_crt:+.2f})")
                                print(f"     CRT Savings: {initial_savings:,.2f} → {updated_savings:,.2f} (Δ {updated_savings - initial_savings:+.2f})")
                                print(f"     CRT Winnings: {initial_winnings:,.2f} → {updated_winnings:,.2f} (Δ {updated_winnings - initial_winnings:+.2f})")
                                
                                # Check if balances updated correctly
                                balance_updated = (updated_crt != initial_crt) or (updated_savings != initial_savings) or (updated_winnings != initial_winnings)
                                
                                if balance_updated:
                                    print(f"   ✅ REAL-TIME BALANCE UPDATES: WORKING")
                                else:
                                    print(f"   ❌ REAL-TIME BALANCE UPDATES: NOT WORKING")
        
        # 4. Test currency selection for different games
        print("\n4. MULTI-CURRENCY GAME TESTING:")
        currencies_to_test = ["CRT", "DOGE"]  # Test with available currencies
        
        for currency in currencies_to_test:
            print(f"\n   Testing {currency} betting:")
            
            # Test different games with this currency
            currency_game_results = []
            for game in ["Slot Machine", "Dice", "Roulette"]:
                bet_payload = {
                    "wallet_address": wallet_address,
                    "game_type": game,
                    "bet_amount": 1.0 if currency == "CRT" else 0.1,  # Smaller amount for DOGE
                    "currency": currency,
                    "network": "solana" if currency == "CRT" else "dogecoin"
                }
                
                async with session.post(f"{BACKEND_URL}/games/bet", json=bet_payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success"):
                            currency_game_results.append({
                                "game": game,
                                "currency": currency,
                                "result": data.get("result"),
                                "success": True
                            })
                            print(f"     {game}: ✅ {data.get('result')}")
                        else:
                            currency_game_results.append({
                                "game": game,
                                "currency": currency,
                                "error": data.get("message"),
                                "success": False
                            })
                            print(f"     {game}: ❌ {data.get('message')}")
                    else:
                        print(f"     {game}: ❌ HTTP {response.status}")
            
            successful_currency_games = [r for r in currency_game_results if r.get("success")]
            print(f"   📊 {currency} Results: {len(successful_currency_games)}/3 games successful")
        
        print("\n" + "=" * 50)
        print("🎯 AUTOPLAY & STATS SUMMARY:")
        
        # Autoplay readiness summary
        autoplay_ready_games = [game for game, result in autoplay_results.items() if result["autoplay_ready"]]
        print(f"🤖 Autoplay Ready Games: {len(autoplay_ready_games)}/6")
        print(f"   ✅ Ready: {autoplay_ready_games}")
        
        not_ready_games = [game for game, result in autoplay_results.items() if not result["autoplay_ready"]]
        if not_ready_games:
            print(f"   ❌ Not Ready: {not_ready_games}")
        
        # High-volume performance
        if len(successful_high_volume) >= 8:
            print(f"🚀 High-Volume Performance: EXCELLENT ({len(successful_high_volume)}/10 bets)")
        else:
            print(f"⚠️  High-Volume Performance: NEEDS IMPROVEMENT ({len(successful_high_volume)}/10 bets)")
        
        print(f"📊 Average Response Time: {sum(r['response_time'] for r in successful_high_volume)/len(successful_high_volume):.3f}s" if successful_high_volume else "N/A")

if __name__ == "__main__":
    asyncio.run(test_autoplay_and_stats())