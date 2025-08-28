import React, { useState } from 'react';
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

    // If game selected, show game
    if (currentGame) {
        const GameComponent = currentGame.component;
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-black">
                <GameComponent onBack={handleBackToLobby} />
            </div>
        );
    }

    return (
        <div className="w-full max-w-4xl mx-auto p-6 bg-gradient-to-br from-slate-900 via-purple-900 to-black min-h-screen">
            {/* Simple Header */}
            <div className="text-center mb-8">
                <h1 className="text-4xl font-bold text-gold-400 mb-4">
                    💎 CASINO 💎
                </h1>
                
                {/* SIMPLE BALANCE - NO CONFUSION */}
                <div className="bg-black/50 p-6 rounded-lg border border-gold-400/30 mb-6">
                    <div className="text-2xl font-bold text-white mb-2">
                        {dogeBalance.toLocaleString()} DOGE
                    </div>
                    <div className="text-lg text-gray-300">
                        ${balanceUSD.toLocaleString()} USD
                    </div>
                    <div className="text-sm text-green-400 mt-2">
                        ✅ Ready to Play
                    </div>
                </div>
            </div>

            {/* Games Grid - Simple */}
            <div className="grid grid-cols-3 gap-4 mb-8">
                {games.map((game) => (
                    <Button
                        key={game.id}
                        onClick={() => handleGameClick(game.id)}
                        className="h-24 bg-gradient-to-br from-slate-700 to-slate-800 hover:from-gold-600 hover:to-gold-700 border border-slate-600 hover:border-gold-400 transition-all"
                    >
                        <div className="text-center">
                            <div className="text-3xl mb-1">{game.icon}</div>
                            <div className="text-sm font-bold">{game.name}</div>
                        </div>
                    </Button>
                ))}
            </div>

            {/* Donation Widget - Clean */}
            <Card className="bg-black/30 border-green-500/30">
                <CardContent className="p-6">
                    <div className="text-center">
                        <h3 className="text-xl font-bold text-green-400 mb-4">
                            💰 $50K DOGE Donation
                        </h3>
                        <p className="text-gray-300 mb-4">
                            Donate to: <span className="text-gold-400 text-sm">D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda</span>
                        </p>
                        
                        {/* Donation Widget */}
                        <div className="flex justify-center">
                            <iframe 
                                src="https://nowpayments.io/embeds/donation-widget?api_key=f9a7e8ba-2573-4da2-9f4f-3e0ffd748212" 
                                width="300" 
                                height="500" 
                                frameBorder="0" 
                                scrolling="no" 
                                style={{overflow: 'hidden'}}
                                title="Donation Widget"
                            />
                        </div>
                        
                        <p className="text-sm text-gray-400 mt-4">
                            Target: 226,244 DOGE ($50,000 USD)
                        </p>
                    </div>
                </CardContent>
            </Card>

            {/* Simple Instructions */}
            <div className="text-center mt-8">
                <div className="bg-blue-900/20 p-4 rounded-lg border border-blue-500/30">
                    <h4 className="text-white font-bold mb-2">How to Play:</h4>
                    <p className="text-sm text-gray-300">
                        1. Click any game above → 2. Game opens → 3. Start playing with your DOGE balance
                    </p>
                </div>
            </div>
        </div>
    );
};

export default CleanCasinoInterface;