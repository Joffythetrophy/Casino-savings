import React from 'react';
import Header from './Header';
import { Gamepad2, Dice6, Spade, Trophy } from 'lucide-react';

const GameCard = ({ title, description, icon: Icon, comingSoon = false }) => {
  return (
    <div className={`relative group bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 transition-all duration-300 ${
      comingSoon ? 'opacity-60' : 'hover:border-yellow-400/30 hover:scale-105 hover:shadow-2xl hover:shadow-yellow-400/20'
    }`}>
      <div className="text-center">
        <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-2xl flex items-center justify-center">
          <Icon className="w-8 h-8 text-black" />
        </div>
        <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
        <p className="text-gray-300 text-sm mb-4">{description}</p>
        {comingSoon && (
          <span className="inline-block px-3 py-1 bg-purple-500/20 text-purple-300 text-xs rounded-full">
            Coming Soon
          </span>
        )}
      </div>
    </div>
  );
};

const GamesPage = () => {
  const games = [
    {
      title: "Dice Roll",
      description: "Classic dice game with crypto rewards",
      icon: Dice6,
      comingSoon: true
    },
    {
      title: "Blackjack",
      description: "Beat the dealer in this card classic",
      icon: Spade,
      comingSoon: true
    },
    {
      title: "Tournament",
      description: "Compete with others for bigger prizes",
      icon: Trophy,
      comingSoon: true
    }
  ];

  return (
    <div className="min-h-screen">
      <Header />
      <main className="pt-32 pb-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-2xl flex items-center justify-center">
              <Gamepad2 className="w-10 h-10 text-black" />
            </div>
            <h1 className="text-5xl font-bold text-white mb-4">Casino Games</h1>
            <p className="text-gray-300 text-lg">Play responsibly while building your savings</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {games.map((game, index) => (
              <GameCard key={index} {...game} />
            ))}
          </div>

          <div className="text-center mt-16">
            <p className="text-gray-400">More games coming soon! Every loss helps grow your savings.</p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default GamesPage;