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

            {/* Donation Widget - Green Theme */}
            <Card className="card-green border-casino-green-500/40 glow-green">
                <CardContent className="p-6">
                    <div className="text-center">
                        <h3 className="text-xl font-bold text-casino-green-400 mb-4">
                            🐅 $50K DOGE Tiger Fund 🐅
                        </h3>
                        <p className="text-casino-green-200 mb-4">
                            Donate to: <span className="text-casino-green-400 text-sm font-mono">D85yb56oTYLCNPW7wuwUkevzEFQVSj4fda</span>
                        </p>
                        
                        {/* Donation Widget */}
                        <div className="flex justify-center border-2 border-casino-green-500/50 rounded-lg p-4 bg-casino-green-950/30">
                            <iframe 
                                src="https://nowpayments.io/embeds/donation-widget?api_key=smart-savings-dapp" 
                                width="300" 
                                height="500" 
                                frameBorder="0" 
                                scrolling="no" 
                                style={{overflow: 'hidden', borderRadius: '8px'}}
                                title="Donation Widget"
                            />
                        </div>
                        
                        <p className="text-sm text-casino-green-300 mt-4">
                            Target: 226,244 DOGE ($50,000 USD) 🐅
                        </p>
                    </div>
                </CardContent>
            </Card>

            {/* Simple Instructions - Green Theme */}
            <div className="text-center mt-8">
                <div className="card-green p-6 rounded-xl border border-casino-green-500/40">
                    <h4 className="text-casino-green-300 font-bold mb-3 text-lg">🎯 How to Play:</h4>
                    <p className="text-sm text-casino-green-200">
                        🐅 <strong>1.</strong> Click any game above → <strong>2.</strong> Game opens → <strong>3.</strong> Hunt big wins with your DOGE balance!
                    </p>
                    <div className="mt-3 text-xs text-casino-green-400">
                        🏆 May the Tiger bring you fortune! 🏆
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CleanCasinoInterface;