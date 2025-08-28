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
    Settings,
    Plus,
    Minus,
    RotateCcw,
    Eye,
    EyeOff
} from 'lucide-react';

const MultiCurrencyTreasuryManager = ({ user, authToken }) => {
    const [treasuryData, setTreasuryData] = useState({
        USDC: { balance: 0, status: 'HEALTHY', totalDeposits: 0, totalWithdrawals: 0 },
        SOL: { balance: 0, status: 'HEALTHY', totalDeposits: 0, totalWithdrawals: 0 },
        USDT: { balance: 0, status: 'HEALTHY', totalDeposits: 0, totalWithdrawals: 0 },
        DOGE: { balance: 0, status: 'HEALTHY', totalDeposits: 0, totalWithdrawals: 0 },
        TRX: { balance: 0, status: 'HEALTHY', totalDeposits: 0, totalWithdrawals: 0 }
    });

    const [adminSettings, setAdminSettings] = useState({
        withdrawalLimits: {
            USDC: { daily: 100000, perTransaction: 10000, minBalance: 50000 },
            SOL: { daily: 1000, perTransaction: 100, minBalance: 500 },
            USDT: { daily: 100000, perTransaction: 10000, minBalance: 50000 },
            DOGE: { daily: 1000000, perTransaction: 100000, minBalance: 500000 },
            TRX: { daily: 100000, perTransaction: 10000, minBalance: 50000 }
        },
        autoFunding: {
            enabled: true,
            thresholds: {
                USDC: 75000, SOL: 750, USDT: 75000, DOGE: 750000, TRX: 75000
            }
        },
        emergencySettings: {
            pauseThresholds: {
                USDC: 25000, SOL: 250, USDT: 25000, DOGE: 250000, TRX: 25000
            }
        }
    });

    const [activeTab, setActiveTab] = useState('overview');
    const [selectedCurrency, setSelectedCurrency] = useState('USDC');
    const [showAdminPanel, setShowAdminPanel] = useState(false);
    const [loading, setLoading] = useState(false);
    const [notifications, setNotifications] = useState([]);

    // Enhanced currency definitions with real-world data
    const supportedCurrencies = [
        { 
            symbol: 'USDC', 
            name: 'USD Coin', 
            decimals: 6, 
            icon: '💵', 
            network: 'Solana',
            color: 'bg-blue-500',
            contractAddress: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
        },
        { 
            symbol: 'SOL', 
            name: 'Solana', 
            decimals: 9, 
            icon: '◎', 
            network: 'Solana',
            color: 'bg-purple-500',
            contractAddress: 'So11111111111111111111111111111111111111112'
        },
        { 
            symbol: 'USDT', 
            name: 'Tether USD', 
            decimals: 6, 
            icon: '💵', 
            network: 'Solana',
            color: 'bg-green-500',
            contractAddress: 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB'
        },
        { 
            symbol: 'DOGE', 
            name: 'Dogecoin', 
            decimals: 8, 
            icon: '🐕', 
            network: 'Dogecoin',
            color: 'bg-yellow-500',
            contractAddress: 'native'
        },
        { 
            symbol: 'TRX', 
            name: 'TRON', 
            decimals: 6, 
            icon: '⚡', 
            network: 'TRON',
            color: 'bg-red-500',
            contractAddress: 'native'
        }
    ];

    const [multiCurrencyForm, setMultiCurrencyForm] = useState({
        operation: 'withdraw',
        currency: 'USDC',
        amount: '',
        destination: '',
        sourceWallet: 'Winnings'
    });

    useEffect(() => {
        fetchMultiCurrencyTreasuryStatus();
        const interval = setInterval(fetchMultiCurrencyTreasuryStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchMultiCurrencyTreasuryStatus = async () => {
        try {
            // Simulate multi-currency treasury data
            // In production, this would call multiple endpoints for different currencies
            const mockData = {
                USDC: { 
                    balance: 250000, 
                    status: 'HEALTHY', 
                    totalDeposits: 500000, 
                    totalWithdrawals: 250000,
                    dailyWithdrawn: 15000
                },
                SOL: { 
                    balance: 1200, 
                    status: 'HEALTHY', 
                    totalDeposits: 2000, 
                    totalWithdrawals: 800,
                    dailyWithdrawn: 50
                },
                USDT: { 
                    balance: 150000, 
                    status: 'AUTO_FUNDING_TRIGGERED', 
                    totalDeposits: 300000, 
                    totalWithdrawals: 150000,
                    dailyWithdrawn: 8000
                },
                DOGE: { 
                    balance: 800000, 
                    status: 'HEALTHY', 
                    totalDeposits: 1500000, 
                    totalWithdrawals: 700000,
                    dailyWithdrawn: 25000
                },
                TRX: { 
                    balance: 100000, 
                    status: 'EMERGENCY_PAUSED', 
                    totalDeposits: 200000, 
                    totalWithdrawals: 100000,
                    dailyWithdrawn: 0
                }
            };

            setTreasuryData(mockData);

            // Check for notifications
            Object.entries(mockData).forEach(([currency, data]) => {
                if (data.status !== 'HEALTHY') {
                    addNotification('warning', `${currency} Treasury: ${data.status}`);
                }
            });

        } catch (error) {
            console.error('Failed to fetch multi-currency treasury status:', error);
            addNotification('error', 'Failed to fetch treasury status');
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
        
        setTimeout(() => {
            setNotifications(prev => prev.filter(n => n.id !== notification.id));
        }, 5000);
    };

    const handleMultiCurrencyOperation = async () => {
        if (!multiCurrencyForm.amount) {
            addNotification('error', 'Please enter an amount');
            return;
        }

        setLoading(true);
        try {
            if (multiCurrencyForm.operation === 'withdraw') {
                // Multi-currency smart contract withdrawal
                const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/treasury/smart-withdraw`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${authToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        wallet_address: user.wallet_address,
                        amount: parseFloat(multiCurrencyForm.amount),
                        destination_address: multiCurrencyForm.destination,
                        currency: multiCurrencyForm.currency,
                        withdrawal_type: multiCurrencyForm.sourceWallet
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    addNotification('success', `${multiCurrencyForm.currency} withdrawal successful!`);
                    setMultiCurrencyForm({
                        operation: 'withdraw',
                        currency: 'USDC',
                        amount: '',
                        destination: '',
                        sourceWallet: 'Winnings'
                    });
                    fetchMultiCurrencyTreasuryStatus();
                } else {
                    addNotification('error', data.message || 'Operation failed');
                }
            } else if (multiCurrencyForm.operation === 'fund') {
                // Multi-currency treasury funding
                addNotification('success', `${multiCurrencyForm.currency} treasury funding initiated`);
            }
        } catch (error) {
            console.error('Multi-currency operation failed:', error);
            addNotification('error', 'Operation failed');
        } finally {
            setLoading(false);
        }
    };

    const handleAdminSettingsUpdate = async (currency, settingType, value) => {
        try {
            const newSettings = { ...adminSettings };
            
            if (settingType === 'dailyLimit') {
                newSettings.withdrawalLimits[currency].daily = value;
            } else if (settingType === 'perTransactionLimit') {
                newSettings.withdrawalLimits[currency].perTransaction = value;
            } else if (settingType === 'minBalance') {
                newSettings.withdrawalLimits[currency].minBalance = value;
            } else if (settingType === 'autoFundingThreshold') {
                newSettings.autoFunding.thresholds[currency] = value;
            }
            
            setAdminSettings(newSettings);
            addNotification('success', `${currency} ${settingType} updated successfully`);
        } catch (error) {
            addNotification('error', `Failed to update ${currency} settings`);
        }
    };

    const formatCurrency = (amount, currency = 'USDC') => {
        const currencyInfo = supportedCurrencies.find(c => c.symbol === currency);
        const decimals = currencyInfo?.decimals === 9 ? 4 : currencyInfo?.decimals === 8 ? 8 : 2;
        
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: decimals > 6 ? 2 : decimals,
            maximumFractionDigits: decimals > 6 ? 4 : decimals
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

    const getCurrencyInfo = (symbol) => {
        return supportedCurrencies.find(c => c.symbol === symbol);
    };

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
                    🐅 Multi-Currency Treasury Manager 🐅
                </h1>
                <p className="text-casino-green-200">
                    Advanced Multi-Blockchain Treasury Management System
                </p>
            </div>

            {/* Multi-Currency Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
                {supportedCurrencies.map(currency => {
                    const data = treasuryData[currency.symbol] || {};
                    return (
                        <Card key={currency.symbol} className="card-green">
                            <CardContent className="p-4">
                                <div className="text-center">
                                    <div className="flex items-center justify-center space-x-2 mb-2">
                                        <span className="text-2xl">{currency.icon}</span>
                                        <h3 className="font-bold text-casino-green-100">{currency.symbol}</h3>
                                    </div>
                                    <p className="text-2xl font-bold text-casino-green-100 mb-1">
                                        {formatCurrency(data.balance, currency.symbol)}
                                    </p>
                                    <Badge 
                                        variant="outline" 
                                        className={`text-xs ${getTreasuryHealthColor(data.status)} border-current`}
                                    >
                                        {data.status === 'HEALTHY' ? '✅ Healthy' : 
                                         data.status === 'AUTO_FUNDING_TRIGGERED' ? '⚠️ Auto-Fund' :
                                         data.status === 'EMERGENCY_PAUSED' ? '🚨 Paused' : '❓ Unknown'}
                                    </Badge>
                                    <p className="text-xs text-casino-green-300 mt-1">
                                        {currency.network}
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    );
                })}
            </div>

            {/* Navigation Tabs */}
            <div className="flex space-x-4 mb-6 overflow-x-auto">
                {[
                    { id: 'overview', label: '📊 Overview', icon: Activity },
                    { id: 'multicurrency', label: '💱 Multi-Currency', icon: ArrowUpRight },
                    { id: 'analytics', label: '📈 Analytics', icon: TrendingUp },
                    { id: 'admin', label: '⚙️ Advanced Admin', icon: Settings }
                ].map(tab => (
                    <Button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`px-6 py-3 whitespace-nowrap ${
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
                            <CardTitle className="text-casino-green-400">Treasury Summary</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {supportedCurrencies.map(currency => {
                                    const data = treasuryData[currency.symbol] || {};
                                    const limits = adminSettings.withdrawalLimits[currency.symbol] || {};
                                    const available = (data.balance || 0) - (limits.minBalance || 0);
                                    
                                    return (
                                        <div key={currency.symbol} className="flex justify-between items-center p-3 rounded-lg bg-casino-green-900/20">
                                            <div className="flex items-center space-x-3">
                                                <span className="text-xl">{currency.icon}</span>
                                                <div>
                                                    <p className="font-bold text-casino-green-100">{currency.symbol}</p>
                                                    <p className="text-xs text-casino-green-300">{currency.network}</p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="font-bold text-casino-green-100">
                                                    {formatCurrency(data.balance, currency.symbol)}
                                                </p>
                                                <p className="text-xs text-casino-green-300">
                                                    Available: {formatCurrency(Math.max(0, available), currency.symbol)}
                                                </p>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="card-green">
                        <CardHeader>
                            <CardTitle className="text-casino-green-400">Network Distribution</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {['Solana', 'Dogecoin', 'TRON'].map(network => {
                                    const networkCurrencies = supportedCurrencies.filter(c => c.network === network);
                                    const totalValue = networkCurrencies.reduce((sum, currency) => {
                                        return sum + (treasuryData[currency.symbol]?.balance || 0);
                                    }, 0);
                                    
                                    return (
                                        <div key={network} className="space-y-2">
                                            <div className="flex justify-between items-center">
                                                <span className="text-casino-green-200">{network}</span>
                                                <span className="font-bold text-casino-green-100">
                                                    {networkCurrencies.length} currencies
                                                </span>
                                            </div>
                                            <div className="flex space-x-2">
                                                {networkCurrencies.map(currency => (
                                                    <div key={currency.symbol} className="text-center flex-1">
                                                        <p className="text-xs text-casino-green-300">{currency.symbol}</p>
                                                        <p className="text-sm font-bold text-casino-green-100">
                                                            {formatCurrency(treasuryData[currency.symbol]?.balance || 0, currency.symbol)}
                                                        </p>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {activeTab === 'multicurrency' && (
                <Card className="card-green max-w-2xl mx-auto">
                    <CardHeader>
                        <CardTitle className="text-casino-green-400">Multi-Currency Operations</CardTitle>
                        <p className="text-casino-green-200">Execute operations across different blockchains</p>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-casino-green-300 mb-2">Operation</label>
                                <Select value={multiCurrencyForm.operation} onValueChange={(value) => setMultiCurrencyForm({...multiCurrencyForm, operation: value})}>
                                    <SelectTrigger className="input-green">
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="withdraw">💸 Withdraw</SelectItem>
                                        <SelectItem value="fund">💰 Fund Treasury</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-casino-green-300 mb-2">Currency</label>
                                <Select value={multiCurrencyForm.currency} onValueChange={(value) => setMultiCurrencyForm({...multiCurrencyForm, currency: value})}>
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
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-casino-green-300 mb-2">
                                Amount ({multiCurrencyForm.currency})
                            </label>
                            <Input
                                type="number"
                                placeholder="Enter amount"
                                value={multiCurrencyForm.amount}
                                onChange={(e) => setMultiCurrencyForm({...multiCurrencyForm, amount: e.target.value})}
                                className="input-green"
                            />
                            <p className="text-xs text-casino-green-400 mt-1">
                                Available: {formatCurrency(treasuryData[multiCurrencyForm.currency]?.balance || 0, multiCurrencyForm.currency)} {multiCurrencyForm.currency}
                            </p>
                        </div>

                        {multiCurrencyForm.operation === 'withdraw' && (
                            <>
                                <div>
                                    <label className="block text-sm font-medium text-casino-green-300 mb-2">Source Wallet</label>
                                    <Select value={multiCurrencyForm.sourceWallet} onValueChange={(value) => setMultiCurrencyForm({...multiCurrencyForm, sourceWallet: value})}>
                                        <SelectTrigger className="input-green">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="Winnings">🎰 Winnings</SelectItem>
                                            <SelectItem value="Savings">🏦 Savings</SelectItem>
                                            <SelectItem value="Liquidity">💧 Liquidity</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-casino-green-300 mb-2">
                                        Destination Address ({getCurrencyInfo(multiCurrencyForm.currency)?.network})
                                    </label>
                                    <Input
                                        type="text"
                                        placeholder={`Enter ${getCurrencyInfo(multiCurrencyForm.currency)?.network} address`}
                                        value={multiCurrencyForm.destination}
                                        onChange={(e) => setMultiCurrencyForm({...multiCurrencyForm, destination: e.target.value})}
                                        className="input-green font-mono text-sm"
                                    />
                                </div>
                            </>
                        )}

                        <Button
                            onClick={handleMultiCurrencyOperation}
                            disabled={loading || !multiCurrencyForm.amount || (multiCurrencyForm.operation === 'withdraw' && !multiCurrencyForm.destination)}
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
                                    Execute {multiCurrencyForm.operation === 'withdraw' ? 'Multi-Currency Withdrawal' : 'Treasury Funding'}
                                </>
                            )}
                        </Button>

                        {/* Currency Info */}
                        <div className="mt-4 p-4 rounded-lg bg-casino-green-900/20 border border-casino-green-500/30">
                            <h4 className="font-bold text-casino-green-300 mb-2">
                                {getCurrencyInfo(multiCurrencyForm.currency)?.icon} {multiCurrencyForm.currency} Treasury Features:
                            </h4>
                            <ul className="text-sm text-casino-green-200 space-y-1">
                                <li>✅ Network: {getCurrencyInfo(multiCurrencyForm.currency)?.network}</li>
                                <li>✅ Smart contract treasury backing</li>
                                <li>✅ Multi-signature authorization</li>
                                <li>✅ Cross-chain compatibility</li>
                                <li>✅ Real-time health monitoring</li>
                            </ul>
                        </div>
                    </CardContent>
                </Card>
            )}

            {activeTab === 'analytics' && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <Card className="card-green">
                        <CardHeader>
                            <CardTitle className="text-casino-green-400">Performance Metrics</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {supportedCurrencies.map(currency => {
                                    const data = treasuryData[currency.symbol] || {};
                                    const limits = adminSettings.withdrawalLimits[currency.symbol] || {};
                                    const dailyUsagePercent = ((data.dailyWithdrawn || 0) / (limits.daily || 1)) * 100;
                                    
                                    return (
                                        <div key={currency.symbol} className="space-y-2">
                                            <div className="flex justify-between items-center">
                                                <span className="text-casino-green-200">
                                                    {currency.icon} {currency.symbol} Daily Usage
                                                </span>
                                                <span className="text-sm text-casino-green-300">
                                                    {formatCurrency(data.dailyWithdrawn || 0, currency.symbol)} / {formatCurrency(limits.daily || 0, currency.symbol)}
                                                </span>
                                            </div>
                                            <Progress 
                                                value={Math.min(dailyUsagePercent, 100)}
                                                className="h-3 progress-green"
                                            />
                                            <p className="text-xs text-casino-green-400">
                                                {dailyUsagePercent.toFixed(1)}% of daily limit used
                                            </p>
                                        </div>
                                    );
                                })}
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="card-green">
                        <CardHeader>
                            <CardTitle className="text-casino-green-400">Treasury Health Scores</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {supportedCurrencies.map(currency => {
                                    const data = treasuryData[currency.symbol] || {};
                                    const limits = adminSettings.withdrawalLimits[currency.symbol] || {};
                                    const balanceRatio = ((data.balance || 0) / (limits.minBalance || 1)) * 100;
                                    const healthScore = Math.min(Math.max(balanceRatio, 0), 100);
                                    
                                    return (
                                        <div key={currency.symbol} className="flex items-center justify-between p-3 rounded-lg bg-casino-green-900/20">
                                            <div className="flex items-center space-x-3">
                                                <span className="text-xl">{currency.icon}</span>
                                                <div>
                                                    <p className="font-bold text-casino-green-100">{currency.symbol}</p>
                                                    <p className="text-xs text-casino-green-300">Health Score</p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className={`text-2xl font-bold ${
                                                    healthScore >= 80 ? 'text-casino-green-400' :
                                                    healthScore >= 50 ? 'text-yellow-400' : 'text-red-400'
                                                }`}>
                                                    {healthScore.toFixed(0)}%
                                                </p>
                                                <p className="text-xs text-casino-green-300">
                                                    {healthScore >= 80 ? '✅ Excellent' :
                                                     healthScore >= 50 ? '⚠️ Good' : '🚨 Critical'}
                                                </p>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {activeTab === 'admin' && user?.username === 'cryptoking' && (
                <div className="space-y-6">
                    {/* Admin Control Toggle */}
                    <div className="flex justify-center mb-6">
                        <Button
                            onClick={() => setShowAdminPanel(!showAdminPanel)}
                            className={`px-8 py-3 ${
                                showAdminPanel 
                                    ? 'bg-red-600 hover:bg-red-700' 
                                    : 'bg-casino-green-600 hover:bg-casino-green-700'
                            } text-white`}
                        >
                            {showAdminPanel ? <EyeOff className="w-4 h-4 mr-2" /> : <Eye className="w-4 h-4 mr-2" />}
                            {showAdminPanel ? 'Hide' : 'Show'} Advanced Admin Controls
                        </Button>
                    </div>

                    {showAdminPanel && (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            {/* Per-Currency Admin Settings */}
                            {supportedCurrencies.map(currency => {
                                const limits = adminSettings.withdrawalLimits[currency.symbol] || {};
                                const autoFunding = adminSettings.autoFunding.thresholds[currency.symbol] || 0;
                                
                                return (
                                    <Card key={currency.symbol} className="card-green">
                                        <CardHeader>
                                            <CardTitle className="text-casino-green-400 flex items-center space-x-2">
                                                <span className="text-2xl">{currency.icon}</span>
                                                <span>{currency.symbol} Settings</span>
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent className="space-y-4">
                                            <div>
                                                <label className="block text-sm font-medium text-casino-green-300 mb-2">
                                                    Daily Withdrawal Limit
                                                </label>
                                                <div className="flex space-x-2">
                                                    <Input
                                                        type="number"
                                                        value={limits.daily || 0}
                                                        onChange={(e) => handleAdminSettingsUpdate(currency.symbol, 'dailyLimit', parseFloat(e.target.value))}
                                                        className="input-green"
                                                    />
                                                    <span className="flex items-center text-casino-green-300">{currency.symbol}</span>
                                                </div>
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-casino-green-300 mb-2">
                                                    Per Transaction Limit
                                                </label>
                                                <div className="flex space-x-2">
                                                    <Input
                                                        type="number"
                                                        value={limits.perTransaction || 0}
                                                        onChange={(e) => handleAdminSettingsUpdate(currency.symbol, 'perTransactionLimit', parseFloat(e.target.value))}
                                                        className="input-green"
                                                    />
                                                    <span className="flex items-center text-casino-green-300">{currency.symbol}</span>
                                                </div>
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-casino-green-300 mb-2">
                                                    Minimum Treasury Balance
                                                </label>
                                                <div className="flex space-x-2">
                                                    <Input
                                                        type="number"
                                                        value={limits.minBalance || 0}
                                                        onChange={(e) => handleAdminSettingsUpdate(currency.symbol, 'minBalance', parseFloat(e.target.value))}
                                                        className="input-green"
                                                    />
                                                    <span className="flex items-center text-casino-green-300">{currency.symbol}</span>
                                                </div>
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-casino-green-300 mb-2">
                                                    Auto-Funding Threshold
                                                </label>
                                                <div className="flex space-x-2">
                                                    <Input
                                                        type="number"
                                                        value={autoFunding}
                                                        onChange={(e) => handleAdminSettingsUpdate(currency.symbol, 'autoFundingThreshold', parseFloat(e.target.value))}
                                                        className="input-green"
                                                    />
                                                    <span className="flex items-center text-casino-green-300">{currency.symbol}</span>
                                                </div>
                                            </div>

                                            {/* Emergency Controls */}
                                            <div className="pt-4 border-t border-casino-green-500/30">
                                                <h4 className="text-sm font-bold text-casino-green-300 mb-2">Emergency Controls</h4>
                                                <div className="flex space-x-2">
                                                    <Button
                                                        size="sm"
                                                        className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                                                    >
                                                        <Pause className="w-3 h-3 mr-1" />
                                                        Pause
                                                    </Button>
                                                    <Button
                                                        size="sm"
                                                        className="flex-1 bg-casino-green-600 hover:bg-casino-green-700 text-white"
                                                    >
                                                        <Play className="w-3 h-3 mr-1" />
                                                        Resume
                                                    </Button>
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                );
                            })}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default MultiCurrencyTreasuryManager;