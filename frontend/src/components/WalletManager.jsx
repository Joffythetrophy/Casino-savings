import React, { useState, useEffect } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import Header from './Header';
import { 
  Wallet, 
  ArrowUpDown, 
  ArrowDownLeft, 
  ArrowUpRight,
  PiggyBank,
  Trophy,
  RefreshCw,
  ArrowLeft,
  QrCode,
  Copy
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../hooks/use-toast';
import axios from 'axios';

const CRTCoin = ({ size = 'w-5 h-5' }) => (
  <img 
    src="https://customer-assets.emergentagent.com/job_blockchain-casino/artifacts/nx4ol97f_copilot_image_1755811225489.jpeg"
    alt="CRT Token"
    className={`${size} rounded-full`}
  />
);

const WalletManager = () => {
  const [wallets, setWallets] = useState({
    deposit: { CRT: 0, DOGE: 0, TRX: 0, USDC: 0 },
    winnings: { CRT: 0, DOGE: 0, TRX: 0, USDC: 0 },
    savings: { CRT: 0, DOGE: 0, TRX: 0, USDC: 0 }
  });
  
  const [conversionRates, setConversionRates] = useState({});
  const [loading, setLoading] = useState(true);
  
  const [activeTab, setActiveTab] = useState('deposit');
  const [convertAmount, setConvertAmount] = useState('');
  const [convertFrom, setConvertFrom] = useState('CRT');
  const [convertTo, setConvertTo] = useState('DOGE');
  const [showQRCode, setShowQRCode] = useState(false);
  const [qrCurrency, setQrCurrency] = useState('CRT');
  
  const navigate = useNavigate();
  const { toast } = useToast();

  // Get backend URL from environment
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
  
  // Mock wallet addresses - in production these would be unique per user
  const walletAddresses = {
    CRT: 'CRT1x9f8k3m2q7w6e5r4t3y2u1i0p9o8i7u6y5t4r3e2w1q',
    DOGE: 'DBXTSy8BQQnBMxBGYo3VVSm4iXbRh7tWgE',
    TRX: 'TR7NHqjeKQxGTCi8q8ZY4pL3kiSRtwjAYB',
    USDC: '0x742d35Cc6634C0532925a3b8D4C31Ebe7F8C9E4B'
  };

  useEffect(() => {
    fetchWalletBalances();
    fetchConversionRates();
  }, []);

  const fetchWalletBalances = async () => {
    try {
      setLoading(true);
      // TODO: Replace with real wallet address from authentication
      const testWallet = 'RealWallet9876543210XYZ';
      
      const response = await axios.get(`${BACKEND_URL}/api/wallet/${testWallet}`);
      
      if (response.data.success && response.data.wallet) {
        const wallet = response.data.wallet;
        setWallets({
          deposit: wallet.deposit_balance || { CRT: 0, DOGE: 0, TRX: 0, USDC: 0 },
          winnings: wallet.winnings_balance || { CRT: 0, DOGE: 0, TRX: 0, USDC: 0 },
          savings: wallet.savings_balance || { CRT: 0, DOGE: 0, TRX: 0, USDC: 0 }
        });
      }
    } catch (error) {
      console.error('Error fetching wallet balances:', error);
      toast({
        title: "Error",
        description: "Failed to fetch wallet balances",
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchConversionRates = async () => {
    try {
      // TODO: Replace with real-time conversion rates from backend
      const response = await axios.get(`${BACKEND_URL}/api/conversion/rates`);
      if (response.data.success) {
        setConversionRates(response.data.rates);
      }
    } catch (error) {
      console.error('Error fetching conversion rates:', error);
      // Fallback to mock rates if API fails
      setConversionRates({
        CRT_DOGE: 21.5,
        CRT_TRX: 9.8,
        CRT_USDC: 0.15,
        DOGE_CRT: 0.047,
        DOGE_TRX: 0.456,
        DOGE_USDC: 0.007,
        TRX_CRT: 0.102,
        TRX_DOGE: 2.19,
        TRX_USDC: 0.015,
        USDC_CRT: 6.67,
        USDC_DOGE: 142.86,
        USDC_TRX: 66.67
      });
    }
  };

  const generateQRCodeURL = (currency, address) => {
    // Generate QR code URL using a free service
    const qrData = `${currency}:${address}`;
    return `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(qrData)}`;
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({
        title: "Copied!",
        description: "Address copied to clipboard",
      });
    } catch (err) {
      toast({
        title: "Failed to copy",
        description: "Please copy the address manually",
      });
    }
  };

  const getCurrencyIcon = (currency) => {
    switch(currency) {
      case 'CRT':
        return <CRTCoin size="w-6 h-6" />;
      case 'DOGE':
        return <div className="w-6 h-6 bg-yellow-500 rounded-full flex items-center justify-center text-sm">🐕</div>;
      case 'TRX':
        return <div className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center text-sm font-bold text-white">T</div>;
      case 'USDC':
        return <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-xs font-bold text-white">$</div>;
      default:
        return <Wallet className="w-6 h-6" />;
    }
  };

  const handleDeposit = async (currency, amount) => {
    if (amount <= 0) return;
    
    try {
      const testWallet = 'RealWallet9876543210XYZ'; // TODO: Replace with real wallet from auth
      
      const response = await axios.post(`${BACKEND_URL}/api/wallet/deposit`, {
        wallet_address: testWallet,
        currency: currency,
        amount: amount
      });
      
      if (response.data.success) {
        await fetchWalletBalances(); // Refresh balances
        toast({
          title: "Deposit Successful!",
          description: response.data.message,
        });
      } else {
        toast({
          title: "Deposit Failed",
          description: response.data.message || "Failed to process deposit",
        });
      }
    } catch (error) {
      console.error('Deposit error:', error);
      toast({
        title: "Deposit Error",
        description: "Failed to process deposit request",
      });
    }
  };

  const handleWithdraw = async (walletType, currency, amount) => {
    if (amount <= 0 || wallets[walletType][currency] < amount) return;
    
    try {
      const testWallet = 'RealWallet9876543210XYZ'; // TODO: Replace with real wallet from auth
      
      const response = await axios.post(`${BACKEND_URL}/api/wallet/withdraw`, {
        wallet_address: testWallet,
        wallet_type: walletType,
        currency: currency,
        amount: amount
      });
      
      if (response.data.success) {
        await fetchWalletBalances(); // Refresh balances
        toast({
          title: "Withdrawal Successful!",
          description: response.data.message,
        });
      } else {
        toast({
          title: "Withdrawal Failed",
          description: response.data.message || "Failed to process withdrawal",
        });
      }
    } catch (error) {
      console.error('Withdrawal error:', error);
      if (error.response?.status === 400) {
        toast({
          title: "Insufficient Balance",
          description: "Not enough funds for withdrawal",
        });
      } else {
        toast({
          title: "Withdrawal Error",
          description: "Failed to process withdrawal request",
        });
      }
    }
  };

  const handleConversion = async () => {
    const amount = parseFloat(convertAmount);
    if (!amount || amount <= 0) return;
    
    if (wallets.deposit[convertFrom] < amount) {
      toast({
        title: "Insufficient Balance",
        description: `Not enough ${convertFrom} in deposit wallet`,
      });
      return;
    }
    
    try {
      const testWallet = 'RealWallet9876543210XYZ'; // TODO: Replace with real wallet from auth
      
      const response = await axios.post(`${BACKEND_URL}/api/wallet/convert`, {
        wallet_address: testWallet,
        from_currency: convertFrom,
        to_currency: convertTo,
        amount: amount
      });
      
      if (response.data.success) {
        await fetchWalletBalances(); // Refresh balances
        toast({
          title: "Conversion Successful!",
          description: response.data.message,
        });
        setConvertAmount('');
      } else {
        toast({
          title: "Conversion Failed",  
          description: response.data.message || "Failed to process conversion",
        });
      }
    } catch (error) {
      console.error('Conversion error:', error);
      toast({
        title: "Conversion Error",
        description: "Failed to process conversion request",
      });
    }
  };

  const WalletCard = ({ title, wallet, type, icon: Icon, color }) => {
    const [depositAmount, setDepositAmount] = useState('');
    const [withdrawAmount, setWithdrawAmount] = useState('');
    const [selectedCurrency, setSelectedCurrency] = useState('CRT');
    
    return (
      <Card className={`p-6 bg-gradient-to-br ${color} border border-opacity-20`}>
        <div className="flex items-center space-x-3 mb-6">
          <Icon className="w-8 h-8" />
          <h3 className="text-2xl font-bold">{title}</h3>
        </div>
        
        {/* Balances */}
        <div className="space-y-3 mb-6">
          {Object.entries(wallet).map(([currency, balance]) => (
            <div key={currency} className="flex items-center justify-between p-3 bg-black/20 rounded-lg">
              <div className="flex items-center space-x-3">
                {getCurrencyIcon(currency)}
                <span className="font-medium">{currency}</span>
              </div>
              <span className="text-xl font-bold">{balance.toFixed(4)}</span>
            </div>
          ))}
        </div>
        
        {/* Actions */}
        {type === 'deposit' && (
          <div className="space-y-4">
            <div className="flex space-x-2">
              <select 
                value={selectedCurrency}
                onChange={(e) => setSelectedCurrency(e.target.value)}
                className="bg-black/20 border border-gray-600 rounded px-3 py-2 text-white"
              >
                <option value="CRT">CRT</option>
                <option value="DOGE">DOGE</option>
                <option value="TRX">TRX</option>
                <option value="USDC">USDC</option>
              </select>
              <Input
                type="number"
                placeholder="Amount"
                value={depositAmount}
                onChange={(e) => setDepositAmount(e.target.value)}
                className="flex-1 bg-black/20 border-gray-600 text-white"
              />
              <Button
                onClick={() => {
                  handleDeposit(selectedCurrency, parseFloat(depositAmount));
                  setDepositAmount('');
                }}
                className="bg-green-600 hover:bg-green-500"
              >
                <ArrowDownLeft className="w-4 h-4 mr-2" />
                Deposit
              </Button>
            </div>
            
            {/* QR Code Button */}
            <div className="flex space-x-2">
              <Button
                onClick={() => {
                  setQrCurrency(selectedCurrency);
                  setShowQRCode(true);
                }}
                className="flex-1 bg-blue-600 hover:bg-blue-500"
              >
                <QrCode className="w-4 h-4 mr-2" />
                Show {selectedCurrency} QR Code
              </Button>
            </div>
          </div>
        )}
        
        {(type === 'winnings' || type === 'savings') && (
          <div className="space-y-4">
            <div className="flex space-x-2">
              <select 
                value={selectedCurrency}
                onChange={(e) => setSelectedCurrency(e.target.value)}
                className="bg-black/20 border border-gray-600 rounded px-3 py-2 text-white"
              >
                <option value="CRT">CRT</option>
                <option value="DOGE">DOGE</option>
                <option value="TRX">TRX</option>
                <option value="USDC">USDC</option>
              </select>
              <Input
                type="number"
                placeholder="Amount"
                value={withdrawAmount}
                onChange={(e) => setWithdrawAmount(e.target.value)}
                max={wallet[selectedCurrency]}
                className="flex-1 bg-black/20 border-gray-600 text-white"
              />
              <Button
                onClick={() => {
                  handleWithdraw(type, selectedCurrency, parseFloat(withdrawAmount));
                  setWithdrawAmount('');
                }}
                className="bg-blue-600 hover:bg-blue-500"
              >
                <ArrowUpRight className="w-4 h-4 mr-2" />
                Withdraw
              </Button>
            </div>
          </div>
        )}
      </Card>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <Header />
      
      <main className="pt-24 pb-12 px-6">
        <div className="max-w-7xl mx-auto">
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
                <Wallet className="w-8 h-8 text-yellow-400" />
                <h1 className="text-4xl font-bold text-yellow-400">Wallet Manager</h1>
              </div>
            </div>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="bg-gray-800 border-yellow-400/20">
              <TabsTrigger value="deposit" className="data-[state=active]:bg-yellow-400 data-[state=active]:text-black">
                💳 Deposit Wallet
              </TabsTrigger>
              <TabsTrigger value="winnings" className="data-[state=active]:bg-yellow-400 data-[state=active]:text-black">
                🏆 Winnings Wallet
              </TabsTrigger>
              <TabsTrigger value="savings" className="data-[state=active]:bg-yellow-400 data-[state=active]:text-black">
                🐷 Savings Vault
              </TabsTrigger>
              <TabsTrigger value="convert" className="data-[state=active]:bg-yellow-400 data-[state=active]:text-black">
                🔄 Convert Crypto
              </TabsTrigger>
            </TabsList>

            <TabsContent value="deposit">
              <WalletCard
                title="Deposit Wallet"
                wallet={wallets.deposit}
                type="deposit"
                icon={Wallet}
                color="from-blue-800/20 to-blue-900/20"
              />
              <Card className="p-4 bg-gray-900/50 border-yellow-400/20 mt-4">
                <p className="text-gray-300 text-sm">
                  💡 <strong>Deposit funds here to start playing.</strong> Your deposit wallet is where you add crypto to fuel your gaming sessions.
                </p>
              </Card>
            </TabsContent>

            <TabsContent value="winnings">
              <WalletCard
                title="Winnings Wallet"
                wallet={wallets.winnings}
                type="winnings"
                icon={Trophy}
                color="from-green-800/20 to-green-900/20"
              />
              <Card className="p-4 bg-gray-900/50 border-yellow-400/20 mt-4">
                <p className="text-gray-300 text-sm">
                  🏆 <strong>Your game winnings accumulate here.</strong> Withdraw your profits anytime or keep playing to win more!
                </p>
              </Card>
            </TabsContent>

            <TabsContent value="savings">
              <WalletCard
                title="Savings Vault"
                wallet={wallets.savings}
                type="savings"
                icon={PiggyBank}
                color="from-purple-800/20 to-purple-900/20"
              />
              <Card className="p-4 bg-gray-900/50 border-yellow-400/20 mt-4">
                <p className="text-gray-300 text-sm">
                  🐷 <strong>Smart Savings System:</strong> When you lose a session, your savings = your peak balance reached during that session! 
                  Example: Deposit 20 DOGE → Win up to 1000 DOGE → Lose it all → Save 1000 DOGE (your peak)!
                </p>
              </Card>
            </TabsContent>

            <TabsContent value="convert">
              <Card className="p-6 bg-gradient-to-br from-orange-800/20 to-orange-900/20 border border-orange-400/20">
                <div className="flex items-center space-x-3 mb-6">
                  <RefreshCw className="w-8 h-8 text-orange-400" />
                  <h3 className="text-2xl font-bold text-orange-400">Crypto Converter</h3>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div className="space-y-4">
                    <label className="text-gray-300">From (Deposit Wallet)</label>
                    <div className="flex space-x-2">
                      <select 
                        value={convertFrom}
                        onChange={(e) => setConvertFrom(e.target.value)}
                        className="bg-black/20 border border-gray-600 rounded px-4 py-3 text-white flex-1"
                      >
                        <option value="CRT">CRT</option>
                        <option value="DOGE">DOGE</option>
                        <option value="TRX">TRX</option>
                        <option value="USDC">USDC</option>
                      </select>
                      <div className="flex items-center px-4 py-3 bg-black/20 rounded border border-gray-600">
                        {getCurrencyIcon(convertFrom)}
                      </div>
                    </div>
                    <div className="text-sm text-gray-400">
                      Available: {wallets.deposit[convertFrom].toFixed(4)} {convertFrom}
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <label className="text-gray-300">To</label>
                    <div className="flex space-x-2">
                      <select 
                        value={convertTo}
                        onChange={(e) => setConvertTo(e.target.value)}
                        className="bg-black/20 border border-gray-600 rounded px-4 py-3 text-white flex-1"
                      >
                        <option value="CRT">CRT</option>
                        <option value="DOGE">DOGE</option>
                        <option value="TRX">TRX</option>
                        <option value="USDC">USDC</option>
                      </select>
                      <div className="flex items-center px-4 py-3 bg-black/20 rounded border border-gray-600">
                        {getCurrencyIcon(convertTo)}
                      </div>
                    </div>
                    <div className="text-sm text-gray-400">
                      Rate: 1 {convertFrom} = {conversionRates[`${convertFrom}_${convertTo}`]?.toFixed(4) || 'N/A'} {convertTo}
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <Input
                    type="number"
                    placeholder={`Amount in ${convertFrom}`}
                    value={convertAmount}
                    onChange={(e) => setConvertAmount(e.target.value)}
                    className="bg-black/20 border-gray-600 text-white text-lg"
                  />
                  
                  {convertAmount && (
                    <div className="text-center p-4 bg-black/20 rounded-lg">
                      <div className="text-lg text-gray-300">
                        {convertAmount} {convertFrom} = <span className="text-yellow-400 font-bold">
                          {(parseFloat(convertAmount) * (conversionRates[`${convertFrom}_${convertTo}`] || 0)).toFixed(4)}
                        </span> {convertTo}
                      </div>
                    </div>
                  )}
                  
                  <Button
                    onClick={handleConversion}
                    disabled={!convertAmount || parseFloat(convertAmount) > wallets.deposit[convertFrom]}
                    className="w-full bg-gradient-to-r from-orange-500 to-orange-600 text-white font-bold hover:from-orange-400 hover:to-orange-500 py-3"
                  >
                    <ArrowUpDown className="w-5 h-5 mr-2" />
                    Convert Crypto
                  </Button>
                </div>
              </Card>
              
              <Card className="p-4 bg-gray-900/50 border-yellow-400/20 mt-4">
                <h4 className="text-yellow-400 font-bold mb-2">Current Conversion Rates</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm text-gray-300">
                  <div>1 CRT = {conversionRates.CRT_DOGE} DOGE</div>
                  <div>1 CRT = {conversionRates.CRT_TRX} TRX</div>
                  <div>1 DOGE = {conversionRates.DOGE_CRT} CRT</div>
                  <div>1 DOGE = {conversionRates.DOGE_TRX} TRX</div>
                  <div>1 TRX = {conversionRates.TRX_CRT} CRT</div>
                  <div>1 TRX = {conversionRates.TRX_DOGE} DOGE</div>
                </div>
              </Card>
            </TabsContent>
          </Tabs>
          
          {/* QR Code Modal */}
          {showQRCode && (
            <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
              <Card className="p-6 bg-gradient-to-br from-gray-800 to-gray-900 border border-yellow-400/50 max-w-md w-full">
                <div className="text-center space-y-4">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-yellow-400">Deposit {qrCurrency}</h3>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowQRCode(false)}
                      className="text-gray-400 hover:text-white"
                    >
                      ✕
                    </Button>
                  </div>
                  
                  {/* QR Code */}
                  <div className="bg-white p-4 rounded-lg inline-block">
                    <img 
                      src={generateQRCodeURL(qrCurrency, walletAddresses[qrCurrency])}
                      alt={`${qrCurrency} Wallet QR Code`}
                      className="w-48 h-48"
                    />
                  </div>
                  
                  {/* Wallet Address */}
                  <div className="space-y-2">
                    <p className="text-gray-300 text-sm">Wallet Address:</p>
                    <div className="bg-black/30 p-3 rounded border border-gray-600 flex items-center space-x-2">
                      <code className="text-sm text-yellow-400 flex-1 break-all">
                        {walletAddresses[qrCurrency]}
                      </code>
                      <Button
                        size="sm"
                        onClick={() => copyToClipboard(walletAddresses[qrCurrency])}
                        className="bg-blue-600 hover:bg-blue-500 shrink-0"
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  
                  {/* Instructions */}
                  <div className="text-left bg-yellow-400/10 p-4 rounded border border-yellow-400/20">
                    <p className="text-yellow-400 font-bold text-sm mb-2">📱 How to deposit:</p>
                    <ol className="text-gray-300 text-xs space-y-1">
                      <li>1. Scan the QR code with your {qrCurrency} wallet</li>
                      <li>2. Or copy the address and send {qrCurrency} to it</li>
                      <li>3. Funds will appear in your deposit wallet</li>
                      <li>4. Start playing casino games!</li>
                    </ol>
                  </div>
                  
                  <Button
                    onClick={() => setShowQRCode(false)}
                    className="w-full bg-yellow-600 hover:bg-yellow-500 text-black font-bold"
                  >
                    Close
                  </Button>
                </div>
              </Card>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default WalletManager;