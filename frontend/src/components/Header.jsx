import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Coins, TrendingUp, Gamepad2, PiggyBank, Zap, Wallet, LogOut, User, BarChart3, Settings, History } from 'lucide-react';
import { useAuth } from './UserAuth';

const Header = ({ isWalletConnected }) => {
  const location = useLocation();
  const { user, logout, isAuthenticated } = useAuth();

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
          <nav className="hidden lg:flex items-center space-x-6">
            <Link 
              to="/" 
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-300 ${
                isActive('/') || isActive('/dashboard')
                  ? 'bg-gold-500 text-black font-medium' 
                  : 'text-gray-300 hover:text-gold-400 hover:bg-white/10'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Dashboard</span>
            </Link>
            
            <Link 
              to="/games" 
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-300 ${
                isActive('/games') 
                  ? 'bg-gold-500 text-black font-medium' 
                  : 'text-gray-300 hover:text-gold-400 hover:bg-white/10'
              }`}
            >
              <Gamepad2 className="w-4 h-4" />
              <span>Casino</span>
            </Link>
            
            <Link 
              to="/savings" 
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-300 ${
                isActive('/savings') 
                  ? 'bg-gold-500 text-black font-medium' 
                  : 'text-gray-300 hover:text-gold-400 hover:bg-white/10'
              }`}
            >
              <PiggyBank className="w-4 h-4" />
              <span>Vault</span>
            </Link>
            
            <Link 
              to="/wallet" 
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-300 ${
                isActive('/wallet') 
                  ? 'bg-gold-500 text-black font-medium' 
                  : 'text-gray-300 hover:text-gold-400 hover:bg-white/10'
              }`}
            >
              <Wallet className="w-4 h-4" />
              <span>Wallet</span>
            </Link>
            
            <Link 
              to="/history" 
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-300 ${
                isActive('/history') 
                  ? 'bg-gold-500 text-black font-medium' 
                  : 'text-gray-300 hover:text-gold-400 hover:bg-white/10'
              }`}
            >
              <History className="w-4 h-4" />
              <span>History</span>
            </Link>
            
            <Link 
              to="/trading" 
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-300 ${
                isActive('/trading') 
                  ? 'bg-gold-500 text-black font-medium' 
                  : 'text-gray-300 hover:text-gold-400 hover:bg-white/10'
              }`}
            >
              <TrendingUp className="w-4 h-4" />
              <span>Trading</span>
            </Link>
            
            <Link 
              to="/admin" 
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-300 ${
                isActive('/admin') 
                  ? 'bg-red-500 text-white font-medium' 
                  : 'text-gray-300 hover:text-red-400 hover:bg-white/10'
              }`}
            >
              <Settings className="w-4 h-4" />
              <span>Admin</span>
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