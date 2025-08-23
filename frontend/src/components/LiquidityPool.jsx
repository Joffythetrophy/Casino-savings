import React, { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { useToast } from '../hooks/use-toast';
import { 
  Droplets, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  Info,
  Zap
} from 'lucide-react';
import axios from 'axios';

const CRTCoin = ({ size = "w-6 h-6" }) => (
  <div className={`${size} rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center`}>
    <span className="text-black font-bold text-xs">C</span>
  </div>
);

const LiquidityPool = () => {
  const [liquidityData, setLiquidityData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [contributing, setContributing] = useState(false);
  const { toast } = useToast();
  
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchLiquidityData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchLiquidityData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchLiquidityData = async () => {
    try {
      setLoading(true);
      const savedUser = localStorage.getItem('casino_user');
      if (!savedUser) return;
      
      const user = JSON.parse(savedUser);
      const response = await axios.get(`${BACKEND_URL}/api/liquidity-pool/${user.wallet_address}`);
      
      if (response.data.success) {
        setLiquidityData(response.data);
      }
    } catch (error) {
      console.error('Error fetching liquidity data:', error);
      toast({
        title: "Error",
        description: "Failed to fetch liquidity pool data",
      });
    } finally {
      setLoading(false);
    }
  };

  const simulateSessionEnd = async () => {
    try {
      setContributing(true);
      const savedUser = localStorage.getItem('casino_user');
      if (!savedUser) return;
      
      const user = JSON.parse(savedUser);
      
      // Simulate a gaming session
      const response = await axios.post(`${BACKEND_URL}/api/liquidity-pool/contribute`, {
        wallet_address: user.wallet_address,
        session_duration: 15, // 15 minutes
        games_played: 5
      });
      
      if (response.data.success) {
        toast({
          title: "Liquidity Contribution Successful!",
          description: `Added ${Object.entries(response.data.contributions).map(([currency, amount]) => `${amount.toFixed(4)} ${currency}`).join(', ')} to your liquidity pool`,
        });
        
        // Refresh data
        await fetchLiquidityData();
      } else {
        toast({
          title: "Contribution Failed",
          description: response.data.message,
        });
      }
    } catch (error) {
      console.error('Error contributing to liquidity:', error);
      toast({
        title: "Error",
        description: "Failed to contribute to liquidity pool",
      });
    } finally {
      setContributing(false);
    }
  };

  const getCurrencyIcon = (currency) => {
    switch(currency) {
      case 'CRT':
        return <CRTCoin size="w-5 h-5" />;
      case 'DOGE':
        return <div className="w-5 h-5 bg-yellow-500 rounded-full flex items-center justify-center text-xs">🐕</div>;
      case 'TRX':
        return <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-xs font-bold text-white">T</div>;
      case 'USDC':
        return <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center text-xs font-bold text-white">$</div>;
      default:
        return <Droplets className="w-5 h-5" />;
    }
  };

  const getLiquidityStatus = (amount) => {
    if (amount === 0) return { status: 'empty', color: 'text-red-400', icon: AlertTriangle };
    if (amount < 10) return { status: 'low', color: 'text-yellow-400', icon: AlertTriangle };
    if (amount < 50) return { status: 'medium', color: 'text-blue-400', icon: Info };
    return { status: 'high', color: 'text-green-400', icon: CheckCircle };
  };

  if (loading) {
    return (
      <Card className="p-6 bg-gradient-to-br from-gray-800 to-gray-900 border border-yellow-400/20">
        <div className="text-center text-gray-400">Loading liquidity pool...</div>
      </Card>
    );
  }

  if (!liquidityData) {
    return (
      <Card className="p-6 bg-gradient-to-br from-gray-800 to-gray-900 border border-yellow-400/20">
        <div className="text-center text-gray-400">No liquidity data available</div>
      </Card>
    );
  }

  const { liquidity_pool, total_liquidity_usd, withdrawal_limits } = liquidityData;

  return (
    <div className="space-y-6">
      {/* Liquidity Pool Header */}
      <Card className="p-6 bg-gradient-to-br from-blue-900/50 to-indigo-900/50 border border-blue-400/30">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center">
              <Droplets className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-blue-400">Personal Liquidity Pool</h2>
              <p className="text-gray-300 text-sm">Your internal trading liquidity</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-white">${total_liquidity_usd}</div>
            <div className="text-blue-400 text-sm">Total Liquidity</div>
          </div>
        </div>

        <div className="bg-blue-900/30 p-4 rounded-lg">
          <div className="flex items-center space-x-2 mb-2">
            <Info className="w-4 h-4 text-blue-400" />
            <span className="text-blue-400 text-sm font-semibold">How it works:</span>
          </div>
          <p className="text-gray-300 text-sm">
            Your liquidity pool enables free currency conversions and withdrawals. 
            After each gaming session, 10% of your savings automatically contributes to increase liquidity.
          </p>
        </div>
      </Card>

      {/* Liquidity Breakdown */}
      <Card className="p-6 bg-gradient-to-br from-gray-800 to-gray-900 border border-yellow-400/20">
        <h3 className="text-lg font-bold text-yellow-400 mb-4">Liquidity by Currency</h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(liquidity_pool).map(([currency, amount]) => {
            if (typeof amount !== 'number') return null;
            
            const { status, color, icon: StatusIcon } = getLiquidityStatus(amount);
            
            return (
              <div key={currency} className="bg-black/20 p-4 rounded-lg border border-gray-600">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    {getCurrencyIcon(currency)}
                    <span className="font-semibold text-white">{currency}</span>
                  </div>
                  <StatusIcon className={`w-4 h-4 ${color}`} />
                </div>
                
                <div className="space-y-1">
                  <div className="text-xl font-bold text-white">
                    {amount.toFixed(4)}
                  </div>
                  <div className="text-xs text-gray-400 capitalize">
                    {status} liquidity
                  </div>
                  <div className="text-xs text-blue-400">
                    Withdraw limit: {withdrawal_limits[currency]?.toFixed(4) || '0.0000'}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {/* Actions */}
      <Card className="p-6 bg-gradient-to-br from-gray-800 to-gray-900 border border-yellow-400/20">
        <h3 className="text-lg font-bold text-yellow-400 mb-4">Liquidity Actions</h3>
        
        <div className="space-y-4">
          <Button
            onClick={simulateSessionEnd}
            disabled={contributing}
            className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-500 hover:to-green-600 text-white font-bold py-3"
          >
            {contributing ? (
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                <span>Contributing...</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4" />
                <span>Simulate Session End (Add 10% from Savings)</span>
              </div>
            )}
          </Button>
          
          <div className="text-center text-xs text-gray-400">
            In the real casino, this happens automatically after each gaming session
          </div>
        </div>
      </Card>

      {/* Liquidity Benefits */}
      <Card className="p-6 bg-gradient-to-br from-gray-800 to-gray-900 border border-yellow-400/20">
        <h3 className="text-lg font-bold text-yellow-400 mb-4">Benefits of Higher Liquidity</h3>
        
        <div className="grid md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span className="text-gray-300 text-sm">Higher withdrawal limits</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span className="text-gray-300 text-sm">Smoother currency conversions</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-green-400" />
              <span className="text-gray-300 text-sm">Better trading flexibility</span>
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-blue-400" />
              <span className="text-gray-300 text-sm">Automatic liquidity growth</span>
            </div>
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-blue-400" />
              <span className="text-gray-300 text-sm">Reduced conversion restrictions</span>
            </div>
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-blue-400" />
              <span className="text-gray-300 text-sm">Enhanced gaming experience</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default LiquidityPool;