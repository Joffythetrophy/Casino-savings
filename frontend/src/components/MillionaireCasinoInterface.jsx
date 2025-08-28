import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Coins, Zap, Crown, Diamond, Star, Trophy, Target, Rocket } from 'lucide-react';

const MillionaireCasinoInterface = ({ userBalance, onNavigate, onGameSelect }) => {
    const [selectedCurrency, setSelectedCurrency] = useState('CRT');
    const [refreshKey, setRefreshKey] = useState(0);

    // Calculate real-time balances
    const getBalances = () => {
        if (!userBalance) return { winnings: 0, savings: 0, liquidity: 0, gaming: 0 };
        
        const winnings = userBalance.winnings_balance?.[selectedCurrency] || 0;
        const savings = userBalance.savings_balance?.[selectedCurrency] || 0;
        const deposit = userBalance.deposit_balance?.[selectedCurrency] || 0;
        const gaming = deposit; // Gaming balance is deposit balance
        const liquidity = gaming * 0.15; // 15% of gaming as available liquidity
        
        return { winnings, savings, liquidity, gaming };
    };

    const balances = getBalances();

    // Currency rates for USD conversion
    const currencyRates = {
        CRT: 0.15,
        DOGE: 0.221,
        TRX: 0.347,
        USDC: 1.0
    };

    const toUSD = (amount) => amount * (currencyRates[selectedCurrency] || 1);

    // Premium casino games with better graphics
    const premiumGames = [
        { id: 'slots', name: 'Diamond Slots', icon: '💎', hot: true, multiplier: '50,000x' },
        { id: 'roulette', name: 'VIP Roulette', icon: '🎯', hot: true, multiplier: '35:1' },
        { id: 'blackjack', name: 'Elite Blackjack', icon: '🂡', hot: false, multiplier: '3:2' },
        { id: 'baccarat', name: 'High Roller Baccarat', icon: '👑', hot: false, multiplier: '8:1' },
        { id: 'dice', name: 'Crypto Dice', icon: '🎲', hot: true, multiplier: '999x' },
        { id: 'plinko', name: 'Million Plinko', icon: '⚡', hot: false, multiplier: '1000x' },
        { id: 'keno', name: 'Luxury Keno', icon: '🎱', hot: false, multiplier: '10,000x' },
        { id: 'mines', name: 'Diamond Mines', icon: '💎', hot: true, multiplier: '5000x' },
        { id: 'crash', name: 'Rocket Crash', icon: '🚀', hot: true, multiplier: '∞' },
        { id: 'wheel', name: 'Fortune Wheel', icon: '🎡', hot: false, multiplier: '50x' },
        { id: 'poker', name: 'Texas Hold\'em', icon: '♠️', hot: false, multiplier: 'Unlimited' },
        { id: 'lottery', name: 'Crypto Lottery', icon: '🎟️', hot: true, multiplier: 'Jackpot' }
    ];

    return (
        <div className="w-full max-w-7xl mx-auto p-6 bg-gradient-to-br from-slate-900 via-purple-900 to-black min-h-screen">
            {/* Premium Header */}
            <div className="text-center mb-6">
                <h1 className="text-5xl font-bold bg-gradient-to-r from-gold-400 via-yellow-500 to-gold-600 bg-clip-text text-transparent mb-2 flex items-center justify-center">
                    <Crown className="w-12 h-12 text-gold-400 mr-4" />
                    💎 MILLIONAIRE CASINO 💎
                    <Crown className="w-12 h-12 text-gold-400 ml-4" />
                </h1>
                <p className="text-xl text-gray-300">Where Legends Are Made & Fortunes Are Won</p>
            </div>

            {/* Currency Selection - Premium Style */}
            <Card className="bg-gradient-to-br from-gold-900/30 to-yellow-900/30 border-gold-500/50 backdrop-blur mb-6">
                <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <Coins className="w-8 h-8 text-gold-400" />
                            <div>
                                <h3 className="text-2xl font-bold text-gold-400">Gaming Currency</h3>
                                <p className="text-gray-300">Select your weapon of choice</p>
                            </div>
                        </div>
                        
                        <Select value={selectedCurrency} onValueChange={setSelectedCurrency}>
                            <SelectTrigger className="w-64 bg-black/50 border-gold-400/50 text-white text-lg h-14">
                                <SelectValue />
                            </SelectTrigger>
                            <SelectContent className="bg-slate-900 border-gold-400/50">
                                <SelectItem value="CRT">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-6 h-6 bg-gradient-to-r from-yellow-400 to-gold-500 rounded-full"></div>
                                        <span className="text-lg">CRT - Premium Token</span>
                                    </div>
                                </SelectItem>
                                <SelectItem value="DOGE">
                                    <div className="flex items-center space-x-3">
                                        <div className="text-2xl">🐕</div>
                                        <span className="text-lg">DOGE - The People's Choice</span>
                                    </div>
                                </SelectItem>
                                <SelectItem value="TRX">
                                    <div className="flex items-center space-x-3">
                                        <div className="text-2xl">🔺</div>
                                        <span className="text-lg">TRX - Speed & Power</span>
                                    </div>
                                </SelectItem>
                                <SelectItem value="USDC">
                                    <div className="flex items-center space-x-3">
                                        <div className="text-2xl">💵</div>
                                        <span className="text-lg">USDC - Stable Luxury</span>
                                    </div>
                                </SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </CardContent>
            </Card>

            {/* FIXED: Treasury Wallets - Proper Labels & All Currencies */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {/* Winnings Wallet */}
                <Card className="bg-gradient-to-br from-emerald-900/50 to-green-900/50 border-emerald-500/30 backdrop-blur">
                    <CardHeader className="text-center">
                        <CardTitle className="flex items-center justify-center text-emerald-300 text-xl">
                            <Trophy className="w-6 h-6 mr-2" />
                            🏆 WINNINGS WALLET
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="text-center">
                        <div className="text-4xl font-bold text-white mb-2">
                            {balances.winnings.toLocaleString()} {selectedCurrency}
                        </div>
                        <div className="text-sm text-gray-400 mb-4">
                            ${toUSD(balances.winnings).toLocaleString()} USD
                        </div>
                        
                        {/* All Currencies Display */}
                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-yellow-400">🟡 CRT:</span>
                                <span className="text-white">{(userBalance?.winnings_balance?.CRT || 0).toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-orange-400">🐕 DOGE:</span>
                                <span className="text-white">{(userBalance?.winnings_balance?.DOGE || 0).toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-red-400">🔺 TRX:</span>
                                <span className="text-white">{(userBalance?.winnings_balance?.TRX || 0).toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-green-400">💵 USDC:</span>
                                <span className="text-white">{(userBalance?.winnings_balance?.USDC || 0).toLocaleString()}</span>
                            </div>
                        </div>
                        
                        <Badge className="mt-4 bg-emerald-600">✅ Available for Gaming</Badge>
                    </CardContent>
                </Card>

                {/* Savings Wallet */}
                <Card className="bg-gradient-to-br from-blue-900/50 to-indigo-900/50 border-blue-500/30 backdrop-blur">
                    <CardHeader className="text-center">
                        <CardTitle className="flex items-center justify-center text-blue-300 text-xl">
                            <Diamond className="w-6 h-6 mr-2" />
                            💎 SAVINGS VAULT
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="text-center">
                        <div className="text-4xl font-bold text-white mb-2">
                            {balances.savings.toLocaleString()} {selectedCurrency}
                        </div>
                        <div className="text-sm text-gray-400 mb-4">
                            ${toUSD(balances.savings).toLocaleString()} USD
                        </div>
                        
                        {/* All Currencies Display */}
                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-yellow-400">🟡 CRT:</span>
                                <span className="text-white">{(userBalance?.savings_balance?.CRT || 0).toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-orange-400">🐕 DOGE:</span>
                                <span className="text-white">{(userBalance?.savings_balance?.DOGE || 0).toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-red-400">🔺 TRX:</span>
                                <span className="text-white">{(userBalance?.savings_balance?.TRX || 0).toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-green-400">💵 USDC:</span>
                                <span className="text-white">{(userBalance?.savings_balance?.USDC || 0).toLocaleString()}</span>
                            </div>
                        </div>
                        
                        <Badge className="mt-4 bg-blue-600">🔒 Secured & Growing</Badge>
                    </CardContent>
                </Card>

                {/* Liquidity Pool */}
                <Card className="bg-gradient-to-br from-purple-900/50 to-pink-900/50 border-purple-500/30 backdrop-blur">
                    <CardHeader className="text-center">
                        <CardTitle className="flex items-center justify-center text-purple-300 text-xl">
                            <Zap className="w-6 h-6 mr-2" />
                            ⚡ LIQUIDITY POOL
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="text-center">
                        <div className="text-4xl font-bold text-white mb-2">
                            {balances.liquidity.toFixed(0)} {selectedCurrency}
                        </div>
                        <div className="text-sm text-gray-400 mb-4">
                            ${toUSD(balances.liquidity).toLocaleString()} USD
                        </div>
                        
                        {/* All Currencies Display */}
                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-yellow-400">🟡 CRT:</span>
                                <span className="text-white">{((userBalance?.deposit_balance?.CRT || 0) * 0.15).toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-orange-400">🐕 DOGE:</span>
                                <span className="text-white">{((userBalance?.deposit_balance?.DOGE || 0) * 0.15).toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-red-400">🔺 TRX:</span>
                                <span className="text-white">{((userBalance?.deposit_balance?.TRX || 0) * 0.15).toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-green-400">💵 USDC:</span>
                                <span className="text-white">{((userBalance?.deposit_balance?.USDC || 0) * 0.15).toLocaleString()}</span>
                            </div>
                        </div>
                        
                        <Badge className="mt-4 bg-purple-600">💧 Available for Withdrawal</Badge>
                    </CardContent>
                </Card>
            </div>

            {/* FIXED: Gaming Balance - Clear & Real-time */}
            <Card className="bg-gradient-to-br from-gold-900/50 to-yellow-900/50 border-gold-500/50 backdrop-blur mb-8">
                <CardHeader>
                    <CardTitle className="flex items-center text-gold-300 text-2xl">
                        <Star className="w-8 h-8 mr-3" />
                        🎮 GAMING BALANCE - READY TO PLAY
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="text-center">
                            <div className="text-5xl font-bold text-gold-400 mb-2">
                                {balances.gaming.toLocaleString()} {selectedCurrency}
                            </div>
                            <div className="text-xl text-gray-300">
                                ${toUSD(balances.gaming).toLocaleString()} USD Available
                            </div>
                            <Badge className="mt-3 bg-gold-600 text-black text-lg px-4 py-2">
                                ✅ READY FOR ALL GAMES
                            </Badge>
                        </div>
                        
                        <div className="bg-black/30 p-4 rounded-lg">
                            <h4 className="text-lg font-bold text-gold-400 mb-3">💡 How Gaming Balance Works:</h4>
                            <ul className="text-sm text-gray-300 space-y-1">
                                <li>• Gaming Balance = Your deposit wallet funds</li>
                                <li>• Use ANY currency for ANY game</li>
                                <li>• Losses automatically save to vault</li>
                                <li>• Winnings added to winnings wallet</li>
                                <li>• Real-time updates after every bet</li>
                            </ul>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* ENHANCED: Premium Casino Games Grid */}
            <Card className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-600/30 backdrop-blur">
                <CardHeader>
                    <CardTitle className="flex items-center text-white text-3xl">
                        <Target className="w-8 h-8 mr-3" />
                        🎰 MILLIONAIRE CASINO GAMES
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {premiumGames.map((game) => (
                            <div 
                                key={game.id}
                                onClick={() => onGameSelect?.(game.id)}
                                className="relative bg-gradient-to-br from-slate-700/50 to-slate-800/50 p-6 rounded-xl border border-slate-600/30 hover:border-gold-400/50 cursor-pointer transition-all hover:scale-105 hover:shadow-2xl group"
                            >
                                {game.hot && (
                                    <div className="absolute -top-2 -right-2">
                                        <Badge className="bg-red-600 text-white animate-pulse">🔥 HOT</Badge>
                                    </div>
                                )}
                                
                                <div className="text-center">
                                    <div className="text-5xl mb-3 group-hover:scale-110 transition-transform">
                                        {game.icon}
                                    </div>
                                    <div className="font-bold text-white text-lg mb-1">{game.name}</div>
                                    <div className="text-sm text-gray-400 mb-2">Max: {game.multiplier}</div>
                                    <div className="text-xs text-gold-300">
                                        Playing with {selectedCurrency}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Action Buttons */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
                <Button 
                    className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 h-20 text-lg"
                    onClick={() => onNavigate?.('wallet')}
                >
                    <div className="text-center">
                        <div className="text-3xl mb-1">💳</div>
                        <div>Wallet Manager</div>
                    </div>
                </Button>
                
                <Button 
                    className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 h-20 text-lg"
                    onClick={() => window.open('https://nowpayments.io/payment/?iid=4383583691&paymentId=5914238505', '_blank')}
                >
                    <div className="text-center">
                        <div className="text-3xl mb-1">💰</div>
                        <div>Add Funds</div>
                    </div>
                </Button>
                
                <Button 
                    className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 h-20 text-lg"
                    onClick={() => setRefreshKey(prev => prev + 1)}
                >
                    <div className="text-center">
                        <div className="text-3xl mb-1">🔄</div>
                        <div>Refresh Balances</div>
                    </div>
                </Button>
                
                <Button 
                    className="bg-gradient-to-r from-gold-600 to-yellow-600 hover:from-gold-700 hover:to-yellow-700 h-20 text-lg"
                    onClick={() => onNavigate?.('dashboard')}
                >
                    <div className="text-center">
                        <div className="text-3xl mb-1">📊</div>
                        <div>Analytics</div>
                    </div>
                </Button>
            </div>
        </div>
    );
};

export default MillionaireCasinoInterface;