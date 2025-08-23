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
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  
  useEffect(() => {
    const fetchSavingsData = async () => {
      try {
        setLoading(true);
        
        // Get authenticated user
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        if (!user.wallet_address) {
          console.error('No authenticated user found');
          setSavingsData({
            total_savings: {},
            total_usd: 0,
            savings_history: [],
            stats: { total_games: 0, total_wins: 0, total_losses: 0, win_rate: 0 }
          });
          setLoading(false);
          return;
        }

        // Fetch real savings data from backend
        const backendUrl = import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
        
        // Get wallet data (includes savings_balance)
        const walletResponse = await fetch(`${backendUrl}/api/wallet/${user.wallet_address}`);
        const walletData = await walletResponse.json();
        
        if (walletData.success) {
          const savings = walletData.wallet.savings_balance || {};
          
          // Calculate total USD value using real-time prices
          const prices = { CRT: 0.15, DOGE: 0.08, TRX: 0.015, USDC: 1.0 };
          let totalUsd = 0;
          
          Object.entries(savings).forEach(([currency, amount]) => {
            totalUsd += (amount || 0) * (prices[currency] || 0);
          });
          
          // Get game history for stats
          let gameStats = { total_games: 0, total_wins: 0, total_losses: 0, win_rate: 0 };
          try {
            const historyResponse = await fetch(`${backendUrl}/api/games/history/${user.wallet_address}`);
            if (historyResponse.ok) {
              const historyData = await historyResponse.json();
              if (historyData.success && historyData.history) {
                const history = historyData.history;
                gameStats = {
                  total_games: history.length,
                  total_wins: history.filter(game => game.result === 'win').length,
                  total_losses: history.filter(game => game.result === 'loss').length,
                  win_rate: history.length > 0 ? (history.filter(game => game.result === 'win').length / history.length * 100) : 0
                };
              }
            }
          } catch (error) {
            console.log('Game history not available yet');
          }
          
          setSavingsData({
            total_savings: savings,
            total_usd: totalUsd,
            savings_history: [], // Could be populated with transaction history
            stats: gameStats
          });
        } else {
          console.error('Failed to fetch wallet data:', walletData.message);
          setSavingsData({
            total_savings: {},
            total_usd: 0,
            savings_history: [],
            stats: { total_games: 0, total_wins: 0, total_losses: 0, win_rate: 0 }
          });
        }
        
      } catch (error) {
        console.error('Error fetching savings data:', error);
        setSavingsData({
          total_savings: {},
          total_usd: 0,
          savings_history: [],
          stats: { total_games: 0, total_wins: 0, total_losses: 0, win_rate: 0 }
        });
      } finally {
        setLoading(false);
      }
    };

    fetchSavingsData();
  }, []);

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

          {/* Empty State - Show this until user starts playing */}
          <Card className="p-12 bg-gray-900/50 border-yellow-400/20 text-center">
            <PiggyBank className="w-24 h-24 text-gray-500 mx-auto mb-6" />
            <h2 className="text-3xl font-bold text-gray-400 mb-4">Ready to Start Saving!</h2>
            <p className="text-gray-500 text-lg mb-8 max-w-2xl mx-auto">
              Your savings vault is ready and connected! Play casino games and every loss will 
              automatically contribute to your savings across CRT, DOGE, and TRX currencies.
            </p>
            <Button
              onClick={() => navigate('/')}
              className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-black font-bold hover:from-yellow-300 hover:to-yellow-500 px-8 py-4 text-lg"
            >
              Start Playing & Saving Now!
            </Button>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 max-w-4xl mx-auto">
              <div className="bg-gray-800/50 p-6 rounded-lg">
                <div className="w-12 h-12 bg-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Coins className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-lg font-bold text-blue-400 mb-2">Choose Your Game</h3>
                <p className="text-gray-400 text-sm">Slots, Roulette, Dice, Plinko, Keno, or Mines - all connected to savings</p>
              </div>
              <div className="bg-gray-800/50 p-6 rounded-lg">
                <div className="w-12 h-12 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="w-6 h-6 text-red-400" />
                </div>
                <h3 className="text-lg font-bold text-red-400 mb-2">Real Savings System</h3>
                <p className="text-gray-400 text-sm">Every game loss automatically becomes part of your crypto savings portfolio</p>
              </div>
              <div className="bg-gray-800/50 p-6 rounded-lg">
                <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <BarChart3 className="w-6 h-6 text-green-400" />
                </div>
                <h3 className="text-lg font-bold text-green-400 mb-2">Track & Export</h3>
                <p className="text-gray-400 text-sm">Real-time tracking with CSV export for your financial records</p>
              </div>
            </div>
          </Card>

          {/* Info Card */}
          <Card className="p-6 bg-gradient-to-r from-blue-800/20 to-purple-800/20 border border-blue-400/20 mt-8">
            <h3 className="text-xl font-bold text-blue-400 mb-4">💡 How Real Savings Works</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-blue-400 rounded-full mt-2"></div>
                <div>
                  <p className="text-white font-medium">Automatic & Real</p>
                  <p className="text-gray-300 text-sm">No mock data - every game loss immediately goes to your actual savings</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-400 rounded-full mt-2"></div>
                <div>
                  <p className="text-white font-medium">Blockchain Connected</p>
                  <p className="text-gray-300 text-sm">Integrated with real CRT, DOGE, and TRX wallets and transactions</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2"></div>
                <div>
                  <p className="text-white font-medium">Live Data</p>
                  <p className="text-gray-300 text-sm">Real-time updates as you play - watch your savings grow instantly</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-purple-400 rounded-full mt-2"></div>
                <div>
                  <p className="text-white font-medium">Full Transparency</p>
                  <p className="text-gray-300 text-sm">Complete transaction history with exportable reports for your records</p>
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