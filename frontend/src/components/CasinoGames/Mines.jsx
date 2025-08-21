import React, { useState, useEffect } from 'react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import CasinoGameLayout, { BettingPanel, useWallet, CRTCoin } from './CasinoGameLayout';
import { useToast } from '../hooks/use-toast';
import { Bomb, Gem } from 'lucide-react';

const Mines = ({ onBack }) => {
  const [mineCount, setMineCount] = useState(5);
  const [gameActive, setGameActive] = useState(false);
  const [board, setBoard] = useState([]);
  const [revealed, setRevealed] = useState([]);
  const [gameOver, setGameOver] = useState(false);
  const [currentMultiplier, setCurrentMultiplier] = useState(1);
  const [betAmount, setBetAmount] = useState(0);
  const [stats, setStats] = useState({
    totalBets: 0,
    totalWon: 0,
    totalLost: 0,
    winRate: 0
  });

  const { updateBalance } = useWallet();
  const { toast } = useToast();

  const boardSize = 25; // 5x5 grid

  useEffect(() => {
    initializeBoard();
  }, [mineCount]);

  const initializeBoard = () => {
    const newBoard = Array(boardSize).fill(false);
    const minePositions = [];
    
    while (minePositions.length < mineCount) {
      const position = Math.floor(Math.random() * boardSize);
      if (!minePositions.includes(position)) {
        minePositions.push(position);
        newBoard[position] = true; // true = mine
      }
    }
    
    setBoard(newBoard);
    setRevealed(Array(boardSize).fill(false));
    setGameOver(false);
    setCurrentMultiplier(1);
  };

  const calculateMultiplier = (gemsFound) => {
    const totalGems = boardSize - mineCount;
    if (gemsFound === 0) return 1;
    
    // Progressive multiplier based on risk
    const baseMultiplier = 1 + (gemsFound * 0.2);
    const riskMultiplier = Math.pow(1.1, gemsFound);
    const mineRiskMultiplier = 1 + (mineCount * 0.05);
    
    return baseMultiplier * riskMultiplier * mineRiskMultiplier;
  };

  const startGame = (amount) => {
    if (gameActive) return;
    
    setBetAmount(amount);
    setGameActive(true);
    updateBalance(-amount);
    initializeBoard();
    
    toast({
      title: "Game Started!",
      description: `Find gems while avoiding ${mineCount} mines`,
    });
  };

  const revealTile = (index) => {
    if (!gameActive || revealed[index] || gameOver) return;
    
    const newRevealed = [...revealed];
    newRevealed[index] = true;
    setRevealed(newRevealed);
    
    if (board[index]) {
      // Hit a mine - game over
      setGameOver(true);
      setGameActive(false);
      
      // Reveal all mines
      const allRevealed = board.map((isMine, idx) => isMine || newRevealed[idx]);
      setRevealed(allRevealed);
      
      toast({
        title: "💣 BOOM!",
        description: `You hit a mine! Lost ${betAmount.toFixed(2)} CRT`,
      });
      
      setStats(prev => ({
        totalBets: prev.totalBets + 1,
        totalWon: prev.totalWon,
        totalLost: prev.totalLost + betAmount,
        winRate: (prev.totalWon / ((prev.totalBets + 1) * 10) * 100)
      }));
    } else {
      // Found a gem
      const gemsFound = newRevealed.filter((revealed, idx) => revealed && !board[idx]).length;
      const newMultiplier = calculateMultiplier(gemsFound);
      setCurrentMultiplier(newMultiplier);
      
      toast({
        title: "💎 Gem Found!",
        description: `Multiplier: ${newMultiplier.toFixed(2)}x`,
      });
    }
  };

  const cashOut = () => {
    if (!gameActive || gameOver) return;
    
    const winAmount = betAmount * currentMultiplier;
    updateBalance(winAmount);
    setGameActive(false);
    
    toast({
      title: "🎉 Cashed Out!",
      description: `Won ${winAmount.toFixed(2)} CRT with ${currentMultiplier.toFixed(2)}x multiplier!`,
    });
    
    setStats(prev => ({
      totalBets: prev.totalBets + 1,
      totalWon: prev.totalWon + winAmount,
      totalLost: prev.totalLost,
      winRate: ((prev.totalWon + winAmount) / ((prev.totalBets + 1) * 10) * 100)
    }));
  };

  const resetGame = () => {
    setGameActive(false);
    setGameOver(false);
    initializeBoard();
  };

  const getTileContent = (index) => {
    if (!revealed[index]) {
      return (
        <div className="w-full h-full bg-gradient-to-br from-gray-600 to-gray-700 rounded border-2 border-gray-500 hover:border-yellow-400 transition-colors cursor-pointer flex items-center justify-center">
          <div className="w-4 h-4 bg-gray-400 rounded-full opacity-50"></div>
        </div>
      );
    }
    
    if (board[index]) {
      return (
        <div className="w-full h-full bg-red-600 rounded border-2 border-red-400 flex items-center justify-center animate-pulse">
          <Bomb className="w-6 h-6 text-white" />
        </div>
      );
    }
    
    return (
      <div className="w-full h-full bg-green-600 rounded border-2 border-green-400 flex items-center justify-center animate-bounce">
        <Gem className="w-6 h-6 text-white" />
      </div>
    );
  };

  return (
    <CasinoGameLayout title="Mines" onBack={onBack} stats={stats}>
      <div className="space-y-6">
        {/* Game Board */}
        <Card className="p-6 bg-gradient-to-br from-gray-900 to-gray-800 border-2 border-yellow-400/30">
          <div className="text-center mb-6">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <CRTCoin size="w-8 h-8" />
              <h2 className="text-2xl font-bold text-yellow-400">MINES</h2>
              <CRTCoin size="w-8 h-8" />
            </div>
            
            {/* Game Status */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-gray-800/50 p-3 rounded">
                <div className="text-sm text-gray-400">Mines</div>
                <div className="text-xl font-bold text-red-400">{mineCount}</div>
              </div>
              <div className="bg-gray-800/50 p-3 rounded">
                <div className="text-sm text-gray-400">Gems</div>
                <div className="text-xl font-bold text-green-400">{boardSize - mineCount}</div>
              </div>
              <div className="bg-gray-800/50 p-3 rounded">
                <div className="text-sm text-gray-400">Multiplier</div>
                <div className="text-xl font-bold text-yellow-400">{currentMultiplier.toFixed(2)}x</div>
              </div>
              <div className="bg-gray-800/50 p-3 rounded">
                <div className="text-sm text-gray-400">Potential Win</div>
                <div className="text-xl font-bold text-green-400">
                  {(betAmount * currentMultiplier).toFixed(2)} CRT
                </div>
              </div>
            </div>
          </div>

          {/* 5x5 Grid */}
          <div className="grid grid-cols-5 gap-2 max-w-md mx-auto mb-6">
            {board.map((_, index) => (
              <div
                key={index}
                className="aspect-square"
                onClick={() => revealTile(index)}
              >
                {getTileContent(index)}
              </div>
            ))}
          </div>

          {/* Game Controls */}
          <div className="flex justify-center space-x-4">
            {gameActive && !gameOver && (
              <Button
                onClick={cashOut}
                className="bg-gradient-to-r from-green-500 to-green-600 text-white font-bold hover:from-green-400 hover:to-green-500 px-8 py-3"
              >
                Cash Out: {(betAmount * currentMultiplier).toFixed(2)} CRT
              </Button>
            )}
            
            {(!gameActive || gameOver) && (
              <Button
                onClick={resetGame}
                variant="outline"
                className="border-yellow-400 text-yellow-400 hover:bg-yellow-400/10 px-8 py-3"
              >
                New Game
              </Button>
            )}
          </div>
        </Card>

        {/* Game Settings */}
        {!gameActive && (
          <Card className="p-4 bg-gray-900/50 border-yellow-400/20">
            <h3 className="text-lg font-bold text-yellow-400 mb-4">Game Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-300 mb-2">Number of Mines (1-20)</label>
                <Input
                  type="number"
                  value={mineCount}
                  onChange={(e) => setMineCount(Math.max(1, Math.min(20, Number(e.target.value))))}
                  min="1"
                  max="20"
                  className="bg-gray-800 border-gray-700 text-white"
                />
              </div>
              
              <div className="text-xs text-gray-400">
                <p>• More mines = higher multipliers but more risk</p>
                <p>• Find gems to increase your multiplier</p>
                <p>• Cash out anytime to secure your winnings</p>
                <p>• Hit a mine and lose everything!</p>
              </div>
            </div>
          </Card>
        )}

        {/* Betting Panel */}
        {!gameActive && (
          <BettingPanel
            onBet={startGame}
            minBet={1}
            maxBet={100}
            disabled={gameActive}
            gameActive={gameActive}
          />
        )}
      </div>
    </CasinoGameLayout>
  );
};

export default Mines;