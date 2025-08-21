import React, { useState } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import CasinoGameLayout, { BettingPanel, useWallet, CRTCoin } from './CasinoGameLayout';
import { useToast } from '../../hooks/use-toast';

const Keno = ({ onBack }) => {
  const [selectedNumbers, setSelectedNumbers] = useState([]);
  const [drawnNumbers, setDrawnNumbers] = useState([]);
  const [drawing, setDrawing] = useState(false);
  const [gameResult, setGameResult] = useState(null);
  const [stats, setStats] = useState({
    totalBets: 0,
    totalWon: 0,
    totalLost: 0,
    winRate: 0
  });

  const { updateBalance } = useWallet();
  const { toast } = useToast();

  const totalNumbers = 80;
  const maxSelection = 10;
  const drawCount = 20;

  // Keno payout table based on numbers selected and hits
  const payoutTable = {
    1: { 1: 3 },
    2: { 2: 12 },
    3: { 2: 1, 3: 42 },
    4: { 2: 1, 3: 4, 4: 108 },
    5: { 3: 1, 4: 12, 5: 810 },
    6: { 3: 1, 4: 3, 5: 36, 6: 1800 },
    7: { 3: 1, 4: 2, 5: 20, 6: 400, 7: 7000 },
    8: { 4: 1, 5: 12, 6: 98, 7: 1652, 8: 10000 },
    9: { 4: 1, 5: 4, 6: 44, 7: 335, 8: 4700, 9: 10000 },
    10: { 5: 2, 6: 24, 7: 142, 8: 1000, 9: 4500, 10: 10000 }
  };

  const toggleNumber = (number) => {
    if (drawing) return;
    
    if (selectedNumbers.includes(number)) {
      setSelectedNumbers(selectedNumbers.filter(n => n !== number));
    } else if (selectedNumbers.length < maxSelection) {
      setSelectedNumbers([...selectedNumbers, number]);
    }
  };

  const drawNumbers = async (betAmount) => {
    if (drawing || selectedNumbers.length === 0) return;
    
    setDrawing(true);
    updateBalance(-betAmount);
    setDrawnNumbers([]);
    setGameResult(null);

    // Animate number drawing
    const drawn = [];
    const availableNumbers = Array.from({ length: totalNumbers }, (_, i) => i + 1);
    
    for (let i = 0; i < drawCount; i++) {
      await new Promise(resolve => setTimeout(resolve, 150));
      
      const randomIndex = Math.floor(Math.random() * availableNumbers.length);
      const drawnNumber = availableNumbers.splice(randomIndex, 1)[0];
      drawn.push(drawnNumber);
      
      setDrawnNumbers([...drawn]);
    }

    // Calculate results
    const hits = selectedNumbers.filter(num => drawn.includes(num)).length;
    const selectedCount = selectedNumbers.length;
    const payout = payoutTable[selectedCount]?.[hits] || 0;
    const winAmount = betAmount * payout;

    setGameResult({
      hits,
      selectedCount,
      payout,
      winAmount,
      matchedNumbers: selectedNumbers.filter(num => drawn.includes(num))
    });

    if (winAmount > 0) {
      updateBalance(winAmount);
      toast({
        title: "🎉 Keno Win!",
        description: `${hits}/${selectedCount} hits! Won ${winAmount.toFixed(2)} CRT`,
      });
      
      setStats(prev => ({
        totalBets: prev.totalBets + 1,
        totalWon: prev.totalWon + winAmount,
        totalLost: prev.totalLost,
        winRate: ((prev.totalWon + winAmount) / ((prev.totalBets + 1) * 10) * 100)
      }));
    } else {
      toast({
        title: "Better luck next time",
        description: `${hits}/${selectedCount} hits - No payout`,
      });
      
      setStats(prev => ({
        totalBets: prev.totalBets + 1,
        totalWon: prev.totalWon,
        totalLost: prev.totalLost + betAmount,
        winRate: (prev.totalWon / ((prev.totalBets + 1) * 10) * 100)
      }));
    }

    setDrawing(false);
  };

  const clearNumbers = () => {
    if (drawing) return;
    setSelectedNumbers([]);
  };

  const quickPick = () => {
    if (drawing) return;
    const numbers = [];
    const available = Array.from({ length: totalNumbers }, (_, i) => i + 1);
    
    for (let i = 0; i < Math.min(8, maxSelection); i++) {
      const randomIndex = Math.floor(Math.random() * available.length);
      numbers.push(available.splice(randomIndex, 1)[0]);
    }
    
    setSelectedNumbers(numbers.sort((a, b) => a - b));
  };

  const getNumberClass = (number) => {
    const isSelected = selectedNumbers.includes(number);
    const isDrawn = drawnNumbers.includes(number);
    const isMatched = gameResult?.matchedNumbers.includes(number);
    
    if (isMatched) {
      return 'bg-green-500 text-white border-green-400 animate-pulse';
    } else if (isSelected && isDrawn) {
      return 'bg-green-600 text-white border-green-400';
    } else if (isSelected) {
      return 'bg-yellow-500 text-black border-yellow-400';
    } else if (isDrawn) {
      return 'bg-blue-500 text-white border-blue-400';
    }
    
    return 'bg-gray-700 text-gray-300 border-gray-600 hover:bg-gray-600 hover:border-yellow-400';
  };

  return (
    <CasinoGameLayout title="Keno" onBack={onBack} stats={stats}>
      <div className="space-y-6">
        {/* Game Status */}
        <Card className="p-6 bg-gradient-to-br from-purple-900 to-blue-900 border-2 border-yellow-400/30">
          <div className="text-center mb-6">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <CRTCoin size="w-8 h-8" />
              <h2 className="text-2xl font-bold text-yellow-400">KENO</h2>
              <CRTCoin size="w-8 h-8" />
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-800/50 p-3 rounded">
                <div className="text-sm text-gray-400">Selected</div>
                <div className="text-xl font-bold text-yellow-400">{selectedNumbers.length}/{maxSelection}</div>
              </div>
              <div className="bg-gray-800/50 p-3 rounded">
                <div className="text-sm text-gray-400">Drawn</div>
                <div className="text-xl font-bold text-blue-400">{drawnNumbers.length}/{drawCount}</div>
              </div>
              <div className="bg-gray-800/50 p-3 rounded">
                <div className="text-sm text-gray-400">Hits</div>
                <div className="text-xl font-bold text-green-400">
                  {gameResult ? `${gameResult.hits}/${gameResult.selectedCount}` : '-'}
                </div>
              </div>
              <div className="bg-gray-800/50 p-3 rounded">
                <div className="text-sm text-gray-400">Payout</div>
                <div className="text-xl font-bold text-green-400">
                  {gameResult ? `${gameResult.payout}x` : '-'}
                </div>
              </div>
            </div>
          </div>

          {/* Number Grid */}
          <div className="mb-6">
            <h3 className="text-lg font-bold text-yellow-400 mb-4 text-center">Select Your Numbers (1-{totalNumbers})</h3>
            <div className="grid grid-cols-10 gap-2 max-w-4xl mx-auto">
              {Array.from({ length: totalNumbers }, (_, i) => i + 1).map(number => (
                <Button
                  key={number}
                  onClick={() => toggleNumber(number)}
                  disabled={drawing}
                  className={`
                    aspect-square text-sm font-bold border-2 transition-all duration-200
                    ${getNumberClass(number)}
                    ${drawing ? 'cursor-not-allowed' : 'cursor-pointer'}
                  `}
                >
                  {number}
                </Button>
              ))}
            </div>
          </div>

          {/* Controls */}
          <div className="flex justify-center space-x-4 mb-4">
            <Button
              onClick={clearNumbers}
              disabled={drawing || selectedNumbers.length === 0}
              variant="outline"
              className="border-red-500 text-red-500 hover:bg-red-500/10"
            >
              Clear All
            </Button>
            <Button
              onClick={quickPick}
              disabled={drawing}
              variant="outline"
              className="border-blue-500 text-blue-500 hover:bg-blue-500/10"
            >
              Quick Pick
            </Button>
          </div>

          {/* Game Result */}
          {gameResult && (
            <div className="text-center p-4 bg-gray-800/50 rounded-lg">
              <div className="text-2xl font-bold mb-2">
                {gameResult.winAmount > 0 ? (
                  <span className="text-green-400">🎉 WIN: {gameResult.winAmount.toFixed(2)} CRT!</span>
                ) : (
                  <span className="text-red-400">No Win This Round</span>
                )}
              </div>
              <div className="text-sm text-gray-300">
                Matched Numbers: {gameResult.matchedNumbers.join(', ') || 'None'}
              </div>
            </div>
          )}

          {/* Legend */}
          <div className="flex justify-center space-x-6 text-sm mt-4">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-yellow-500 rounded border border-yellow-400"></div>
              <span className="text-gray-300">Selected</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-blue-500 rounded border border-blue-400"></div>
              <span className="text-gray-300">Drawn</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-green-500 rounded border border-green-400"></div>
              <span className="text-gray-300">Match</span>
            </div>
          </div>
        </Card>

        {/* Payout Table */}
        <Card className="p-4 bg-gray-900/50 border-yellow-400/20">
          <h3 className="text-lg font-bold text-yellow-400 mb-4">Payout Table</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-xs">
            {Object.entries(payoutTable).map(([selected, payouts]) => (
              <div key={selected} className="bg-gray-800 p-3 rounded">
                <div className="text-yellow-400 font-bold mb-2">{selected} Picks</div>
                {Object.entries(payouts).map(([hits, payout]) => (
                  <div key={hits} className="flex justify-between">
                    <span className="text-gray-300">{hits} hits:</span>
                    <span className="text-green-400">{payout}x</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </Card>

        {/* Betting Panel */}
        <BettingPanel
          onBet={drawNumbers}
          minBet={1}
          maxBet={100}
          disabled={drawing || selectedNumbers.length === 0}
          gameActive={drawing}
        />

        {/* Game Rules */}
        <Card className="p-4 bg-gray-900/50 border-yellow-400/20">
          <h3 className="text-lg font-bold text-yellow-400 mb-2">How to Play Keno</h3>
          <ul className="text-sm text-gray-300 space-y-1">
            <li>• Select 1-10 numbers from 1-80</li>
            <li>• 20 numbers will be drawn randomly</li>
            <li>• Payouts based on how many of your numbers match</li>
            <li>• More selections = higher potential payouts</li>
            <li>• Use Quick Pick for random selection</li>
          </ul>
        </Card>
      </div>
    </CasinoGameLayout>
  );
};

export default Keno;