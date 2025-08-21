import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Coins, TrendingUp, Gamepad2, PiggyBank, Zap } from 'lucide-react';

const Header = ({ isWalletConnected }) => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-black/20 backdrop-blur-md border-b border-white/10">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center transform group-hover:scale-110 transition-transform duration-300">
              <Coins className="w-6 h-6 text-black" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-yellow-400">Casino Savings</h1>
              <p className="text-xs text-gray-400">Save while you play</p>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link 
              to="/games" 
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-300 ${
                isActive('/games') 
                  ? 'bg-yellow-400 text-black font-medium' 
                  : 'text-gray-300 hover:text-yellow-400 hover:bg-white/10'
              }`}
            >
              <Gamepad2 className="w-4 h-4" />
              <span>Games</span>
            </Link>
            
            <Link 
              to="/savings" 
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-300 ${
                isActive('/savings') 
                  ? 'bg-yellow-400 text-black font-medium' 
                  : 'text-gray-300 hover:text-yellow-400 hover:bg-white/10'
              }`}
            >
              <PiggyBank className="w-4 h-4" />
              <span>Savings</span>
            </Link>
            
            <Link 
              to="/trading" 
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-300 ${
                isActive('/trading') 
                  ? 'bg-yellow-400 text-black font-medium' 
                  : 'text-gray-300 hover:text-yellow-400 hover:bg-white/10'
              }`}
            >
              <TrendingUp className="w-4 h-4" />
              <span>AI Trading</span>
            </Link>
          </nav>

          {/* Solana Live Indicator */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 px-3 py-2 bg-green-500/20 rounded-full border border-green-500/30">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-green-400 text-sm font-medium">Solana Live</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;