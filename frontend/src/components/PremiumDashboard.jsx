import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Target, Car, DollarSign, Coins, Trophy, Zap, Calendar, BarChart3 } from 'lucide-react';

const PremiumDashboard = ({ userBalance, conversionRates, onNavigate }) => {
    const [goalSettings, setGoalSettings] = useState({
        corvetteGoal: 85000, // $85k for a Corvette
        financialFreedomGoal: 1000000, // $1M for financial independence
        monthlyIncomeGoal: 5000 // $5k monthly passive income
    });

    const [passiveIncomeData, setPassiveIncomeData] = useState([
        { month: 'Jan', income: 1250, savings: 12500 },
        { month: 'Feb', income: 1890, savings: 18900 },
        { month: 'Mar', income: 2340, savings: 23400 },
        { month: 'Apr', income: 3100, savings: 31000 },
        { month: 'May', income: 4200, savings: 42000 },
        { month: 'Jun', income: 5680, savings: 56800 }
    ]);

    // Calculate total portfolio value
    const calculatePortfolioValue = () => {
        if (!userBalance || !conversionRates) return 0;
        
        let totalUSD = 0;
        const treasuries = ['deposit_balance', 'winnings_balance', 'savings_balance'];
        
        treasuries.forEach(treasury => {
            if (userBalance[treasury]) {
                Object.entries(userBalance[treasury]).forEach(([currency, amount]) => {
                    if (amount > 0) {
                        const rate = conversionRates[`${currency}_USD`] || 
                                   (currency === 'DOGE' ? 0.221 : 
                                    currency === 'TRX' ? 0.347 :
                                    currency === 'USDC' ? 1.0 :
                                    currency === 'CRT' ? 0.15 : 0);
                        totalUSD += amount * rate;
                    }
                });
            }
        });
        
        return totalUSD;
    };

    const portfolioValue = calculatePortfolioValue();
    const corvetteProgress = (portfolioValue / goalSettings.corvetteGoal) * 100;
    const freedomProgress = (portfolioValue / goalSettings.financialFreedomGoal) * 100;
    const currentMonthlyIncome = passiveIncomeData[passiveIncomeData.length - 1]?.income || 0;
    const incomeProgress = (currentMonthlyIncome / goalSettings.monthlyIncomeGoal) * 100;

    // Treasury breakdown for pie chart
    const treasuryBreakdown = [
        { name: 'Savings Treasury', value: 60, color: '#10B981', amount: portfolioValue * 0.6 },
        { name: 'Liquidity Treasury', value: 30, color: '#3B82F6', amount: portfolioValue * 0.3 },
        { name: 'Winnings Treasury', value: 10, color: '#8B5CF6', amount: portfolioValue * 0.1 }
    ];

    // Liquidity pool calculation
    const liquidityPool = portfolioValue * 0.15; // 15% of total as withdrawable liquidity
    const savingsGrowth = portfolioValue * 0.008; // 0.8% monthly growth simulation

    return (
        <div className="w-full max-w-7xl mx-auto p-6 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 min-h-screen">
            {/* Premium Header */}
            <div className="text-center mb-8">
                <h1 className="text-5xl font-bold bg-gradient-to-r from-gold-400 via-yellow-500 to-gold-600 bg-clip-text text-transparent mb-2">
                    💎 JOFFY CASINO SAVER 💎
                </h1>
                <p className="text-xl text-gray-300">Your Million-Dollar Casino Savings Empire</p>
                <div className="flex justify-center items-center space-x-4 mt-4">
                    <Badge className="bg-gradient-to-r from-green-500 to-emerald-600 text-white px-4 py-2">
                        <DollarSign className="w-4 h-4 mr-1" />
                        Total Portfolio: ${portfolioValue.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0})}
                    </Badge>
                    <Badge className="bg-gradient-to-r from-blue-500 to-cyan-600 text-white px-4 py-2">
                        <Zap className="w-4 h-4 mr-1" />
                        Monthly Income: ${currentMonthlyIncome.toLocaleString()}
                    </Badge>
                </div>
            </div>

            {/* Goal Tracking Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {/* Corvette Goal */}
                <Card className="bg-gradient-to-br from-red-900/50 to-orange-900/50 border-red-500/30 backdrop-blur">
                    <CardHeader className="text-center">
                        <CardTitle className="flex items-center justify-center text-orange-300">
                            <Car className="w-6 h-6 mr-2" />
                            Corvette Goal 🏎️
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-center mb-4">
                            <div className="text-3xl font-bold text-white">
                                ${portfolioValue.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0})}
                            </div>
                            <div className="text-sm text-gray-300">
                                of ${goalSettings.corvetteGoal.toLocaleString()} goal
                            </div>
                        </div>
                        <Progress 
                            value={Math.min(corvetteProgress, 100)} 
                            className="mb-2"
                            style={{background: 'rgba(0,0,0,0.3)'}}
                        />
                        <div className="text-center text-sm">
                            {corvetteProgress >= 100 ? (
                                <span className="text-green-400 font-bold">🎉 GOAL ACHIEVED! 🎉</span>
                            ) : (
                                <span className="text-orange-300">
                                    {corvetteProgress.toFixed(1)}% Complete
                                </span>
                            )}
                        </div>
                    </CardContent>
                </Card>

                {/* Financial Independence Goal */}
                <Card className="bg-gradient-to-br from-green-900/50 to-emerald-900/50 border-green-500/30 backdrop-blur">
                    <CardHeader className="text-center">
                        <CardTitle className="flex items-center justify-center text-emerald-300">
                            <Target className="w-6 h-6 mr-2" />
                            Financial Freedom 🚀
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-center mb-4">
                            <div className="text-3xl font-bold text-white">
                                {freedomProgress.toFixed(1)}%
                            </div>
                            <div className="text-sm text-gray-300">
                                to ${goalSettings.financialFreedomGoal.toLocaleString()} goal
                            </div>
                        </div>
                        <Progress 
                            value={Math.min(freedomProgress, 100)} 
                            className="mb-2"
                        />
                        <div className="text-center text-sm">
                            {freedomProgress >= 100 ? (
                                <span className="text-green-400 font-bold">🎉 FINANCIALLY FREE! 🎉</span>
                            ) : (
                                <span className="text-emerald-300">
                                    ${(goalSettings.financialFreedomGoal - portfolioValue).toLocaleString()} to go
                                </span>
                            )}
                        </div>
                    </CardContent>
                </Card>

                {/* Monthly Income Goal */}
                <Card className="bg-gradient-to-br from-purple-900/50 to-indigo-900/50 border-purple-500/30 backdrop-blur">
                    <CardHeader className="text-center">
                        <CardTitle className="flex items-center justify-center text-purple-300">
                            <Calendar className="w-6 h-6 mr-2" />
                            Monthly Income 💰
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-center mb-4">
                            <div className="text-3xl font-bold text-white">
                                ${currentMonthlyIncome.toLocaleString()}
                            </div>
                            <div className="text-sm text-gray-300">
                                of ${goalSettings.monthlyIncomeGoal.toLocaleString()} goal
                            </div>
                        </div>
                        <Progress 
                            value={Math.min(incomeProgress, 100)} 
                            className="mb-2"
                        />
                        <div className="text-center text-sm">
                            {incomeProgress >= 100 ? (
                                <span className="text-green-400 font-bold">🎯 INCOME GOAL MET! 🎯</span>
                            ) : (
                                <span className="text-purple-300">
                                    {incomeProgress.toFixed(1)}% Complete
                                </span>
                            )}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Analytics Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Passive Income Chart */}
                <Card className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-600/30 backdrop-blur">
                    <CardHeader>
                        <CardTitle className="flex items-center text-cyan-300">
                            <TrendingUp className="w-5 h-5 mr-2" />
                            Passive Income Growth
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={250}>
                            <LineChart data={passiveIncomeData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis dataKey="month" stroke="#9CA3AF" />
                                <YAxis stroke="#9CA3AF" />
                                <Tooltip 
                                    contentStyle={{
                                        backgroundColor: '#1F2937',
                                        border: '1px solid #374151',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Line 
                                    type="monotone" 
                                    dataKey="income" 
                                    stroke="#06B6D4" 
                                    strokeWidth={3}
                                    dot={{ fill: '#06B6D4', strokeWidth: 2, r: 6 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                        <div className="text-center mt-4">
                            <Badge className="bg-cyan-600 text-white">
                                +{((currentMonthlyIncome / passiveIncomeData[0].income - 1) * 100).toFixed(1)}% Growth
                            </Badge>
                        </div>
                    </CardContent>
                </Card>

                {/* Treasury Breakdown */}
                <Card className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 border-slate-600/30 backdrop-blur">
                    <CardHeader>
                        <CardTitle className="flex items-center text-gold-300">
                            <BarChart3 className="w-5 h-5 mr-2" />
                            Treasury Distribution
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center justify-center">
                            <ResponsiveContainer width="100%" height={200}>
                                <PieChart>
                                    <Pie
                                        data={treasuryBreakdown}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={100}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {treasuryBreakdown.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip 
                                        formatter={(value, name) => [`${value}%`, name]}
                                        contentStyle={{
                                            backgroundColor: '#1F2937',
                                            border: '1px solid #374151',
                                            borderRadius: '8px'
                                        }}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="space-y-2 mt-4">
                            {treasuryBreakdown.map((treasury, index) => (
                                <div key={index} className="flex justify-between items-center">
                                    <div className="flex items-center">
                                        <div 
                                            className="w-3 h-3 rounded-full mr-2"
                                            style={{ backgroundColor: treasury.color }}
                                        ></div>
                                        <span className="text-sm text-gray-300">{treasury.name}</span>
                                    </div>
                                    <span className="text-sm font-medium text-white">
                                        ${treasury.amount.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0})}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Liquidity & Withdrawal Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Liquidity Pool Meter */}
                <Card className="bg-gradient-to-br from-blue-900/50 to-indigo-900/50 border-blue-500/30 backdrop-blur">
                    <CardHeader>
                        <CardTitle className="flex items-center text-blue-300">
                            <Coins className="w-5 h-5 mr-2" />
                            Liquidity Pool Status
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-center mb-6">
                            <div className="text-4xl font-bold text-white mb-2">
                                ${liquidityPool.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0})}
                            </div>
                            <div className="text-sm text-gray-300 mb-4">Available for Withdrawal</div>
                            
                            <div className="bg-slate-700 rounded-full h-4 mb-2">
                                <div 
                                    className="bg-gradient-to-r from-blue-500 to-cyan-400 h-4 rounded-full transition-all duration-500"
                                    style={{ width: `${(liquidityPool / portfolioValue) * 100}%` }}
                                ></div>
                            </div>
                            <div className="text-xs text-gray-400">
                                {((liquidityPool / portfolioValue) * 100).toFixed(1)}% of Total Portfolio
                            </div>
                        </div>
                        
                        <Button 
                            className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700"
                            onClick={() => onNavigate?.('wallet')}
                        >
                            💰 Access Withdrawal
                        </Button>
                    </CardContent>
                </Card>

                {/* Savings Growth */}
                <Card className="bg-gradient-to-br from-emerald-900/50 to-green-900/50 border-emerald-500/30 backdrop-blur">
                    <CardHeader>
                        <CardTitle className="flex items-center text-emerald-300">
                            <Trophy className="w-5 h-5 mr-2" />
                            Savings Growth Engine
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                                <span className="text-gray-300">Monthly Growth Rate</span>
                                <span className="text-green-400 font-bold">+0.8%</span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                                <span className="text-gray-300">Projected Monthly Gain</span>
                                <span className="text-green-400 font-bold">
                                    +${savingsGrowth.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0})}
                                </span>
                            </div>
                            <div className="flex justify-between items-center p-3 bg-slate-800/50 rounded-lg">
                                <span className="text-gray-300">Annual Projection</span>
                                <span className="text-green-400 font-bold">
                                    +${(savingsGrowth * 12).toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0})}
                                </span>
                            </div>
                        </div>
                        
                        <Button 
                            className="w-full mt-4 bg-gradient-to-r from-emerald-600 to-green-600 hover:from-emerald-700 hover:to-green-700"
                            onClick={() => onNavigate?.('games')}
                        >
                            🎰 Start Gaming to Save
                        </Button>
                    </CardContent>
                </Card>
            </div>

            {/* Action Buttons */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <Button 
                    className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 h-16"
                    onClick={() => onNavigate?.('games')}
                >
                    <div className="text-center">
                        <div className="text-2xl mb-1">🎰</div>
                        <div className="text-sm">Casino Games</div>
                    </div>
                </Button>
                
                <Button 
                    className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 h-16"
                    onClick={() => onNavigate?.('savings')}
                >
                    <div className="text-center">
                        <div className="text-2xl mb-1">🏦</div>
                        <div className="text-sm">Savings Vault</div>
                    </div>
                </Button>
                
                <Button 
                    className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 h-16"
                    onClick={() => onNavigate?.('wallet')}
                >
                    <div className="text-center">
                        <div className="text-2xl mb-1">💳</div>
                        <div className="text-sm">Wallet Manager</div>
                    </div>
                </Button>
                
                <Button 
                    className="bg-gradient-to-r from-gold-600 to-yellow-600 hover:from-gold-700 hover:to-yellow-700 h-16"
                    onClick={() => onNavigate?.('trading')}
                >
                    <div className="text-center">
                        <div className="text-2xl mb-1">📈</div>
                        <div className="text-sm">Trading</div>
                    </div>
                </Button>
            </div>

            {/* Footer Stats */}
            <div className="mt-8 text-center">
                <div className="inline-flex space-x-8 text-sm text-gray-400">
                    <span>🎯 Games Won: 1,247</span>
                    <span>💰 Total Saved: ${(portfolioValue * 0.75).toLocaleString()}</span>
                    <span>📅 Days Active: 89</span>
                    <span>🏆 Streak: 12 days</span>
                </div>
            </div>
        </div>
    );
};

export default PremiumDashboard;