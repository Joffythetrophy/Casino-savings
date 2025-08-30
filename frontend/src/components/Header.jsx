import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Coins, TrendingUp, Gamepad2, PiggyBank, Zap, Wallet, LogOut, User, BarChart3, Settings, History, Shield } from 'lucide-react';
import { useAuth } from './UserAuth';

const Header = ({ isWalletConnected }) => {
  const location = useLocation();
  const { user, logout, isAuthenticated } = useAuth();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="fixed top-0 left-0 right-0 z-50 nav-green border-b border-casino-green-500/30">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="w-10 h-10 bg-gradient-to-r from-casino-green-400 to-emerald-casino-500 rounded-full flex items-center justify-center transform group-hover:scale-110 transition-transform duration-300 glow-green">
              <span className="text-2xl">🐅</span>
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-casino-green-400 via-emerald-casino-400 to-casino-green-500 bg-clip-text text-transparent">
                🐅 CRT TIGER CASINO 🐅
              </h1>
              <p className="text-xs text-casino-green-300">Hunt the Fortune</p>
            </div>
          </Link>

          {/* Navigation - Always visible */}
          <nav className="flex items-center space-x-2 overflow-x-auto">
            <Link 
              to="/" 
              className={`flex items-center space-x-1 px-2 py-1 rounded-lg transition-all duration-300 text-xs whitespace-nowrap ${
                isActive('/') || isActive('/dashboard')
                  ? 'bg-casino-green-500 text-white font-medium glow-green' 
                  : 'text-casino-green-200 hover:text-casino-green-400 hover:bg-casino-green-800/30'
              }`}
            >
              <BarChart3 className="w-3 h-3" />
              <span className="hidden sm:block">Dashboard</span>
              <span className="sm:hidden">📊</span>
            </Link>
            
            <Link 
              to="/games" 
              className={`flex items-center space-x-1 px-2 py-1 rounded-lg transition-all duration-300 text-xs whitespace-nowrap ${
                isActive('/games') 
                  ? 'bg-casino-green-500 text-white font-medium glow-green' 
                  : 'text-casino-green-200 hover:text-casino-green-400 hover:bg-casino-green-800/30'
              }`}
            >
              <Gamepad2 className="w-3 h-3" />
              <span className="hidden sm:block">Casino</span>
              <span className="sm:hidden">🎮</span>
            </Link>
            
            <Link 
              to="/wallet" 
              className={`flex items-center space-x-1 px-2 py-1 rounded-lg transition-all duration-300 text-xs whitespace-nowrap ${
                isActive('/wallet') 
                  ? 'bg-casino-green-500 text-white font-medium glow-green' 
                  : 'text-casino-green-200 hover:text-casino-green-400 hover:bg-casino-green-800/30'
              }`}
            >
              <Wallet className="w-3 h-3" />
              <span className="hidden sm:block">Wallet</span>
              <span className="sm:hidden">💰</span>
            </Link>
            
            <Link 
              to="/treasury" 
              className={`flex items-center space-x-1 px-2 py-1 rounded-lg transition-all duration-300 text-xs whitespace-nowrap ${
                isActive('/treasury') 
                  ? 'bg-casino-green-500 text-white font-medium glow-green' 
                  : 'text-casino-green-200 hover:text-casino-green-400 hover:bg-casino-green-800/30'
              }`}
            >
              <Shield className="w-3 h-3" />
              <span className="hidden sm:block">🐅 Treasury</span>
              <span className="sm:hidden">🐅</span>
            </Link>
            
            <Link 
              to="/dex" 
              className={`flex items-center space-x-1 px-2 py-1 rounded-lg transition-all duration-300 text-xs whitespace-nowrap ${
                isActive('/dex') 
                  ? 'bg-casino-green-500 text-white font-medium glow-green' 
                  : 'text-casino-green-200 hover:text-casino-green-400 hover:bg-casino-green-800/30'
              }`}
            >
              <TrendingUp className="w-3 h-3" />
              <span className="hidden sm:block">🌊 DEX</span>
              <span className="sm:hidden">🌊</span>
            </Link>
            
            <Link 
              to="/savings" 
              className={`flex items-center space-x-1 px-2 py-1 rounded-lg transition-all duration-300 text-xs whitespace-nowrap ${
                isActive('/savings') 
                  ? 'bg-casino-green-500 text-white font-medium glow-green' 
                  : 'text-casino-green-200 hover:text-casino-green-400 hover:bg-casino-green-800/30'
              }`}
            >
              <PiggyBank className="w-3 h-3" />
              <span className="hidden sm:block">Vault</span>
              <span className="sm:hidden">🏦</span>
            </Link>
          </nav>

          {/* Solana Live Indicator */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 px-3 py-2 bg-green-500/20 rounded-full border border-green-500/30">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-green-400 text-sm font-medium">Solana Live</span>
            </div>
          </div>

          {/* User Info & Actions */}
          <div className="flex items-center space-x-4">
            {isAuthenticated && user ? (
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2 text-gray-300">
                  <User className="w-4 h-4" />
                  <span className="hidden md:block text-sm">
                    {user.wallet_address.substring(0, 8)}...
                  </span>
                </div>
                <button
                  onClick={logout}
                  className="flex items-center space-x-2 px-3 py-2 rounded-lg text-gray-300 hover:text-yellow-400 hover:bg-white/10 transition-all duration-300"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="hidden md:block">Logout</span>
                </button>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;