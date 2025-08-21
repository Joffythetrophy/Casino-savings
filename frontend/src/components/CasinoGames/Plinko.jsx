import React, { useState, useRef, useEffect } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import CasinoGameLayout, { BettingPanel, useWallet, CRTCoin } from './CasinoGameLayout';
import { useToast } from '../../hooks/use-toast';

const Plinko = ({ onBack }) => {
  const [dropping, setDropping] = useState(false);
  const [balls, setBalls] = useState([]);
  const [lastMultiplier, setLastMultiplier] = useState(null);
  const [stats, setStats] = useState({
    totalBets: 0,
    totalWon: 0,
    totalLost: 0,
    winRate: 0
  });

  const { updateBalance } = useWallet();
  const { toast } = useToast();

  // Plinko multipliers (16 slots)
  const multipliers = [1000, 130, 26, 9, 4, 2, 1.5, 1, 0.5, 1, 1.5, 2, 4, 9, 26, 130, 1000];
  const rows = 16;

  const dropBall = async (betAmount) => {
    if (dropping) return;
    
    setDropping(true);
    updateBalance(-betAmount);

    // Simulate ball physics
    let position = 8; // Start in middle (0-15)
    
    // Ball path simulation
    const ballPath = [position];
    for (let row = 0; row < rows; row++) {
      // Random left or right with slight center bias
      const direction = Math.random() > 0.5 ? 1 : -1;
      position = Math.max(0, Math.min(15, position + direction));
      ballPath.push(position);
    }

    // Animate ball drop
    const newBall = {
      id: Date.now(),
      path: ballPath,
      currentRow: 0,
      finalSlot: position
    };

    setBalls(prev => [...prev, newBall]);

    // Animate ball movement
    let currentRow = 0;
    const animationInterval = setInterval(() => {
      currentRow++;
      setBalls(prev => 
        prev.map(ball => 
          ball.id === newBall.id 
            ? { ...ball, currentRow }
            : ball
        )
      );

      if (currentRow >= rows) {
        clearInterval(animationInterval);
        
        // Calculate win
        const multiplier = multipliers[position];
        const winAmount = betAmount * multiplier;
        setLastMultiplier(multiplier);

        if (multiplier >= 1) {
          updateBalance(winAmount);
          toast({
            title: multiplier > 1 ? "🎉 Big Win!" : "💰 Win!",
            description: `Hit ${multiplier}x multiplier! Won ${winAmount.toFixed(2)} CRT`,
          });
          
          setStats(prev => ({
            totalBets: prev.totalBets + 1,
            totalWon: prev.totalWon + winAmount,
            totalLost: prev.totalLost,
            winRate: ((prev.totalWon + winAmount) / ((prev.totalBets + 1) * 10) * 100)
          }));
        } else {
          toast({
            title: "💔 Close!",
            description: `Hit ${multiplier}x - Lost ${betAmount.toFixed(2)} CRT`,
          });
          
          setStats(prev => ({
            totalBets: prev.totalBets + 1,
            totalWon: prev.totalWon,
            totalLost: prev.totalLost + betAmount,
            winRate: (prev.totalWon / ((prev.totalBets + 1) * 10) * 100)
          }));
        }

        // Clean up ball after delay
        setTimeout(() => {
          setBalls(prev => prev.filter(ball => ball.id !== newBall.id));
          setDropping(false);
        }, 1500);
      }
    }, 100);
  };

  const getMultiplierColor = (multiplier) => {
    if (multiplier >= 100) return 'bg-gradient-to-t from-purple-600 to-purple-400 text-white';
    if (multiplier >= 10) return 'bg-gradient-to-t from-red-600 to-red-400 text-white';
    if (multiplier >= 2) return 'bg-gradient-to-t from-orange-600 to-orange-400 text-white';
    if (multiplier >= 1) return 'bg-gradient-to-t from-green-600 to-green-400 text-white';
    return 'bg-gradient-to-t from-gray-600 to-gray-400 text-white';
  };

  return (
    <CasinoGameLayout title="Plinko" onBack={onBack} stats={stats}>
      <div className="space-y-6">
        {/* Plinko Board */}
        <Card className="p-6 bg-gradient-to-b from-blue-900 to-indigo-900 border-2 border-yellow-400/30 overflow-hidden">
          <div className="text-center mb-4">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <CRTCoin size="w-8 h-8" />
              <h2 className="text-2xl font-bold text-yellow-400">PLINKO</h2>
              <CRTCoin size="w-8 h-8" />
            </div>
          </div>

          {/* Plinko Board */}
          <div className="relative bg-black/30 rounded-lg p-4 max-w-2xl mx-auto">
            {/* Pegs */}
            <div className="relative" style={{ height: '400px' }}>
              {Array.from({ length: rows }, (_, row) => (
                <div
                  key={row}
                  className="absolute w-full flex justify-center"
                  style={{ 
                    top: `${(row * 24) + 20}px`,
                    left: `${row % 2 === 0 ? 0 : 15}px`
                  }}
                >
                  {Array.from({ length: row + 2 }, (_, peg) => (
                    <div
                      key={peg}
                      className="w-3 h-3 bg-white rounded-full mx-3 shadow-lg"
                    />
                  ))}
                </div>
              ))}

              {/* Balls */}
              {balls.map(ball => {
                const row = Math.min(ball.currentRow, rows - 1);
                const position = ball.path[row];
                const leftOffset = (position * 30) + 30; // Approximate positioning
                const topOffset = (row * 24) + 40;
                
                return (
                  <div
                    key={ball.id}
                    className="absolute w-4 h-4 bg-yellow-400 rounded-full shadow-lg transition-all duration-100"
                    style={{
                      left: `${leftOffset}px`,
                      top: `${topOffset}px`,
                      zIndex: 10
                    }}
                  />
                );
              })}

              {/* Drop indicator */}
              <div className="absolute top-0 left-1/2 transform -translate-x-1/2">
                <div className="w-6 h-6 bg-yellow-400 rounded-full animate-pulse" />
                <div className="text-yellow-400 text-xs mt-1">DROP</div>
              </div>
            </div>

            {/* Multiplier Slots */}
            <div className="grid grid-cols-8 lg:grid-cols-16 gap-1 mt-4">
              {multipliers.map((multiplier, index) => (
                <div
                  key={index}
                  className={`
                    h-12 flex items-center justify-center text-xs font-bold rounded
                    ${getMultiplierColor(multiplier)}
                    ${lastMultiplier === multiplier ? 'animate-pulse ring-2 ring-yellow-400' : ''}
                  `}
                >
                  {multiplier >= 1 ? `${multiplier}x` : `${multiplier}x`}
                </div>
              ))}
            </div>

            {lastMultiplier !== null && (
              <div className="text-center mt-4">
                <div className={`text-2xl font-bold ${
                  lastMultiplier >= 1 ? 'text-green-400' : 'text-red-400'
                }`}>
                  Hit {lastMultiplier}x Multiplier!
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Betting Panel */}
        <BettingPanel
          onBet={dropBall}
          minBet={1}
          maxBet={50}
          disabled={dropping}
          gameActive={dropping}
        />

        {/* Multiplier Legend */}
        <Card className="p-4 bg-gray-900/50 border-yellow-400/20">
          <h3 className="text-lg font-bold text-yellow-400 mb-4">Multiplier Values</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-t from-purple-600 to-purple-400 rounded"></div>
              <span className="text-purple-400">1000x - Jackpot!</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-t from-red-600 to-red-400 rounded"></div>
              <span className="text-red-400">9x-130x - Big Win</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-t from-orange-600 to-orange-400 rounded"></div>
              <span className="text-orange-400">2x-4x - Good Win</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-gradient-to-t from-green-600 to-green-400 rounded"></div>
              <span className="text-green-400">1x-1.5x - Small Win</span>
            </div>
          </div>
          
          <div className="mt-4 text-xs text-gray-400">
            <p>• Ball drops from center and bounces off pegs randomly</p>
            <p>• Edge slots have higher multipliers but lower probability</p>
            <p>• Center slots are more likely but lower multipliers</p>
          </div>
        </Card>
      </div>
    </CasinoGameLayout>
  );
};

export default Plinko;