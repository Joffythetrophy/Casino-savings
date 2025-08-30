import React, { useState, useEffect } from 'react';

const CRTCasinoInterface = ({ walletAddress, crtBalance, onBalanceUpdate, backendUrl }) => {
  const [availableGames, setAvailableGames] = useState({});
  const [selectedGame, setSelectedGame] = useState('slots');
  const [betAmount, setBetAmount] = useState(1000);
  const [gameResult, setGameResult] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [gameHistory, setGameHistory] = useState([]);

  useEffect(() => {
    fetchAvailableGames();
  }, []);

  const fetchAvailableGames = async () => {
    try {
      const response = await fetch(`${backendUrl}/casino/games`);
      const data = await response.json();
      
      if (data.success) {
        setAvailableGames(data.games);
      }
    } catch (error) {
      console.error('Failed to fetch games:', error);
    }
  };

  const placeBet = async () => {
    if (betAmount > crtBalance) {
      alert('Insufficient CRT balance!');
      return;
    }

    setIsPlaying(true);
    setGameResult(null);

    try {
      const gameParams = getGameParams();
      
      const response = await fetch(`${backendUrl}/casino/bet-crt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: walletAddress,
          game: selectedGame,
          bet_amount: betAmount,
          game_params: gameParams
        })
      });

      const result = await response.json();
      
      if (result.success) {
        setGameResult(result.bet_result);
        
        // Add to history
        const historyEntry = {
          game: selectedGame,
          bet_amount: betAmount,
          result: result.bet_result,
          timestamp: new Date().toISOString()
        };
        setGameHistory(prev => [historyEntry, ...prev.slice(0, 9)]); // Keep last 10
        
        // Update balance
        setTimeout(onBalanceUpdate, 1000);
      } else {
        alert(`Bet failed: ${result.error}`);
      }
    } catch (error) {
      console.error('Bet failed:', error);
      alert('Bet failed due to network error');
    }

    setIsPlaying(false);
  };

  const getGameParams = () => {
    switch (selectedGame) {
      case 'roulette':
        return {
          bet_type: 'red',
          bet_value: null
        };
      case 'dice':
        return {
          target: 50,
          over_under: 'over'
        };
      default:
        return {};
    }
  };

  const renderGameResult = () => {
    if (!gameResult) return null;

    const { won, payout, net_result, game_data, multiplier } = gameResult;

    return (
      <div className={`game-result ${won ? 'win' : 'loss'}`}>
        <div className="result-header">
          <h3>{won ? '🎉 YOU WON!' : '😢 YOU LOST'}</h3>
          <div className="payout-info">
            <span className="bet-amount">Bet: {betAmount.toLocaleString()} CRT</span>
            <span className="net-result">
              {won ? `+${net_result.toLocaleString()}` : net_result.toLocaleString()} CRT
            </span>
          </div>
        </div>

        <div className="game-details">
          {selectedGame === 'slots' && (
            <div className="slots-result">
              <div className="reels">
                {game_data.reels?.map((symbol, i) => (
                  <div key={i} className="reel">{symbol}</div>
                ))}
              </div>
              <p>{game_data.payout_reason}</p>
            </div>
          )}

          {selectedGame === 'blackjack' && (
            <div className="blackjack-result">
              <div className="cards">
                <div className="player-cards">
                  <strong>Your Cards:</strong> {game_data.player_cards?.join(', ')} 
                  (Total: {game_data.player_total})
                </div>
                <div className="dealer-cards">
                  <strong>Dealer Cards:</strong> {game_data.dealer_cards?.join(', ')} 
                  (Total: {game_data.dealer_total})
                </div>
              </div>
            </div>
          )}

          {selectedGame === 'roulette' && (
            <div className="roulette-result">
              <div className="wheel-result">
                <strong>Result:</strong> {game_data.result} ({game_data.color})
              </div>
              <p>Bet: {game_data.bet_type}</p>
            </div>
          )}

          {selectedGame === 'dice' && (
            <div className="dice-result">
              <div className="dice-roll">
                <strong>Roll:</strong> {game_data.roll}
              </div>
              <p>Target: {game_data.over_under} {game_data.target}</p>
              <p>Win Chance: {game_data.win_chance?.toFixed(1)}%</p>
            </div>
          )}
        </div>

        {won && (
          <div className="multiplier-info">
            <span>Multiplier: {multiplier}x</span>
          </div>
        )}

        {!won && gameResult.savings_created && (
          <div className="savings-info">
            <p>💰 {(betAmount * 0.5).toLocaleString()} CRT automatically saved for investment!</p>
          </div>
        )}
      </div>
    );
  };

  const currentGame = availableGames[selectedGame];

  return (
    <div className="crt-casino-interface">
      <div className="casino-header">
        <h2>🎰 CRT Token Casino</h2>
        <div className="balance-display">
          <span className="balance-label">Your CRT Balance:</span>
          <span className="balance-amount">{crtBalance.toLocaleString()} CRT</span>
        </div>
      </div>

      <div className="casino-content">
        {/* Game Selection */}
        <div className="game-selection">
          <h3>Choose Your Game</h3>
          <div className="game-buttons">
            {Object.entries(availableGames).map(([gameKey, game]) => (
              <button
                key={gameKey}
                className={`game-button ${selectedGame === gameKey ? 'active' : ''}`}
                onClick={() => setSelectedGame(gameKey)}
              >
                <div className="game-name">{game.name}</div>
                <div className="game-desc">{game.description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Current Game Info */}
        {currentGame && (
          <div className="current-game-info">
            <h3>{currentGame.name}</h3>
            <div className="game-limits">
              <span>Min Bet: {currentGame.min_bet.toLocaleString()} CRT</span>
              <span>Max Bet: {currentGame.max_bet.toLocaleString()} CRT</span>
              <span>Max Win: {currentGame.max_multiplier}x</span>
            </div>
          </div>
        )}

        {/* Betting Interface */}
        <div className="betting-interface">
          <div className="bet-amount-section">
            <label>Bet Amount (CRT):</label>
            <div className="bet-controls">
              <input
                type="number"
                value={betAmount}
                onChange={(e) => setBetAmount(Number(e.target.value))}
                min={currentGame?.min_bet || 100}
                max={Math.min(currentGame?.max_bet || 1000000, crtBalance)}
                step="100"
              />
              <div className="quick-bet-buttons">
                <button onClick={() => setBetAmount(1000)}>1K</button>
                <button onClick={() => setBetAmount(10000)}>10K</button>
                <button onClick={() => setBetAmount(100000)}>100K</button>
                <button onClick={() => setBetAmount(Math.floor(crtBalance * 0.1))}>10%</button>
                <button onClick={() => setBetAmount(Math.floor(crtBalance * 0.5))}>50%</button>
              </div>
            </div>
          </div>

          <button
            className="place-bet-button"
            onClick={placeBet}
            disabled={isPlaying || betAmount > crtBalance || betAmount < (currentGame?.min_bet || 100)}
          >
            {isPlaying ? '🎰 Playing...' : `🎲 Bet ${betAmount.toLocaleString()} CRT`}
          </button>
        </div>

        {/* Game Result */}
        {renderGameResult()}

        {/* Game History */}
        {gameHistory.length > 0 && (
          <div className="game-history">
            <h3>Recent Games</h3>
            <div className="history-list">
              {gameHistory.map((entry, index) => (
                <div key={index} className={`history-item ${entry.result.won ? 'win' : 'loss'}`}>
                  <span className="game-name">{entry.game}</span>
                  <span className="bet-amount">{entry.bet_amount.toLocaleString()} CRT</span>
                  <span className="result">
                    {entry.result.won ? `+${entry.result.net_result.toLocaleString()}` : entry.result.net_result.toLocaleString()} CRT
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .crt-casino-interface {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
        }

        .casino-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
          padding: 20px;
          background: linear-gradient(135deg, #1a5f1a, #2d8f2d);
          border-radius: 10px;
          color: white;
        }

        .balance-display {
          font-size: 1.2em;
          font-weight: bold;
        }

        .balance-amount {
          color: #90ee90;
          margin-left: 10px;
        }

        .game-selection {
          margin-bottom: 30px;
        }

        .game-buttons {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 15px;
          margin-top: 15px;
        }

        .game-button {
          padding: 20px;
          border: 2px solid #4caf50;
          background: white;
          border-radius: 10px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .game-button:hover {
          background: #f0f8f0;
          transform: translateY(-2px);
        }

        .game-button.active {
          background: #4caf50;
          color: white;
        }

        .game-name {
          font-weight: bold;
          font-size: 1.1em;
          margin-bottom: 5px;
        }

        .current-game-info {
          margin-bottom: 30px;
          padding: 15px;
          background: #f8f9fa;
          border-radius: 8px;
        }

        .game-limits {
          display: flex;
          gap: 20px;
          margin-top: 10px;
          font-size: 0.9em;
          color: #666;
        }

        .betting-interface {
          margin-bottom: 30px;
          padding: 20px;
          border: 2px solid #4caf50;
          border-radius: 10px;
        }

        .bet-controls {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .bet-controls input {
          padding: 10px;
          font-size: 1.1em;
          border: 1px solid #ddd;
          border-radius: 5px;
          width: 200px;
        }

        .quick-bet-buttons {
          display: flex;
          gap: 10px;
        }

        .quick-bet-buttons button {
          padding: 8px 12px;
          border: 1px solid #4caf50;
          background: white;
          color: #4caf50;
          border-radius: 5px;
          cursor: pointer;
        }

        .quick-bet-buttons button:hover {
          background: #4caf50;
          color: white;
        }

        .place-bet-button {
          padding: 15px 30px;
          font-size: 1.2em;
          font-weight: bold;
          background: linear-gradient(135deg, #4caf50, #45a049);
          color: white;
          border: none;
          border-radius: 10px;
          cursor: pointer;
          transition: all 0.3s ease;
          margin-top: 15px;
        }

        .place-bet-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
        }

        .place-bet-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .game-result {
          margin-bottom: 30px;
          padding: 20px;
          border-radius: 10px;
          animation: slideIn 0.5s ease;
        }

        .game-result.win {
          background: linear-gradient(135deg, #d4edda, #c3e6cb);
          border: 2px solid #28a745;
        }

        .game-result.loss {
          background: linear-gradient(135deg, #f8d7da, #f5c6cb);
          border: 2px solid #dc3545;
        }

        .result-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 15px;
        }

        .result-header h3 {
          margin: 0;
          font-size: 1.5em;
        }

        .payout-info {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 5px;
        }

        .net-result {
          font-weight: bold;
          font-size: 1.2em;
        }

        .reels {
          display: flex;
          justify-content: center;
          gap: 20px;
          margin: 15px 0;
        }

        .reel {
          font-size: 3em;
          padding: 20px;
          background: white;
          border-radius: 10px;
          border: 2px solid #ddd;
        }

        .savings-info {
          margin-top: 15px;
          padding: 10px;
          background: rgba(255, 193, 7, 0.2);
          border-radius: 5px;
          font-weight: bold;
        }

        .game-history {
          margin-top: 30px;
        }

        .history-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
          max-height: 300px;
          overflow-y: auto;
        }

        .history-item {
          display: flex;
          justify-content: space-between;
          padding: 10px;
          border-radius: 5px;
          font-size: 0.9em;
        }

        .history-item.win {
          background: #d4edda;
        }

        .history-item.loss {
          background: #f8d7da;
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

export default CRTCasinoInterface;