import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

function App() {
  // Multi-token state
  const [balances, setBalances] = useState({});
  const [savings, setSavings] = useState({});
  const [poolAllocation, setPoolAllocation] = useState({});
  const [portfolio, setPortfolio] = useState(null);
  const [supportedTokens, setSupportedTokens] = useState({});
  const [exchangeRates, setExchangeRates] = useState({});
  
  // Game state
  const [betAmount, setBetAmount] = useState(10);
  const [selectedToken, setSelectedToken] = useState('TKA');
  const [selectedGame, setSelectedGame] = useState('blackjack');
  const [gameResult, setGameResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [games, setGames] = useState([]);
  
  // Swap state
  const [showSwapModal, setShowSwapModal] = useState(false);
  const [swapFromToken, setSwapFromToken] = useState('TKA');
  const [swapToToken, setSwapToToken] = useState('TKB');
  const [swapAmount, setSwapAmount] = useState(100);
  const [swapResult, setSwapResult] = useState(null);
  
  // Transaction history
  const [showTransactions, setShowTransactions] = useState(false);
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    fetchUserBalance();
    fetchUserPortfolio();
    fetchSupportedTokens();
    fetchGames();
    fetchExchangeRates();
  }, []);

  const fetchUserBalance = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/user/user123/balance`);
      setBalances(response.data.balances);
      setSavings(response.data.savings);
      setPoolAllocation(response.data.pool_allocation);
    } catch (error) {
      console.error('Error fetching balance:', error);
    }
  };

  const fetchUserPortfolio = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/user/user123/portfolio`);
      setPortfolio(response.data);
    } catch (error) {
      console.error('Error fetching portfolio:', error);
    }
  };

  const fetchSupportedTokens = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/tokens`);
      setSupportedTokens(response.data.tokens);
      setExchangeRates(response.data.exchange_rates);
    } catch (error) {
      console.error('Error fetching tokens:', error);
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

  const fetchExchangeRates = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/tokens/rates`);
      setExchangeRates(response.data.rates);
    } catch (error) {
      console.error('Error fetching rates:', error);
    }
  };

  const fetchTransactions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/user/user123/transactions`);
      setTransactions(response.data);
    } catch (error) {
      console.error('Error fetching transactions:', error);
    }
  };

  const playGame = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/game/play?game_type=${selectedGame}&bet_amount=${betAmount}&bet_token=${selectedToken}&user_id=user123`);
      setGameResult(response.data);
      
      // Refresh balances and portfolio
      setTimeout(() => {
        fetchUserBalance();
        fetchUserPortfolio();
      }, 500);
    } catch (error) {
      console.error('Error playing game:', error);
      alert('Error playing game: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const executeSwap = async () => {
    if (swapAmount > (balances[swapFromToken] || 0)) {
      alert('Insufficient balance for swap');
      return;
    }

    try {
      const response = await axios.post(`${API_BASE}/api/tokens/swap`, {
        from_token: swapFromToken,
        to_token: swapToToken,
        amount: swapAmount,
        user_id: 'user123'
      });
      
      setSwapResult(response.data);
      
      // Refresh balances
      setTimeout(() => {
        fetchUserBalance();
        fetchUserPortfolio();
      }, 500);
      
    } catch (error) {
      console.error('Error swapping tokens:', error);
      alert('Swap failed: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const getTokenIcon = (tokenSymbol) => {
    const token = supportedTokens[tokenSymbol];
    if (token?.logo && token.logo.startsWith('http')) {
      return <img src={token.logo} alt={tokenSymbol} style={{width: '24px', height: '24px'}} />;
    }
    return <span style={{fontSize: '24px'}}>{token?.logo || '🪙'}</span>;
  };

  const formatBalance = (amount, decimals = 2) => {
    return amount ? amount.toFixed(decimals) : '0.00';
  };

  const getTokenValue = (tokenSymbol, amount) => {
    const rate = exchangeRates[tokenSymbol] || 0;
    return (amount * rate).toFixed(2);
  };

  return (
    <div style={{padding: '20px', fontFamily: 'Arial', maxWidth: '1200px', margin: '0 auto'}}>
      <header style={{textAlign: 'center', marginBottom: '30px'}}>
        <h1 style={{background: 'linear-gradient(45deg, #ff6b35, #f7931e)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', fontSize: '3em'}}>
          🐅 TIGER BANK GAMES 🎮
        </h1>
        <p style={{fontSize: '18px', color: '#666'}}>Multi-Token Gaming That Grows Your Wealth!</p>
        {portfolio && (
          <div style={{backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '10px', margin: '20px 0'}}>
            <h3>💰 Total Portfolio Value: ${formatBalance(portfolio.total_value_usd)}</h3>
            <div style={{display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '10px'}}>
              <span>🎮 Playing: ${formatBalance(portfolio.playing_balance_usd)}</span>
              <span>🐷 Savings: ${formatBalance(portfolio.savings_usd)}</span>
              <span>🏊‍♂️ Pools: ${formatBalance(portfolio.pools_usd)}</span>
            </div>
          </div>
        )}
      </header>

      {/* Token Balances Grid */}
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px'}}>
        {Object.entries(balances).map(([token, balance]) => (
          <div key={token} style={{
            padding: '20px', 
            border: '2px solid ' + (token === selectedToken ? '#007bff' : '#e0e0e0'), 
            borderRadius: '15px', 
            textAlign: 'center',
            backgroundColor: token === selectedToken ? '#f8f9ff' : 'white',
            cursor: 'pointer',
            transition: 'all 0.3s ease'
          }} onClick={() => setSelectedToken(token)}>
            <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', marginBottom: '10px'}}>
              {getTokenIcon(token)}
              <h3 style={{margin: 0}}>{token}</h3>
            </div>
            <p style={{fontSize: '24px', fontWeight: 'bold', margin: '5px 0', color: '#333'}}>
              {formatBalance(balance)}
            </p>
            <p style={{fontSize: '14px', color: '#666', margin: '5px 0'}}>
              ≈ ${getTokenValue(token, balance)}
            </p>
            <div style={{display: 'flex', justifyContent: 'space-between', marginTop: '15px', fontSize: '12px'}}>
              <div>
                <div>🐷 Savings</div>
                <div>{formatBalance(savings[token] || 0)}</div>
              </div>
              <div>
                <div>🏊‍♂️ Pools</div>
                <div>{formatBalance(poolAllocation[token] || 0)}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div style={{display: 'flex', justifyContent: 'center', gap: '15px', marginBottom: '30px', flexWrap: 'wrap'}}>
        <button 
          onClick={() => setShowSwapModal(true)}
          style={{
            padding: '12px 24px',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            cursor: 'pointer'
          }}
        >
          🔄 Swap Tokens
        </button>
        <button 
          onClick={() => {setShowTransactions(true); fetchTransactions();}}
          style={{
            padding: '12px 24px',
            backgroundColor: '#17a2b8',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            cursor: 'pointer'
          }}
        >
          📊 Transaction History
        </button>
      </div>

      {/* Gaming Section */}
      <div style={{backgroundColor: '#f8f9fa', padding: '30px', borderRadius: '15px', marginBottom: '30px'}}>
        <h2 style={{textAlign: 'center', marginBottom: '20px'}}>🎰 Play Games</h2>
        
        <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '15px', marginBottom: '20px', flexWrap: 'wrap'}}>
          <div>
            <label style={{display: 'block', marginBottom: '5px'}}>Game:</label>
            <select 
              value={selectedGame} 
              onChange={(e) => setSelectedGame(e.target.value)}
              style={{padding: '10px', fontSize: '16px', borderRadius: '5px', border: '1px solid #ddd'}}
            >
              {games.map(game => (
                <option key={game.id} value={game.id}>
                  {game.name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label style={{display: 'block', marginBottom: '5px'}}>Token:</label>
            <select 
              value={selectedToken} 
              onChange={(e) => setSelectedToken(e.target.value)}
              style={{padding: '10px', fontSize: '16px', borderRadius: '5px', border: '1px solid #ddd'}}
            >
              {Object.keys(balances).map(token => (
                <option key={token} value={token}>
                  {token} ({formatBalance(balances[token])})
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label style={{display: 'block', marginBottom: '5px'}}>Bet Amount:</label>
            <input
              type="number"
              value={betAmount}
              onChange={(e) => setBetAmount(parseFloat(e.target.value))}
              min="1"
              max={balances[selectedToken] || 0}
              style={{padding: '10px', fontSize: '16px', width: '120px', borderRadius: '5px', border: '1px solid #ddd'}}
            />
          </div>
          
          <div style={{marginTop: '20px'}}>
            <button 
              onClick={playGame}
              disabled={loading || betAmount > (balances[selectedToken] || 0)}
              style={{
                padding: '12px 24px', 
                fontSize: '18px', 
                backgroundColor: loading ? '#ccc' : '#007bff', 
                color: 'white', 
                border: 'none', 
                borderRadius: '8px',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? 'Playing...' : `🎲 Bet ${betAmount} ${selectedToken}`}
            </button>
          </div>
        </div>

        {/* Game Result */}
        {gameResult && (
          <div style={{
            padding: '20px', 
            border: '2px solid ' + (gameResult.result === 'win' ? '#28a745' : '#dc3545'), 
            borderRadius: '10px', 
            backgroundColor: gameResult.result === 'win' ? '#d4edda' : '#f8d7da',
            textAlign: 'center'
          }}>
            <h3>{gameResult.result === 'win' ? '🎉 YOU WON!' : '😔 You Lost'}</h3>
            <p><strong>Game:</strong> {gameResult.game_type}</p>
            <p><strong>Bet:</strong> {gameResult.bet_amount} {gameResult.bet_token}</p>
            {gameResult.result === 'win' ? (
              <p><strong>Winnings:</strong> {formatBalance(gameResult.winnings)} {gameResult.winnings_token}</p>
            ) : (
              <div>
                <p><strong>🐷 Saved to Piggy Bank:</strong> {formatBalance(gameResult.bet_amount * 0.50)} {gameResult.bet_token}</p>
                <p><strong>🏊‍♂️ Allocated to Pools:</strong> {formatBalance(gameResult.bet_amount * 0.50)} {gameResult.bet_token}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Swap Modal */}
      {showSwapModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
          <div style={{backgroundColor: 'white', padding: '30px', borderRadius: '15px', minWidth: '400px'}}>
            <h3 style={{textAlign: 'center', marginBottom: '20px'}}>🔄 Token Swap</h3>
            
            <div style={{marginBottom: '15px'}}>
              <label>From Token:</label>
              <select 
                value={swapFromToken} 
                onChange={(e) => setSwapFromToken(e.target.value)}
                style={{width: '100%', padding: '10px', marginTop: '5px', borderRadius: '5px', border: '1px solid #ddd'}}
              >
                {Object.keys(balances).map(token => (
                  <option key={token} value={token}>
                    {token} (Balance: {formatBalance(balances[token])})
                  </option>
                ))}
              </select>
            </div>
            
            <div style={{marginBottom: '15px'}}>
              <label>To Token:</label>
              <select 
                value={swapToToken} 
                onChange={(e) => setSwapToToken(e.target.value)}
                style={{width: '100%', padding: '10px', marginTop: '5px', borderRadius: '5px', border: '1px solid #ddd'}}
              >
                {Object.keys(balances).filter(token => token !== swapFromToken).map(token => (
                  <option key={token} value={token}>{token}</option>
                ))}
              </select>
            </div>
            
            <div style={{marginBottom: '20px'}}>
              <label>Amount:</label>
              <input
                type="number"
                value={swapAmount}
                onChange={(e) => setSwapAmount(parseFloat(e.target.value))}
                max={balances[swapFromToken] || 0}
                style={{width: '100%', padding: '10px', marginTop: '5px', borderRadius: '5px', border: '1px solid #ddd'}}
              />
              <small style={{color: '#666'}}>Available: {formatBalance(balances[swapFromToken] || 0)} {swapFromToken}</small>
            </div>
            
            {swapAmount > 0 && (
              <div style={{backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '8px', marginBottom: '20px'}}>
                <p>📈 Estimated: ~{formatBalance((swapAmount * exchangeRates[swapFromToken]) / exchangeRates[swapToToken])} {swapToToken}</p>
                <p style={{fontSize: '12px', color: '#666'}}>* Includes 0.5% swap fee</p>
              </div>
            )}
            
            <div style={{display: 'flex', gap: '10px'}}>
              <button 
                onClick={executeSwap}
                style={{
                  flex: 1, padding: '12px', backgroundColor: '#28a745', color: 'white', 
                  border: 'none', borderRadius: '8px', cursor: 'pointer'
                }}
              >
                🔄 Execute Swap
              </button>
              <button 
                onClick={() => {setShowSwapModal(false); setSwapResult(null);}}
                style={{
                  flex: 1, padding: '12px', backgroundColor: '#6c757d', color: 'white', 
                  border: 'none', borderRadius: '8px', cursor: 'pointer'
                }}
              >
                Cancel
              </button>
            </div>
            
            {swapResult && (
              <div style={{marginTop: '20px', padding: '15px', backgroundColor: '#d4edda', borderRadius: '8px'}}>
                <h4>✅ Swap Successful!</h4>
                <p>Swapped {swapResult.from_amount} {swapResult.from_token} → {formatBalance(swapResult.to_amount)} {swapResult.to_token}</p>
                <p>Fee: {formatBalance(swapResult.fee)} {swapResult.to_token}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Transaction History Modal */}
      {showTransactions && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
          <div style={{backgroundColor: 'white', padding: '30px', borderRadius: '15px', minWidth: '600px', maxHeight: '80vh', overflow: 'auto'}}>
            <h3 style={{textAlign: 'center', marginBottom: '20px'}}>📊 Transaction History</h3>
            
            <div style={{marginBottom: '20px'}}>
              <h4>💸 Transactions ({transactions.total_transactions || 0})</h4>
              {transactions.transactions?.map((tx, index) => (
                <div key={index} style={{padding: '10px', border: '1px solid #eee', borderRadius: '5px', marginBottom: '10px'}}>
                  <div style={{display: 'flex', justifyContent: 'space-between'}}>
                    <span>{tx.type}: {tx.amount} {tx.token}</span>
                    <span style={{fontSize: '12px', color: '#666'}}>{tx.timestamp}</span>
                  </div>
                </div>
              ))}
            </div>
            
            <div style={{marginBottom: '20px'}}>
              <h4>🔄 Swaps ({transactions.total_swaps || 0})</h4>
              {transactions.swaps?.map((swap, index) => (
                <div key={index} style={{padding: '10px', border: '1px solid #eee', borderRadius: '5px', marginBottom: '10px'}}>
                  <div>
                    {formatBalance(swap.from_amount)} {swap.from_token} → {formatBalance(swap.to_amount)} {swap.to_token}
                  </div>
                  <div style={{fontSize: '12px', color: '#666'}}>
                    Rate: {formatBalance(swap.rate)} | Fee: {formatBalance(swap.fee)}
                  </div>
                </div>
              ))}
            </div>
            
            <button 
              onClick={() => setShowTransactions(false)}
              style={{
                width: '100%', padding: '12px', backgroundColor: '#6c757d', color: 'white', 
                border: 'none', borderRadius: '8px', cursor: 'pointer'
              }}
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* How It Works */}
      <div style={{backgroundColor: '#f8f9fa', padding: '20px', borderRadius: '10px'}}>
        <h3>🏦 How Tiger Bank Multi-Token System Works</h3>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px'}}>
          <div>
            <h4>🎯 Multi-Token Gaming</h4>
            <ul>
              <li>Bet with TKA, TKB, USDC, or SOL</li>
              <li>Different limits per token</li>
              <li>Real-time USD values</li>
            </ul>
          </div>
          <div>
            <h4>🔄 Token Swapping</h4>
            <ul>
              <li>Instant token exchanges</li>
              <li>0.5% swap fee</li>
              <li>Real-time exchange rates</li>
            </ul>
          </div>
          <div>
            <h4>🐷 Smart Allocation</h4>
            <ul>
              <li>50% of losses → Savings</li>
              <li>50% of losses → Investment pools</li>
              <li>Protected from future gambling</li>
            </ul>
          </div>
          <div>
            <h4>📊 Portfolio Tracking</h4>
            <ul>
              <li>Total USD portfolio value</li>
              <li>Per-token breakdown</li>
              <li>Transaction history</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;