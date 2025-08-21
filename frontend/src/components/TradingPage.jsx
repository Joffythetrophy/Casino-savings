import React from 'react';
import Header from './Header';
import { TrendingUp, Bot, BarChart3, Zap } from 'lucide-react';

const TradingPage = () => {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="pt-32 pb-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-2xl flex items-center justify-center">
              <Bot className="w-10 h-10 text-black" />
            </div>
            <h1 className="text-5xl font-bold text-white mb-4">AI Trading</h1>
            <p className="text-gray-300 text-lg">Intelligent crypto trading to grow your savings</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
              <div className="flex items-center space-x-3 mb-6">
                <TrendingUp className="w-8 h-8 text-green-400" />
                <h3 className="text-2xl font-bold text-white">Portfolio Performance</h3>
              </div>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">CRT Token</span>
                  <span className="text-green-400 font-bold">+15.2%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">DOGE</span>
                  <span className="text-green-400 font-bold">+8.7%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">TRX (Tron)</span>
                  <span className="text-red-400 font-bold">-2.3%</span>
                </div>
              </div>
            </div>

            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10">
              <div className="flex items-center space-x-3 mb-6">
                <BarChart3 className="w-8 h-8 text-blue-400" />
                <h3 className="text-2xl font-bold text-white">Trading Stats</h3>
              </div>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Success Rate</span>
                  <span className="text-yellow-400 font-bold">73%</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Active Trades</span>
                  <span className="text-white font-bold">0</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Total Volume</span>
                  <span className="text-white font-bold">$0.00</span>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center">
            <div className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 max-w-2xl mx-auto">
              <Zap className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-white mb-4">AI Trading Coming Soon</h3>
              <p className="text-gray-300">
                Our advanced AI will automatically trade your savings to maximize returns while maintaining risk management.
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default TradingPage;