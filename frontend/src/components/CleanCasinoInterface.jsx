import React, { useState, useEffect } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import SlotMachine from './CasinoGames/SlotMachine';
import Roulette from './CasinoGames/Roulette';
import Dice from './CasinoGames/Dice';
import Plinko from './CasinoGames/Plinko';
import Keno from './CasinoGames/Keno';
import Mines from './CasinoGames/Mines';

const CleanCasinoInterface = ({ userBalance }) => {
    const [currentGame, setCurrentGame] = useState(null);
    const [orcaPools, setOrcaPools] = useState([]);
    const [orcaPrice, setOrcaPrice] = useState(null);

    // Simple balance calculation - just show DOGE balance
    const dogeBalance = userBalance?.deposit_balance?.DOGE || 0;
    const balanceUSD = dogeBalance * 0.221;

    // Games array
    const games = [
        { id: 'slots', name: 'Slots', component: SlotMachine, icon: '💎' },
        { id: 'roulette', name: 'Roulette', component: Roulette, icon: '🎯' },
        { id: 'dice', name: 'Dice', component: Dice, icon: '🎲' },
        { id: 'plinko', name: 'Plinko', component: Plinko, icon: '⚡' },
        { id: 'keno', name: 'Keno', component: Keno, icon: '🎱' },
        { id: 'mines', name: 'Mines', component: Mines, icon: '💣' }
    ];

    // Fetch Orca pool data
    useEffect(() => {
        const fetchOrcaData = async () => {
            try {
                // Fetch pool data
                const poolsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/dex/pools`);
                if (poolsResponse.ok) {
                    const poolsData = await poolsResponse.json();
                    setOrcaPools(poolsData.pools || []);
                }

                // Fetch price data
                const priceResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/dex/crt-price`);
                if (priceResponse.ok) {
                    const priceData = await priceResponse.json();
                    setOrcaPrice(priceData.price_data);
                }
            } catch (error) {
                console.error('Failed to fetch Orca data:', error);
            }
        };

        fetchOrcaData();
        const interval = setInterval(fetchOrcaData, 30000); // Update every 30 seconds
        return () => clearInterval(interval);
    }, []);

    // Handle game click
    const handleGameClick = (gameId) => {
        const game = games.find(g => g.id === gameId);
        if (game) {
            setCurrentGame(game);
        }
    };

    // Handle back to lobby
    const handleBackToLobby = () => {
        setCurrentGame(null);
    };

    // Add liquidity from winnings
    const handleAddLiquidity = async (currency, amount) => {
        try {
            const user = JSON.parse(localStorage.getItem('casino_user') || '{}');
            const authToken = localStorage.getItem('casino_auth_token');

            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/orca/add-liquidity`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    wallet_address: user.wallet_address,
                    currency: currency,
                    amount: amount,
                    source: 'winnings'
                })
            });

            const data = await response.json();
            if (data.success) {
                alert(`✅ Successfully added ${amount} ${currency} liquidity to Orca pool!`);
                // Refresh balance and pool data
                window.location.reload();
            } else {
                alert(`❌ Failed to add liquidity: ${data.message}`);
            }
        } catch (error) {
            console.error('Add liquidity failed:', error);
            alert('❌ Failed to add liquidity - please try again');
        }
    };

    // If game selected, show game
    if (currentGame) {
        const GameComponent = currentGame.component;
        return (
            <div className="min-h-screen bg-gradient-to-br from-casino-green-900 via-emerald-casino-800 to-casino-green-950">
                <GameComponent onBack={handleBackToLobby} />
            </div>
        );
    }

    return (
        <div className="w-full max-w-4xl mx-auto p-6 min-h-screen">
            {/* Simple Header */}
            <div className="text-center mb-8">
                <h1 className="text-5xl font-bold text-casino-green-400 mb-4 glow-green">
                    🐅 CRT CASINO 🐅
                </h1>
                
                {/* SIMPLE BALANCE - NO CONFUSION */}
                <div className="card-green p-6 rounded-xl border border-casino-green-500/50 mb-6 glow-green">
                    <div className="text-3xl font-bold text-casino-green-100 mb-2">
                        {dogeBalance.toLocaleString()} DOGE
                    </div>
                    <div className="text-xl text-casino-green-200">
                        ${balanceUSD.toLocaleString()} USD
                    </div>
                    <div className="text-sm text-casino-green-400 mt-2 pulse-green">
                        ✅ Ready to Hunt Big Wins
                    </div>
                </div>
            </div>

            {/* Games Grid - Green Theme */}
            <div className="grid grid-cols-3 gap-4 mb-8">
                {games.map((game) => (
                    <Button
                        key={game.id}
                        onClick={() => handleGameClick(game.id)}
                        className="h-28 game-card-green text-casino-green-100 hover:text-white shadow-lg hover:shadow-casino-green-500/50"
                    >
                        <div className="text-center">
                            <div className="text-4xl mb-2">{game.icon}</div>
                            <div className="text-sm font-bold">{game.name}</div>
                        </div>
                    </Button>
                ))}
            </div>

            {/* ORCA POOL STATS & DATA - Replacing Donation Widget */}
            <Card className="card-green border-casino-green-500/40 glow-green mb-6">
                <CardContent className="p-6">
                    <div className="text-center mb-6">
                        <h3 className="text-xl font-bold text-casino-green-400 mb-4">
                            🌊 ORCA CRT LIQUIDITY POOLS 🌊
                        </h3>
                    </div>
                    
                    {/* Pool Statistics */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        <div className="text-center p-4 rounded-lg bg-casino-green-900/30 border border-casino-green-500/50">
                            <p className="text-sm text-casino-green-300">CRT Price</p>
                            <p className="text-xl font-bold text-casino-green-100">
                                ${orcaPrice?.price?.usd?.toFixed(4) || '0.0100'}
                            </p>
                            <p className="text-xs text-casino-green-300">
                                {orcaPrice?.price?.sol?.toFixed(6) || '0.0001'} SOL
                            </p>
                        </div>
                        <div className="text-center p-4 rounded-lg bg-casino-green-900/30 border border-casino-green-500/50">
                            <p className="text-sm text-casino-green-300">Active Pools</p>
                            <p className="text-xl font-bold text-casino-green-100">
                                {orcaPools?.length || 0}
                            </p>
                            <p className="text-xs text-casino-green-300">CRT Liquidity Pairs</p>
                        </div>
                        <div className="text-center p-4 rounded-lg bg-casino-green-900/30 border border-casino-green-500/50">
                            <p className="text-sm text-casino-green-300">Total TVL</p>
                            <p className="text-xl font-bold text-casino-green-100">
                                ${orcaPrice?.market_data?.liquidity?.total_value_locked?.toLocaleString() || '40,000'}
                            </p>
                            <p className="text-xs text-casino-green-300">Across all CRT pools</p>
                        </div>
                    </div>

                    {/* Active Pools Display */}
                    <div className="space-y-3 mb-6">
                        {orcaPools && orcaPools.length > 0 ? (
                            orcaPools.map((pool, index) => (
                                <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-casino-green-900/20 border border-casino-green-500/30">
                                    <div className="flex items-center space-x-3">
                                        <span className="text-lg">🌊</span>
                                        <div>
                                            <p className="font-bold text-casino-green-100">{pool.pool_pair}</p>
                                            <p className="text-xs text-casino-green-300">
                                                {pool.dex} • Address: {pool.pool_address?.slice(0, 8)}...
                                            </p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm font-bold text-casino-green-200">{pool.status}</p>
                                        {pool.transaction_hash && (
                                            <a 
                                                href={`https://explorer.solana.com/tx/${pool.transaction_hash}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-xs text-casino-green-400 hover:text-casino-green-300"
                                            >
                                                View TX ↗
                                            </a>
                                        )}
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="text-center py-4 text-casino-green-300">
                                <p>🔍 No active Orca pools detected</p>
                                <p className="text-xs mt-1">Admin can create pools from DEX Manager</p>
                            </div>
                        )}
                    </div>

                    {/* Liquidity Addition from Winnings */}
                    <div className="border-t border-casino-green-500/30 pt-4">
                        <h4 className="text-casino-green-300 font-bold mb-3 text-center">💰 Add Liquidity from Your Wins 💰</h4>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                            {['CRT', 'DOGE', 'USDC'].map(currency => {
                                const balance = userBalance?.winnings_balance?.[currency] || 0;
                                return (
                                    <div key={currency} className="p-3 rounded-lg bg-casino-green-900/20 border border-casino-green-500/30">
                                        <p className="text-xs text-casino-green-300 mb-1">Your {currency} Winnings</p>
                                        <p className="text-lg font-bold text-casino-green-100 mb-2">
                                            {balance.toLocaleString()}
                                        </p>
                                        {balance > 0 && (
                                            <Button
                                                onClick={() => handleAddLiquidity(currency, balance * 0.5)}
                                                className="w-full text-xs bg-casino-green-600 hover:bg-casino-green-500 text-white"
                                            >
                                                Add 50% to Pool
                                            </Button>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                        <p className="text-xs text-casino-green-400 text-center mt-3">
                            🚀 Convert your wins into pool liquidity and earn trading fees! 🚀
                        </p>
                    </div>
                </CardContent>
            </Card>

            {/* Simple Instructions - Green Theme */}
            <div className="text-center mt-8">
                <div className="card-green p-6 rounded-xl border border-casino-green-500/40">
                    <h4 className="text-casino-green-300 font-bold mb-3 text-lg">🎯 How to Play & Fund Pools:</h4>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div className="text-casino-green-200">
                            <strong>1. Play Games</strong><br/>
                            Hunt big wins with DOGE balance!
                        </div>
                        <div className="text-casino-green-200">
                            <strong>2. Win Big</strong><br/>
                            Accumulate winnings across currencies
                        </div>
                        <div className="text-casino-green-200">
                            <strong>3. Add Liquidity</strong><br/>
                            Use wins to fund Orca pools above
                        </div>
                    </div>
                    <div className="mt-3 text-xs text-casino-green-400">
                        🏆 May the Tiger bring you fortune and pool profits! 🏆
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CleanCasinoInterface;