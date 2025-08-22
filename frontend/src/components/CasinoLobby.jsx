import React, { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import Header from './Header';
import { WalletProvider, CRTCoin } from './CasinoGames/CasinoGameLayout';
import SlotMachine from './CasinoGames/SlotMachine';
import Roulette from './CasinoGames/Roulette';
import Dice from './CasinoGames/Dice';
import Plinko from './CasinoGames/Plinko';
import Keno from './CasinoGames/Keno';
import Mines from './CasinoGames/Mines';
import { 
  Dices, 
  CircleDot, 
  Zap, 
  Target, 
  Grid3x3, 
  Bomb,
  TrendingUp,
  Users,
  Trophy,
  Clock
} from 'lucide-react';

const GameCard = ({ title, description, icon: Icon, onClick, players, jackpot, isHot = false }) => {
  return (
    <Card className="group relative bg-gradient-to-br from-gray-800/50 to-gray-900/50 border border-yellow-400/20 hover:border-yellow-400/50 transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-yellow-400/20 cursor-pointer overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-yellow-400/5 to-purple-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
      
      {isHot && (
        <div className="absolute top-2 right-2 bg-red-500 text-white text-xs px-2 py-1 rounded-full animate-pulse">
          🔥 HOT
        </div>
      )}
      
      <div className="relative z-10 p-6" onClick={onClick}>
        {/* Icon */}
        <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-2xl flex items-center justify-center group-hover:rotate-12 transition-transform duration-500">
          <Icon className="w-8 h-8 text-black" />
        </div>
        
        {/* Title */}
        <h3 className="text-xl font-bold text-white mb-2 text-center group-hover:text-yellow-400 transition-colors duration-300">
          {title}
        </h3>
        
        {/* Description */}
        <p className="text-gray-300 text-sm text-center mb-4 group-hover:text-gray-200 transition-colors duration-300">
          {description}
        </p>
        
        {/* Stats */}
        <div className="flex justify-between items-center text-xs text-gray-400">
          <div className="flex items-center space-x-1">
            <Users className="w-3 h-3" />
            <span>{players}</span>
          </div>
          <div className="flex items-center space-x-1">
            <CRTCoin size="w-3 h-3" />
            <span>{jackpot} CRT</span>
          </div>
        </div>
      </div>
    </Card>
  );
};

const StatCard = ({ title, value, icon: Icon, change, color = "text-yellow-400" }) => {
  return (
    <Card className="p-6 bg-gradient-to-br from-gray-800/30 to-gray-900/30 border border-yellow-400/20">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm">{title}</p>
          <p className={`text-2xl font-bold ${color}`}>{value}</p>
          {change && (
            <div className="flex items-center space-x-1 mt-1">
              <TrendingUp className="w-4 h-4 text-green-400" />
              <span className="text-green-400 text-sm">{change}</span>
            </div>
          )}
        </div>
        <div className={`w-12 h-12 ${color.replace('text-', 'bg-').replace('400', '400/20')} rounded-lg flex items-center justify-center`}>
          <Icon className={`w-6 h-6 ${color}`} />
        </div>
      </div>
    </Card>
  );
};

const CasinoLobby = () => {
  const [currentGame, setCurrentGame] = useState(null);
  
  const games = [
    {
      id: 'slots',
      title: 'Slot Machine',
      description: 'Classic 3-reel slots with CRT multipliers',
      icon: Dices,
      component: SlotMachine,
      players: 234,
      jackpot: '15,420',
      isHot: true
    },
    {
      id: 'roulette',
      title: 'Roulette',
      description: 'European roulette with crypto betting',
      icon: CircleDot,
      component: Roulette,
      players: 156,
      jackpot: '8,932',
    },
    {
      id: 'dice',
      title: 'Dice',
      description: 'Provably fair dice with custom multipliers',
      icon: Dices,
      component: Dice,
      players: 89,
      jackpot: '5,621',
      isHot: true
    },
    {
      id: 'plinko',
      title: 'Plinko',
      description: 'Drop balls for massive multipliers',
      icon: Zap,
      component: Plinko,
      players: 167,
      jackpot: '12,100'
    },
    {
      id: 'keno',
      title: 'Keno',
      description: 'Pick numbers and win big payouts',
      icon: Target,
      component: Keno,
      players: 78,
      jackpot: '3,456'
    },
    {
      id: 'mines',
      title: 'Mines',
      description: 'Find gems while avoiding mines',
      icon: Bomb,
      component: Mines,
      players: 123,
      jackpot: '7,890'
    }
  ];

  const handleGameSelect = (game) => {
    setCurrentGame(game);
  };

  const handleBackToLobby = () => {
    setCurrentGame(null);
  };

  if (currentGame) {
    const GameComponent = currentGame.component;
    return (
      <WalletProvider>
        <GameComponent onBack={handleBackToLobby} />
      </WalletProvider>
    );
  }

  return (
    <WalletProvider>
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
        <Header />
        
        <main className="pt-24 pb-12 px-6">
          <div className="max-w-7xl mx-auto">
            {/* Hero Section */}
            <div className="text-center mb-12">
              <div className="flex items-center justify-center space-x-3 mb-6">
                <img 
                  src="https://customer-assets.emergentagent.com/job_blockchain-casino/artifacts/nx4ol97f_copilot_image_1755811225489.jpeg"
                  alt="CRT Token"
                  className="w-16 h-16 rounded-full"
                />
                <h1 className="text-6xl font-bold bg-gradient-to-r from-yellow-300 via-yellow-400 to-yellow-600 bg-clip-text text-transparent">
                  Casino Savings
                </h1>
                <img 
                  src="https://customer-assets.emergentagent.com/job_blockchain-casino/artifacts/lyppdbel_copilot_image_1755811422449.jpeg"
                  alt="CRT Token"
                  className="w-16 h-16 rounded-full"
                />
              </div>
              <p className="text-xl text-gray-300 max-w-2xl mx-auto">
                Your private crypto casino with intelligent savings. Play, win, and automatically save your progress!
              </p>
            </div>

            {/* Games Grid */}
            <div className="mb-12">
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-3xl font-bold text-yellow-400">Choose Your Game</h2>
                <div className="flex items-center space-x-2 text-gray-400">
                  <Clock className="w-4 h-4" />
                  <span className="text-sm">All games are provably fair</span>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {games.map(game => (
                  <GameCard
                    key={game.id}
                    title={game.title}
                    description={game.description}
                    icon={game.icon}
                    players={game.players}
                    jackpot={game.jackpot}
                    isHot={game.isHot}
                    onClick={() => handleGameSelect(game)}
                  />
                ))}
              </div>
            </div>

            {/* Recent Activity - Private Session Stats */}
            <Card className="p-6 bg-gradient-to-r from-gray-800/30 to-gray-900/30 border border-yellow-400/20 mb-12">
              <h3 className="text-2xl font-bold text-yellow-400 mb-6">💼 Your Wallet System</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-blue-800/20 p-6 rounded-lg border border-blue-400/20">
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <Coins className="w-4 h-4 text-white" />
                    </div>
                    <h4 className="text-lg font-bold text-blue-400">Deposit Wallet</h4>
                  </div>
                  <p className="text-gray-300 text-sm mb-4">Add funds to start playing. Supports CRT, DOGE, and TRX.</p>
                  <div className="text-2xl font-bold text-white">Ready to deposit</div>
                </div>
                
                <div className="bg-green-800/20 p-6 rounded-lg border border-green-400/20">
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                      <Trophy className="w-4 h-4 text-white" />
                    </div>
                    <h4 className="text-lg font-bold text-green-400">Winnings Wallet</h4>
                  </div>
                  <p className="text-gray-300 text-sm mb-4">Collect your game winnings here. Withdraw anytime.</p>
                  <div className="text-2xl font-bold text-white">0.00 CRT</div>
                </div>
                
                <div className="bg-purple-800/20 p-6 rounded-lg border border-purple-400/20">
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                      <PiggyBank className="w-4 h-4 text-white" />
                    </div>
                    <h4 className="text-lg font-bold text-purple-400">Savings Vault</h4>
                  </div>
                  <p className="text-gray-300 text-sm mb-4">Automatic savings from your session losses and winnings.</p>
                  <div className="text-2xl font-bold text-white">0.00 Total</div>
                </div>
              </div>
            </Card>

            {/* Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
              <Card className="p-6 bg-gradient-to-br from-green-800/20 to-green-900/20 border border-green-400/20">
                <div className="text-center">
                  <div className="w-12 h-12 mx-auto mb-4 bg-green-500/20 rounded-full flex items-center justify-center">
                    <Zap className="w-6 h-6 text-green-400" />
                  </div>
                  <h3 className="text-lg font-bold text-green-400 mb-2">Instant Payouts</h3>
                  <p className="text-gray-300 text-sm">Winnings are paid instantly to your wallet</p>
                </div>
              </Card>
              
              <Card className="p-6 bg-gradient-to-br from-blue-800/20 to-blue-900/20 border border-blue-400/20">
                <div className="text-center">
                  <div className="w-12 h-12 mx-auto mb-4 bg-blue-500/20 rounded-full flex items-center justify-center">
                    <Target className="w-6 h-6 text-blue-400" />
                  </div>
                  <h3 className="text-lg font-bold text-blue-400 mb-2">Provably Fair</h3>
                  <p className="text-gray-300 text-sm">All games use verifiable randomness</p>
                </div>
              </Card>
              
              <Card className="p-6 bg-gradient-to-br from-purple-800/20 to-purple-900/20 border border-purple-400/20">
                <div className="text-center">
                  <div className="w-12 h-12 mx-auto mb-4 bg-purple-500/20 rounded-full flex items-center justify-center">
                    <Trophy className="w-6 h-6 text-purple-400" />
                  </div>
                  <h3 className="text-lg font-bold text-purple-400 mb-2">Auto Savings</h3>
                  <p className="text-gray-300 text-sm">Losses automatically build your savings</p>
                </div>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </WalletProvider>
  );
};

export default CasinoLobby;