import React, { useState, useEffect } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import CasinoGameLayout, { BettingPanel, useWallet, CRTCoin } from './CasinoGameLayout';
import { useToast } from '../../hooks/use-toast';

const SlotMachine = ({ onBack }) => {
  const [reels, setReels] = useState([['🍒', '🍋', '🍊'], ['🍒', '🍋', '🍊'], ['🍒', '🍋', '🍊']]);
  const [spinning, setSpinning] = useState(false);
  const [lastWin, setLastWin] = useState(0);
  const [stats, setStats] = useState({
    totalBets: 0,
    totalWon: 0,
    totalLost: 0,
    winRate: 0
  });
  
  const { balance, placeBet, refreshBalance } = useWallet();
  const { toast } = useToast();

  const symbols = ['🍒', '🍋', '🍊', '🍇', '🔔', '💎', '⭐', '🍀'];
  const payouts = {
    '💎💎💎': 50,
    '⭐⭐⭐': 25,
    '🔔🔔🔔': 15,
    '🍀🍀🍀': 12,
    '🍇🍇🍇': 8,
    '🍊🍊🍊': 6,
    '🍋🍋🍋': 4,
    '🍒🍒🍒': 3,
    // Two of a kind
    '💎💎': 5,
    '⭐⭐': 3,
    '🔔🔔': 2
  };

  const spinReel = () => {
    const newSymbols = [];
    for (let i = 0; i < 3; i++) {
      newSymbols.push(symbols[Math.floor(Math.random() * symbols.length)]);
    }
    return newSymbols;
  };

  const checkWin = (reelResult) => {
    const line = reelResult.map(reel => reel[1]).join(''); // Middle line
    
    // Check for exact match
    if (payouts[line]) {
      return payouts[line];
    }
    
    // Check for two of a kind
    const symbols = line.split('');
    const counts = {};
    symbols.forEach(symbol => {
      counts[symbol] = (counts[symbol] || 0) + 1;
    });
    
    for (const [symbol, count] of Object.entries(counts)) {
      if (count >= 2 && payouts[symbol.repeat(2)]) {
        return payouts[symbol.repeat(2)];
      }
    }
    
    return 0;
  };

  const handleSpin = async (betAmount) => {
    if (spinning || betAmount > balance) return;
    
    setSpinning(true);
    
    try {
      // Place real bet through backend API
      const betResult = await placeBet('Slot Machine', betAmount);
      
      if (!betResult.success) {
        toast({
          title: "❌ Bet Failed",
          description: betResult.error || "Could not place bet",
          variant: "destructive"
        });
        setSpinning(false);
        return;
      }
      
      // Animate spinning
      const spinDuration = 2000;
      const spinInterval = 100;
      const spins = spinDuration / spinInterval;
      
      let currentSpin = 0;
      const spinAnimation = setInterval(() => {
        setReels([spinReel(), spinReel(), spinReel()]);
        currentSpin++;
        
        if (currentSpin >= spins) {
          clearInterval(spinAnimation);
          
          // Final result - use backend result
          const finalReels = [spinReel(), spinReel(), spinReel()];
          setReels(finalReels);
          
          const isWin = betResult.result === 'win';
          const payout = betResult.payout || 0;
          
          if (isWin && payout > 0) {
            setLastWin(payout);
            toast({
              title: "🎉 Winner!",
              description: `You won ${payout.toFixed(2)} CRT!`,
              duration: 5000
            });
            
            setStats(prev => ({
              totalBets: prev.totalBets + 1,
              totalWon: prev.totalWon + payout,
              totalLost: prev.totalLost,
              winRate: ((prev.totalWon + payout) / ((prev.totalWon + payout) + prev.totalLost) * 100)
            }));
          } else {
            // Loss - show savings message
            const savingsAdded = betResult.savings_contribution || betAmount;
            const liquidityAdded = betResult.liquidity_added || 0;
            
            toast({
              title: "💰 Saved to Vault!",
              description: `Lost ${betAmount} CRT but saved ${savingsAdded.toFixed(2)} CRT to your vault! (+${liquidityAdded.toFixed(2)} to liquidity)`,
              duration: 5000
            });
            
            setStats(prev => ({
              totalBets: prev.totalBets + 1,
              totalWon: prev.totalWon,
              totalLost: prev.totalLost + betAmount,
              winRate: prev.totalWon / (prev.totalWon + prev.totalLost + betAmount) * 100
            }));
          }
          
          setSpinning(false);
        }
      }, spinInterval);
      
    } catch (error) {
      console.error('Error in handleSpin:', error);
      toast({
        title: "❌ Error",
        description: "Failed to place bet. Please try again.",
        variant: "destructive"
      });
      setSpinning(false);
    }
  };

  return (
    <CasinoGameLayout title="Slot Machine" onBack={onBack} stats={stats}>
      <div className="space-y-6">
        {/* Slot Machine */}
        <Card className="p-8 bg-gradient-to-b from-gray-800 to-gray-900 border-2 border-yellow-400/30">
          <div className="text-center mb-6">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <CRTCoin size="w-8 h-8" />
              <h2 className="text-2xl font-bold text-yellow-400">CRT SLOTS</h2>
              <CRTCoin size="w-8 h-8" />
            </div>
            
            {/* Slot Display */}
            <div className="bg-black/50 p-6 rounded-lg border-2 border-yellow-400/50 mb-6">
              <div className="grid grid-cols-3 gap-4 mb-4">
                {reels.map((reel, reelIndex) => (
                  <div key={reelIndex} className="space-y-2">
                    {reel.map((symbol, symbolIndex) => (
                      <div
                        key={symbolIndex}
                        className={`
                          w-20 h-20 flex items-center justify-center text-4xl
                          bg-gradient-to-br from-gray-700 to-gray-800 rounded-lg border-2
                          ${symbolIndex === 1 ? 'border-yellow-400 shadow-lg shadow-yellow-400/50' : 'border-gray-600'}
                          ${spinning ? 'animate-pulse' : ''}
                        `}
                      >
                        {symbol}
                      </div>
                    ))}
                  </div>
                ))}
              </div>
              
              {/* Payline indicator */}
              <div className="text-yellow-400 text-sm">
                ← PAYLINE →
              </div>
            </div>

            {lastWin > 0 && (
              <div className="text-center mb-4">
                <div className="text-3xl font-bold text-green-400 animate-pulse">
                  🎉 WIN: {lastWin.toFixed(2)} CRT! 🎉
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Paytable */}
        <Card className="p-4 bg-gray-900/50 border-yellow-400/20">
          <h3 className="text-lg font-bold text-yellow-400 mb-4">Paytable (Multipliers)</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
            <div className="text-center p-2 bg-gray-800 rounded">
              <div className="text-lg">💎💎💎</div>
              <div className="text-yellow-400">50x</div>
            </div>
            <div className="text-center p-2 bg-gray-800 rounded">
              <div className="text-lg">⭐⭐⭐</div>
              <div className="text-yellow-400">25x</div>
            </div>
            <div className="text-center p-2 bg-gray-800 rounded">
              <div className="text-lg">🔔🔔🔔</div>
              <div className="text-yellow-400">15x</div>
            </div>
            <div className="text-center p-2 bg-gray-800 rounded">
              <div className="text-lg">🍀🍀🍀</div>
              <div className="text-yellow-400">12x</div>
            </div>
            <div className="text-center p-2 bg-gray-800 rounded">
              <div className="text-lg">🍇🍇🍇</div>
              <div className="text-yellow-400">8x</div>
            </div>
            <div className="text-center p-2 bg-gray-800 rounded">
              <div className="text-lg">🍊🍊🍊</div>
              <div className="text-yellow-400">6x</div>
            </div>
            <div className="text-center p-2 bg-gray-800 rounded">
              <div className="text-lg">🍋🍋🍋</div>
              <div className="text-yellow-400">4x</div>
            </div>
            <div className="text-center p-2 bg-gray-800 rounded">
              <div className="text-lg">🍒🍒🍒</div>
              <div className="text-yellow-400">3x</div>
            </div>
          </div>
        </Card>

        {/* Betting Panel */}
        <BettingPanel
          onBet={handleSpin}
          minBet={1}
          maxBet={100}
          disabled={spinning}
          gameActive={spinning}
        />
      </div>
    </CasinoGameLayout>
  );
};

export default SlotMachine;