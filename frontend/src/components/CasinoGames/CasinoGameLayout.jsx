import React, { useState, useContext, useEffect } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { useToast } from '../../hooks/use-toast';
import { ArrowLeft, Coins, TrendingUp, TrendingDown } from 'lucide-react';
import axios from 'axios';
import MoneyTracker from './MoneyTracker';
import BigLossTracker from './BigLossTracker';
import GamingDepositManager from './GamingDepositManager';

// CRT Token Component
const CRTCoin = ({ size = 'w-8 h-8', className = '' }) => {
  return (
    <img 
      src="https://customer-assets.emergentagent.com/job_blockchain-casino/artifacts/nx4ol97f_copilot_image_1755811225489.jpeg"
      alt="CRT Token"
      className={`${size} rounded-full ${className}`}
    />
  );
};

// Wallet Context
const WalletContext = React.createContext();

export const useWallet = () => {
  const context = useContext(WalletContext);
  if (!context) {
    return {
      balance: 0,
      updateBalance: () => {},
      isConnected: false,
      loading: true,
      refreshBalance: () => {}
    };
  }
  return context;
};

export const WalletProvider = ({ children }) => {
  const [balance, setBalance] = useState(0);
  const [isConnected, setIsConnected] = useState(true);
  const [loading, setLoading] = useState(true);
  
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchBalance();
  }, []);

  const fetchBalance = async () => {
    try {
      setLoading(true);
      
      // Get authenticated user from localStorage
      const user = JSON.parse(localStorage.getItem('casino_user') || '{}');
      if (!user.wallet_address) {
        console.error('No authenticated user found');
        setBalance(0);
        setIsConnected(false);
        setLoading(false);
        return;
      }
      
      const response = await axios.get(`${BACKEND_URL}/api/wallet/${user.wallet_address}`);
      
      if (response.data.success && response.data.wallet) {
        // Use deposit wallet balance for gaming
        const depositBalance = response.data.wallet.deposit_balance?.CRT || 0;
        setBalance(depositBalance);
        setIsConnected(true);
      } else {
        console.error('Failed to fetch wallet:', response.data.message);
        setBalance(0);
        setIsConnected(false);
      }
    } catch (error) {
      console.error('Error fetching balance:', error);
      setBalance(0);
      setIsConnected(false);
    } finally {
      setLoading(false);
    }
  };
  
  const updateBalance = async (amount) => {
    // This function should not be used directly for bets anymore
    // Use placeBet() instead for proper API integration
    setBalance(prev => Math.max(0, prev + amount));
  };
  
  const placeBet = async (gameType, betAmount, currency) => {
    try {
      if (!currency) {
        throw new Error('Currency is required for betting');
      }
      
      // Get authenticated user
      const user = JSON.parse(localStorage.getItem('casino_user') || '{}');
      if (!user.wallet_address) {
        throw new Error('No authenticated user found');
      }
      
      // Call the real betting API
      const response = await axios.post(`${BACKEND_URL}/api/games/bet`, {
        wallet_address: user.wallet_address,
        game_type: gameType,
        bet_amount: betAmount,
        currency: currency,
        network: 'solana'
      });
      
      if (response.data.success) {
        // Refresh balance from backend to get updated values
        await fetchBalance();
        
        return {
          success: true,
          result: response.data.result,
          payout: response.data.payout,
          savings_contribution: response.data.savings_contribution,
          liquidity_added: response.data.liquidity_added,
          message: response.data.message
        };
      } else {
        throw new Error(response.data.message || 'Bet failed');
      }
    } catch (error) {
      console.error('Error placing bet:', error);
      return {
        success: false,
        error: error.message
      };
    }
  };

  return (
    <WalletContext.Provider value={{ 
      balance, 
      updateBalance, 
      placeBet,
      isConnected, 
      loading,
      refreshBalance: fetchBalance 
    }}>
      {children}
    </WalletContext.Provider>
  );
};

