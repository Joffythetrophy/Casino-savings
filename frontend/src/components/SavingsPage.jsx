import React, { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import Header from './Header';
import { 
  PiggyBank, 
  TrendingUp, 
  Calendar,
  BarChart3,
  Download,
  Eye,
  Coins,
  ArrowLeft
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const CRTCoin = ({ size = 'w-5 h-5' }) => (
  <img 
    src="https://customer-assets.emergentagent.com/job_blockchain-casino/artifacts/nx4ol97f_copilot_image_1755811225489.jpeg"
    alt="CRT Token"
    className={`${size} rounded-full`}
  />
);

const SavingsPage = () => {
  const [savingsData, setSavingsData] = useState(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState('all');
  const navigate = useNavigate();
  
import React, { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import Header from './Header';
import { 
  PiggyBank, 
  TrendingUp, 
  Calendar,
  BarChart3,
  Download,
  Eye,
  Coins,
  ArrowLeft
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CRTCoin = ({ size = 'w-5 h-5' }) => (
  <img 
    src="https://customer-assets.emergentagent.com/job_blockchain-casino/artifacts/nx4ol97f_copilot_image_1755811225489.jpeg"
    alt="CRT Token"
    className={`${size} rounded-full`}
  />
);

const SavingsPage = () => {
  const [savingsData, setSavingsData] = useState(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  
  // Demo wallet address - in production this would come from wallet connection
  const walletAddress = "demo_wallet_123";
  
  useEffect(() => {
    fetchSavingsData();
  }, []);
  
  const fetchSavingsData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // For demo purposes, we'll simulate API response since auth is not fully implemented
      // In production, this would be a real API call with JWT token
      
      // Simulate empty initial state - user needs to play games to accumulate savings
      const mockEmptyResponse = {
        success: true,
        wallet_address: walletAddress,
        total_savings: {},
        total_usd: 0,
        savings_history: [],
        stats: {
          total_games: 0,
          total_wins: 0,
          total_losses: 0,
          win_rate: 0
        }
      };
      
      setSavingsData(mockEmptyResponse);
      setLoading(false);
      
    } catch (err) {
      console.error('Error fetching savings data:', err);
      setError('Failed to load savings data');
      setLoading(false);
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
      default:
        return <Coins className="w-5 h-5" />;
    }
  };

  const exportSavings = () => {
    if (!savingsData || savingsData.savings_history.length === 0) {
      alert('No savings data to export. Start playing games to build your savings!');
      return;
    }
    
    const csvData = savingsData.savings_history.map(row => 
      `${row.date},${row.game},${row.currency},${row.amount},${row.game_result},${row.running_total}`
    );
    const csv = "Date,Game,Currency,Amount,Result,Running Total\n" + csvData.join("\n");
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', 'casino-savings-report.csv');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading your savings data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-red-400 text-xl">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <Header />
      
      <main className="pt-24 pb-12 px-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                onClick={() => navigate('/')}
                className="text-yellow-400 hover:text-yellow-300"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back to Casino
              </Button>
              <div className="flex items-center space-x-3">
                <PiggyBank className="w-8 h-8 text-yellow-400" />
                <h1 className="text-4xl font-bold text-yellow-400">My Savings Vault</h1>
              </div>
            </div>
            <Button
              onClick={exportSavings}
              className="bg-green-600 hover:bg-green-500 text-white"
              disabled={!savingsData || savingsData.savings_history.length === 0}
            >
              <Download className="w-4 h-4 mr-2" />
              Export Report
            </Button>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="p-6 bg-gradient-to-br from-green-800/20 to-green-900/20 border border-green-400/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Total Saved (USD)</p>
                  <p className="text-3xl font-bold text-green-400">
                    ${savingsData?.total_usd?.toFixed(2) || '0.00'}
                  </p>
                  <div className="flex items-center space-x-1 mt-1">
                    <TrendingUp className="w-4 h-4 text-green-400" />
                    <span className="text-green-400 text-sm">
                      {savingsData?.stats?.total_losses > 0 ? '+Growing' : 'Start playing to save!'}
                    </span>
                  </div>
                </div>
                <PiggyBank className="w-12 h-12 text-green-400" />
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-yellow-800/20 to-yellow-900/20 border border-yellow-400/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">CRT Tokens Saved</p>
                  <p className="text-2xl font-bold text-yellow-400">
                    {savingsData?.total_savings?.CRT?.toFixed(2) || '0.00'}
                  </p>
                  <p className="text-yellow-300 text-sm">
                    ≈ ${((savingsData?.total_savings?.CRT || 0) * 5.02).toFixed(2)}
                  </p>
                </div>
                <CRTCoin size="w-12 h-12" />
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-orange-800/20 to-orange-900/20 border border-orange-400/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">DOGE Saved</p>
                  <p className="text-2xl font-bold text-orange-400">
                    {savingsData?.total_savings?.DOGE?.toFixed(2) || '0.00'}
                  </p>
                  <p className="text-orange-300 text-sm">
                    ≈ ${((savingsData?.total_savings?.DOGE || 0) * 0.24).toFixed(2)}
                  </p>
                </div>
                <div className="w-12 h-12 bg-yellow-500 rounded-full flex items-center justify-center text-2xl">🐕</div>
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-red-800/20 to-red-900/20 border border-red-400/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">TRX Saved</p>
                  <p className="text-2xl font-bold text-red-400">
                    {savingsData?.total_savings?.TRX?.toFixed(2) || '0.00'}
                  </p>
                  <p className="text-red-300 text-sm">
                    ≈ ${((savingsData?.total_savings?.TRX || 0) * 0.51).toFixed(2)}
                  </p>
                </div>
                <div className="w-12 h-12 bg-red-500 rounded-full flex items-center justify-center text-xl font-bold text-white">T</div>
              </div>
            </Card>
          </div>

          {savingsData?.savings_history?.length === 0 ? (
            // Empty State
            <Card className="p-12 bg-gray-900/50 border-yellow-400/20 text-center">
              <PiggyBank className="w-24 h-24 text-gray-500 mx-auto mb-6" />
              <h2 className="text-3xl font-bold text-gray-400 mb-4">Start Building Your Savings!</h2>
              <p className="text-gray-500 text-lg mb-8 max-w-2xl mx-auto">
                Your savings vault is empty. Play casino games and every loss will automatically 
                contribute to your savings across CRT, DOGE, and TRX currencies!
              </p>
              <Button
                onClick={() => navigate('/')}
                className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-black font-bold hover:from-yellow-300 hover:to-yellow-500 px-8 py-4 text-lg"
              >
                Start Playing Casino Games
              </Button>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 max-w-4xl mx-auto">
                <div className="bg-gray-800/50 p-6 rounded-lg">
                  <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Coins className="w-6 h-6 text-blue-400" />
                  </div>
                  <h3 className="text-lg font-bold text-blue-400 mb-2">Play Games</h3>
                  <p className="text-gray-400 text-sm">Choose from Slots, Roulette, Dice, Plinko, Keno, or Mines</p>
                </div>
                <div className="bg-gray-800/50 p-6 rounded-lg">
                  <div className="w-12 h-12 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <TrendingUp className="w-6 h-6 text-red-400" />
                  </div>
                  <h3 className="text-lg font-bold text-red-400 mb-2">Losses = Savings</h3>
                  <p className="text-gray-400 text-sm">Every game loss automatically goes to your savings vault</p>
                </div>
                <div className="bg-gray-800/50 p-6 rounded-lg">
                  <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                    <PiggyBank className="w-6 h-6 text-green-400" />
                  </div>
                  <h3 className="text-lg font-bold text-green-400 mb-2">Watch It Grow</h3>
                  <p className="text-gray-400 text-sm">Track your savings growth across multiple cryptocurrencies</p>
                </div>
              </div>
            </Card>
          ) : (
            // Savings History Table (when data exists)
            <>
              {/* Filters */}
              <Card className="p-4 mb-6 bg-gray-900/50 border-yellow-400/20">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <Calendar className="w-5 h-5 text-yellow-400" />
                    <span className="text-gray-300">Time Period:</span>
                    <div className="flex space-x-2">
                      {['7d', '30d', '90d', 'all'].map(period => (
                        <Button
                          key={period}
                          size="sm"
                          variant={selectedTimeframe === period ? "default" : "outline"}
                          onClick={() => setSelectedTimeframe(period)}
                          className={selectedTimeframe === period 
                            ? "bg-yellow-400 text-black" 
                            : "border-yellow-400/50 text-yellow-400 hover:bg-yellow-400/10"
                          }
                        >
                          {period === 'all' ? 'All Time' : period}
                        </Button>
                      ))}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 text-gray-400">
                    <Eye className="w-4 h-4" />
                    <span className="text-sm">Showing {savingsData?.savings_history?.length || 0} transactions</span>
                  </div>
                </div>
              </Card>

              <Card className="p-6 bg-gray-900/50 border-yellow-400/20 mb-8">
                <div className="flex items-center space-x-3 mb-6">
                  <BarChart3 className="w-6 h-6 text-yellow-400" />
                  <h2 className="text-2xl font-bold text-yellow-400">Savings History</h2>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="border-b border-gray-700">
                        <th className="pb-3 text-gray-400 font-medium">Date & Time</th>
                        <th className="pb-3 text-gray-400 font-medium">Game</th>
                        <th className="pb-3 text-gray-400 font-medium">Currency</th>
                        <th className="pb-3 text-gray-400 font-medium">Amount Saved</th>
                        <th className="pb-3 text-gray-400 font-medium">Result</th>
                        <th className="pb-3 text-gray-400 font-medium">Running Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {savingsData?.savings_history?.map((transaction, index) => (
                        <tr 
                          key={transaction._id} 
                          className={`border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors ${
                            index === 0 ? 'bg-yellow-400/5' : ''
                          }`}
                        >
                          <td className="py-4 text-gray-300">{transaction.date}</td>
                          <td className="py-4">
                            <div className="flex items-center space-x-2">
                              <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                              <span className="text-white font-medium">{transaction.game}</span>
                            </div>
                          </td>
                          <td className="py-4">
                            <div className="flex items-center space-x-2">
                              {getCurrencyIcon(transaction.currency)}
                              <span className="text-white font-medium">{transaction.currency}</span>
                            </div>
                          </td>
                          <td className="py-4">
                            <span className="text-green-400 font-bold">+{transaction.amount.toFixed(2)}</span>
                          </td>
                          <td className="py-4">
                            <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-sm">
                              {transaction.game_result}
                            </span>
                          </td>
                          <td className="py-4">
                            <span className="text-yellow-400 font-bold">{transaction.running_total.toFixed(2)}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </>
          )}

          {/* Game Stats */}
          {savingsData?.stats && (
            <Card className="p-6 bg-gray-900/50 border-yellow-400/20 mb-8">
              <h3 className="text-xl font-bold text-yellow-400 mb-4">Gaming Statistics</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">{savingsData.stats.total_games}</div>
                  <div className="text-gray-400 text-sm">Total Games</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-400">{savingsData.stats.total_wins}</div>
                  <div className="text-gray-400 text-sm">Wins</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-400">{savingsData.stats.total_losses}</div>
                  <div className="text-gray-400 text-sm">Losses (Saved)</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-400">{savingsData.stats.win_rate.toFixed(1)}%</div>
                  <div className="text-gray-400 text-sm">Win Rate</div>
                </div>
              </div>
            </Card>
          )}

          {/* Info Card */}
          <Card className="p-6 bg-gradient-to-r from-blue-800/20 to-purple-800/20 border border-blue-400/20">
            <h3 className="text-xl font-bold text-blue-400 mb-4">💡 How Casino Savings Works</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-blue-400 rounded-full mt-2"></div>
                <div>
                  <p className="text-white font-medium">Automatic Savings</p>
                  <p className="text-gray-300 text-sm">Every game loss automatically goes to your savings vault</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-400 rounded-full mt-2"></div>
                <div>
                  <p className="text-white font-medium">Multi-Currency Support</p>
                  <p className="text-gray-300 text-sm">Save in CRT, DOGE, and TRX from different games</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2"></div>
                <div>
                  <p className="text-white font-medium">Real-Time Tracking</p>
                  <p className="text-gray-300 text-sm">Watch your savings grow with each game session</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-purple-400 rounded-full mt-2"></div>
                <div>
                  <p className="text-white font-medium">Export Reports</p>
                  <p className="text-gray-300 text-sm">Download your savings history as CSV for records</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

  const getCurrencyIcon = (currency) => {
    switch(currency) {
      case 'CRT':
        return <CRTCoin size="w-5 h-5" />;
      case 'DOGE':
        return <div className="w-5 h-5 bg-yellow-500 rounded-full flex items-center justify-center text-xs">🐕</div>;
      case 'TRX':
        return <div className="w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-xs font-bold text-white">T</div>;
      default:
        return <Coins className="w-5 h-5" />;
    }
  };

  const exportSavings = () => {
    const csvData = savingsData.savingsHistory.map(row => 
      `${row.date},${row.game},${row.currency},${row.amount},${row.gameResult},${row.runningTotal},${row.multiplier}`
    );
    const csv = "Date,Game,Currency,Amount,Result,Running Total,Multiplier\n" + csvData.join("\n");
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', 'casino-savings-report.csv');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  if (!savingsData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white">Loading savings data...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <Header />
      
      <main className="pt-24 pb-12 px-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                onClick={() => navigate('/')}
                className="text-yellow-400 hover:text-yellow-300"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back to Casino
              </Button>
              <div className="flex items-center space-x-3">
                <PiggyBank className="w-8 h-8 text-yellow-400" />
                <h1 className="text-4xl font-bold text-yellow-400">My Savings Vault</h1>
              </div>
            </div>
            <Button
              onClick={exportSavings}
              className="bg-green-600 hover:bg-green-500 text-white"
            >
              <Download className="w-4 h-4 mr-2" />
              Export Report
            </Button>
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className="p-6 bg-gradient-to-br from-green-800/20 to-green-900/20 border border-green-400/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Total Saved (USD)</p>
                  <p className="text-3xl font-bold text-green-400">${savingsData.totalSavings.totalUSD.toFixed(2)}</p>
                  <div className="flex items-center space-x-1 mt-1">
                    <TrendingUp className="w-4 h-4 text-green-400" />
                    <span className="text-green-400 text-sm">+15.2% this month</span>
                  </div>
                </div>
                <PiggyBank className="w-12 h-12 text-green-400" />
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-yellow-800/20 to-yellow-900/20 border border-yellow-400/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">CRT Tokens Saved</p>
                  <p className="text-2xl font-bold text-yellow-400">{savingsData.totalSavings.CRT.toFixed(2)}</p>
                  <p className="text-yellow-300 text-sm">≈ $742.73</p>
                </div>
                <CRTCoin size="w-12 h-12" />
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-orange-800/20 to-orange-900/20 border border-orange-400/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">DOGE Saved</p>
                  <p className="text-2xl font-bold text-orange-400">{savingsData.totalSavings.DOGE.toFixed(2)}</p>
                  <p className="text-orange-300 text-sm">≈ $1,256.32</p>
                </div>
                <div className="w-12 h-12 bg-yellow-500 rounded-full flex items-center justify-center text-2xl">🐕</div>
              </div>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-red-800/20 to-red-900/20 border border-red-400/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">TRX Saved</p>
                  <p className="text-2xl font-bold text-red-400">{savingsData.totalSavings.TRX.toFixed(2)}</p>
                  <p className="text-red-300 text-sm">≈ $457.73</p>
                </div>
                <div className="w-12 h-12 bg-red-500 rounded-full flex items-center justify-center text-xl font-bold text-white">T</div>
              </div>
            </Card>
          </div>

          {/* Filters */}
          <Card className="p-4 mb-6 bg-gray-900/50 border-yellow-400/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Calendar className="w-5 h-5 text-yellow-400" />
                <span className="text-gray-300">Time Period:</span>
                <div className="flex space-x-2">
                  {['7d', '30d', '90d', 'all'].map(period => (
                    <Button
                      key={period}
                      size="sm"
                      variant={selectedTimeframe === period ? "default" : "outline"}
                      onClick={() => setSelectedTimeframe(period)}
                      className={selectedTimeframe === period 
                        ? "bg-yellow-400 text-black" 
                        : "border-yellow-400/50 text-yellow-400 hover:bg-yellow-400/10"
                      }
                    >
                      {period === 'all' ? 'All Time' : period}
                    </Button>
                  ))}
                </div>
              </div>
              <div className="flex items-center space-x-2 text-gray-400">
                <Eye className="w-4 h-4" />
                <span className="text-sm">Showing {savingsData.savingsHistory.length} transactions</span>
              </div>
            </div>
          </Card>

          {/* Savings History Table */}
          <Card className="p-6 bg-gray-900/50 border-yellow-400/20 mb-8">
            <div className="flex items-center space-x-3 mb-6">
              <BarChart3 className="w-6 h-6 text-yellow-400" />
              <h2 className="text-2xl font-bold text-yellow-400">Savings History</h2>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="pb-3 text-gray-400 font-medium">Date & Time</th>
                    <th className="pb-3 text-gray-400 font-medium">Game</th>
                    <th className="pb-3 text-gray-400 font-medium">Currency</th>
                    <th className="pb-3 text-gray-400 font-medium">Amount Saved</th>
                    <th className="pb-3 text-gray-400 font-medium">Multiplier Missed</th>
                    <th className="pb-3 text-gray-400 font-medium">Result</th>
                    <th className="pb-3 text-gray-400 font-medium">Running Total</th>
                  </tr>
                </thead>
                <tbody>
                  {savingsData.savingsHistory.map((transaction, index) => (
                    <tr 
                      key={transaction.id} 
                      className={`border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors ${
                        index === 0 ? 'bg-yellow-400/5' : ''
                      }`}
                    >
                      <td className="py-4 text-gray-300">{transaction.date}</td>
                      <td className="py-4">
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                          <span className="text-white font-medium">{transaction.game}</span>
                        </div>
                      </td>
                      <td className="py-4">
                        <div className="flex items-center space-x-2">
                          {getCurrencyIcon(transaction.currency)}
                          <span className="text-white font-medium">{transaction.currency}</span>
                        </div>
                      </td>
                      <td className="py-4">
                        <span className="text-green-400 font-bold">+{transaction.amount.toFixed(2)}</span>
                      </td>
                      <td className="py-4">
                        <span className="text-red-300">{transaction.multiplier}</span>
                      </td>
                      <td className="py-4">
                        <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-sm">
                          {transaction.gameResult}
                        </span>
                      </td>
                      <td className="py-4">
                        <span className="text-yellow-400 font-bold">{transaction.runningTotal.toFixed(2)}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Info Card */}
          <Card className="p-6 bg-gradient-to-r from-blue-800/20 to-purple-800/20 border border-blue-400/20">
            <h3 className="text-xl font-bold text-blue-400 mb-4">💡 How Casino Savings Works</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-blue-400 rounded-full mt-2"></div>
                <div>
                  <p className="text-white font-medium">Automatic Savings</p>
                  <p className="text-gray-300 text-sm">Every game loss automatically goes to your savings vault</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-400 rounded-full mt-2"></div>
                <div>
                  <p className="text-white font-medium">Multi-Currency Support</p>
                  <p className="text-gray-300 text-sm">Save in CRT, DOGE, and TRX from different games</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2"></div>
                <div>
                  <p className="text-white font-medium">Real-Time Tracking</p>
                  <p className="text-gray-300 text-sm">Watch your savings grow with each game session</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-purple-400 rounded-full mt-2"></div>
                <div>
                  <p className="text-white font-medium">Export Reports</p>
                  <p className="text-gray-300 text-sm">Download your savings history as CSV for records</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default SavingsPage;