import React, { useState, useEffect, useRef } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Slider } from '../ui/slider';
import { Switch } from '../ui/switch';
import { useToast } from '../../hooks/use-toast';
import { Play, Pause, Square, Settings, TrendingUp, TrendingDown, Zap } from 'lucide-react';
import { useWallet } from './CasinoGameLayout';

const AutoPlayPanel = ({ 
  onBet, 
  gameType = 'Generic',
  gameSpecificSettings = {},
  disabled = false,
  minBet = 1,
  maxBet = 100
}) => {
  const [isAutoPlaying, setIsAutoPlaying] = useState(false);
  const [autoPlayConfig, setAutoPlayConfig] = useState({
    // Basic Settings
    baseBetAmount: 10,
    numberOfBets: 100,
    maxLoss: 50,
    maxWin: 200,
    
    // Strategy Settings
    strategy: 'constant', // constant, martingale, fibonacci, customPattern
    onWinAction: 'reset', // reset, increase, decrease, stop
    onLossAction: 'reset', // reset, increase, decrease, stop
    multiplier: 2.0,
    
    // Advanced Settings
    stopOnWin: false,
    stopOnLoss: false,
    targetProfit: 100,
    maxConsecutiveLosses: 5,
    
    // Speed Settings
    delayBetweenBets: 1000, // milliseconds
    
    // Game-specific settings (dice prediction, etc.)
    ...gameSpecificSettings
  });
  
  const [autoPlayStats, setAutoPlayStats] = useState({
    betsPlaced: 0,
    totalWon: 0,
    totalLost: 0,
    netProfit: 0,
    consecutiveWins: 0,
    consecutiveLosses: 0,
    currentStreak: 0,
    largestWin: 0,
    largestLoss: 0
  });
  
  const [currentBetAmount, setCurrentBetAmount] = useState(autoPlayConfig.baseBetAmount);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const autoPlayRef = useRef(null);
  const fibonacciSequence = useRef([1, 1]);
  const fibIndex = useRef(0);
  
  const { balance } = useWallet();
  const { toast } = useToast();

  // AI Betting Strategies
  const calculateNextBet = (lastResult, currentBet) => {
    const { strategy, onWinAction, onLossAction, multiplier, baseBetAmount } = autoPlayConfig;
    
    switch (strategy) {
      case 'martingale':
        if (lastResult === 'loss') {
          return Math.min(currentBet * multiplier, maxBet, balance);
        }
        return baseBetAmount;
        
      case 'fibonacci':
        if (lastResult === 'loss') {
          fibIndex.current = Math.min(fibIndex.current + 1, fibonacciSequence.current.length - 1);
          // Extend fibonacci if needed
          if (fibIndex.current >= fibonacciSequence.current.length - 1) {
            const len = fibonacciSequence.current.length;
            fibonacciSequence.current.push(
              fibonacciSequence.current[len - 1] + fibonacciSequence.current[len - 2]
            );
          }
        } else {
          fibIndex.current = Math.max(0, fibIndex.current - 2);
        }
        return Math.min(
          baseBetAmount * fibonacciSequence.current[fibIndex.current], 
          maxBet, 
          balance
        );
        
      case 'antiMartingale':
        if (lastResult === 'win') {
          return Math.min(currentBet * multiplier, maxBet, balance);
        }
        return baseBetAmount;
        
      case 'customPattern':
        // Apply win/loss actions
        if (lastResult === 'win') {
          switch (onWinAction) {
            case 'increase': return Math.min(currentBet * multiplier, maxBet, balance);
            case 'decrease': return Math.max(currentBet / multiplier, minBet);
            case 'reset': return baseBetAmount;
            default: return currentBet;
          }
        } else {
          switch (onLossAction) {
            case 'increase': return Math.min(currentBet * multiplier, maxBet, balance);
            case 'decrease': return Math.max(currentBet / multiplier, minBet);
            case 'reset': return baseBetAmount;
            default: return currentBet;
          }
        }
        
      case 'constant':
      default:
        return baseBetAmount;
    }
  };

  // Smart Stop Conditions
  const shouldStopAutoPlay = () => {
    const { 
      numberOfBets, maxLoss, maxWin, targetProfit, 
      maxConsecutiveLosses, stopOnWin, stopOnLoss 
    } = autoPlayConfig;
    
    const { betsPlaced, netProfit, consecutiveLosses } = autoPlayStats;
    
    // Basic stop conditions
    if (betsPlaced >= numberOfBets) {
      toast({
        title: "🔄 Auto-Play Complete",
        description: `Completed ${numberOfBets} bets. Net profit: ${netProfit.toFixed(2)} CRT`,
      });
      return true;
    }
    
    if (netProfit <= -Math.abs(maxLoss)) {
      toast({
        title: "🛑 Max Loss Reached",
        description: `Stopped at loss limit: ${Math.abs(netProfit).toFixed(2)} CRT`,
        variant: "destructive"
      });
      return true;
    }
    
    if (netProfit >= targetProfit) {
      toast({
        title: "🎯 Target Profit Reached!",
        description: `Stopped at profit target: ${netProfit.toFixed(2)} CRT`,
      });
      return true;
    }
    
    if (consecutiveLosses >= maxConsecutiveLosses) {
      toast({
        title: "📉 Max Consecutive Losses",
        description: `Stopped after ${consecutiveLosses} consecutive losses`,
        variant: "destructive"
      });
      return true;
    }
    
    if (currentBetAmount > balance) {
      toast({
        title: "💰 Insufficient Balance",
        description: "Not enough balance for next bet",
        variant: "destructive"
      });
      return true;
    }
    
    return false;
  };

  // Auto-play execution
  const executeAutoPlay = async () => {
    if (!onBet || shouldStopAutoPlay()) {
      stopAutoPlay();
      return;
    }
    
    try {
      // Place the bet
      const betResult = await onBet(currentBetAmount);
      
      // Update stats based on result
      const isWin = betResult && (betResult.success && betResult.result === 'win');
      const payout = betResult?.payout || 0;
      const netResult = isWin ? payout - currentBetAmount : -currentBetAmount;
      
      setAutoPlayStats(prev => {
        const newStats = {
          betsPlaced: prev.betsPlaced + 1,
          totalWon: prev.totalWon + (isWin ? payout : 0),
          totalLost: prev.totalLost + (isWin ? 0 : currentBetAmount),
          netProfit: prev.netProfit + netResult,
          consecutiveWins: isWin ? prev.consecutiveWins + 1 : 0,
          consecutiveLosses: isWin ? 0 : prev.consecutiveLosses + 1,
          currentStreak: isWin ? 
            (prev.currentStreak >= 0 ? prev.currentStreak + 1 : 1) :
            (prev.currentStreak <= 0 ? prev.currentStreak - 1 : -1),
          largestWin: Math.max(prev.largestWin, isWin ? payout : 0),
          largestLoss: Math.max(prev.largestLoss, isWin ? 0 : currentBetAmount)
        };
        
        return newStats;
      });
      
      // Calculate next bet amount
      const nextBet = calculateNextBet(isWin ? 'win' : 'loss', currentBetAmount);
      setCurrentBetAmount(nextBet);
      
      // Schedule next bet
      if (isAutoPlaying) {
        autoPlayRef.current = setTimeout(() => {
          executeAutoPlay();
        }, autoPlayConfig.delayBetweenBets);
      }
      
    } catch (error) {
      console.error('Auto-play error:', error);
      toast({
        title: "❌ Auto-Play Error",
        description: "An error occurred during auto-play",
        variant: "destructive"
      });
      stopAutoPlay();
    }
  };

  const startAutoPlay = () => {
    if (disabled || currentBetAmount > balance) {
      toast({
        title: "❌ Cannot Start Auto-Play",
        description: "Insufficient balance or game disabled",
        variant: "destructive"
      });
      return;
    }
    
    setIsAutoPlaying(true);
    // Reset some stats
    setAutoPlayStats(prev => ({
      ...prev,
      betsPlaced: 0,
      netProfit: 0,
      consecutiveWins: 0,
      consecutiveLosses: 0,
      currentStreak: 0
    }));
    
    setCurrentBetAmount(autoPlayConfig.baseBetAmount);
    fibIndex.current = 0; // Reset fibonacci index
    
    toast({
      title: "🤖 Auto-Play Started",
      description: `Starting ${autoPlayConfig.strategy} strategy with ${currentBetAmount} CRT bets`,
    });
    
    // Start first bet after a short delay
    autoPlayRef.current = setTimeout(executeAutoPlay, 500);
  };

  const stopAutoPlay = () => {
    setIsAutoPlaying(false);
    if (autoPlayRef.current) {
      clearTimeout(autoPlayRef.current);
      autoPlayRef.current = null;
    }
    
    toast({
      title: "⏹️ Auto-Play Stopped",
      description: `Final profit: ${autoPlayStats.netProfit.toFixed(2)} CRT`,
    });
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (autoPlayRef.current) {
        clearTimeout(autoPlayRef.current);
      }
    };
  }, []);

  return (
    <Card className="p-4 bg-gradient-to-br from-purple-900/50 to-blue-900/50 border-2 border-yellow-400/30">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-yellow-400" />
            <h3 className="text-lg font-bold text-yellow-400">AI Auto-Play</h3>
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
            className="text-gray-400 hover:text-yellow-400"
          >
            <Settings className="w-4 h-4" />
          </Button>
        </div>

        {/* Auto-play Controls */}
        <div className="flex items-center space-x-2">
          <Button
            onClick={startAutoPlay}
            disabled={isAutoPlaying || disabled || currentBetAmount > balance}
            className="bg-green-600 hover:bg-green-500 text-white font-bold flex-1"
          >
            <Play className="w-4 h-4 mr-2" />
            Start Auto-Play
          </Button>
          <Button
            onClick={stopAutoPlay}
            disabled={!isAutoPlaying}
            className="bg-red-600 hover:bg-red-500 text-white font-bold flex-1"
          >
            <Square className="w-4 h-4 mr-2" />
            Stop
          </Button>
        </div>

        {/* Basic Settings */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-gray-300">Base Bet</label>
            <Input
              type="number"
              value={autoPlayConfig.baseBetAmount}
              onChange={(e) => {
                const value = Math.min(Math.max(Number(e.target.value), minBet), maxBet);
                setAutoPlayConfig(prev => ({ ...prev, baseBetAmount: value }));
                if (!isAutoPlaying) setCurrentBetAmount(value);
              }}
              min={minBet}
              max={maxBet}
              className="bg-gray-800 border-gray-700 text-white"
              disabled={isAutoPlaying}
            />
          </div>
          <div>
            <label className="text-sm text-gray-300">Number of Bets</label>
            <Input
              type="number"
              value={autoPlayConfig.numberOfBets}
              onChange={(e) => setAutoPlayConfig(prev => ({ 
                ...prev, 
                numberOfBets: Math.max(1, Number(e.target.value)) 
              }))}
              min="1"
              className="bg-gray-800 border-gray-700 text-white"
              disabled={isAutoPlaying}
            />
          </div>
        </div>

        {/* Strategy Selection */}
        <div>
          <label className="text-sm text-gray-300">Strategy</label>
          <select
            value={autoPlayConfig.strategy}
            onChange={(e) => setAutoPlayConfig(prev => ({ ...prev, strategy: e.target.value }))}
            className="w-full p-2 bg-gray-800 border border-gray-700 text-white rounded"
            disabled={isAutoPlaying}
          >
            <option value="constant">Constant Bet</option>
            <option value="martingale">Martingale (Double on Loss)</option>
            <option value="antiMartingale">Anti-Martingale (Double on Win)</option>
            <option value="fibonacci">Fibonacci Sequence</option>
            <option value="customPattern">Custom Pattern</option>
          </select>
        </div>

        {/* Advanced Settings */}
        {showAdvancedSettings && (
          <div className="space-y-4 border-t border-gray-700 pt-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-gray-300">Max Loss</label>
                <Input
                  type="number"
                  value={autoPlayConfig.maxLoss}
                  onChange={(e) => setAutoPlayConfig(prev => ({ 
                    ...prev, 
                    maxLoss: Math.max(0, Number(e.target.value)) 
                  }))}
                  className="bg-gray-800 border-gray-700 text-white"
                  disabled={isAutoPlaying}
                />
              </div>
              <div>
                <label className="text-sm text-gray-300">Target Profit</label>
                <Input
                  type="number" 
                  value={autoPlayConfig.targetProfit}
                  onChange={(e) => setAutoPlayConfig(prev => ({ 
                    ...prev, 
                    targetProfit: Math.max(0, Number(e.target.value)) 
                  }))}
                  className="bg-gray-800 border-gray-700 text-white"
                  disabled={isAutoPlaying}
                />
              </div>
            </div>

            {autoPlayConfig.strategy === 'customPattern' && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-gray-300">On Win</label>
                  <select
                    value={autoPlayConfig.onWinAction}
                    onChange={(e) => setAutoPlayConfig(prev => ({ ...prev, onWinAction: e.target.value }))}
                    className="w-full p-2 bg-gray-800 border border-gray-700 text-white rounded"
                    disabled={isAutoPlaying}
                  >
                    <option value="reset">Reset to Base</option>
                    <option value="increase">Increase Bet</option>
                    <option value="decrease">Decrease Bet</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm text-gray-300">On Loss</label>
                  <select
                    value={autoPlayConfig.onLossAction}
                    onChange={(e) => setAutoPlayConfig(prev => ({ ...prev, onLossAction: e.target.value }))}
                    className="w-full p-2 bg-gray-800 border border-gray-700 text-white rounded"
                    disabled={isAutoPlaying}
                  >
                    <option value="reset">Reset to Base</option>
                    <option value="increase">Increase Bet</option>
                    <option value="decrease">Decrease Bet</option>
                  </select>
                </div>
              </div>
            )}

            <div>
              <label className="text-sm text-gray-300">
                Delay Between Bets: {autoPlayConfig.delayBetweenBets}ms
              </label>
              <Slider
                value={[autoPlayConfig.delayBetweenBets]}
                onValueChange={(value) => setAutoPlayConfig(prev => ({ 
                  ...prev, 
                  delayBetweenBets: value[0] 
                }))}
                max={5000}
                min={500}
                step={250}
                className="w-full"
                disabled={isAutoPlaying}
              />
            </div>
          </div>
        )}

        {/* Auto-play Stats */}
        {isAutoPlaying && (
          <div className="bg-gray-800/50 p-3 rounded space-y-2">
            <h4 className="text-yellow-400 font-bold">Live Stats</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-300">Bets:</span>
                <span className="text-white">{autoPlayStats.betsPlaced}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Next Bet:</span>
                <span className="text-yellow-400">{currentBetAmount.toFixed(2)} CRT</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Profit:</span>
                <span className={autoPlayStats.netProfit >= 0 ? 'text-green-400' : 'text-red-400'}>
                  {autoPlayStats.netProfit >= 0 ? '+' : ''}{autoPlayStats.netProfit.toFixed(2)} CRT
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-300">Streak:</span>
                <span className={autoPlayStats.currentStreak >= 0 ? 'text-green-400' : 'text-red-400'}>
                  {autoPlayStats.currentStreak >= 0 ? '+' : ''}{autoPlayStats.currentStreak}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Status Indicator */}
        <div className="flex items-center justify-center">
          <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-bold ${
            isAutoPlaying 
              ? 'bg-green-600/20 text-green-400 border border-green-600/50' 
              : 'bg-gray-600/20 text-gray-400 border border-gray-600/50'
          }`}>
            {isAutoPlaying ? (
              <>
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                AI Playing...
              </>
            ) : (
              <>
                <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                Ready to Play
              </>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default AutoPlayPanel;