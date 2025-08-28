import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
    Wallet, 
    Shield, 
    TrendingUp, 
    AlertTriangle, 
    CheckCircle, 
    Clock, 
    ExternalLink,
    Pause,
    Play,
    DollarSign,
    Users,
    Activity,
    Lock,
    Unlock,
    ArrowUpRight,
    ArrowDownLeft,
    Settings
} from 'lucide-react';

const SmartContractTreasuryDashboard = ({ user, authToken }) => {
    const [treasuryStatus, setTreasuryStatus] = useState(null);
    const [withdrawalForm, setWithdrawalForm] = useState({
        currency: 'USDC',
        amount: '',
        destinationAddress: '',
        withdrawalType: 'Winnings'
    });
    const [fundingForm, setFundingForm] = useState({
        amount: ''
    });
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('overview');
    const [notifications, setNotifications] = useState([]);

    // Multi-currency support
    const supportedCurrencies = [
        { symbol: 'USDC', name: 'USD Coin', decimals: 6, icon: '💵' },
        { symbol: 'SOL', name: 'Solana', decimals: 9, icon: '◎' },
        { symbol: 'USDT', name: 'Tether USD', decimals: 6, icon: '💵' }
    ];

    const withdrawalTypes = [
        { value: 'Winnings', label: '🎰 Winnings', color: 'bg-casino-green-500' },
        { value: 'Savings', label: '🏦 Savings', color: 'bg-emerald-casino-500' },
        { value: 'Liquidity', label: '💧 Liquidity', color: 'bg-jade-500' }
    ];

    useEffect(() => {
        fetchTreasuryStatus();
        fetchTransactions();
        const interval = setInterval(() => {
            fetchTreasuryStatus();
        }, 30000); // Update every 30 seconds

        return () => clearInterval(interval);
    }, []);

    const fetchTreasuryStatus = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/treasury/status`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                setTreasuryStatus(data);
                
                // Check for notifications
                if (data.treasury?.health?.status !== 'HEALTHY') {
                    addNotification('warning', `Treasury Status: ${data.treasury?.health?.status}`);
                }
            }
        } catch (error) {
            console.error('Failed to fetch treasury status:', error);
            addNotification('error', 'Failed to fetch treasury status');
        }
    };

    const fetchTransactions = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/user/transactions`, {
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                // Filter for treasury transactions
                const treasuryTxs = data.transactions?.filter(tx => 
                    tx.service === 'smart_contract_treasury' || tx.type === 'smart_contract_withdrawal'
                ) || [];
                setTransactions(treasuryTxs);
            }
        } catch (error) {
            console.error('Failed to fetch transactions:', error);
        }
    };

    const addNotification = (type, message) => {
        const notification = {
            id: Date.now(),
            type,
            message,
            timestamp: new Date()
        };
        setNotifications(prev => [notification, ...prev.slice(0, 4)]);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            setNotifications(prev => prev.filter(n => n.id !== notification.id));
        }, 5000);
    };

    const handleSmartWithdrawal = async () => {
        if (!withdrawalForm.amount || !withdrawalForm.destinationAddress) {
            addNotification('error', 'Please fill all required fields');
            return;
        }

        setLoading(true);
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/treasury/smart-withdraw`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    wallet_address: user.wallet_address,
                    amount: parseFloat(withdrawalForm.amount),
                    destination_address: withdrawalForm.destinationAddress,
                    withdrawal_type: withdrawalForm.withdrawalType
                })
            });

            const data = await response.json();
            
            if (data.success) {
                addNotification('success', `Smart contract withdrawal successful: ${withdrawalForm.amount} ${withdrawalForm.currency}`);
                setWithdrawalForm({ currency: 'USDC', amount: '', destinationAddress: '', withdrawalType: 'Winnings' });
                fetchTreasuryStatus();
                fetchTransactions();
            } else {
                addNotification('error', data.message || 'Withdrawal failed');
            }
        } catch (error) {
            console.error('Withdrawal failed:', error);
            addNotification('error', 'Withdrawal request failed');
        } finally {
            setLoading(false);
        }
    };

    const handleTreasuryFunding = async () => {
        if (!fundingForm.amount) {
            addNotification('error', 'Please enter funding amount');
            return;
        }

        setLoading(true);
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/treasury/fund`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    amount: parseFloat(fundingForm.amount)
                })
            });

            const data = await response.json();
            
            if (data.success) {
                addNotification('success', `Treasury funded: ${fundingForm.amount} USDC`);
                setFundingForm({ amount: '' });
                fetchTreasuryStatus();
            } else {
                addNotification('error', data.message || 'Funding failed');
            }
        } catch (error) {
            console.error('Funding failed:', error);
            addNotification('error', 'Treasury funding failed');
        } finally {
            setLoading(false);
        }
    };

    const handleEmergencyAction = async (action) => {
        const confirmMessage = action === 'pause' 
            ? 'Are you sure you want to pause the treasury? This will stop all withdrawals.'
            : 'Are you sure you want to resume treasury operations?';
            
        if (!window.confirm(confirmMessage)) return;

        setLoading(true);
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/treasury/emergency-${action}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            
            if (data.success) {
                addNotification('success', `Treasury ${action}d successfully`);
                fetchTreasuryStatus();
            } else {
                addNotification('error', data.message || `Failed to ${action} treasury`);
            }
        } catch (error) {
            console.error(`Emergency ${action} failed:`, error);
            addNotification('error', `Emergency ${action} failed`);
        } finally {
            setLoading(false);
        }
    };

    const formatCurrency = (amount, currency = 'USDC') => {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: currency === 'SOL' ? 9 : 6
        }).format(amount || 0);
    };

    const getTreasuryHealthColor = (status) => {
        switch (status) {
            case 'HEALTHY': return 'text-casino-green-400';
            case 'AUTO_FUNDING_TRIGGERED': return 'text-yellow-400';
            case 'EMERGENCY_PAUSED': return 'text-red-400';
            default: return 'text-gray-400';
        }
    };

    const getTreasuryHealthIcon = (status) => {
        switch (status) {
            case 'HEALTHY': return <CheckCircle className="w-5 h-5" />;
            case 'AUTO_FUNDING_TRIGGERED': return <AlertTriangle className="w-5 h-5" />;
            case 'EMERGENCY_PAUSED': return <Pause className="w-5 h-5" />;
            default: return <Clock className="w-5 h-5" />;
        }
    };

    if (!treasuryStatus) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-casino-green-400">
                    🐅 Loading Treasury Dashboard...
                </div>
            </div>
        );
    }

    return (
        <div className="w-full max-w-7xl mx-auto p-6 space-y-6">
            {/* Notifications */}
            {notifications.length > 0 && (
                <div className="fixed top-20 right-4 z-50 space-y-2">
                    {notifications.map(notification => (
                        <div
                            key={notification.id}
                            className={`p-4 rounded-lg shadow-lg backdrop-blur-md border ${
                                notification.type === 'success' 
                                    ? 'bg-casino-green-900/80 border-casino-green-500/50 text-casino-green-100'
                                    : notification.type === 'error'
                                    ? 'bg-red-900/80 border-red-500/50 text-red-100'
                                    : 'bg-yellow-900/80 border-yellow-500/50 text-yellow-100'
                            }`}
                        >
                            {notification.message}
                        </div>
                    ))}
                </div>
            )}

            {/* Header */}
            <div className="text-center mb-8">
                <h1 className="text-4xl font-bold text-casino-green-400 mb-2">
                    🐅 Smart Contract Treasury 🐅
                </h1>
                <p className="text-casino-green-200">
                    Decentralized Treasury Management with Solana Smart Contracts
                </p>
            </div>

            {/* Treasury Status Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <Card className="card-green">
                    <CardContent className="p-4">
                        <div className="flex items-center space-x-3">
                            <Wallet className="w-8 h-8 text-casino-green-400" />
                            <div>
                                <p className="text-sm text-casino-green-300">Treasury Balance</p>
                                <p className="text-xl font-bold text-casino-green-100">
                                    {formatCurrency(treasuryStatus.treasury?.balance || 0)} USDC
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="card-green">
                    <CardContent className="p-4">
                        <div className="flex items-center space-x-3">
                            <div className={getTreasuryHealthColor(treasuryStatus.treasury?.health?.status)}>
                                {getTreasuryHealthIcon(treasuryStatus.treasury?.health?.status)}
                            </div>
                            <div>
                                <p className="text-sm text-casino-green-300">Health Status</p>
                                <p className={`text-lg font-bold ${getTreasuryHealthColor(treasuryStatus.treasury?.health?.status)}`}>
                                    {treasuryStatus.treasury?.health?.status || 'Unknown'}
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="card-green">
                    <CardContent className="p-4">
                        <div className="flex items-center space-x-3">
                            <DollarSign className="w-8 h-8 text-casino-green-400" />
                            <div>
                                <p className="text-sm text-casino-green-300">Daily Limit</p>
                                <p className="text-lg font-bold text-casino-green-100">
                                    {formatCurrency(treasuryStatus.withdrawal_limits?.max_daily || 100000)}
                                </p>
                                <Progress 
                                    value={((treasuryStatus.treasury?.dailyWithdrawals?.totalWithdrawn || 0) / (treasuryStatus.withdrawal_limits?.max_daily || 100000)) * 100}
                                    className="mt-1 h-2 progress-green"
                                />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="card-green">
                    <CardContent className="p-4">
                        <div className="flex items-center space-x-3">
                            <Shield className="w-8 h-8 text-casino-green-400" />
                            <div>
                                <p className="text-sm text-casino-green-300">Smart Contract</p>
                                <div className="flex items-center space-x-2">
                                    <div className="w-2 h-2 bg-casino-green-400 rounded-full animate-pulse"></div>
                                    <p className="text-lg font-bold text-casino-green-100">Active</p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Navigation Tabs */}
            <div className="flex space-x-4 mb-6">
                {[
                    { id: 'overview', label: '📊 Overview', icon: Activity },
                    { id: 'withdraw', label: '💸 Withdraw', icon: ArrowUpRight },
                    { id: 'transactions', label: '📜 History', icon: Clock },
                    { id: 'admin', label: '⚙️ Admin', icon: Settings }
                ].map(tab => (
                    <Button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`px-6 py-3 ${
                            activeTab === tab.id 
                                ? 'bg-casino-green-500 text-white' 
                                : 'bg-casino-green-800/30 text-casino-green-200 hover:bg-casino-green-700/50'
                        }`}
                    >
                        <tab.icon className="w-4 h-4 mr-2" />
                        {tab.label}
                    </Button>
                ))}
            </div>

            {/* Tab Content */}
            {activeTab === 'overview' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <Card className="card-green">
                        <CardHeader>
                            <CardTitle className="text-casino-green-400">Treasury Analytics</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                <div className="flex justify-between items-center">
                                    <span className="text-casino-green-200">Total Deposits</span>
                                    <span className="font-bold text-casino-green-100">
                                        {formatCurrency(treasuryStatus.treasury?.stats?.totalDeposits || 0)} USDC
                                    </span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-casino-green-200">Total Withdrawals</span>
                                    <span className="font-bold text-casino-green-100">
                                        {formatCurrency(treasuryStatus.treasury?.stats?.totalWithdrawals || 0)} USDC
                                    </span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="text-casino-green-200">Available for Withdrawal</span>
                                    <span className="font-bold text-casino-green-100">
                                        {formatCurrency((treasuryStatus.treasury?.balance || 0) - (treasuryStatus.withdrawal_limits?.min_treasury_balance || 50000))} USDC
                                    </span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="card-green">
                        <CardHeader>
                            <CardTitle className="text-casino-green-400">Multi-Currency Balances</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {supportedCurrencies.map(currency => (
                                    <div key={currency.symbol} className="flex items-center justify-between p-3 rounded-lg bg-casino-green-900/20">
                                        <div className="flex items-center space-x-3">
                                            <span className="text-2xl">{currency.icon}</span>
                                            <div>
                                                <p className="font-bold text-casino-green-100">{currency.symbol}</p>
                                                <p className="text-sm text-casino-green-300">{currency.name}</p>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <p className="font-bold text-casino-green-100">
                                                {currency.symbol === 'USDC' ? formatCurrency(treasuryStatus.treasury?.balance || 0) : '0.00'}
                                            </p>
                                            <Badge variant="outline" className="text-xs border-casino-green-500/50 text-casino-green-300">
                                                Available
                                            </Badge>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {activeTab === 'withdraw' && (
                <Card className="card-green max-w-2xl mx-auto">
                    <CardHeader>
                        <CardTitle className="text-casino-green-400">🐅 Treasury-Backed Smart Withdrawal</CardTitle>
                        <p className="text-casino-green-200">Secure withdrawals backed by smart contract treasury</p>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-casino-green-300 mb-2">Currency</label>
                                <Select value={withdrawalForm.currency} onValueChange={(value) => setWithdrawalForm({...withdrawalForm, currency: value})}>
                                    <SelectTrigger className="input-green">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {supportedCurrencies.map(currency => (
                                            <SelectItem key={currency.symbol} value={currency.symbol}>
                                                {currency.icon} {currency.symbol} - {currency.name}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-casino-green-300 mb-2">Withdrawal Type</label>
                                <Select value={withdrawalForm.withdrawalType} onValueChange={(value) => setWithdrawalForm({...withdrawalForm, withdrawalType: value})}>
                                    <SelectTrigger className="input-green">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        {withdrawalTypes.map(type => (
                                            <SelectItem key={type.value} value={type.value}>
                                                {type.label}
                                            </SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-casino-green-300 mb-2">Amount ({withdrawalForm.currency})</label>
                            <Input
                                type="number"
                                placeholder="Enter amount"
                                value={withdrawalForm.amount}
                                onChange={(e) => setWithdrawalForm({...withdrawalForm, amount: e.target.value})}
                                className="input-green"
                            />
                            <p className="text-xs text-casino-green-400 mt-1">
                                Max: {formatCurrency(treasuryStatus.withdrawal_limits?.max_per_transaction || 10000)} {withdrawalForm.currency}
                            </p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-casino-green-300 mb-2">Destination Address</label>
                            <Input
                                type="text"
                                placeholder="Enter Solana wallet address"
                                value={withdrawalForm.destinationAddress}
                                onChange={(e) => setWithdrawalForm({...withdrawalForm, destinationAddress: e.target.value})}
                                className="input-green font-mono text-sm"
                            />
                        </div>

                        <Button
                            onClick={handleSmartWithdrawal}
                            disabled={loading || !withdrawalForm.amount || !withdrawalForm.destinationAddress}
                            className="w-full btn-primary py-3 text-lg glow-green"
                        >
                            {loading ? (
                                <div className="flex items-center space-x-2">
                                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                    <span>Processing...</span>
                                </div>
                            ) : (
                                <>
                                    <Shield className="w-5 h-5 mr-2" />
                                    Execute Smart Contract Withdrawal
                                </>
                            )}
                        </Button>

                        {/* Withdrawal Info */}
                        <div className="mt-4 p-4 rounded-lg bg-casino-green-900/20 border border-casino-green-500/30">
                            <h4 className="font-bold text-casino-green-300 mb-2">🐅 Smart Contract Features:</h4>
                            <ul className="text-sm text-casino-green-200 space-y-1">
                                <li>✅ Treasury-backed liquidity guarantee</li>
                                <li>✅ Multi-signature authorization</li>
                                <li>✅ Automatic health monitoring</li>
                                <li>✅ Emergency pause protection</li>
                                <li>✅ On-chain transaction verification</li>
                            </ul>
                        </div>
                    </CardContent>
                </Card>
            )}

            {activeTab === 'transactions' && (
                <Card className="card-green">
                    <CardHeader>
                        <CardTitle className="text-casino-green-400">Treasury Transaction History</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {transactions.length > 0 ? (
                            <div className="space-y-3">
                                {transactions.map((tx, index) => (
                                    <div key={index} className="flex items-center justify-between p-4 rounded-lg bg-casino-green-900/20 border border-casino-green-500/30">
                                        <div className="flex items-center space-x-4">
                                            <div className="w-10 h-10 rounded-full bg-casino-green-500/20 flex items-center justify-center">
                                                {tx.type === 'smart_contract_withdrawal' ? (
                                                    <ArrowUpRight className="w-5 h-5 text-casino-green-400" />
                                                ) : (
                                                    <ArrowDownLeft className="w-5 h-5 text-emerald-casino-400" />
                                                )}
                                            </div>
                                            <div>
                                                <p className="font-bold text-casino-green-100">
                                                    {tx.type === 'smart_contract_withdrawal' ? 'Smart Withdrawal' : 'Treasury Deposit'}
                                                </p>
                                                <p className="text-sm text-casino-green-300">
                                                    {new Date(tx.created_at).toLocaleString()}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <p className="font-bold text-casino-green-100">
                                                {formatCurrency(tx.amount)} {tx.currency}
                                            </p>
                                            {tx.explorer_url && (
                                                <a
                                                    href={tx.explorer_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="inline-flex items-center text-xs text-casino-green-400 hover:text-casino-green-300"
                                                >
                                                    View on Explorer <ExternalLink className="w-3 h-3 ml-1" />
                                                </a>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-casino-green-300">
                                No treasury transactions yet
                            </div>
                        )}
                    </CardContent>
                </Card>
            )}

            {activeTab === 'admin' && user?.username === 'cryptoking' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <Card className="card-green">
                        <CardHeader>
                            <CardTitle className="text-casino-green-400">Treasury Funding</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-casino-green-300 mb-2">Funding Amount (USDC)</label>
                                <Input
                                    type="number"
                                    placeholder="Enter amount to fund"
                                    value={fundingForm.amount}
                                    onChange={(e) => setFundingForm({...fundingForm, amount: e.target.value})}
                                    className="input-green"
                                />
                            </div>
                            <Button
                                onClick={handleTreasuryFunding}
                                disabled={loading || !fundingForm.amount}
                                className="w-full btn-primary"
                            >
                                <DollarSign className="w-4 h-4 mr-2" />
                                Fund Treasury
                            </Button>
                        </CardContent>
                    </Card>

                    <Card className="card-green">
                        <CardHeader>
                            <CardTitle className="text-casino-green-400">Emergency Controls</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <p className="text-sm text-casino-green-200">
                                Emergency controls for treasury operations
                            </p>
                            <div className="space-y-3">
                                <Button
                                    onClick={() => handleEmergencyAction('pause')}
                                    disabled={loading}
                                    className="w-full bg-red-600 hover:bg-red-700 text-white"
                                >
                                    <Pause className="w-4 h-4 mr-2" />
                                    Emergency Pause
                                </Button>
                                <Button
                                    onClick={() => handleEmergencyAction('resume')}
                                    disabled={loading}
                                    className="w-full bg-casino-green-600 hover:bg-casino-green-700 text-white"
                                >
                                    <Play className="w-4 h-4 mr-2" />
                                    Resume Operations
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
};

export default SmartContractTreasuryDashboard;