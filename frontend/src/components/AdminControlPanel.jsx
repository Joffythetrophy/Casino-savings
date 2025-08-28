import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Switch } from './ui/switch';
import { Slider } from './ui/slider';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Settings, DollarSign, Percent, Clock, Shield, BarChart3, Zap, Target } from 'lucide-react';

const AdminControlPanel = ({ onSettingsChange }) => {
    const [adminSettings, setAdminSettings] = useState({
        // CRT Conversion Settings
        crtConversionRate: 0.15, // $0.15 per CRT
        maxCrtConversionPerMonth: 2000000, // 2M CRT per month
        conversionCooldown: 24, // 24 hours
        
        // Liquidity Pool Settings
        liquidityAllocationPercentage: 50, // 50% of savings to liquidity
        withdrawalLiquidityMinimum: 1000, // Min $1000 in liquidity for withdrawals
        liquidityRebalanceFrequency: 7, // days
        
        // Savings Settings
        savingsInterestRate: 0.8, // 0.8% monthly
        autoSavingsEnabled: true,
        savingsLockPeriod: 0, // days (0 = no lock)
        
        // Game Settings
        slotWinRate: 15, // 15% win rate
        rouletteWinRate: 47, // 47% win rate (red/black)
        diceWinRate: 49, // 49% win rate
        maxBetAmount: 1000, // Max $1000 bet
        minBetAmount: 1, // Min $1 bet
        
        // Auto-Play Settings
        autoPlayEnabled: true,
        maxAutoPlayBets: 100, // Max 100 bets per session
        autoPlayCooldown: 5, // 5 seconds between bets
        
        // Security Settings
        withdrawalRequire2FA: false,
        maxWithdrawalPerDay: 10000, // $10k per day
        suspiciousActivityMonitoring: true,
        
        // Goal Settings
        corvetteGoalAmount: 85000, // $85k
        financialFreedomGoal: 1000000, // $1M
        monthlyIncomeGoal: 5000, // $5k
        
        // System Settings
        maintenanceMode: false,
        newUserRegistration: true,
        realTimeUpdates: true
    });

    const [systemStats, setSystemStats] = useState({
        totalUsers: 1,
        totalPortfolioValue: 7703483,
        totalLiquidityPool: 1155522,
        totalSavingsPool: 4622090,
        monthlyActiveUsers: 1,
        totalGamesPlayed: 1247,
        averageSessionLength: 45, // minutes
        conversionRate: 85 // % of visitors who convert
    });

    const handleSettingChange = (key, value) => {
        setAdminSettings(prev => ({
            ...prev,
            [key]: value
        }));
        
        // Notify parent component of changes
        onSettingsChange?.(key, value);
    };

    const saveAllSettings = async () => {
        try {
            // In a real app, this would save to backend
            console.log('Saving admin settings:', adminSettings);
            alert('Settings saved successfully!');
        } catch (error) {
            alert('Error saving settings: ' + error.message);
        }
    };

    return (
        <div className="w-full max-w-6xl mx-auto p-6 bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 min-h-screen">
            {/* Header */}
            <div className="text-center mb-8">
                <h1 className="text-4xl font-bold bg-gradient-to-r from-gold-400 via-yellow-500 to-gold-600 bg-clip-text text-transparent mb-2">
                    ⚙️ ADMIN CONTROL PANEL ⚙️
                </h1>
                <p className="text-xl text-gray-300">Casino Savings Empire Management</p>
                <div className="flex justify-center space-x-4 mt-4">
                    <Badge className="bg-green-600 text-white px-4 py-2">
                        <DollarSign className="w-4 h-4 mr-1" />
                        Total Value: ${systemStats.totalPortfolioValue.toLocaleString()}
                    </Badge>
                    <Badge className="bg-blue-600 text-white px-4 py-2">
                        <BarChart3 className="w-4 h-4 mr-1" />
                        Active Users: {systemStats.totalUsers}
                    </Badge>
                </div>
            </div>

            {/* System Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <Card className="bg-gradient-to-br from-green-900/50 to-emerald-900/50 border-green-500/30">
                    <CardContent className="p-4 text-center">
                        <div className="text-2xl font-bold text-white">
                            ${systemStats.totalPortfolioValue.toLocaleString()}
                        </div>
                        <div className="text-sm text-emerald-300">Total Portfolio</div>
                    </CardContent>
                </Card>
                
                <Card className="bg-gradient-to-br from-blue-900/50 to-cyan-900/50 border-blue-500/30">
                    <CardContent className="p-4 text-center">
                        <div className="text-2xl font-bold text-white">
                            ${systemStats.totalLiquidityPool.toLocaleString()}
                        </div>
                        <div className="text-sm text-cyan-300">Liquidity Pool</div>
                    </CardContent>
                </Card>
                
                <Card className="bg-gradient-to-br from-purple-900/50 to-indigo-900/50 border-purple-500/30">
                    <CardContent className="p-4 text-center">
                        <div className="text-2xl font-bold text-white">
                            {systemStats.totalGamesPlayed.toLocaleString()}
                        </div>
                        <div className="text-sm text-purple-300">Games Played</div>
                    </CardContent>
                </Card>
                
                <Card className="bg-gradient-to-br from-orange-900/50 to-red-900/50 border-orange-500/30">
                    <CardContent className="p-4 text-center">
                        <div className="text-2xl font-bold text-white">
                            {systemStats.conversionRate}%
                        </div>
                        <div className="text-sm text-orange-300">Conversion Rate</div>
                    </CardContent>
                </Card>
            </div>

            {/* Settings Tabs */}
            <Tabs defaultValue="conversion" className="w-full">
                <TabsList className="grid w-full grid-cols-6 bg-slate-800/50">
                    <TabsTrigger value="conversion">CRT & Conversion</TabsTrigger>
                    <TabsTrigger value="liquidity">Liquidity Pool</TabsTrigger>
                    <TabsTrigger value="games">Game Settings</TabsTrigger>
                    <TabsTrigger value="savings">Savings & Interest</TabsTrigger>
                    <TabsTrigger value="goals">Goals & Targets</TabsTrigger>
                    <TabsTrigger value="security">Security</TabsTrigger>
                </TabsList>

                {/* CRT Conversion Settings */}
                <TabsContent value="conversion">
                    <Card className="bg-slate-800/50 border-slate-600/30">
                        <CardHeader>
                            <CardTitle className="flex items-center text-gold-300">
                                <DollarSign className="w-5 h-5 mr-2" />
                                CRT Conversion Management
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <Label htmlFor="crtRate" className="text-white">CRT to USD Rate</Label>
                                    <div className="flex items-center space-x-4 mt-2">
                                        <span className="text-gray-300">$</span>
                                        <Input
                                            id="crtRate"
                                            type="number"
                                            step="0.01"
                                            value={adminSettings.crtConversionRate}
                                            onChange={(e) => handleSettingChange('crtConversionRate', parseFloat(e.target.value))}
                                            className="bg-slate-700 border-slate-600 text-white"
                                        />
                                        <span className="text-gray-300">per CRT</span>
                                    </div>
                                </div>
                                
                                <div>
                                    <Label htmlFor="maxConversion" className="text-white">Max Monthly Conversion</Label>
                                    <Input
                                        id="maxConversion"
                                        type="number"
                                        value={adminSettings.maxCrtConversionPerMonth}
                                        onChange={(e) => handleSettingChange('maxCrtConversionPerMonth', parseInt(e.target.value))}
                                        className="bg-slate-700 border-slate-600 text-white mt-2"
                                    />
                                    <div className="text-sm text-gray-400 mt-1">CRT tokens per month</div>
                                </div>
                            </div>
                            
                            <div>
                                <Label className="text-white">Conversion Cooldown: {adminSettings.conversionCooldown} hours</Label>
                                <Slider
                                    value={[adminSettings.conversionCooldown]}
                                    onValueChange={([value]) => handleSettingChange('conversionCooldown', value)}
                                    max={168}
                                    min={1}
                                    step={1}
                                    className="mt-2"
                                />
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Liquidity Pool Settings */}
                <TabsContent value="liquidity">
                    <Card className="bg-slate-800/50 border-slate-600/30">
                        <CardHeader>
                            <CardTitle className="flex items-center text-blue-300">
                                <BarChart3 className="w-5 h-5 mr-2" />
                                Liquidity Pool Management
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div>
                                <Label className="text-white">
                                    Savings to Liquidity Allocation: {adminSettings.liquidityAllocationPercentage}%
                                </Label>
                                <Slider
                                    value={[adminSettings.liquidityAllocationPercentage]}
                                    onValueChange={([value]) => handleSettingChange('liquidityAllocationPercentage', value)}
                                    max={100}
                                    min={10}
                                    step={5}
                                    className="mt-2"
                                />
                                <div className="text-sm text-gray-400 mt-1">
                                    Percentage of savings automatically added to liquidity pool
                                </div>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <Label htmlFor="withdrawalMin" className="text-white">Min Liquidity for Withdrawals</Label>
                                    <Input
                                        id="withdrawalMin"
                                        type="number"
                                        value={adminSettings.withdrawalLiquidityMinimum}
                                        onChange={(e) => handleSettingChange('withdrawalLiquidityMinimum', parseInt(e.target.value))}
                                        className="bg-slate-700 border-slate-600 text-white mt-2"
                                    />
                                    <div className="text-sm text-gray-400 mt-1">USD minimum</div>
                                </div>
                                
                                <div>
                                    <Label htmlFor="rebalanceFreq" className="text-white">Rebalance Frequency</Label>
                                    <Input
                                        id="rebalanceFreq"
                                        type="number"
                                        value={adminSettings.liquidityRebalanceFrequency}
                                        onChange={(e) => handleSettingChange('liquidityRebalanceFrequency', parseInt(e.target.value))}
                                        className="bg-slate-700 border-slate-600 text-white mt-2"
                                    />
                                    <div className="text-sm text-gray-400 mt-1">Days between rebalancing</div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Game Settings */}
                <TabsContent value="games">
                    <Card className="bg-slate-800/50 border-slate-600/30">
                        <CardHeader>
                            <CardTitle className="flex items-center text-purple-300">
                                <Zap className="w-5 h-5 mr-2" />
                                Casino Game Configuration
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div>
                                    <Label className="text-white">Slot Machine Win Rate: {adminSettings.slotWinRate}%</Label>
                                    <Slider
                                        value={[adminSettings.slotWinRate]}
                                        onValueChange={([value]) => handleSettingChange('slotWinRate', value)}
                                        max={50}
                                        min={5}
                                        step={1}
                                        className="mt-2"
                                    />
                                </div>
                                
                                <div>
                                    <Label className="text-white">Roulette Win Rate: {adminSettings.rouletteWinRate}%</Label>
                                    <Slider
                                        value={[adminSettings.rouletteWinRate]}
                                        onValueChange={([value]) => handleSettingChange('rouletteWinRate', value)}
                                        max={50}
                                        min={40}
                                        step={1}
                                        className="mt-2"
                                    />
                                </div>
                                
                                <div>
                                    <Label className="text-white">Dice Win Rate: {adminSettings.diceWinRate}%</Label>
                                    <Slider
                                        value={[adminSettings.diceWinRate]}
                                        onValueChange={([value]) => handleSettingChange('diceWinRate', value)}
                                        max={50}
                                        min={40}
                                        step={1}
                                        className="mt-2"
                                    />
                                </div>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div>
                                    <Label htmlFor="maxBet" className="text-white">Maximum Bet Amount</Label>
                                    <Input
                                        id="maxBet"
                                        type="number"
                                        value={adminSettings.maxBetAmount}
                                        onChange={(e) => handleSettingChange('maxBetAmount', parseInt(e.target.value))}
                                        className="bg-slate-700 border-slate-600 text-white mt-2"
                                    />
                                    <div className="text-sm text-gray-400 mt-1">USD per bet</div>
                                </div>
                                
                                <div>
                                    <Label htmlFor="minBet" className="text-white">Minimum Bet Amount</Label>
                                    <Input
                                        id="minBet"
                                        type="number"
                                        value={adminSettings.minBetAmount}
                                        onChange={(e) => handleSettingChange('minBetAmount', parseInt(e.target.value))}
                                        className="bg-slate-700 border-slate-600 text-white mt-2"
                                    />
                                    <div className="text-sm text-gray-400 mt-1">USD per bet</div>
                                </div>
                            </div>
                            
                            <div className="flex items-center space-x-4">
                                <Switch
                                    checked={adminSettings.autoPlayEnabled}
                                    onCheckedChange={(checked) => handleSettingChange('autoPlayEnabled', checked)}
                                />
                                <Label className="text-white">Enable Auto-Play Feature</Label>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Savings Settings */}
                <TabsContent value="savings">
                    <Card className="bg-slate-800/50 border-slate-600/30">
                        <CardHeader>
                            <CardTitle className="flex items-center text-emerald-300">
                                <Percent className="w-5 h-5 mr-2" />
                                Savings & Interest Configuration
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div>
                                <Label className="text-white">
                                    Monthly Interest Rate: {adminSettings.savingsInterestRate}%
                                </Label>
                                <Slider
                                    value={[adminSettings.savingsInterestRate]}
                                    onValueChange={([value]) => handleSettingChange('savingsInterestRate', value)}
                                    max={5.0}
                                    min={0.1}
                                    step={0.1}
                                    className="mt-2"
                                />
                                <div className="text-sm text-gray-400 mt-1">
                                    Applied monthly to savings balances
                                </div>
                            </div>
                            
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="flex items-center space-x-4">
                                    <Switch
                                        checked={adminSettings.autoSavingsEnabled}
                                        onCheckedChange={(checked) => handleSettingChange('autoSavingsEnabled', checked)}
                                    />
                                    <Label className="text-white">Auto-Save Game Losses</Label>
                                </div>
                                
                                <div>
                                    <Label htmlFor="lockPeriod" className="text-white">Savings Lock Period</Label>
                                    <Input
                                        id="lockPeriod"
                                        type="number"
                                        value={adminSettings.savingsLockPeriod}
                                        onChange={(e) => handleSettingChange('savingsLockPeriod', parseInt(e.target.value))}
                                        className="bg-slate-700 border-slate-600 text-white mt-2"
                                    />
                                    <div className="text-sm text-gray-400 mt-1">Days (0 = no lock)</div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Goals & Targets */}
                <TabsContent value="goals">
                    <Card className="bg-slate-800/50 border-slate-600/30">
                        <CardHeader>
                            <CardTitle className="flex items-center text-orange-300">
                                <Target className="w-5 h-5 mr-2" />
                                Goal & Target Configuration
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div>
                                    <Label htmlFor="corvetteGoal" className="text-white">Corvette Goal Amount</Label>
                                    <Input
                                        id="corvetteGoal"
                                        type="number"
                                        value={adminSettings.corvetteGoalAmount}
                                        onChange={(e) => handleSettingChange('corvetteGoalAmount', parseInt(e.target.value))}
                                        className="bg-slate-700 border-slate-600 text-white mt-2"
                                    />
                                    <div className="text-sm text-gray-400 mt-1">USD</div>
                                </div>
                                
                                <div>
                                    <Label htmlFor="freedomGoal" className="text-white">Financial Freedom Goal</Label>
                                    <Input
                                        id="freedomGoal"
                                        type="number"
                                        value={adminSettings.financialFreedomGoal}
                                        onChange={(e) => handleSettingChange('financialFreedomGoal', parseInt(e.target.value))}
                                        className="bg-slate-700 border-slate-600 text-white mt-2"
                                    />
                                    <div className="text-sm text-gray-400 mt-1">USD</div>
                                </div>
                                
                                <div>
                                    <Label htmlFor="incomeGoal" className="text-white">Monthly Income Goal</Label>
                                    <Input
                                        id="incomeGoal"
                                        type="number"
                                        value={adminSettings.monthlyIncomeGoal}
                                        onChange={(e) => handleSettingChange('monthlyIncomeGoal', parseInt(e.target.value))}
                                        className="bg-slate-700 border-slate-600 text-white mt-2"
                                    />
                                    <div className="text-sm text-gray-400 mt-1">USD per month</div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Security Settings */}
                <TabsContent value="security">
                    <Card className="bg-slate-800/50 border-slate-600/30">
                        <CardHeader>
                            <CardTitle className="flex items-center text-red-300">
                                <Shield className="w-5 h-5 mr-2" />
                                Security & Risk Management
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="flex items-center space-x-4">
                                    <Switch
                                        checked={adminSettings.withdrawalRequire2FA}
                                        onCheckedChange={(checked) => handleSettingChange('withdrawalRequire2FA', checked)}
                                    />
                                    <Label className="text-white">Require 2FA for Withdrawals</Label>
                                </div>
                                
                                <div className="flex items-center space-x-4">
                                    <Switch
                                        checked={adminSettings.suspiciousActivityMonitoring}
                                        onCheckedChange={(checked) => handleSettingChange('suspiciousActivityMonitoring', checked)}
                                    />
                                    <Label className="text-white">Monitor Suspicious Activity</Label>
                                </div>
                            </div>
                            
                            <div>
                                <Label htmlFor="maxWithdrawal" className="text-white">Max Daily Withdrawal</Label>
                                <Input
                                    id="maxWithdrawal"
                                    type="number"
                                    value={adminSettings.maxWithdrawalPerDay}
                                    onChange={(e) => handleSettingChange('maxWithdrawalPerDay', parseInt(e.target.value))}
                                    className="bg-slate-700 border-slate-600 text-white mt-2"
                                />
                                <div className="text-sm text-gray-400 mt-1">USD per day</div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>

            {/* Save Button */}
            <div className="mt-8 text-center">
                <Button 
                    onClick={saveAllSettings}
                    className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 px-8 py-3 text-lg"
                >
                    💾 Save All Settings
                </Button>
            </div>
        </div>
    );
};

export default AdminControlPanel;