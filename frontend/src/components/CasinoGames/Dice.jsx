import React, { useState } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Slider } from '../ui/slider';
import CasinoGameLayout, { BettingPanel, useWallet, CRTCoin } from './CasinoGameLayout';
import { useToast } from '../hooks/use-toast';

const Dice = ({ onBack }) => {
  const [prediction, setPrediction] = useState(50);
  const [rollOver, setRollOver] = useState(true);
  const [rolling, setRolling] = useState(false);
  const [lastRoll, setLastRoll] = useState(null);
  const [diceAnimation, setDiceAnimation] = useState(false);
  const [stats, setStats] = useState({
    totalBets: 0,
    totalWon: 0,
    totalLost: 0,
    winRate: 0
  });

  const { updateBalance } = useWallet();
  const { toast } = useToast();

  // Calculate win chance and multiplier
  const winChance = rollOver ? (100 - prediction) : prediction;
  const multiplier = winChance > 0 ? (99 / winChance) : 1;

  const rollDice = async (betAmount) => {
    if (rolling) return;
    
    setRolling(true);
    setDiceAnimation(true);
    updateBalance(-betAmount);

    // Simulate rolling animation
    setTimeout(() => {
      const result = Math.floor(Math.random() * 100) + 1;
      setLastRoll(result);
      setDiceAnimation(false);

      // Check win condition
      const isWin = rollOver ? result > prediction : result < prediction;
      
      if (isWin) {
        const winAmount = betAmount * multiplier;
        updateBalance(winAmount);
        toast({
          title: "🎉 You Win!",
          description: `Rolled ${result}! Won ${winAmount.toFixed(2)} CRT`,
        });
        
        setStats(prev => ({
          totalBets: prev.totalBets + 1,
          totalWon: prev.totalWon + winAmount,
          totalLost: prev.totalLost,
          winRate: ((prev.totalWon + winAmount) / ((prev.totalBets + 1) * 10) * 100)
        }));
      } else {
        toast({
          title: "House Wins",
          description: `Rolled ${result}. Better luck next time!`,
        });
        
        setStats(prev => ({
          totalBets: prev.totalBets + 1,
          totalWon: prev.totalWon,
          totalLost: prev.totalLost + betAmount,
          winRate: (prev.totalWon / ((prev.totalBets + 1) * 10) * 100)
        }));
      }
      
      setRolling(false);
    }, 2000);
  };

  const getDiceDisplay = () => {
    if (diceAnimation) {
      return '🎲';
    }
    if (lastRoll !== null) {
      return lastRoll.toString();
    }
    return '?';
  };

  return (
    <CasinoGameLayout title="Dice Game" onBack={onBack} stats={stats}>
      <div className="space-y-6">
        {/* Dice Display */}
        <Card className="p-8 bg-gradient-to-br from-blue-900 to-purple-900 border-2 border-yellow-400/30">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-6">
              <CRTCoin size="w-8 h-8" />
              <h2 className="text-2xl font-bold text-yellow-400">DICE ROLL</h2>
              <CRTCoin size="w-8 h-8" />
            </div>

            {/* Dice */}
            <div className="relative mb-8">
              <div 
                className={`w-32 h-32 mx-auto bg-white rounded-2xl border-4 border-gray-300 shadow-2xl flex items-center justify-center text-4xl font-bold text-gray-800 ${
                  diceAnimation ? 'animate-bounce' : ''
                }`}
              >
                {getDiceDisplay()}
              </div>
              
              {lastRoll !== null && !diceAnimation && (
                <div className="mt-4">
                  <div className={`text-2xl font-bold ${
                    (rollOver && lastRoll > prediction) || (!rollOver && lastRoll < prediction)
                      ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {(rollOver && lastRoll > prediction) || (!rollOver && lastRoll < prediction)
                      ? '🎉 WIN!' : '💔 LOSE'}
                  </div>
                </div>
              )}
            </div>

            {/* Prediction Setup */}
            <div className="space-y-6 max-w-md mx-auto">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-300">Prediction:</span>
                  <Input
                    type="number"
                    value={prediction}
                    onChange={(e) => setPrediction(Math.max(1, Math.min(99, Number(e.target.value))))}
                    min="1"
                    max="99"
                    className="w-20 bg-gray-800 border-gray-700 text-white text-center"
                  />
                </div>
                <Slider
                  value={[prediction]}
                  onValueChange={(value) => setPrediction(value[0])}
                  max={99}
                  min={1}
                  step={1}
                  className="w-full"
                />
              </div>

              <div className="flex justify-center space-x-4">
                <Button
                  onClick={() => setRollOver(false)}
                  className={`px-6 py-3 font-bold ${
                    !rollOver 
                      ? 'bg-green-600 hover:bg-green-500 text-white' 
                      : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                  }`}
                >
                  Roll Under {prediction}
                </Button>
                <Button
                  onClick={() => setRollOver(true)}
                  className={`px-6 py-3 font-bold ${
                    rollOver 
                      ? 'bg-green-600 hover:bg-green-500 text-white' 
                      : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                  }`}
                >
                  Roll Over {prediction}
                </Button>
              </div>

              {/* Game Info */}
              <div className="grid grid-cols-2 gap-4 text-center">
                <div className="bg-gray-800/50 p-3 rounded">
                  <div className="text-sm text-gray-400">Win Chance</div>
                  <div className="text-xl font-bold text-yellow-400">{winChance.toFixed(1)}%</div>
                </div>
                <div className="bg-gray-800/50 p-3 rounded">
                  <div className="text-sm text-gray-400">Multiplier</div>
                  <div className="text-xl font-bold text-green-400">{multiplier.toFixed(2)}x</div>
                </div>
              </div>
            </div>
          </div>
        </Card>

        {/* Betting Panel */}
        <BettingPanel
          onBet={rollDice}
          minBet={1}
          maxBet={100}
          disabled={rolling}
          gameActive={rolling}
        />

        {/* Game Rules */}
        <Card className="p-4 bg-gray-900/50 border-yellow-400/20">
          <h3 className="text-lg font-bold text-yellow-400 mb-2">How to Play</h3>
          <ul className="text-sm text-gray-300 space-y-1">
            <li>• Set your prediction number (1-99)</li>
            <li>• Choose "Roll Over" to win if result > prediction</li>
            <li>• Choose "Roll Under" to win if result &lt; prediction</li>
            <li>• Lower win chance = higher multiplier</li>
            <li>• House edge: 1%</li>
          </ul>
        </Card>
      </div>
    </CasinoGameLayout>
  );
};

export default Dice;