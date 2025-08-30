import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
    TrendingUp, 
    DollarSign, 
    ExternalLink,
    CheckCircle,
    Clock,
    AlertTriangle,
    Waves,
    Star,
    BarChart3,
    Settings,
    Plus,
    Activity,
    Globe,
    Zap
} from 'lucide-react';

const CRTTokenDEXManager = ({ user, authToken }) => {
    const [dexStatus, setDexStatus] = useState(null);
    const [priceData, setPriceData] = useState(null);
    const [pools, setPools] = useState([]);
    const [loading, setLoading] = useState(false);
    const [notifications, setNotifications] = useState([]);
    const [activeTab, setActiveTab] = useState('overview');

    // CRT Token Information
    const crtToken = {
        mint: '9pjWtc6x88wrRMXTxkBcNB6YtcN7NNcyzDAfUMfRknty',
        symbol: 'CRT',
        name: 'CRT Tiger Token',
        logo: 'https://customer-assets.emergentagent.com/job_smart-savings-dapp/artifacts/b3v23rrw_copilot_image_1755811225489.jpeg'
    };

    // DEX Platforms
    const dexPlatforms = [
        { name: 'Orca', icon: '🌊', color: 'bg-blue-500' },
        { name: 'Jupiter', icon: '🪐', color: 'bg-purple-500' },
        { name: 'Raydium', icon: '⚡', color: 'bg-yellow-500' },
        { name: 'Serum', icon: '🔥', color: 'bg-red-500' },
        { name: 'Aldrin', icon: '🚀', color: 'bg-green-500' }
    ];

    useEffect(() => {
        fetchDEXData();
        const interval = setInterval(fetchDEXData, 30000); // Update every 30 seconds
        return () => clearInterval(interval);
    }, []);

    const fetchDEXData = async () => {
        try {
            await Promise.all([
                fetchDEXStatus(),
                fetchPriceData(),
                fetchLiquidityPools()
            ]);
        } catch (error) {
            console.error('Failed to fetch DEX data:', error);
            addNotification('error', 'Failed to fetch DEX data');
        }
    };

    const fetchDEXStatus = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/dex/listing-status`);
            if (response.ok) {
                const data = await response.json();
                setDexStatus(data);
            }
        } catch (error) {
            console.error('Failed to fetch DEX status:', error);
        }
    };

    const fetchPriceData = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/dex/crt-price`);
            if (response.ok) {
                const data = await response.json();
                setPriceData(data.price_data);
            }
        } catch (error) {
            console.error('Failed to fetch price data:', error);
        }
    };

    const fetchLiquidityPools = async () => {
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/dex/pools`);
            if (response.ok) {
                const data = await response.json();
                setPools(data.pools || []);
            }
        } catch (error) {
            console.error('Failed to fetch pools:', error);
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

    const handleCreateOrcaPool = async (poolPair) => {
        if (!user?.username === 'cryptoking') {
            addNotification('error', 'Admin access required for pool creation');
            return;
        }

        setLoading(true);
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/dex/create-orca-pool`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    pool_pair: poolPair,
                    wallet_address: user.wallet_address
                })
            });

            const data = await response.json();
            
            if (data.success) {
                addNotification('success', `🌊 ${poolPair} Orca pool created successfully!`);
                await fetchDEXData();
            } else {
                addNotification('error', data.message || 'Pool creation failed');
            }
        } catch (error) {
            console.error('Pool creation failed:', error);
            addNotification('error', 'Pool creation request failed');
        } finally {
            setLoading(false);
        }
    };

    const handleJupiterSubmission = async () => {
        if (!user?.username === 'cryptoking') {
            addNotification('error', 'Admin access required for Jupiter submission');
            return;
        }

        setLoading(true);
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/dex/submit-jupiter-listing`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    wallet_address: user.wallet_address
                })
            });

            const data = await response.json();
            
            if (data.success) {
                addNotification('success', '🪐 CRT token submitted to Jupiter aggregator!');
                await fetchDEXStatus();
            } else {
                addNotification('error', data.message || 'Jupiter submission failed');
            }
        } catch (error) {
            console.error('Jupiter submission failed:', error);
            addNotification('error', 'Jupiter submission request failed');
        } finally {
            setLoading(false);
        }
    };

    const formatPrice = (price) => {
        if (!price) return '0.00';
        return price < 0.01 ? price.toFixed(6) : price.toFixed(4);
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount || 0);
    };

    if (!dexStatus || !priceData) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-casino-green-400">
                    🐅 Loading CRT Token DEX Manager...
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
                <div className="flex items-center justify-center space-x-4 mb-4">
                    <img 
                        src={crtToken.logo} 
                        alt="CRT Token" 
                        className="w-16 h-16 rounded-full glow-green"
                    />
                    <div>
                        <h1 className="text-4xl font-bold text-casino-green-400">
                            🐅 CRT Token DEX Manager 🐅
                        </h1>
                        <p className="text-casino-green-200">
                            Liquidity Pools, Price Discovery & DEX Listings
                        </p>
                    </div>
                </div>
            </div>

            {/* Price Overview */}
            <Card className="card-green mb-6">
                <CardHeader>
                    <CardTitle className="text-casino-green-400 flex items-center space-x-2">
                        <DollarSign className="w-5 h-5" />
                        <span>CRT Token Price</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="text-center p-4 rounded-lg bg-casino-green-900/20">
                            <p className="text-sm text-casino-green-300">USD Price</p>
                            <p className="text-2xl font-bold text-casino-green-100">
                                ${formatPrice(priceData?.price?.usd)}
                            </p>
                        </div>
                        <div className="text-center p-4 rounded-lg bg-casino-green-900/20">
                            <p className="text-sm text-casino-green-300">SOL Price</p>
                            <p className="text-2xl font-bold text-casino-green-100">
                                {formatPrice(priceData?.price?.sol)} SOL
                            </p>
                        </div>
                        <div className="text-center p-4 rounded-lg bg-casino-green-900/20">
                            <p className="text-sm text-casino-green-300">Total Liquidity</p>
                            <p className="text-2xl font-bold text-casino-green-100">
                                {formatCurrency(priceData?.market_data?.liquidity?.total_value_locked)}
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Navigation Tabs */}
            <div className="flex space-x-4 mb-6 overflow-x-auto">
                {[
                    { id: 'overview', label: '📊 Overview', icon: BarChart3 },
                    { id: 'pools', label: '🌊 Pools', icon: Waves },
                    { id: 'listings', label: '📈 Listings', icon: TrendingUp },
                    { id: 'manage', label: '⚙️ Manage', icon: Settings }
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
                            <CardTitle className="text-casino-green-400">DEX Listing Progress</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="text-casino-green-200">Overall Progress</span>
                                    <span className="text-casino-green-100">
                                        {dexStatus?.summary?.listing_percentage?.toFixed(1) || 0}%
                                    </span>
                                </div>
                                <Progress 
                                    value={dexStatus?.summary?.listing_percentage || 0}
                                    className="h-3 progress-green"
                                />
                                <p className="text-sm text-casino-green-300">
                                    Listed on {dexStatus?.summary?.listed_on || 0} of {dexStatus?.summary?.total_dexs || 10} platforms
                                </p>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="card-green">
                        <CardHeader>
                            <CardTitle className="text-casino-green-400">Active Pools</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {pools.length > 0 ? pools.map((pool, index) => (
                                    <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-casino-green-900/20">
                                        <div className="flex items-center space-x-3">
                                            <Waves className="w-5 h-5 text-casino-green-400" />
                                            <div>
                                                <p className="font-bold text-casino-green-100">{pool.pool_pair}</p>
                                                <p className="text-xs text-casino-green-300">{pool.dex}</p>
                                            </div>
                                        </div>
                                        <Badge variant="outline" className="border-casino-green-500/50 text-casino-green-300">
                                            Active
                                        </Badge>
                                    </div>
                                )) : (
                                    <div className="text-center py-4 text-casino-green-300">
                                        No active pools yet
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}

            {activeTab === 'pools' && (
                <div className="space-y-6">
                    <Card className="card-green">
                        <CardHeader>
                            <CardTitle className="text-casino-green-400">Create Liquidity Pools</CardTitle>
                            <p className="text-casino-green-200">Create trading pairs on Orca DEX</p>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="p-4 rounded-lg border border-casino-green-500/30 bg-casino-green-900/10">
                                    <div className="flex items-center justify-between mb-3">
                                        <h3 className="font-bold text-casino-green-100">CRT/SOL Pool</h3>
                                        <Badge variant="outline" className="border-blue-500/50 text-blue-300">
                                            Orca
                                        </Badge>
                                    </div>
                                    <p className="text-sm text-casino-green-200 mb-4">
                                        Initial Liquidity: 1M CRT + 100 SOL
                                    </p>
                                    <Button
                                        onClick={() => handleCreateOrcaPool('CRT/SOL')}
                                        disabled={loading}
                                        className="w-full btn-primary"
                                    >
                                        <Plus className="w-4 h-4 mr-2" />
                                        Create CRT/SOL Pool
                                    </Button>
                                </div>

                                <div className="p-4 rounded-lg border border-casino-green-500/30 bg-casino-green-900/10">
                                    <div className="flex items-center justify-between mb-3">
                                        <h3 className="font-bold text-casino-green-100">CRT/USDC Pool</h3>
                                        <Badge variant="outline" className="border-blue-500/50 text-blue-300">
                                            Orca
                                        </Badge>
                                    </div>
                                    <p className="text-sm text-casino-green-200 mb-4">
                                        Initial Liquidity: 1M CRT + $10,000 USDC
                                    </p>
                                    <Button
                                        onClick={() => handleCreateOrcaPool('CRT/USDC')}
                                        disabled={loading}
                                        className="w-full btn-primary"
                                    >
                                        <Plus className="w-4 h-4 mr-2" />
                                        Create CRT/USDC Pool
                                    </Button>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Existing Pools */}
                    <Card className="card-green">
                        <CardHeader>
                            <CardTitle className="text-casino-green-400">Existing Pools</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {pools.length > 0 ? (
                                <div className="space-y-3">
                                    {pools.map((pool, index) => (
                                        <div key={index} className="flex items-center justify-between p-4 rounded-lg bg-casino-green-900/20 border border-casino-green-500/30">
                                            <div className="flex items-center space-x-4">
                                                <Waves className="w-6 h-6 text-casino-green-400" />
                                                <div>
                                                    <p className="font-bold text-casino-green-100">{pool.pool_pair}</p>
                                                    <p className="text-sm text-casino-green-300">{pool.dex} • Created: {new Date(pool.created_at).toLocaleDateString()}</p>
                                                </div>
                                            </div>
                                            <div className="flex items-center space-x-3">
                                                <Badge variant="outline" className="border-casino-green-500/50 text-casino-green-300">
                                                    {pool.status}
                                                </Badge>
                                                {pool.transaction_hash && (
                                                    <Button size="sm" variant="outline" asChild>
                                                        <a 
                                                            href={`https://explorer.solana.com/tx/${pool.transaction_hash}`}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                        >
                                                            <ExternalLink className="w-3 h-3" />
                                                        </a>
                                                    </Button>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-8 text-casino-green-300">
                                    No pools created yet. Create your first pool above!
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            )}

            {activeTab === 'listings' && (
                <Card className="card-green">
                    <CardHeader>
                        <CardTitle className="text-casino-green-400">DEX Platform Listings</CardTitle>
                        <p className="text-casino-green-200">Track CRT token listings across DEX platforms</p>
                    </CardHeader>
                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {dexPlatforms.map(platform => {
                                const status = dexStatus?.listing_status?.[platform.name] || {};
                                const isListed = status.listed || false;
                                
                                return (
                                    <div key={platform.name} className="p-4 rounded-lg border border-casino-green-500/30 bg-casino-green-900/10">
                                        <div className="flex items-center justify-between mb-3">
                                            <div className="flex items-center space-x-2">
                                                <span className="text-xl">{platform.icon}</span>
                                                <h3 className="font-bold text-casino-green-100">{platform.name}</h3>
                                            </div>
                                            {isListed ? (
                                                <CheckCircle className="w-5 h-5 text-casino-green-400" />
                                            ) : (
                                                <Clock className="w-5 h-5 text-yellow-400" />
                                            )}
                                        </div>
                                        <Badge 
                                            variant="outline" 
                                            className={`${
                                                isListed 
                                                    ? 'border-casino-green-500/50 text-casino-green-300' 
                                                    : 'border-yellow-500/50 text-yellow-300'
                                            }`}
                                        >
                                            {isListed ? 'Listed' : status.status || 'Not Listed'}
                                        </Badge>
                                    </div>
                                );
                            })}
                        </div>
                    </CardContent>
                </Card>
            )}

            {activeTab === 'manage' && user?.username === 'cryptoking' && (
                <div className="space-y-6">
                    <Card className="card-green">
                        <CardHeader>
                            <CardTitle className="text-casino-green-400">Jupiter Aggregator</CardTitle>
                            <p className="text-casino-green-200">Submit CRT token to Jupiter for aggregation</p>
                        </CardHeader>
                        <CardContent>
                            <div className="flex items-center justify-between p-4 rounded-lg bg-casino-green-900/20 border border-casino-green-500/30">
                                <div className="flex items-center space-x-4">
                                    <span className="text-3xl">🪐</span>
                                    <div>
                                        <h3 className="font-bold text-casino-green-100">Jupiter Token List</h3>
                                        <p className="text-sm text-casino-green-200">Submit for aggregation across all Solana DEXs</p>
                                    </div>
                                </div>
                                <Button
                                    onClick={handleJupiterSubmission}
                                    disabled={loading}
                                    className="btn-primary"
                                >
                                    <Star className="w-4 h-4 mr-2" />
                                    Submit to Jupiter
                                </Button>
                            </div>
                        </CardContent>
                    </Card>

                    <Card className="card-green">
                        <CardHeader>
                            <CardTitle className="text-casino-green-400">Token Information</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-casino-green-300 mb-1">Token Mint</label>
                                    <p className="text-casino-green-100 font-mono text-sm break-all">{crtToken.mint}</p>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-casino-green-300 mb-1">Symbol</label>
                                    <p className="text-casino-green-100 font-bold">{crtToken.symbol}</p>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-casino-green-300 mb-1">Name</label>
                                    <p className="text-casino-green-100">{crtToken.name}</p>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-casino-green-300 mb-1">Logo</label>
                                    <img src={crtToken.logo} alt="CRT Token" className="w-12 h-12 rounded-full" />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
};

export default CRTTokenDEXManager;