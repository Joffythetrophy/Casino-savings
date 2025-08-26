import React, { useState, useEffect } from 'react';
import { Card } from '../ui/card';
import { useToast } from '../../hooks/use-toast';
import axios from 'axios';

const MoneyTracker = ({ gameType = 'Casino' }) => {
  const [stats, setStats] = useState({
    sessionWon: 0,
    sessionLost: 0,
    sessionNetProfit: 0,
    totalSaved: 0,
    liquidityContributed: 0,
    vaultBalance: 0,
    totalBets: 0,
    winRate: 0
  });
  const [loading, setLoading] = useState(true);
  
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const { toast } = useToast();

  useEffect(() => {
    fetchMoneyStats();
  }, []);

  const fetchMoneyStats = async () => {
    try {
      setLoading(true);
      const savedUser = localStorage.getItem('casino_user');
      if (!savedUser) return;
      
      const user = JSON.parse(savedUser);
      
      // Get user wallet info with savings
      const walletResponse = await axios.get(`${BACKEND_URL}/api/wallet/${user.wallet_address}`);
      
      if (walletResponse.data.success) {
        const wallet = walletResponse.data.wallet;
        const savingsBalance = wallet.savings_balance || {};
        const depositBalance = wallet.deposit_balance || {};
        
        // Calculate total saved across all currencies
        const totalSaved = Object.values(savingsBalance).reduce((sum, amount) => sum + (amount || 0), 0);
        
        // Get recent game stats
        const gamesResponse = await axios.get(`${BACKEND_URL}/api/games/stats/${user.wallet_address}`);
        let gameStats = { sessionWon: 0, sessionLost: 0, totalBets: 0, winRate: 0 };
        
        if (gamesResponse.data.success) {
          gameStats = gamesResponse.data.stats;
        }
        
        // Get vault balance
        const vaultResponse = await axios.get(`${BACKEND_URL}/api/savings/vault/${user.wallet_address}`);
        let vaultBalance = 0;
        if (vaultResponse.data.success) {
          const vaultBalances = vaultResponse.data.vault_balances || {};
          vaultBalance = Object.values(vaultBalances).reduce((sum, amount) => sum + (amount || 0), 0);
        }
        
        setStats({
          sessionWon: gameStats.sessionWon || 0,
          sessionLost: gameStats.sessionLost || 0,
          sessionNetProfit: (gameStats.sessionWon || 0) - (gameStats.sessionLost || 0),
          totalSaved: totalSaved,
          liquidityContributed: totalSaved * 0.1, // 10% goes to liquidity
          vaultBalance: vaultBalance,
          totalBets: gameStats.totalBets || 0,
          winRate: gameStats.winRate || 0
        });
      }
    } catch (error) {
      console.error('Error fetching money stats:', error);
    } finally {
      setLoading(false);
    }
  };

  // Update stats when game results come in
  const updateStats = (betAmount, won, currency, savingsAdded = 0, liquidityAdded = 0) => {
    setStats(prev => ({
      ...prev,
      sessionWon: prev.sessionWon + (won ? betAmount : 0),
      sessionLost: prev.sessionLost + (won ? 0 : betAmount),
      sessionNetProfit: prev.sessionNetProfit + (won ? betAmount : -betAmount),
      totalSaved: prev.totalSaved + savingsAdded,
      liquidityContributed: prev.liquidityContributed + liquidityAdded,
      totalBets: prev.totalBets + 1,
      winRate: won ? Math.min(100, prev.winRate + 1) : Math.max(0, prev.winRate - 1)
    }));
  };

  // Currency symbols
  const getCurrencySymbol = (currency) => {
    const symbols = { 'USDC': '$', 'DOGE': 'Ð', 'TRX': 'T', 'CRT': 'C' };
    return symbols[currency] || '';
  };

  if (loading) {
    return (
      <Card className="p-6 bg-gradient-to-br from-gray-900 to-gray-800 border-2 border-yellow-400/30">
        <div className="text-center text-gray-400">Loading money stats...</div>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Session Statistics - Big Visual Box */}
      <Card className="p-6 bg-gradient-to-br from-purple-900/70 to-blue-900/70 border-3 border-yellow-400/50">
        <h3 className="text-2xl font-bold text-yellow-400 mb-4 text-center">
          💰 {gameType} Session Money Tracker
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* Session Won */}
          <div className="bg-green-900/30 border-2 border-green-400/50 rounded-lg p-4 text-center">
            <div className="text-green-400 text-lg font-semibold">Session Won</div>
            <div className="text-3xl font-bold text-green-300">
              +{stats.sessionWon.toFixed(2)}
            </div>
            <div className="text-green-400/80 text-sm">Total Winnings</div>
          </div>
          
          {/* Session Lost */}
          <div className="bg-red-900/30 border-2 border-red-400/50 rounded-lg p-4 text-center">
            <div className="text-red-400 text-lg font-semibold">Session Lost</div>
            <div className="text-3xl font-bold text-red-300">
              -{stats.sessionLost.toFixed(2)}
            </div>
            <div className="text-red-400/80 text-sm">Total Losses</div>
          </div>
          
          {/* Net Profit */}
          <div className={`border-2 rounded-lg p-4 text-center ${
            stats.sessionNetProfit >= 0 
              ? 'bg-green-900/30 border-green-400/50' 
              : 'bg-red-900/30 border-red-400/50'
          }`}>
            <div className="text-yellow-400 text-lg font-semibold">Net Profit</div>
            <div className={`text-3xl font-bold ${
              stats.sessionNetProfit >= 0 ? 'text-green-300' : 'text-red-300'
            }`}>
              {stats.sessionNetProfit >= 0 ? '+' : ''}{stats.sessionNetProfit.toFixed(2)}
            </div>
            <div className="text-yellow-400/80 text-sm">Session Total</div>
          </div>
        </div>
        
        {/* Game Stats Row */}
        <div className="flex justify-between items-center bg-gray-800/50 rounded-lg p-4">
          <div className="text-center">
            <div className="text-gray-300 text-sm">Total Bets</div>
            <div className="text-xl font-bold text-white">{stats.totalBets}</div>
          </div>
          <div className="text-center">
            <div className="text-gray-300 text-sm">Win Rate</div>
            <div className={`text-xl font-bold ${stats.winRate >= 50 ? 'text-green-400' : 'text-red-400'}`}>
              {stats.winRate.toFixed(1)}%
            </div>
          </div>
        </div>
      </Card>

      {/* Savings & Vault - Big Visual Box */}
      <Card className="p-6 bg-gradient-to-br from-green-900/70 to-emerald-900/70 border-3 border-green-400/50">
        <h3 className="text-2xl font-bold text-green-400 mb-4 text-center">
          🏦 Savings Vault & Liquidity Tracker
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Non-Custodial Savings Vault */}
          <div className="space-y-4">
            <div className="bg-green-900/40 border-2 border-green-400/60 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-green-400 font-semibold">💎 Savings Vault</span>
                <span className="text-xs bg-green-600 text-white px-2 py-1 rounded">NON-CUSTODIAL</span>
              </div>
              <div className="text-3xl font-bold text-green-300 mb-1">
                {stats.totalSaved.toFixed(2)}
              </div>
              <div className="text-green-400/80 text-sm">Total Saved from Losses</div>
              <div className="text-xs text-green-300 mt-2">
                🔐 You control the private keys
              </div>
            </div>
            
            <div className="bg-blue-900/40 border-2 border-blue-400/60 rounded-lg p-4">
              <div className="text-blue-400 font-semibold mb-2">🔗 Real Vault Balance</div>
              <div className="text-2xl font-bold text-blue-300 mb-1">
                {stats.vaultBalance.toFixed(4)}
              </div>
              <div className="text-blue-400/80 text-sm">Blockchain Verified</div>
            </div>
          </div>
          
          {/* Liquidity Pool Contribution */}
          <div className="space-y-4">
            <div className="bg-purple-900/40 border-2 border-purple-400/60 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-purple-400 font-semibold">🌊 Liquidity Pool</span>
                <span className="text-xs bg-purple-600 text-white px-2 py-1 rounded">10%</span>
              </div>
              <div className="text-3xl font-bold text-purple-300 mb-1">
                {stats.liquidityContributed.toFixed(2)}
              </div>
              <div className="text-purple-400/80 text-sm">Your Contribution</div>
              <div className="text-xs text-purple-300 mt-2">
                💧 Helps other users withdraw
              </div>
            </div>
            
            <div className="bg-yellow-900/40 border-2 border-yellow-400/60 rounded-lg p-4">
              <div className="text-yellow-400 font-semibold mb-2">⚡ Smart Savings</div>
              <div className="text-sm text-yellow-300">
                Every loss = Automatic save to your vault!
              </div>
              <div className="text-xs text-yellow-400/80 mt-1">
                90% to vault + 10% to liquidity
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Action Buttons */}
      <Card className="p-4 bg-gray-900/50 border border-gray-700">
        <div className="flex justify-between items-center">
          <button
            onClick={fetchMoneyStats}
            className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded font-semibold"
          >
            🔄 Refresh Stats
          </button>
          
          <div className="text-right">
            <div className="text-xs text-gray-400">Last Updated</div>
            <div className="text-sm text-white">{new Date().toLocaleTimeString()}</div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default MoneyTracker;