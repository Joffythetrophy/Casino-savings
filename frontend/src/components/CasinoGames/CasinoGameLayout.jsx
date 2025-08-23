import React, { useState, useContext, useEffect } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { useToast } from '../../hooks/use-toast';
import { ArrowLeft, Coins, TrendingUp, TrendingDown } from 'lucide-react';
import axios from 'axios';

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
      const user = JSON.parse(localStorage.getItem('user') || '{}');
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
  
  const placeBet = async (gameType, betAmount, currency = 'CRT') => {
    try {
      // Get authenticated user
      const user = JSON.parse(localStorage.getItem('user') || '{}');
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
      isConnected, 
      loading,
      refreshBalance: fetchBalance 
    }}>
      {children}
    </WalletContext.Provider>
  );
};

// Betting Component
export const BettingPanel = ({ 
  onBet, 
  minBet = 1, 
  maxBet = 100, 
  disabled = false,
  gameActive = false 
}) => {
  const [betAmount, setBetAmount] = useState(10);
  const { balance, loading } = useWallet();

  const quickBets = [1, 5, 10, 25, 50];

  const handleBet = () => {
    if (betAmount <= balance && betAmount >= minBet && betAmount <= maxBet) {
      onBet(betAmount);
    }
  };

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
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CRTCoin size="w-6 h-6" />
            <span className="text-yellow-400 font-bold">Balance: {balance.toFixed(2)}</span>
          </div>
        </div>
        
        <div className="space-y-2">
          <label className="text-sm text-gray-300">Bet Amount</label>
          <div className="flex space-x-2">
            <Input
              type="number"
              value={betAmount}
              onChange={(e) => setBetAmount(Number(e.target.value))}
              min={minBet}
              max={Math.min(maxBet, balance)}
              className="flex-1 bg-gray-800 border-gray-700 text-white"
            />
            <Button
              onClick={handleBet}
              disabled={disabled || gameActive || betAmount > balance || loading}
              className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-black font-bold hover:from-yellow-300 hover:to-yellow-500"
            >
              {gameActive ? 'Playing...' : 'Bet'}
            </Button>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {quickBets.map(amount => (
            <Button
              key={amount}
              size="sm"
              variant="outline"
              onClick={() => setBetAmount(amount)}
              disabled={amount > balance}
              className="border-yellow-400/50 text-yellow-400 hover:bg-yellow-400/10"
            >
              {amount}
            </Button>
          ))}
          <Button
            size="sm"
            variant="outline"
            onClick={() => setBetAmount(Math.floor(balance / 2))}
            disabled={balance === 0}
            className="border-yellow-400/50 text-yellow-400 hover:bg-yellow-400/10"
          >
            Half
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => setBetAmount(balance)}
            disabled={balance === 0}
            className="border-yellow-400/50 text-yellow-400 hover:bg-yellow-400/10"
          >
            Max
          </Button>
        </div>

        <div className="text-xs text-gray-400">
          Min: {minBet} CRT | Max: {maxBet} CRT
        </div>
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
const CasinoGameLayout = ({ children, title, onBack, stats }) => {
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
          </div>
        </div>
      </div>
    </div>
  );
};

export { CRTCoin };
export default CasinoGameLayout;