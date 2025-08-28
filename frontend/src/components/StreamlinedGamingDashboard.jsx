import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Gamepad2, TrendingUp, Wallet, RotateCcw, Play, Settings, DollarSign } from 'lucide-react';

const StreamlinedGamingDashboard = ({ userBalance, onNavigate, onGameSelect }) => {
    const [selectedCurrency, setSelectedCurrency] = useState('CRT');
    const [gameStats, setGameStats] = useState({
        totalGames: 1247,
        wins: 312,
        losses: 935,
        winRate: 25.0,
        totalWagered: 45680,
        totalWon: 12340,
        totalLost: 33340,
        netResult: -21000
    });

    const [realTimeStats, setRealTimeStats] = useState({
        currentStreak: 3,
        todayGames: 45,
        todayWins: 12,
        todayLosses: 33,
        liquidity: 1155522,
        savingsGrowth: 4622090
    });

    // Calculate balances for selected currency
    const getCurrentBalance = () => {
        if (!userBalance) return { gaming: 0, savings: 0, liquidity: 0, total: 0 };
        
        const gaming = (userBalance.deposit_balance?.[selectedCurrency] || 0) + 
                      (userBalance.winnings_balance?.[selectedCurrency] || 0);
        const savings = userBalance.savings_balance?.[selectedCurrency] || 0;
        
        // Estimate liquidity as percentage of total
        const total = gaming + savings;
        const liquidity = total * 0.15; // 15% as liquidity
        
        return { gaming, savings, liquidity, total };
    };

    const balances = getCurrentBalance();

    // Currency rates for conversion
    const currencyRates = {
        CRT: 0.15,
        DOGE: 0.221,
        TRX: 0.347,
        USDC: 1.0
    };

    const convertToUSD = (amount) => {
        return amount * (currencyRates[selectedCurrency] || 1);
    };

    // Available games
    const games = [
        { id: 'slots', name: 'Slot Machine', icon: '🎰', description: 'Classic 3-reel slots' },
        { id: 'roulette', name: 'Roulette', icon: '🎯', description: 'European roulette wheel' },
        { id: 'dice', name: 'Dice', icon: '🎲', description: 'Prediction dice game' },
        { id: 'plinko', name: 'Plinko', icon: '⚡', description: 'Drop and win' },
        { id: 'keno', name: 'Keno', icon: '🎱', description: 'Number lottery' },
        { id: 'mines', name: 'Mines', icon: '💎', description: 'Find gems, avoid mines' }
    ];

    return (
        <div className="w-full max-w-6xl mx-auto p-6 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 min-h-screen">
            {/* Header */}
            <div className="text-center mb-8">
                <h1 className="text-4xl font-bold bg-gradient-to-r from-gold-400 via-yellow-500 to-gold-600 bg-clip-text text-transparent mb-2">
                    🎰 GAMING DASHBOARD
                </h1>
                <p className="text-xl text-gray-300">Real-Time Gaming & Savings</p>
            </div>

            {/* Currency Selection */}
            <Card className="bg-slate-800/50 border-slate-600/30 backdrop-blur mb-6">
                <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h3 className="text-lg font-bold text-white">Select Gaming Currency</h3>
                            <p className="text-sm text-gray-400">Choose your preferred currency for all games</p>
                        </div>
                        
                        <Select value={selectedCurrency} onValueChange={setSelectedCurrency}>
                            <SelectTrigger className="w-48 bg-slate-700 border-slate-600 text-white">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="CRT">
                                    <div className="flex items-center space-x-2">
                                        <span>🟡</span>
                                        <span>CRT (${currencyRates.CRT})</span>
                                    </div>
                                </SelectItem>
                                <SelectItem value="DOGE">
                                    <div className="flex items-center space-x-2">
                                        <span>🐕</span>
                                        <span>DOGE (${currencyRates.DOGE})</span>
                                    </div>
                                </SelectItem>
                                <SelectItem value="TRX">
                                    <div className="flex items-center space-x-2">
                                        <span>🔺</span>
                                        <span>TRX (${currencyRates.TRX})</span>
                                    </div>
                                </SelectItem>
                                <SelectItem value="USDC">
                                    <div className="flex items-center space-x-2">
                                        <span>💵</span>
                                        <span>USDC (${currencyRates.USDC})</span>
                                    </div>
                                </SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </CardContent>
            </Card>

            {/* Real-Time Stats - Focused on W/L and Liquidity */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <Card className="bg-gradient-to-br from-green-900/50 to-emerald-900/50 border-green-500/30">
                    <CardContent className="p-4 text-center">
                        <div className="text-2xl font-bold text-white">
                            {gameStats.wins}/{gameStats.losses}
                        </div>
                        <div className="text-sm text-emerald-300">Wins/Losses</div>
                        <div className="text-xs text-gray-400">{gameStats.winRate}% Win Rate</div>
                    </CardContent>
                </Card>
                
                <Card className="bg-gradient-to-br from-blue-900/50 to-cyan-900/50 border-blue-500/30">
                    <CardContent className="p-4 text-center">
                        <div className="text-2xl font-bold text-white">
                            ${convertToUSD(balances.liquidity).toLocaleString()}
                        </div>
                        <div className="text-sm text-cyan-300">Liquidity Available</div>
                        <div className="text-xs text-gray-400">{balances.liquidity.toFixed(0)} {selectedCurrency}</div>
                    </CardContent>
                </Card>
                
                <Card className="bg-gradient-to-br from-purple-900/50 to-indigo-900/50 border-purple-500/30">
                    <CardContent className="p-4 text-center">
                        <div className="text-2xl font-bold text-white">
                            {balances.gaming.toLocaleString()}
                        </div>
                        <div className="text-sm text-purple-300">Gaming Balance</div>
                        <div className="text-xs text-gray-400">${convertToUSD(balances.gaming).toLocaleString()}</div>
                    </CardContent>
                </Card>
                
                <Card className="bg-gradient-to-br from-gold-900/50 to-yellow-900/50 border-gold-500/30">
                    <CardContent className="p-4 text-center">
                        <div className="text-2xl font-bold text-white">
                            {balances.savings.toLocaleString()}
                        </div>
                        <div className="text-sm text-gold-300">Savings Vault</div>
                        <div className="text-xs text-gray-400">${convertToUSD(balances.savings).toLocaleString()}</div>
                    </CardContent>
                </Card>
            </div>

            {/* Treasury Wallets Visual */}
            <Card className="bg-slate-800/50 border-slate-600/30 backdrop-blur mb-6">
                <CardHeader>
                    <CardTitle className="flex items-center text-gold-300">
                        <Wallet className="w-5 h-5 mr-2" />
                        Treasury Wallets ({selectedCurrency})
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {/* Savings Treasury */}
                        <div className="bg-emerald-900/20 p-4 rounded-lg border border-emerald-500/30">
                            <div className="text-center">
                                <div className="text-3xl mb-2">🏦</div>
                                <div className="font-bold text-emerald-300">Savings Treasury</div>
                                <div className="text-2xl font-bold text-white mt-2">
                                    {balances.savings.toLocaleString()} {selectedCurrency}
                                </div>
                                <div className="text-sm text-gray-400">
                                    ${convertToUSD(balances.savings).toLocaleString()}
                                </div>
                                <Badge className="mt-2 bg-emerald-600">60% Allocation</Badge>
                            </div>
                        </div>

                        {/* Liquidity Treasury */}
                        <div className="bg-cyan-900/20 p-4 rounded-lg border border-cyan-500/30">
                            <div className="text-center">
                                <div className="text-3xl mb-2">💧</div>
                                <div className="font-bold text-cyan-300">Liquidity Treasury</div>
                                <div className="text-2xl font-bold text-white mt-2">
                                    {balances.liquidity.toFixed(0)} {selectedCurrency}
                                </div>
                                <div className="text-sm text-gray-400">
                                    ${convertToUSD(balances.liquidity).toLocaleString()}
                                </div>
                                <Badge className="mt-2 bg-cyan-600">30% Allocation</Badge>
                            </div>
                        </div>

                        {/* Gaming Treasury */}
                        <div className="bg-purple-900/20 p-4 rounded-lg border border-purple-500/30">
                            <div className="text-center">
                                <div className="text-3xl mb-2">🎮</div>
                                <div className="font-bold text-purple-300">Gaming Treasury</div>
                                <div className="text-2xl font-bold text-white mt-2">
                                    {balances.gaming.toLocaleString()} {selectedCurrency}
                                </div>
                                <div className="text-sm text-gray-400">
                                    ${convertToUSD(balances.gaming).toLocaleString()}
                                </div>
                                <Badge className="mt-2 bg-purple-600">10% Allocation</Badge>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Game Selection */}
            <Card className="bg-slate-800/50 border-slate-600/30 backdrop-blur">
                <CardHeader>
                    <CardTitle className="flex items-center text-gold-300">
                        <Gamepad2 className="w-5 h-5 mr-2" />
                        Select Casino Game
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {games.map((game) => (
                            <div 
                                key={game.id}
                                onClick={() => onGameSelect?.(game.id)}
                                className="bg-slate-700/50 p-4 rounded-lg border border-slate-600/30 hover:border-gold-400/50 cursor-pointer transition-all hover:scale-105"
                            >
                                <div className="text-center">
                                    <div className="text-4xl mb-2">{game.icon}</div>
                                    <div className="font-bold text-white">{game.name}</div>
                                    <div className="text-sm text-gray-400 mt-1">{game.description}</div>
                                    <div className="text-xs text-gold-300 mt-2">
                                        Playing with {selectedCurrency}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Quick Actions */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                <Button 
                    className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 h-16"
                    onClick={() => onNavigate?.('savings')}
                >
                    <div className="text-center">
                        <div className="text-2xl mb-1">💰</div>
                        <div className="text-sm">Savings Vault</div>
                    </div>
                </Button>
                
                <Button 
                    className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 h-16"
                    onClick={() => onNavigate?.('wallet')}
                >
                    <div className="text-center">
                        <div className="text-2xl mb-1">💳</div>
                        <div className="text-sm">Wallet Manager</div>
                    </div>
                </Button>
                
                <Button 
                    className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 h-16"
                    onClick={() => onNavigate?.('history')}
                >
                    <div className="text-center">
                        <div className="text-2xl mb-1">📊</div>
                        <div className="text-sm">History</div>
                    </div>
                </Button>
                
                <Button 
                    className="bg-gradient-to-r from-gold-600 to-yellow-600 hover:from-gold-700 hover:to-yellow-700 h-16"
                    onClick={() => onNavigate?.('dashboard')}
                >
                    <div className="text-center">
                        <div className="text-2xl mb-1">📈</div>
                        <div className="text-sm">Full Dashboard</div>
                    </div>
                </Button>
            </div>
        </div>
    );
};

export default StreamlinedGamingDashboard;