import React from 'react';
import Header from './Header';
import { PiggyBank, TrendingUp, Coins, Wallet } from 'lucide-react';

const SavingsPage = () => {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="pt-32 pb-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-2xl flex items-center justify-center">
              <PiggyBank className="w-10 h-10 text-black" />
            </div>
            <h1 className="text-5xl font-bold text-white mb-4">Your Savings</h1>
            <p className="text-gray-300 text-lg">Track your automatic savings from casino activities</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
              <div className="flex items-center justify-between mb-4">
                <Coins className="w-8 h-8 text-yellow-400" />
                <span className="text-green-400 text-sm">+5.2%</span>
              </div>
              <div className="text-2xl font-bold text-white mb-1">0.00 CRT</div>
              <div className="text-gray-400 text-sm">Total Savings</div>
            </div>

            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
              <div className="flex items-center justify-between mb-4">
                <TrendingUp className="w-8 h-8 text-green-400" />
                <span className="text-green-400 text-sm">+12.8%</span>
              </div>
              <div className="text-2xl font-bold text-white mb-1">0.00 SOL</div>
              <div className="text-gray-400 text-sm">Monthly Growth</div>
            </div>

            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
              <div className="flex items-center justify-between mb-4">
                <Wallet className="w-8 h-8 text-blue-400" />
                <span className="text-red-400 text-sm">-2.1%</span>
              </div>
              <div className="text-2xl font-bold text-white mb-1">0</div>
              <div className="text-gray-400 text-sm">Games Played</div>
            </div>

            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
              <div className="flex items-center justify-between mb-4">
                <PiggyBank className="w-8 h-8 text-purple-400" />
                <span className="text-green-400 text-sm">Active</span>
              </div>
              <div className="text-2xl font-bold text-white mb-1">100%</div>
              <div className="text-gray-400 text-sm">Auto-Save Rate</div>
            </div>
          </div>

          <div className="text-center">
            <p className="text-gray-400 text-lg">
              Connect your wallet to start tracking your savings!
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default SavingsPage;