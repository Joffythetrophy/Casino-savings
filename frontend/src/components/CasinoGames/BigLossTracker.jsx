import React, { useState, useEffect } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { useToast } from '../../hooks/use-toast';
import axios from 'axios';
import { TrendingDown, TrendingUp, Vault, Coins, Eye, Zap } from 'lucide-react';

const BigLossTracker = ({ gameType = 'Casino' }) => {
  const [lossData, setLossData] = useState({
    totalLost: 0,
    totalSaved: 0,
    sessionLosses: 0,
    vaultBalance: 0,
    liquidityContributed: 0,
    recentLosses: [],
    currency: 'USDC'
  });
  const [loading, setLoading] = useState(true);
  const [showDetails, setShowDetails] = useState(false);
  
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const { toast } = useToast();

  // Currency configurations
  const currencies = {
    'USDC': { symbol: '$', color: 'text-green-400', icon: '🟢' },
    'DOGE': { symbol: 'Ð', color: 'text-yellow-400', icon: '🐕' },
    'TRX': { symbol: 'T', color: 'text-red-400', icon: '🔴' },
    'CRT': { symbol: 'C', color: 'text-blue-400', icon: '🟦' }
  };

  useEffect(() => {
    fetchLossData();
    // Update every 10 seconds during active gaming
    const interval = setInterval(fetchLossData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchLossData = async () => {
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
        
        // Get recent game transactions
        const transactionsResponse = await axios.get(`${BACKEND_URL}/api/games/transactions/${user.wallet_address}?limit=10`);
        let recentLosses = [];
        let sessionLosses = 0;
        
        if (transactionsResponse.data.success) {
          recentLosses = transactionsResponse.data.transactions
            .filter(tx => tx.result === 'loss')
            .slice(0, 5);
          sessionLosses = recentLosses.reduce((sum, tx) => sum + (tx.bet_amount || 0), 0);
        }
        
        // Calculate totals across all currencies
        const totalSaved = Object.values(savingsBalance).reduce((sum, amount) => sum + (amount || 0), 0);
        
        // Get vault balance
        const vaultResponse = await axios.get(`${BACKEND_URL}/api/savings/vault/${user.wallet_address}`);
        let vaultBalance = 0;
        if (vaultResponse.data.success) {
          const vaultBalances = vaultResponse.data.vault_balances || {};
          vaultBalance = Object.values(vaultBalances).reduce((sum, amount) => sum + (amount || 0), 0);
        }
        
        setLossData({
          totalLost: sessionLosses, // This session's losses
          totalSaved: totalSaved,
          sessionLosses: sessionLosses,
          vaultBalance: vaultBalance,
          liquidityContributed: totalSaved * 0.1, // 10% goes to liquidity
          recentLosses: recentLosses,
          currency: 'USDC' // Default display currency
        });
      }
    } catch (error) {
      console.error('Error fetching loss data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCurrencySymbol = (currency) => {
    return currencies[currency]?.symbol || '';
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toFixed(2);
  };

  if (loading) {
    return (
      <Card className="p-8 bg-gradient-to-br from-red-900/70 to-orange-900/70 border-4 border-red-400/50">
        <div className="text-center text-gray-400 text-xl">Loading loss tracker...</div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* MAIN LOSS DISPLAY - HUGE BOX */}
      <Card className="p-8 bg-gradient-to-br from-red-900/80 to-orange-900/80 border-4 border-red-400/60 shadow-2xl">
        <div className="text-center mb-6">
          <h2 className="text-4xl font-bold text-red-400 mb-2">
            💸 CRYPTO LOSS TRACKER
          </h2>
          <div className="text-lg text-red-300">{gameType} Session</div>
        </div>

        {/* MASSIVE LOSS COUNTER */}
        <div className="bg-red-900/50 border-3 border-red-400/70 rounded-xl p-8 mb-6">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-4 mb-4">
              <TrendingDown className="w-12 h-12 text-red-400 animate-pulse" />
              <div className="text-6xl font-bold text-red-300">
                ${formatNumber(lossData.sessionLosses)}
              </div>
              <TrendingDown className="w-12 h-12 text-red-400 animate-pulse" />
            </div>
            <div className="text-2xl text-red-400 font-semibold">
              TOTAL LOST THIS SESSION
            </div>
            <div className="text-lg text-red-300/80 mt-2">
              Every loss = Automatic savings to your vault! 💎
            </div>
          </div>
        </div>

        {/* SAVINGS VISUALIZATION */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Total Saved */}
          <div className="bg-green-900/40 border-2 border-green-400/60 rounded-lg p-6 text-center">
            <Vault className="w-8 h-8 text-green-400 mx-auto mb-2" />
            <div className="text-3xl font-bold text-green-300">
              ${formatNumber(lossData.totalSaved)}
            </div>
            <div className="text-green-400 font-semibold">SAVED TO VAULT</div>
            <div className="text-xs text-green-300/80 mt-1">
              🔐 Non-custodial (you control)
            </div>
          </div>

          {/* Liquidity Contributed */}
          <div className="bg-blue-900/40 border-2 border-blue-400/60 rounded-lg p-6 text-center">
            <Coins className="w-8 h-8 text-blue-400 mx-auto mb-2" />
            <div className="text-3xl font-bold text-blue-300">
              ${formatNumber(lossData.liquidityContributed)}
            </div>
            <div className="text-blue-400 font-semibold">LIQUIDITY POOL</div>
            <div className="text-xs text-blue-300/80 mt-1">
              💧 10% helps others withdraw
            </div>
          </div>

          {/* Vault Balance */}
          <div className="bg-purple-900/40 border-2 border-purple-400/60 rounded-lg p-6 text-center">
            <Zap className="w-8 h-8 text-purple-400 mx-auto mb-2" />
            <div className="text-3xl font-bold text-purple-300">
              ${formatNumber(lossData.vaultBalance)}
            </div>
            <div className="text-purple-400 font-semibold">REAL VAULT</div>
            <div className="text-xs text-purple-300/80 mt-1">
              🌐 Blockchain verified
            </div>
          </div>
        </div>
      </Card>

      {/* RECENT LOSSES DETAIL */}
      <Card className="p-6 bg-gradient-to-br from-gray-900/80 to-gray-800/80 border-2 border-orange-400/50">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-2xl font-bold text-orange-400">
            📊 Recent Loss Details
          </h3>
          <Button
            onClick={() => setShowDetails(!showDetails)}
            variant="outline"
            className="border-orange-400 text-orange-400 hover:bg-orange-400/20"
          >
            <Eye className="w-4 h-4 mr-2" />
            {showDetails ? 'Hide' : 'Show'} Details
          </Button>
        </div>

        {showDetails && (
          <div className="space-y-3">
            {lossData.recentLosses.length > 0 ? (
              lossData.recentLosses.map((loss, index) => (
                <div key={index} className="bg-red-900/20 border border-red-400/30 rounded-lg p-4">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-red-600 rounded-full flex items-center justify-center">
                        <span className="text-white font-bold text-sm">{index + 1}</span>
                      </div>
                      <div>
                        <div className="text-white font-semibold">
                          {loss.game_type} - Lost ${(loss.bet_amount || 0).toFixed(2)}
                        </div>
                        <div className="text-gray-400 text-sm">
                          {new Date(loss.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-green-400 font-semibold">
                        +${((loss.bet_amount || 0) * 0.9).toFixed(2)} Saved
                      </div>
                      <div className="text-blue-400 text-sm">
                        +${((loss.bet_amount || 0) * 0.1).toFixed(2)} Liquidity
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center text-gray-400 py-8">
                No recent losses. Start playing to see your savings grow! 🎮
              </div>
            )}
          </div>
        )}
      </Card>

      {/* MOTIVATIONAL MESSAGE */}
      <Card className="p-6 bg-gradient-to-br from-green-900/50 to-emerald-900/50 border-2 border-green-400/50">
        <div className="text-center">
          <h3 className="text-2xl font-bold text-green-400 mb-3">
            💡 Smart Savings in Action!
          </h3>
          <div className="text-lg text-green-300">
            Every time you lose, <strong>90%</strong> goes to your secure vault + <strong>10%</strong> helps the liquidity pool.
          </div>
          <div className="text-green-200 mt-2">
            Your losses become your savings! This is the Casino Savings advantage. 🚀
          </div>
          
          {/* Update Button */}
          <Button
            onClick={fetchLossData}
            className="mt-4 bg-green-600 hover:bg-green-500 text-white font-bold"
          >
            🔄 Update Loss Data
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default BigLossTracker;