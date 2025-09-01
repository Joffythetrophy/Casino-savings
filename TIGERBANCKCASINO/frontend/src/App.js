import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

function App() {
  const [balance, setBalance] = useState(0);
  const [savings, setSavings] = useState(0);
  const [poolAllocation, setPoolAllocation] = useState(0);
  const [betAmount, setBetAmount] = useState(10);
  const [selectedGame, setSelectedGame] = useState('blackjack');
  const [gameResult, setGameResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [games, setGames] = useState([]);

  useEffect(() => {
    fetchUserBalance();
    fetchGames();
  }, []);

  const fetchUserBalance = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/user/user123/balance`);
      setBalance(response.data.balance);
      setSavings(response.data.savings);
      setPoolAllocation(response.data.pool_allocation);
    } catch (error) {
      console.error('Error fetching balance:', error);
    }
  };

  const fetchGames = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/games`);
      setGames(response.data.games);
    } catch (error) {
      console.error('Error fetching games:', error);
    }
  };

  const playGame = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/game/play?game_type=${selectedGame}&bet_amount=${betAmount}&user_id=user123`);
      setGameResult(response.data);
      setBalance(response.data.balance_after);
      
      // Refresh balance to get updated savings
      setTimeout(fetchUserBalance, 500);
    } catch (error) {
      console.error('Error playing game:', error);
      alert('Error playing game: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🐅 TIGER BANK CASINO 🏦</h1>
        <p>A casino that saves your losses like a piggy bank!</p>
      </header>

      <main className="casino-main">
        <div className="balance-section">
          <div className="balance-card">
            <h2>💰 Playing Balance</h2>
            <p className="balance-amount">${balance.toFixed(2)}</p>
          </div>
          <div className="savings-card">
            <h2>🐷 Piggy Bank Savings</h2>
            <p className="savings-amount">${savings.toFixed(2)}</p>
            <small>50% of losses saved here!</small>
          </div>
          <div className="pool-card">
            <h2>🏊‍♂️ Pool Investment</h2>
            <p className="pool-amount">${poolAllocation.toFixed(2)}</p>
            <small>50% of losses in DeFi pools!</small>
          </div>
        </div>

        <div className="game-section">
          <h2>🎰 Play Games</h2>
          <div className="game-controls">
            <select 
              value={selectedGame} 
              onChange={(e) => setSelectedGame(e.target.value)}
              className="game-select"
            >
              {games.map(game => (
                <option key={game.id} value={game.id}>
                  {game.name}
                </option>
              ))}
            </select>
            
            <input
              type="number"
              value={betAmount}
              onChange={(e) => setBetAmount(parseFloat(e.target.value))}
              min="1"
              max={balance}
              className="bet-input"
              placeholder="Bet amount"
            />
            
            <button 
              onClick={playGame}
              disabled={loading || betAmount > balance}
              className="play-button"
            >
              {loading ? 'Playing...' : `Bet $${betAmount}`}
            </button>
          </div>
        </div>

        {gameResult && (
          <div className={`game-result ${gameResult.result}`}>
            <h3>Game Result</h3>
            <p><strong>Game:</strong> {gameResult.game_type}</p>
            <p><strong>Bet:</strong> ${gameResult.bet_amount}</p>
            <p><strong>Result:</strong> {gameResult.result.toUpperCase()}</p>
            {gameResult.result === 'win' ? (
              <p><strong>Winnings:</strong> ${gameResult.winnings.toFixed(2)}</p>
            ) : (
              <div>
                <p><strong>Saved to Piggy Bank:</strong> ${(gameResult.bet_amount * 0.50).toFixed(2)}</p>
                <p><strong>Allocated to Pools:</strong> ${(gameResult.bet_amount * 0.50).toFixed(2)}</p>
              </div>
            )}
          </div>
        )}

        <div className="info-section">
          <h3>🏦 How Tiger Bank Works</h3>
          <ul>
            <li>🎯 Play casino games with real bets</li>
            <li>🐷 50% of every loss goes to your Piggy Bank</li>
            <li>🏊‍♂️ 50% of every loss goes to DeFi investment pools</li>
            <li>💰 Both savings and investments grow automatically</li>
            <li>🔒 Your allocated funds are protected from gambling</li>
          </ul>
        </div>
      </main>
    </div>
  );
}

export default App;