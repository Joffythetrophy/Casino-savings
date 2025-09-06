import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { useToast } from './ui/use-toast';

const DevelopmentFundDashboard = () => {
  const [portfolio, setPortfolio] = useState(null);
  const [balances, setBalances] = useState(null);
  const [loading, setLoading] = useState(true);
  const [withdrawForm, setWithdrawForm] = useState({
    currency: '',
    amount: '',
    destination_address: ''
  });
  const [convertForm, setConvertForm] = useState({
    from_currency: '',
    to_currency: '',
    amount: ''
  });
  const { toast } = useToast();

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const fetchPortfolioData = async () => {
    try {
      setLoading(true);
      
      // Fetch portfolio
      const portfolioResponse = await fetch(`${backendUrl}/api/portfolio`);
      const portfolioData = await portfolioResponse.json();
      
      // Fetch balances
      const balancesResponse = await fetch(`${backendUrl}/api/balances`);
      const balancesData = await balancesResponse.json();
      
      if (portfolioData.success) {
        setPortfolio(portfolioData);
      }
      
      if (balancesData.success) {
        setBalances(balancesData);
      }
      
    } catch (error) {
      console.error('Error fetching portfolio data:', error);
      toast({
        title: "Error",
        description: "Failed to fetch portfolio data",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleWithdraw = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${backendUrl}/api/withdraw`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(withdrawForm)
      });
      
      const data = await response.json();
      
      if (data.success) {
        toast({
          title: "Withdrawal Successful",
          description: data.message,
          variant: "default"
        });
        
        // Reset form and refresh data
        setWithdrawForm({ currency: '', amount: '', destination_address: '' });
        fetchPortfolioData();
      } else {
        throw new Error(data.detail || 'Withdrawal failed');
      }
      
    } catch (error) {
      toast({
        title: "Withdrawal Failed",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  const handleConvert = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${backendUrl}/api/convert`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(convertForm)
      });
      
      const data = await response.json();
      
      if (data.success) {
        toast({
          title: "Conversion Successful",
          description: data.message,
          variant: "default"
        });
        
        // Reset form and refresh data
        setConvertForm({ from_currency: '', to_currency: '', amount: '' });
        fetchPortfolioData();
      } else {
        throw new Error(data.detail || 'Conversion failed');
      }
      
    } catch (error) {
      toast({
        title: "Conversion Failed",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg">Loading Development Fund Dashboard...</p>
        </div>
      </div>
    );
  }

  const currencies = portfolio?.portfolio ? Object.keys(portfolio.portfolio) : [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 p-6">
      <div className="max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            🏦 Tiger Bank Games - Development Fund System
          </h1>
          <p className="text-xl text-blue-200">
            Multi-token portfolio management with CDT bridge integration
          </p>
          {portfolio?.summary && (
            <div className="mt-4">
              <Badge variant="secondary" className="text-lg px-4 py-2">
                Total Portfolio Value: ${portfolio.summary.total_value_usd.toLocaleString()}
              </Badge>
            </div>
          )}
        </div>

        {/* Portfolio Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {balances?.balances && Object.entries(balances.balances).map(([symbol, data]) => (
            <Card key={symbol} className="bg-white/10 backdrop-blur-sm border-white/20">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center justify-between text-white">
                  <span className="flex items-center gap-2">
                    <span className="text-2xl">{data.logo}</span>
                    {symbol}
                  </span>
                  <Badge variant="outline" className="text-white border-white/30">
                    ${data.price}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-white">
                    <span>Balance:</span>
                    <span className="font-mono">{data.balance.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-green-300">
                    <span>USD Value:</span>
                    <span className="font-mono">${data.usd_value.toLocaleString()}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Action Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Withdrawal Form */}
          <Card className="bg-white/10 backdrop-blur-sm border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                💸 Withdraw to Development Wallet
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleWithdraw} className="space-y-4">
                <div>
                  <label className="block text-white mb-2">Currency</label>
                  <select
                    value={withdrawForm.currency}
                    onChange={(e) => setWithdrawForm({...withdrawForm, currency: e.target.value})}
                    className="w-full p-3 rounded-lg bg-white/20 text-white border border-white/30"
                    required
                  >
                    <option value="">Select Currency</option>
                    {currencies.map(currency => (
                      <option key={currency} value={currency} className="text-black">
                        {currency}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-white mb-2">Amount</label>
                  <Input
                    type="number"
                    step="0.00000001"
                    value={withdrawForm.amount}
                    onChange={(e) => setWithdrawForm({...withdrawForm, amount: e.target.value})}
                    className="bg-white/20 text-white border-white/30"
                    placeholder="Enter amount"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-white mb-2">Destination Address</label>
                  <Input
                    value={withdrawForm.destination_address}
                    onChange={(e) => setWithdrawForm({...withdrawForm, destination_address: e.target.value})}
                    className="bg-white/20 text-white border-white/30"
                    placeholder="Enter wallet address"
                    required
                  />
                </div>
                
                <Button type="submit" className="w-full bg-green-600 hover:bg-green-700">
                  Withdraw Funds
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Conversion Form */}
          <Card className="bg-white/10 backdrop-blur-sm border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                🔄 Convert Between Currencies
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleConvert} className="space-y-4">
                <div>
                  <label className="block text-white mb-2">From Currency</label>
                  <select
                    value={convertForm.from_currency}
                    onChange={(e) => setConvertForm({...convertForm, from_currency: e.target.value})}
                    className="w-full p-3 rounded-lg bg-white/20 text-white border border-white/30"
                    required
                  >
                    <option value="">Select Currency</option>
                    {currencies.map(currency => (
                      <option key={currency} value={currency} className="text-black">
                        {currency}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-white mb-2">To Currency</label>
                  <select
                    value={convertForm.to_currency}
                    onChange={(e) => setConvertForm({...convertForm, to_currency: e.target.value})}
                    className="w-full p-3 rounded-lg bg-white/20 text-white border border-white/30"
                    required
                  >
                    <option value="">Select Currency</option>
                    {currencies.map(currency => (
                      <option key={currency} value={currency} className="text-black">
                        {currency}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-white mb-2">Amount</label>
                  <Input
                    type="number"
                    step="0.00000001"
                    value={convertForm.amount}
                    onChange={(e) => setConvertForm({...convertForm, amount: e.target.value})}
                    className="bg-white/20 text-white border-white/30"
                    placeholder="Enter amount"
                    required
                  />
                </div>
                
                <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700">
                  Convert Currency
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* CDT Bridge Info */}
        <Card className="mt-8 bg-gradient-to-r from-purple-600/20 to-pink-600/20 backdrop-blur-sm border-purple-300/30">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              🎨 CDT Bridge Integration
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-white">
              <div>
                <p className="text-sm text-gray-300">Token Address</p>
                <p className="font-mono text-sm break-all">3ZP9KAKwJTMbhcbJdiaLvLXAgkmKVoAeNMQ6wNavjupx</p>
              </div>
              <div>
                <p className="text-sm text-gray-300">Current Price</p>
                <p className="text-lg font-bold">$0.10</p>
              </div>
              <div>
                <p className="text-sm text-gray-300">Status</p>
                <Badge variant="secondary" className="bg-green-600">Bridge Ready</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Refresh Button */}
        <div className="text-center mt-8">
          <Button 
            onClick={fetchPortfolioData}
            className="bg-white/20 hover:bg-white/30 text-white border border-white/30"
          >
            🔄 Refresh Portfolio Data
          </Button>
        </div>
      </div>
    </div>
  );
};

export default DevelopmentFundDashboard;