// Multi-Currency Betting Component
export const BettingPanel = ({ 
  onBet, 
  minBet = 1, 
  maxBet = 100, 
  disabled = false,
  gameActive = false 
}) => {
  const [betAmount, setBetAmount] = useState(10);
  const [selectedCurrency, setSelectedCurrency] = useState('USDC');
  const [allBalances, setAllBalances] = useState({});
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();
  
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  // Currency configurations
  const currencies = {
    'USDC': { 
      symbol: '$', 
      color: 'text-green-400', 
      icon: '🟢', 
      name: 'USDC'
    },
    'DOGE': { 
      symbol: 'Ð', 
      color: 'text-yellow-400', 
      icon: '🐕', 
      name: 'DOGE'
    },
    'TRX': { 
      symbol: 'T', 
      color: 'text-red-400', 
      icon: '🔴', 
      name: 'TRX'
    },
    'CRT': { 
      symbol: 'C', 
      color: 'text-blue-400', 
      icon: '🟦', 
      name: 'CRT'
    }
  };

  useEffect(() => {
    fetchAllBalances();
  }, []);

  const fetchAllBalances = async () => {
    try {
      setLoading(true);
      const savedUser = localStorage.getItem('casino_user');
      if (!savedUser) return;
      
      const user = JSON.parse(savedUser);
      const response = await axios.get(`${BACKEND_URL}/api/wallet/${user.wallet_address}`);
      
      if (response.data.success && response.data.wallet) {
        const depositBalance = response.data.wallet.deposit_balance || {};
        setAllBalances(depositBalance);
        
        // Auto-select currency with highest balance > 0
        const availableCurrency = Object.keys(depositBalance).find(currency => 
          depositBalance[currency] > 0 && currencies[currency]
        );
        if (availableCurrency) {
          setSelectedCurrency(availableCurrency);
        }
      }
    } catch (error) {
      console.error('Error fetching balances:', error);
      toast({
        title: "❌ Error",
        description: "Failed to load wallet balances",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleBet = () => {
    const currentBalance = allBalances[selectedCurrency] || 0;
    if (betAmount <= currentBalance && betAmount >= minBet && betAmount <= maxBet) {
      onBet(betAmount, selectedCurrency);
    } else {
      toast({
        title: "❌ Invalid Bet",
        description: `Insufficient ${selectedCurrency} balance or invalid amount`,
        variant: "destructive"
      });
    }
  };

  const quickBets = [1, 5, 10, 25, 50, 100];
  const currentBalance = allBalances[selectedCurrency] || 0;
  const currencyConfig = currencies[selectedCurrency];

  if (loading) {
    return (
      <Card className="p-4 bg-gray-900/50 border-yellow-400/20">
        <div className="text-center text-gray-400">Loading wallet...</div>
      </Card>
    );
  }

  return (
    <Card className="p-4 bg-gray-900/50 border-yellow-400/20">
      <div className="space-y-4">
        {/* Currency Selector */}
        <div className="space-y-2">
          <label className="text-sm text-gray-300">Choose Currency:</label>
          <select
            value={selectedCurrency}
            onChange={(e) => setSelectedCurrency(e.target.value)}
            className="w-full p-2 bg-gray-800 border border-gray-700 text-white rounded"
            disabled={gameActive}
          >
            {Object.entries(currencies).map(([currency, config]) => {
              const balance = allBalances[currency] || 0;
              return (
                <option key={currency} value={currency} disabled={balance <= 0}>
                  {config.icon} {config.name} - Balance: {balance.toFixed(2)}
                  {balance <= 0 ? ' (No Balance)' : ''}
                </option>
              );
            })}
          </select>
        </div>

        {/* Selected Currency Balance Display */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">{currencyConfig?.icon}</span>
            <span className={`font-bold ${currencyConfig?.color}`}>
              Balance: {currencyConfig?.symbol}{currentBalance.toFixed(2)} {selectedCurrency}
            </span>
          </div>
        </div>

        {/* Bet Amount Input */}
        <div className="space-y-2">
          <label className="text-sm text-gray-300">Bet Amount:</label>
          <Input
            type="number"
            value={betAmount}
            onChange={(e) => setBetAmount(Number(e.target.value))}
            min={minBet}
            max={Math.min(maxBet, currentBalance)}
            className="bg-gray-800 border-gray-700 text-white"
            disabled={disabled || gameActive || currentBalance <= 0}
          />
        </div>

        {/* Quick Bet Buttons */}
        <div className="grid grid-cols-3 gap-2">
          {quickBets
            .filter(amount => amount <= currentBalance && amount <= maxBet)
            .map((amount) => (
            <Button
              key={amount}
              onClick={() => setBetAmount(amount)}
              variant="outline"
              size="sm"
              className="border-gray-600 text-gray-300 hover:bg-yellow-400/20"
              disabled={disabled || gameActive || amount > currentBalance}
            >
              {currencyConfig?.symbol}{amount}
            </Button>
          ))}
        </div>

        {/* Bet Button */}
        <Button
          onClick={handleBet}
          disabled={disabled || gameActive || betAmount > currentBalance || betAmount < minBet || currentBalance <= 0}
          className="w-full bg-yellow-600 hover:bg-yellow-500 text-black font-bold"
        >
          {gameActive ? 'Game In Progress...' : 
           currentBalance <= 0 ? `No ${selectedCurrency} Balance` :
           `Bet ${currencyConfig?.symbol}${betAmount} ${selectedCurrency}`}
        </Button>

        {/* Balance Warning */}
        {currentBalance <= 0 && (
          <div className="text-center text-red-400 text-sm">
            No {selectedCurrency} balance. Choose a different currency or add funds.
          </div>
        )}
      </div>
    </Card>
  );
};

// Game Stats Component
export const GameStats = ({ stats }) => {
  return (
    <Card className="p-4 bg-gray-900/50 border-yellow-400/20">
      <h3 className="text-lg font-bold text-yellow-400 mb-3">Game Stats</h3>
      <div className="space-y-2">
        <div className="flex justify-between">
          <span className="text-gray-300">Total Bets:</span>
          <span className="text-white">{stats.totalBets || 0}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-300">Total Won:</span>
          <div className="flex items-center space-x-1">
            <TrendingUp className="w-4 h-4 text-green-400" />
            <span className="text-green-400">{(stats.totalWon || 0).toFixed(2)} CRT</span>
          </div>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-300">Total Lost:</span>
          <div className="flex items-center space-x-1">
            <TrendingDown className="w-4 h-4 text-red-400" />
            <span className="text-red-400">{(stats.totalLost || 0).toFixed(2)} CRT</span>
          </div>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-300">Win Rate:</span>
          <span className="text-yellow-400">{(stats.winRate || 0).toFixed(1)}%</span>
        </div>
      </div>
    </Card>
  );
};

// Main Game Layout
const CasinoGameLayout = ({ children, title, onBack, stats, sidebarContent }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              onClick={onBack}
              className="text-yellow-400 hover:text-yellow-300"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back to Casino
            </Button>
            <div className="flex items-center space-x-2">
              <CRTCoin size="w-8 h-8" />
              <h1 className="text-3xl font-bold text-yellow-400">{title}</h1>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-3">
            {children}
          </div>
          <div className="space-y-4">
            <GameStats stats={stats} />
            {sidebarContent}
          </div>
        </div>
        
        {/* Full-width Money Tracker */}
        <div className="mt-8 space-y-6">
          <GamingDepositManager />
          <BigLossTracker gameType={title} />
          <MoneyTracker gameType={title} />
        </div>
      </div>
    </div>
  );
};

export { CRTCoin };
export default CasinoGameLayout;