import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Crown, Coins, Trophy, Diamond } from 'lucide-react';
import SlotMachine from './CasinoGames/SlotMachine';
import Roulette from './CasinoGames/Roulette';
import Dice from './CasinoGames/Dice';
import Plinko from './CasinoGames/Plinko';
import Keno from './CasinoGames/Keno';
import Mines from './CasinoGames/Mines';

const SimplifiedCasinoInterface = ({ userBalance }) => {
    const [currentGame, setCurrentGame] = useState(null);
    const [selectedCurrency, setSelectedCurrency] = useState('DOGE');

    // Calculate gaming balance
    const getGamingBalance = () => {
        if (!userBalance) return 0;
        return userBalance.deposit_balance?.[selectedCurrency] || 0;
    };

    const gamingBalance = getGamingBalance();

    // Games with proper navigation
    const games = [
        { id: 'slots', name: 'Diamond Slots', component: SlotMachine, icon: '💎' },
        { id: 'roulette', name: 'VIP Roulette', component: Roulette, icon: '🎯' },
        { id: 'dice', name: 'Crypto Dice', component: Dice, icon: '🎲' },
        { id: 'plinko', name: 'Million Plinko', component: Plinko, icon: '⚡' },
        { id: 'keno', name: 'Luxury Keno', component: Keno, icon: '🎱' },
        { id: 'mines', name: 'Diamond Mines', component: Mines, icon: '💣' }
    ];

    // Handle game selection
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

    // If a game is selected, render the game component
    if (currentGame) {
        const GameComponent = currentGame.component;
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-black">
                <GameComponent onBack={handleBackToLobby} />
            </div>
        );
    }

    return (
        <div className="w-full max-w-6xl mx-auto p-6 bg-gradient-to-br from-slate-900 via-purple-900 to-black min-h-screen">
            {/* Premium Header */}
            <div className="text-center mb-8">
                <h1 className="text-5xl font-bold bg-gradient-to-r from-gold-400 via-yellow-500 to-gold-600 bg-clip-text text-transparent mb-2 flex items-center justify-center">
                    <Crown className="w-12 h-12 text-gold-400 mr-4" />
                    💎 MILLIONAIRE CASINO 💎
                    <Crown className="w-12 h-12 text-gold-400 ml-4" />
                </h1>
                <p className="text-xl text-gray-300">$50,000 DOGE Donation Ready</p>
            </div>

            {/* Gaming Balance Display */}
            <Card className="bg-gradient-to-br from-gold-900/50 to-yellow-900/50 border-gold-500/50 backdrop-blur mb-8">
                <CardHeader>
                    <CardTitle className="flex items-center text-gold-300 text-2xl justify-center">
                        <Coins className="w-8 h-8 mr-3" />
                        🎮 GAMING BALANCE
                    </CardTitle>
                </CardHeader>
                <CardContent className="text-center">
                    <div className="text-5xl font-bold text-gold-400 mb-2">
                        {gamingBalance.toLocaleString()} DOGE
                    </div>
                    <div className="text-xl text-gray-300">
                        ${(gamingBalance * 0.221).toLocaleString()} USD Available
                    </div>
                    <div className="mt-4">
                        <select 
                            value={selectedCurrency}
                            onChange={(e) => setSelectedCurrency(e.target.value)}
                            className="bg-black/50 border-gold-400/50 text-white px-4 py-2 rounded-lg"
                        >
                            <option value="CRT">🟡 CRT Token</option>
                            <option value="DOGE">🐕 DOGE</option>
                            <option value="TRX">🔺 TRX</option>
                            <option value="USDC">💵 USDC</option>
                        </select>
                    </div>
                </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Games Section */}
                <Card className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-600/30 backdrop-blur">
                    <CardHeader>
                        <CardTitle className="flex items-center text-white text-2xl">
                            <Trophy className="w-6 h-6 mr-3" />
                            🎰 CASINO GAMES
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-2 gap-4">
                            {games.map((game) => (
                                <div 
                                    key={game.id}
                                    onClick={() => handleGameClick(game.id)}
                                    className="bg-gradient-to-br from-slate-700/50 to-slate-800/50 p-4 rounded-xl border border-slate-600/30 hover:border-gold-400/50 cursor-pointer transition-all hover:scale-105 hover:shadow-2xl group"
                                >
                                    <div className="text-center">
                                        <div className="text-4xl mb-2 group-hover:scale-110 transition-transform">
                                            {game.icon}
                                        </div>
                                        <div className="font-bold text-white text-sm">{game.name}</div>
                                        <div className="text-xs text-gold-300 mt-1">
                                            Play with {selectedCurrency}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* NOWPayments Donation Widget */}
                <Card className="bg-gradient-to-br from-green-900/50 to-emerald-900/50 border-green-500/30 backdrop-blur">
                    <CardHeader>
                        <CardTitle className="flex items-center text-emerald-300 text-2xl">
                            <Diamond className="w-6 h-6 mr-3" />
                            💰 $50K DOGE DONATION
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-center mb-4">
                            <p className="text-white mb-2">Donate to: <span className="text-gold-400">D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda</span></p>
                            <p className="text-gray-300 text-sm">Target: $50,000 worth of DOGE</p>
                        </div>
                        
                        {/* NOWPayments Widget */}
                        <div className="flex justify-center">
                            <iframe 
                                src="https://nowpayments.io/embeds/donation-widget?api_key=smart-savings-dapp" 
                                width="346" 
                                height="623" 
                                frameBorder="0" 
                                scrolling="no" 
                                style={{overflow: 'hidden'}}
                                title="NOWPayments Donation Widget"
                            />
                        </div>
                        
                        <div className="mt-4 text-center">
                            <p className="text-sm text-gray-400">Use the widget above to donate DOGE</p>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Payment Instructions */}
            <Card className="bg-gradient-to-br from-blue-900/50 to-cyan-900/50 border-blue-500/30 backdrop-blur mt-8">
                <CardHeader>
                    <CardTitle className="text-center text-cyan-300 text-xl">
                        💡 HOW TO PAY & PLAY
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
                        <div>
                            <div className="text-3xl mb-2">1️⃣</div>
                            <h3 className="text-white font-bold mb-2">Use Donation Widget</h3>
                            <p className="text-sm text-gray-300">Use the NOWPayments widget to send DOGE to the casino or donation address</p>
                        </div>
                        
                        <div>
                            <div className="text-3xl mb-2">2️⃣</div>
                            <h3 className="text-white font-bold mb-2">Balance Updates</h3>
                            <p className="text-sm text-gray-300">Your casino balance updates automatically after payment confirmation</p>
                        </div>
                        
                        <div>
                            <div className="text-3xl mb-2">3️⃣</div>
                            <h3 className="text-white font-bold mb-2">Start Gaming</h3>
                            <p className="text-sm text-gray-300">Click any game above to start playing with real-time balance updates</p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default SimplifiedCasinoInterface;