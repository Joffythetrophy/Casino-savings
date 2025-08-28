import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Calendar, Download, Filter, TrendingUp, ArrowUpRight, ArrowDownRight, DollarSign, Clock, Search } from 'lucide-react';

const ConversionHistoryTracker = ({ userBalance }) => {
    const [transactions, setTransactions] = useState([
        {
            id: "treasury_rebalance_1703462400",
            type: "treasury_rebalance",
            sourceAmount: 34831540,
            sourceCurrency: "DOGE",
            targetCurrencies: ["DOGE", "TRX", "USDC"],
            usdValue: 7703483,
            timestamp: "2025-08-27T21:20:56Z",
            status: "completed",
            description: "Multi-currency treasury redistribution"
        },
        {
            id: "crt_conversion_001",
            type: "crt_conversion",
            sourceAmount: 1000000,
            sourceCurrency: "CRT",
            targetAmount: 150000,
            targetCurrency: "USDC",
            conversionRate: 0.15,
            usdValue: 150000,
            timestamp: "2025-08-26T15:30:00Z",
            status: "completed",
            description: "CRT to USDC conversion for gaming"
        },
        {
            id: "game_loss_savings_001",
            type: "game_savings",
            sourceAmount: 2500,
            sourceCurrency: "USDC",
            targetAmount: 2500,
            targetCurrency: "DOGE",
            usdValue: 2500,
            timestamp: "2025-08-26T14:45:00Z",
            status: "completed",
            description: "Slot machine losses saved"
        },
        {
            id: "liquidity_allocation_001",
            type: "liquidity_transfer",
            sourceAmount: 125000,
            sourceCurrency: "USDC",
            targetAmount: 125000,
            targetCurrency: "USDC",
            usdValue: 125000,
            timestamp: "2025-08-25T18:20:00Z",
            status: "completed",
            description: "50% savings to liquidity pool"
        },
        {
            id: "interest_payment_001",
            type: "interest_payment",
            sourceAmount: 0,
            sourceCurrency: "SYSTEM",
            targetAmount: 3850,
            targetCurrency: "USDC",
            interestRate: 0.8,
            usdValue: 3850,
            timestamp: "2025-08-25T00:00:00Z",
            status: "completed",
            description: "Monthly interest payment (0.8%)"
        }
    ]);

    const [filteredTransactions, setFilteredTransactions] = useState(transactions);
    const [filters, setFilters] = useState({
        type: 'all',
        currency: 'all',
        dateRange: '30d',
        searchTerm: ''
    });

    const [chartData, setChartData] = useState([
        { date: '2025-08-01', portfolio: 6500000, savings: 3900000, liquidity: 1950000 },
        { date: '2025-08-05', portfolio: 6750000, savings: 4050000, liquidity: 2025000 },
        { date: '2025-08-10', portfolio: 7000000, savings: 4200000, liquidity: 2100000 },
        { date: '2025-08-15', portfolio: 7250000, savings: 4350000, liquidity: 2175000 },
        { date: '2025-08-20', portfolio: 7500000, savings: 4500000, liquidity: 2250000 },
        { date: '2025-08-25', portfolio: 7703483, savings: 4622090, liquidity: 2311045 },
        { date: '2025-08-27', portfolio: 7703483, savings: 4622090, liquidity: 2311045 }
    ]);

    // Filter transactions based on selected filters
    useEffect(() => {
        let filtered = transactions;

        if (filters.type !== 'all') {
            filtered = filtered.filter(tx => tx.type === filters.type);
        }

        if (filters.currency !== 'all') {
            filtered = filtered.filter(tx => 
                tx.sourceCurrency === filters.currency || 
                tx.targetCurrency === filters.currency ||
                (tx.targetCurrencies && tx.targetCurrencies.includes(filters.currency))
            );
        }

        if (filters.searchTerm) {
            filtered = filtered.filter(tx => 
                tx.description.toLowerCase().includes(filters.searchTerm.toLowerCase()) ||
                tx.id.toLowerCase().includes(filters.searchTerm.toLowerCase())
            );
        }

        setFilteredTransactions(filtered);
    }, [filters, transactions]);

    const getTransactionIcon = (type) => {
        switch (type) {
            case 'crt_conversion': return '🔄';
            case 'treasury_rebalance': return '⚖️';
            case 'game_savings': return '🎰';
            case 'liquidity_transfer': return '💧';
            case 'interest_payment': return '📈';
            default: return '💱';
        }
    };

    const getTransactionColor = (type) => {
        switch (type) {
            case 'crt_conversion': return 'bg-blue-600';
            case 'treasury_rebalance': return 'bg-purple-600';
            case 'game_savings': return 'bg-green-600';
            case 'liquidity_transfer': return 'bg-cyan-600';
            case 'interest_payment': return 'bg-gold-600';
            default: return 'bg-gray-600';
        }
    };

    const formatCurrency = (amount, currency) => {
        if (currency === 'USD' || currency === 'USDC') {
            return `$${amount.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0})}`;
        }
        return `${amount.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 2})} ${currency}`;
    };

    const exportTransactions = () => {
        const csvContent = [
            ['Date', 'Type', 'Description', 'Source', 'Target', 'USD Value', 'Status'],
            ...filteredTransactions.map(tx => [
                new Date(tx.timestamp).toLocaleDateString(),
                tx.type,
                tx.description,
                `${tx.sourceAmount} ${tx.sourceCurrency}`,
                tx.targetCurrency ? `${tx.targetAmount} ${tx.targetCurrency}` : 'Multiple',
                `$${tx.usdValue.toLocaleString()}`,
                tx.status
            ])
        ].map(row => row.join(',')).join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'transaction_history.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    };

    return (
        <div className="w-full max-w-7xl mx-auto p-6 bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 min-h-screen">
            {/* Header */}
            <div className="text-center mb-8">
                <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 bg-clip-text text-transparent mb-2">
                    📊 CONVERSION HISTORY TRACKER
                </h1>
                <p className="text-xl text-gray-300">Complete Transaction & Portfolio Analytics</p>
            </div>

            {/* Portfolio Growth Chart */}
            <Card className="bg-slate-800/50 border-slate-600/30 backdrop-blur mb-8">
                <CardHeader>
                    <CardTitle className="flex items-center text-cyan-300">
                        <TrendingUp className="w-5 h-5 mr-2" />
                        Portfolio Growth Timeline
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={chartData}>
                            <defs>
                                <linearGradient id="portfolioGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.8}/>
                                    <stop offset="95%" stopColor="#06B6D4" stopOpacity={0.1}/>
                                </linearGradient>
                                <linearGradient id="savingsGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.8}/>
                                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.1}/>
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                            <XAxis dataKey="date" stroke="#9CA3AF" />
                            <YAxis stroke="#9CA3AF" />
                            <Tooltip 
                                contentStyle={{
                                    backgroundColor: '#1F2937',
                                    border: '1px solid #374151',
                                    borderRadius: '8px'
                                }}
                                formatter={(value, name) => [
                                    `$${value.toLocaleString()}`,
                                    name === 'portfolio' ? 'Total Portfolio' :
                                    name === 'savings' ? 'Savings Pool' : 'Liquidity Pool'
                                ]}
                            />
                            <Area 
                                type="monotone" 
                                dataKey="portfolio" 
                                stroke="#06B6D4" 
                                fillOpacity={1} 
                                fill="url(#portfolioGradient)" 
                            />
                            <Area 
                                type="monotone" 
                                dataKey="savings" 
                                stroke="#10B981" 
                                fillOpacity={1} 
                                fill="url(#savingsGradient)" 
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <Card className="bg-gradient-to-br from-green-900/50 to-emerald-900/50 border-green-500/30">
                    <CardContent className="p-4 text-center">
                        <div className="text-2xl font-bold text-white">
                            {filteredTransactions.length}
                        </div>
                        <div className="text-sm text-emerald-300">Total Transactions</div>
                    </CardContent>
                </Card>
                
                <Card className="bg-gradient-to-br from-blue-900/50 to-cyan-900/50 border-blue-500/30">
                    <CardContent className="p-4 text-center">
                        <div className="text-2xl font-bold text-white">
                            ${filteredTransactions.reduce((sum, tx) => sum + tx.usdValue, 0).toLocaleString()}
                        </div>
                        <div className="text-sm text-cyan-300">Total Volume</div>
                    </CardContent>
                </Card>
                
                <Card className="bg-gradient-to-br from-purple-900/50 to-indigo-900/50 border-purple-500/30">
                    <CardContent className="p-4 text-center">
                        <div className="text-2xl font-bold text-white">
                            ${(chartData[chartData.length - 1].portfolio - chartData[0].portfolio).toLocaleString()}
                        </div>
                        <div className="text-sm text-purple-300">Portfolio Growth</div>
                    </CardContent>
                </Card>
                
                <Card className="bg-gradient-to-br from-gold-900/50 to-yellow-900/50 border-gold-500/30">
                    <CardContent className="p-4 text-center">
                        <div className="text-2xl font-bold text-white">
                            {((chartData[chartData.length - 1].portfolio / chartData[0].portfolio - 1) * 100).toFixed(1)}%
                        </div>
                        <div className="text-sm text-gold-300">Total Return</div>
                    </CardContent>
                </Card>
            </div>

            {/* Filters and Controls */}
            <Card className="bg-slate-800/50 border-slate-600/30 backdrop-blur mb-6">
                <CardContent className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-center">
                        <div>
                            <label className="text-sm text-gray-300 mb-1 block">Transaction Type</label>
                            <Select value={filters.type} onValueChange={(value) => setFilters(prev => ({...prev, type: value}))}>
                                <SelectTrigger className="bg-slate-700 border-slate-600">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Types</SelectItem>
                                    <SelectItem value="crt_conversion">CRT Conversion</SelectItem>
                                    <SelectItem value="treasury_rebalance">Treasury Rebalance</SelectItem>
                                    <SelectItem value="game_savings">Game Savings</SelectItem>
                                    <SelectItem value="liquidity_transfer">Liquidity Transfer</SelectItem>
                                    <SelectItem value="interest_payment">Interest Payment</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div>
                            <label className="text-sm text-gray-300 mb-1 block">Currency</label>
                            <Select value={filters.currency} onValueChange={(value) => setFilters(prev => ({...prev, currency: value}))}>
                                <SelectTrigger className="bg-slate-700 border-slate-600">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="all">All Currencies</SelectItem>
                                    <SelectItem value="CRT">CRT</SelectItem>
                                    <SelectItem value="DOGE">DOGE</SelectItem>
                                    <SelectItem value="TRX">TRX</SelectItem>
                                    <SelectItem value="USDC">USDC</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div>
                            <label className="text-sm text-gray-300 mb-1 block">Date Range</label>
                            <Select value={filters.dateRange} onValueChange={(value) => setFilters(prev => ({...prev, dateRange: value}))}>
                                <SelectTrigger className="bg-slate-700 border-slate-600">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="7d">Last 7 Days</SelectItem>
                                    <SelectItem value="30d">Last 30 Days</SelectItem>
                                    <SelectItem value="90d">Last 90 Days</SelectItem>
                                    <SelectItem value="all">All Time</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div>
                            <label className="text-sm text-gray-300 mb-1 block">Search</label>
                            <div className="relative">
                                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                                <Input
                                    placeholder="Search transactions..."
                                    value={filters.searchTerm}
                                    onChange={(e) => setFilters(prev => ({...prev, searchTerm: e.target.value}))}
                                    className="bg-slate-700 border-slate-600 pl-10"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="text-sm text-gray-300 mb-1 block">&nbsp;</label>
                            <Button 
                                onClick={exportTransactions}
                                className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
                            >
                                <Download className="w-4 h-4 mr-2" />
                                Export CSV
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Transaction List */}
            <Card className="bg-slate-800/50 border-slate-600/30 backdrop-blur">
                <CardHeader>
                    <CardTitle className="flex items-center text-white">
                        <Clock className="w-5 h-5 mr-2" />
                        Transaction History ({filteredTransactions.length} records)
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {filteredTransactions.map((transaction, index) => (
                            <div 
                                key={transaction.id}
                                className="flex items-center justify-between p-4 bg-slate-700/30 rounded-lg border border-slate-600/30 hover:bg-slate-700/50 transition-colors"
                            >
                                <div className="flex items-center space-x-4">
                                    <div className={`w-12 h-12 rounded-full ${getTransactionColor(transaction.type)} flex items-center justify-center text-white text-xl`}>
                                        {getTransactionIcon(transaction.type)}
                                    </div>
                                    
                                    <div>
                                        <div className="font-medium text-white">
                                            {transaction.description}
                                        </div>
                                        <div className="text-sm text-gray-400">
                                            {new Date(transaction.timestamp).toLocaleString()} • ID: {transaction.id.slice(-8)}
                                        </div>
                                        <div className="flex items-center space-x-2 mt-1">
                                            <Badge variant="outline" className="text-xs">
                                                {transaction.type.replace('_', ' ').toUpperCase()}
                                            </Badge>
                                            <Badge 
                                                className={transaction.status === 'completed' ? 'bg-green-600' : 'bg-yellow-600'}
                                            >
                                                {transaction.status.toUpperCase()}
                                            </Badge>
                                        </div>
                                    </div>
                                </div>

                                <div className="text-right">
                                    <div className="font-bold text-white text-lg">
                                        ${transaction.usdValue.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0})}
                                    </div>
                                    
                                    {transaction.sourceCurrency && transaction.targetCurrency ? (
                                        <div className="text-sm text-gray-300">
                                            {formatCurrency(transaction.sourceAmount, transaction.sourceCurrency)}
                                            {transaction.targetCurrency !== transaction.sourceCurrency && (
                                                <>
                                                    <ArrowUpRight className="w-3 h-3 inline mx-1" />
                                                    {formatCurrency(transaction.targetAmount, transaction.targetCurrency)}
                                                </>
                                            )}
                                        </div>
                                    ) : transaction.targetCurrencies ? (
                                        <div className="text-sm text-gray-300">
                                            {formatCurrency(transaction.sourceAmount, transaction.sourceCurrency)}
                                            <ArrowUpRight className="w-3 h-3 inline mx-1" />
                                            Multi-Currency
                                        </div>
                                    ) : null}
                                    
                                    {transaction.conversionRate && (
                                        <div className="text-xs text-gray-400">
                                            Rate: ${transaction.conversionRate} per {transaction.sourceCurrency}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}

                        {filteredTransactions.length === 0 && (
                            <div className="text-center py-12">
                                <div className="text-6xl mb-4">📊</div>
                                <div className="text-gray-400 text-lg">No transactions match your current filters</div>
                                <Button 
                                    onClick={() => setFilters({type: 'all', currency: 'all', dateRange: '30d', searchTerm: ''})}
                                    className="mt-4 bg-slate-600 hover:bg-slate-700"
                                >
                                    Clear Filters
                                </Button>
                            </div>
                        )}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default ConversionHistoryTracker;