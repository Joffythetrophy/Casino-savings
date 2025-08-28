import React, { useState, useEffect } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import CasinoGameLayout, { BettingPanel, useWallet, CRTCoin } from './CasinoGameLayout';
import AutoPlayPanel from './AutoPlayPanel';
import { useToast } from '../../hooks/use-toast';

const Roulette = ({ onBack }) => {
  const [spinning, setSpinning] = useState(false);
  const [currentNumber, setCurrentNumber] = useState(null);
  const [bets, setBets] = useState({});
  const [wheelRotation, setWheelRotation] = useState(0);
  const [stats, setStats] = useState({
    totalBets: 0,
    totalWon: 0,
    totalLost: 0,
    winRate: 0
  });

  const { updateBalance } = useWallet();
  const { toast } = useToast();

  // Roulette numbers in order on wheel
  const wheelNumbers = [
    0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5,
    24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26
  ];

  const redNumbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36];
  const blackNumbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35];

  const getNumberColor = (num) => {
    if (num === 0) return 'green';
    return redNumbers.includes(num) ? 'red' : 'black';
  };

  const payouts = {
    straight: 35,
    red: 1,
    black: 1,
    odd: 1,
    even: 1,
    low: 1, // 1-18
    high: 1, // 19-36
    dozen1: 2, // 1-12
    dozen2: 2, // 13-24
    dozen3: 2, // 25-36
  };

  const checkWins = (winningNumber) => {
    let totalWin = 0;
    const winningBets = [];

    Object.entries(bets).forEach(([betType, amount]) => {
      let won = false;
      let payout = 0;

      switch (betType) {
        case `straight_${winningNumber}`:
          won = true;
          payout = payouts.straight;
          break;
        case 'red':
          won = redNumbers.includes(winningNumber);
          payout = payouts.red;
          break;
        case 'black':
          won = blackNumbers.includes(winningNumber);
          payout = payouts.black;
          break;
        case 'odd':
          won = winningNumber > 0 && winningNumber % 2 === 1;
          payout = payouts.odd;
          break;
        case 'even':
          won = winningNumber > 0 && winningNumber % 2 === 0;
          payout = payouts.even;
          break;
        case 'low':
          won = winningNumber >= 1 && winningNumber <= 18;
          payout = payouts.low;
          break;
        case 'high':
          won = winningNumber >= 19 && winningNumber <= 36;
          payout = payouts.high;
          break;
        case 'dozen1':
          won = winningNumber >= 1 && winningNumber <= 12;
          payout = payouts.dozen1;
          break;
        case 'dozen2':
          won = winningNumber >= 13 && winningNumber <= 24;
          payout = payouts.dozen2;
          break;
        case 'dozen3':
          won = winningNumber >= 25 && winningNumber <= 36;
          payout = payouts.dozen3;
          break;
      }

      if (won) {
        const winAmount = amount * (payout + 1);
        totalWin += winAmount;
        winningBets.push({ betType, amount, winAmount });
      }
    });

    return { totalWin, winningBets };
  };

  const spinWheel = async () => {
    if (spinning || Object.keys(bets).length === 0) return;

    setSpinning(true);
    
    // Calculate total bet amount
    const totalBetAmount = Object.values(bets).reduce((sum, amount) => sum + amount, 0);
    updateBalance(-totalBetAmount);

    // Spin animation
    const spins = 5 + Math.random() * 5;
    const finalRotation = wheelRotation + (spins * 360);
    setWheelRotation(finalRotation);

    // Determine winning number
    const winningNumber = wheelNumbers[Math.floor(Math.random() * wheelNumbers.length)];
    
    setTimeout(() => {
      setCurrentNumber(winningNumber);
      
      const { totalWin, winningBets } = checkWins(winningNumber);
      
      if (totalWin > 0) {
        updateBalance(totalWin);
        toast({
          title: "🎉 Winner!",
          description: `Number ${winningNumber} (${getNumberColor(winningNumber)}) - Won ${totalWin.toFixed(2)} CRT!`,
        });
        
        setStats(prev => ({
          totalBets: prev.totalBets + 1,
          totalWon: prev.totalWon + totalWin,
          totalLost: prev.totalLost,
          winRate: ((prev.totalWon + totalWin) / ((prev.totalBets + 1) * 10) * 100)
        }));
      } else {
        toast({
          title: "House wins",
          description: `Number ${winningNumber} (${getNumberColor(winningNumber)}) - Better luck next time!`,
        });
        
        setStats(prev => ({
          totalBets: prev.totalBets + 1,
          totalWon: prev.totalWon,
          totalLost: prev.totalLost + totalBetAmount,
          winRate: (prev.totalWon / ((prev.totalBets + 1) * 10) * 100)
        }));
      }
      
      setBets({});
      setSpinning(false);
    }, 3000);
  };

  const placeBet = (betType, amount) => {
    setBets(prev => {
      const newBets = {
        ...prev,
        [betType]: (prev[betType] || 0) + amount
      };
      setLastBet(newBets);
      return newBets;
    });
  };

  const clearBets = () => {
    setBets({});
  };

  const [autoPlaySettings, setAutoPlaySettings] = useState({
    autoBetType: 'red',
    isAutoPlaying: false
  });

  const [lastBet, setLastBet] = useState(null);

  // AutoPlay function
  const handleAutoPlay = async (settings) => {
    if (!settings.enabled) {
      setAutoPlaySettings(prev => ({ ...prev, isAutoPlaying: false }));
      return;
    }

    setAutoPlaySettings(prev => ({ ...prev, isAutoPlaying: true }));
    
    try {
      // Clear current bets and place auto bet
      setBets({});
      const newBets = { [autoPlaySettings.autoBetType]: settings.betAmount };
      setBets(newBets);
      setLastBet(newBets);
      
      // Trigger spin automatically
      setTimeout(() => {
        if (autoPlaySettings.isAutoPlaying) {
          spinWheel();
        }
      }, 100);
      
    } catch (error) {
      console.error('AutoPlay error:', error);
      setAutoPlaySettings(prev => ({ ...prev, isAutoPlaying: false }));
    }
  };

  // Repeat last bet function
  const repeatLastBet = () => {
    if (lastBet && Object.keys(lastBet).length > 0) {
      setBets(lastBet);
      toast({
        title: "Bet Repeated",
        description: "Your previous bet has been placed again!",
        duration: 2000
      });
    } else {
      toast({
        title: "No Previous Bet",
        description: "Place a bet first to use repeat bet feature",
        duration: 2000,
        variant: "destructive"
      });
    }
  };

  return (
    <CasinoGameLayout 
      title="CRT Roulette" 
      onBack={onBack}
      stats={stats}
      rightSidebar={
        <div className="space-y-4">
          {/* Currency & Bet Controls */}
          <div className="bg-gray-800/50 p-4 rounded-lg">
            <h3 className="text-lg font-bold text-yellow-400 mb-3">Quick Actions</h3>
            
            <Button
              onClick={repeatLastBet}
              className="w-full mb-2 bg-blue-600 hover:bg-blue-700 text-white"
              disabled={spinning || !lastBet}
            >
              🔄 Repeat Last Bet
            </Button>
            
            <Button
              onClick={() => setBets({})}
              className="w-full bg-red-600 hover:bg-red-700 text-white"
              disabled={spinning}
            >
              🗑️ Clear All Bets
            </Button>
          </div>

          {/* AutoPlay Panel */}
          <AutoPlayPanel 
            onAutoPlay={handleAutoPlay}
            gameSpecificSettings={
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-300">Auto-Bet Type</label>
                <select 
                  value={autoPlaySettings.autoBetType}
                  onChange={(e) => setAutoPlaySettings(prev => ({ ...prev, autoBetType: e.target.value }))}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                >
                  <option value="red">Red (1:1)</option>
                  <option value="black">Black (1:1)</option>
                  <option value="odd">Odd (1:1)</option>
                  <option value="even">Even (1:1)</option>
                  <option value="low">Low 1-18 (1:1)</option>
                  <option value="high">High 19-36 (1:1)</option>
                </select>
              </div>
            }
          />
        </div>
      }
    >
      <div className="space-y-6">
        {/* Roulette Wheel */}
        <Card className="p-8 bg-gradient-to-br from-green-900 to-green-800 border-2 border-yellow-400/30">
          <div className="text-center">
            <div className="relative w-64 h-64 mx-auto mb-6">
              {/* Wheel */}
              <div 
                className={`w-full h-full rounded-full border-8 border-yellow-400 bg-gradient-to-br from-green-700 to-green-900 relative ${spinning ? 'animate-spin' : ''}`}
                style={{ 
                  transform: `rotate(${wheelRotation}deg)`,
                  transition: spinning ? 'transform 3s cubic-bezier(0.25, 0.46, 0.45, 0.94)' : 'none'
                }}
              >
                {/* Numbers around the wheel */}
                {wheelNumbers.map((num, index) => {
                  const angle = (index * 360) / wheelNumbers.length;
                  const isRed = redNumbers.includes(num);
                  const isBlack = blackNumbers.includes(num);
                  
                  return (
                    <div
                      key={num}
                      className={`absolute w-8 h-8 flex items-center justify-center text-xs font-bold rounded
                        ${num === 0 ? 'bg-green-500 text-white' : ''}
                        ${isRed ? 'bg-red-500 text-white' : ''}
                        ${isBlack ? 'bg-black text-white' : ''}
                      `}
                      style={{
                        transform: `rotate(${angle}deg) translateY(-100px)`,
                        transformOrigin: 'center 100px'
                      }}
                    >
                      {num}
                    </div>
                  );
                })}
                
                {/* Center */}
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center">
                  <CRTCoin size="w-6 h-6" />
                </div>
              </div>
              
              {/* Ball indicator */}
              <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-2 w-4 h-4 bg-white rounded-full border-2 border-gray-800"></div>
            </div>

            {currentNumber !== null && (
              <div className="text-center mb-4">
                <div className={`inline-block px-6 py-3 rounded-lg text-2xl font-bold ${
                  currentNumber === 0 ? 'bg-green-500' : 
                  redNumbers.includes(currentNumber) ? 'bg-red-500' : 'bg-black'
                } text-white`}>
                  {currentNumber}
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Betting Board */}
        <Card className="p-6 bg-gray-900/50 border-yellow-400/20">
          <h3 className="text-lg font-bold text-yellow-400 mb-4">Place Your Bets</h3>
          
          {/* Number Grid */}
          <div className="grid grid-cols-12 gap-1 mb-4">
            {[...Array(36)].map((_, i) => {
              const num = i + 1;
              const isRed = redNumbers.includes(num);
              const betAmount = bets[`straight_${num}`] || 0;
              
              return (
                <Button
                  key={num}
                  onClick={() => placeBet(`straight_${num}`, 5)}
                  className={`h-12 text-white font-bold relative ${
                    isRed ? 'bg-red-600 hover:bg-red-500' : 'bg-gray-800 hover:bg-gray-700'
                  }`}
                  disabled={spinning}
                >
                  {num}
                  {betAmount > 0 && (
                    <div className="absolute -top-1 -right-1 bg-yellow-400 text-black text-xs rounded-full w-5 h-5 flex items-center justify-center">
                      {betAmount}
                    </div>
                  )}
                </Button>
              );
            })}
          </div>

          {/* Outside Bets */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-2 mb-4">
            {[
              { key: 'red', label: 'Red', color: 'bg-red-600' },
              { key: 'black', label: 'Black', color: 'bg-gray-800' },
              { key: 'odd', label: 'Odd', color: 'bg-blue-600' },
              { key: 'even', label: 'Even', color: 'bg-blue-600' },
              { key: 'low', label: '1-18', color: 'bg-purple-600' },
              { key: 'high', label: '19-36', color: 'bg-purple-600' },
            ].map(bet => (
              <Button
                key={bet.key}
                onClick={() => placeBet(bet.key, 5)}
                className={`h-12 text-white font-bold relative ${bet.color} hover:opacity-80`}
                disabled={spinning}
              >
                {bet.label}
                {bets[bet.key] && (
                  <div className="absolute -top-1 -right-1 bg-yellow-400 text-black text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {bets[bet.key]}
                  </div>
                )}
              </Button>
            ))}
          </div>

          {/* Dozens */}
          <div className="grid grid-cols-3 gap-2 mb-4">
            {[
              { key: 'dozen1', label: '1st 12', range: '1-12' },
              { key: 'dozen2', label: '2nd 12', range: '13-24' },
              { key: 'dozen3', label: '3rd 12', range: '25-36' },
            ].map(bet => (
              <Button
                key={bet.key}
                onClick={() => placeBet(bet.key, 5)}
                className="h-12 bg-green-600 hover:bg-green-500 text-white font-bold relative"
                disabled={spinning}
              >
                {bet.label}
                <div className="text-xs">{bet.range}</div>
                {bets[bet.key] && (
                  <div className="absolute -top-1 -right-1 bg-yellow-400 text-black text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {bets[bet.key]}
                  </div>
                )}
              </Button>
            ))}
          </div>

          {/* Controls */}
          <div className="flex justify-center space-x-4">
            <Button
              onClick={spinWheel}
              disabled={spinning || Object.keys(bets).length === 0}
              className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-black font-bold hover:from-yellow-300 hover:to-yellow-500 px-8 py-3"
            >
              {spinning ? 'Spinning...' : 'SPIN'}
            </Button>
            <Button
              onClick={clearBets}
              disabled={spinning}
              variant="outline"
              className="border-red-500 text-red-500 hover:bg-red-500/10"
            >
              Clear Bets
            </Button>
          </div>

          {/* Current Bets Display */}
          {Object.keys(bets).length > 0 && (
            <div className="mt-4 p-3 bg-gray-800 rounded">
              <div className="text-sm text-gray-300">Current Bets:</div>
              <div className="flex flex-wrap gap-2 mt-2">
                {Object.entries(bets).map(([betType, amount]) => (
                  <span key={betType} className="bg-yellow-400 text-black px-2 py-1 rounded text-xs">
                    {betType.replace('_', ' ')}: {amount} CRT
                  </span>
                ))}
              </div>
              <div className="text-yellow-400 font-bold mt-2">
                Total Bet: {Object.values(bets).reduce((sum, amount) => sum + amount, 0)} CRT
              </div>
            </div>
          )}
        </Card>
      </div>
    </CasinoGameLayout>
  );
};

export default Roulette;