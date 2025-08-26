import React, { useState, useEffect } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { useToast } from '../../hooks/use-toast';
import axios from 'axios';

const GamingDepositManager = () => {
  const [portfolio, setPortfolio] = useState({});
  const [gamingBalance, setGamingBalance] = useState({});
  const [depositAmount, setDepositAmount] = useState('');
  const [selectedCurrency, setSelectedCurrency] = useState('USDC');
  const [loading, setLoading] = useState(true);
  
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  const { toast } = useToast();

  // Currency configurations
  const currencies = {
    'USDC': { 
      symbol: '$', 
      color: 'text-green-400', 
      icon: '🟢', 
      name: 'USDC',
      description: 'Stable Gaming ($1.00 = 1 USDC)'
    },
    'DOGE': { 
      symbol: 'Ð', 
      color: 'text-yellow-400', 
      icon: '🐕', 
      name: 'DOGE',
      description: 'Popular Crypto Gaming'
    },
    'TRX': { 
      symbol: 'T', 
      color: 'text-red-400', 
      icon: '🔴', 
      name: 'TRX',
      description: 'Fast Transaction Gaming'
    },
    'CRT': { 
      symbol: 'C', 
      color: 'text-blue-400', 
      icon: '🟦', 
      name: 'CRT',
      description: 'Premium Token Gaming'
    }
  };

  useEffect(() => {
    fetchBalances();
  }, []);

  const fetchBalances = async () => {
    try {
      setLoading(true);
      const savedUser = localStorage.getItem('casino_user');
      if (!savedUser) return;
      
      const user = JSON.parse(savedUser);
      const response = await axios.get(`${BACKEND_URL}/api/wallet/${user.wallet_address}`);
      
      if (response.data.success && response.data.wallet) {
        const wallet = response.data.wallet;
        setPortfolio(wallet.deposit_balance || {});
        // Gaming balance is separate from main portfolio for clearer separation
        setGamingBalance(wallet.gaming_balance || {});
      }
    } catch (error) {
      console.error('Error fetching balances:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDepositToGaming = async () => {
    try {
      const amount = parseFloat(depositAmount);
      const availablePortfolio = portfolio[selectedCurrency] || 0;
      
      if (!amount || amount <= 0) {
        toast({
          title: "❌ Invalid Amount",
          description: "Please enter a valid deposit amount",
          variant: "destructive"
        });
        return;
      }
      
      if (amount > availablePortfolio) {
        toast({
          title: "❌ Insufficient Balance",
          description: `You only have ${availablePortfolio.toFixed(2)} ${selectedCurrency} available`,
          variant: "destructive"
        });
        return;
      }

      const savedUser = localStorage.getItem('casino_user');
      if (!savedUser) return;
      
      const user = JSON.parse(savedUser);
      
      // Transfer from portfolio to gaming balance
      const response = await axios.post(`${BACKEND_URL}/api/wallet/transfer-to-gaming`, {
        wallet_address: user.wallet_address,
        currency: selectedCurrency,
        amount: amount
      });
      
      if (response.data.success) {
        toast({
          title: "✅ Deposit Successful",
          description: `${amount} ${selectedCurrency} transferred to gaming balance`,
        });
        setDepositAmount('');
        await fetchBalances();
      } else {
        throw new Error(response.data.message || 'Transfer failed');
      }
    } catch (error) {
      toast({
        title: "❌ Transfer Failed",
        description: error.message || "Could not transfer to gaming balance",
        variant: "destructive"
      });
    }
  };

  const currencyConfig = currencies[selectedCurrency];
  const portfolioAmount = portfolio[selectedCurrency] || 0;
  const gamingAmount = gamingBalance[selectedCurrency] || 0;

  if (loading) {
    return (
      <Card className="p-6 bg-gradient-to-br from-purple-900/70 to-blue-900/70 border-3 border-purple-400/50">
        <div className="text-center text-gray-400">Loading gaming manager...</div>
      </Card>
    );
  }

  return (
    <Card className="p-6 bg-gradient-to-br from-purple-900/70 to-blue-900/70 border-3 border-purple-400/50">
      <h2 className="text-3xl font-bold text-purple-400 mb-6 text-center">
        🎮 Gaming Deposit Manager
      </h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Portfolio Balance */}
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-yellow-400">💎 Main Portfolio</h3>
          
          <div className="space-y-3">
            {Object.entries(currencies).map(([currency, config]) => {
              const balance = portfolio[currency] || 0;
              return (
                <div key={currency} className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">{config.icon}</span>
                      <div>
                        <span className={`font-bold ${config.color}`}>{config.name}</span>
                        <div className="text-xs text-gray-400">{config.description}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-lg font-bold ${config.color}`}>
                        {config.symbol}{balance.toFixed(2)}
                      </div>
                      <div className="text-xs text-gray-400">Portfolio</div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Gaming Balance */}
        <div className="space-y-4">
          <h3 className="text-xl font-bold text-green-400">🎰 Gaming Balance</h3>
          
          <div className="space-y-3">
            {Object.entries(currencies).map(([currency, config]) => {
              const balance = gamingBalance[currency] || 0;
              return (
                <div key={currency} className="bg-green-900/20 border border-green-400/30 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">{config.icon}</span>
                      <div>
                        <span className={`font-bold ${config.color}`}>{config.name}</span>
                        <div className="text-xs text-green-400">Ready for Gaming</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-lg font-bold ${config.color}`}>
                        {config.symbol}{balance.toFixed(2)}
                      </div>
                      <div className="text-xs text-green-400">Gaming</div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Deposit Section */}
      <div className="mt-6 bg-purple-900/30 border-2 border-purple-400/50 rounded-lg p-6">
        <h3 className="text-xl font-bold text-purple-400 mb-4">
          💰 Transfer to Gaming Balance
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Currency Selection */}
          <div>
            <label className="text-sm text-gray-300 mb-2 block">Select Currency:</label>
            <select
              value={selectedCurrency}
              onChange={(e) => setSelectedCurrency(e.target.value)}
              className="w-full p-3 bg-gray-800 border border-gray-700 text-white rounded"
            >
              {Object.entries(currencies).map(([currency, config]) => {
                const balance = portfolio[currency] || 0;
                return (
                  <option key={currency} value={currency} disabled={balance <= 0}>
                    {config.icon} {config.name} - Available: {config.symbol}{balance.toFixed(2)}
                    {balance <= 0 ? ' (No Balance)' : ''}
                  </option>
                );
              })}
            </select>
          </div>

          {/* Amount Input */}
          <div>
            <label className="text-sm text-gray-300 mb-2 block">Deposit Amount:</label>
            <Input
              type="number"
              value={depositAmount}
              onChange={(e) => setDepositAmount(e.target.value)}
              placeholder={`Enter ${selectedCurrency} amount`}
              max={portfolioAmount}
              min="0"
              step="0.01"
              className="bg-gray-800 border-gray-700 text-white"
            />
            <div className="text-xs text-gray-400 mt-1">
              Available: {currencyConfig?.symbol}{portfolioAmount.toFixed(2)} {selectedCurrency}
            </div>
          </div>

          {/* Deposit Button */}
          <div>
            <label className="text-sm text-gray-300 mb-2 block">Action:</label>
            <Button
              onClick={handleDepositToGaming}
              disabled={!depositAmount || parseFloat(depositAmount) <= 0 || parseFloat(depositAmount) > portfolioAmount}
              className="w-full bg-purple-600 hover:bg-purple-500 text-white font-bold"
            >
              Transfer to Gaming
            </Button>
          </div>
        </div>

        {/* Quick Amount Buttons */}
        <div className="mt-4">
          <div className="text-sm text-gray-300 mb-2">Quick Amounts:</div>
          <div className="flex flex-wrap gap-2">
            {[100, 1000, 5000, 10000].map((amount) => (
              <Button
                key={amount}
                onClick={() => setDepositAmount(amount.toString())}
                variant="outline"
                size="sm"
                className="border-purple-600 text-purple-400 hover:bg-purple-600/20"
                disabled={amount > portfolioAmount}
              >
                {currencyConfig?.symbol}{amount}
              </Button>
            ))}
            <Button
              onClick={() => setDepositAmount(portfolioAmount.toString())}
              variant="outline"
              size="sm"
              className="border-purple-600 text-purple-400 hover:bg-purple-600/20"
              disabled={portfolioAmount <= 0}
            >
              All ({currencyConfig?.symbol}{portfolioAmount.toFixed(0)})
            </Button>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="mt-4 bg-gray-800/50 rounded-lg p-4">
        <h4 className="text-yellow-400 font-bold mb-2">💡 How It Works:</h4>
        <ul className="text-sm text-gray-300 space-y-1">
          <li>• <strong>Portfolio</strong>: Your main cryptocurrency holdings</li>
          <li>• <strong>Gaming Balance</strong>: Funds specifically allocated for casino gaming</li>
          <li>• <strong>Separation</strong>: Keep gaming funds separate from main portfolio for better control</li>
          <li>• <strong>Safety</strong>: Only risk what you transfer to gaming balance</li>
        </ul>
      </div>
    </Card>
  );
};

export default GamingDepositManager;