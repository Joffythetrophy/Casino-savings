import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

function App() {
  // State management
  const [balances, setBalances] = useState({});
  const [savings, setSavings] = useState({});
  const [poolAllocation, setPoolAllocation] = useState({});
  const [portfolio, setPortfolio] = useState(null);
  const [supportedTokens, setSupportedTokens] = useState({});
  
  // Game state
  const [betAmount, setBetAmount] = useState(10);
  const [selectedToken, setSelectedToken] = useState('TKA');
  const [selectedGame, setSelectedGame] = useState('blackjack');
  const [gameResult, setGameResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [games, setGames] = useState([]);
  
  // Payment state
  const [showDepositModal, setShowDepositModal] = useState(false);
  const [showWithdrawModal, setShowWithdrawModal] = useState(false);
  const [showCRTBridge, setShowCRTBridge] = useState(false);
  
  // Withdrawal state
  const [withdrawToken, setWithdrawToken] = useState('USDC');
  const [withdrawAmount, setWithdrawAmount] = useState(100);
  const [withdrawAddress, setWithdrawAddress] = useState('');
  const [withdrawNetwork, setWithdrawNetwork] = useState('solana');
  
  // CRT Bridge state
  const [crtAmount, setCrtAmount] = useState(1000);
  const [crtDestToken, setCrtDestToken] = useState('USDC');
  const [crtStatus, setCrtStatus] = useState(null);

  useEffect(() => {
    fetchUserBalance();
    fetchUserPortfolio();
    fetchSupportedTokens();
    fetchGames();
    fetchCRTStatus();
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

  const fetchCRTStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/crt/bridge/status`);
      setCrtStatus(response.data);
    } catch (error) {
      console.error('Error fetching CRT status:', error);
    }
  };

  const playGame = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/game/play?game_type=${selectedGame}&bet_amount=${betAmount}&bet_token=${selectedToken}&user_id=user123`);
      setGameResult(response.data);
      
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

  const initiateDeposit = async (packageId) => {
    try {
      const response = await axios.post(`${API_BASE}/api/payments/deposit`, {
        package_id: packageId,
        origin_url: window.location.origin
      });
      
      // Redirect to Stripe checkout
      window.location.href = response.data.checkout_url;
    } catch (error) {
      alert('Deposit failed: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const initiateWithdrawal = async () => {
    if (!withdrawAddress) {
      alert('Please enter withdrawal address');
      return;
    }

    try {
      const response = await axios.post(`${API_BASE}/api/crypto/withdraw`, {
        token_symbol: withdrawToken,
        amount: withdrawAmount,
        destination_address: withdrawAddress,
        network: withdrawNetwork,
        user_id: 'user123'
      });
      
      alert(`Withdrawal initiated: ${response.data.message}`);
      setShowWithdrawModal(false);
      fetchUserBalance();
    } catch (error) {
      alert('Withdrawal failed: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const bridgeCRT = async () => {
    try {
      const response = await axios.post(`${API_BASE}/api/crt/bridge`, {
        amount: crtAmount,
        destination_token: crtDestToken,
        user_wallet: 'user_wallet_address',
        promissory_note: true
      });
      
      alert(`CRT Bridge Success: ${response.data.message}`);
      setShowCRTBridge(false);
      fetchUserBalance();
      fetchCRTStatus();
    } catch (error) {
      alert('CRT Bridge failed: ' + (error.response?.data?.detail || 'Unknown error'));
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

  return (
    <div style={{padding: '20px', fontFamily: 'Arial', maxWidth: '1200px', margin: '0 auto'}}>
      {/* Header */}
      <header style={{textAlign: 'center', marginBottom: '30px'}}>
        <h1 style={{background: 'linear-gradient(45deg, #ff6b35, #f7931e)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', fontSize: '3em'}}>
          🐅 TIGER BANK GAMES 🎮
        </h1>
        <p style={{fontSize: '18px', color: '#666'}}>Complete System: Multi-Token Gaming + Real Payments + DeFi Pools!</p>
        
        {portfolio && (
          <div style={{backgroundColor: '#f8f9fa', padding: '15px', borderRadius: '10px', margin: '20px 0'}}>
            <h3>💰 Total Portfolio Value: ${formatBalance(portfolio.total_value_usd)}</h3>
            <div style={{display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '10px', flexWrap: 'wrap'}}>
              <span>🎮 Playing: ${formatBalance(portfolio.playing_balance_usd)}</span>
              <span>🐷 Savings: ${formatBalance(portfolio.savings_usd)}</span>
              <span>🏊‍♂️ Pools: ${formatBalance(portfolio.pools_usd)}</span>
              <span>🌊 DeFi: ${formatBalance(portfolio.defi_value_usd)}</span>
            </div>
          </div>
        )}
      </header>

      {/* CRT Bridge Alert */}
      {crtStatus && crtStatus.internal_pool_value > 0 && (
        <div style={{backgroundColor: '#fff3cd', padding: '15px', borderRadius: '10px', margin: '20px 0', border: '1px solid #ffeaa7'}}>
          <h4>💎 CRT Bridge Available!</h4>
          <p>You have ${formatBalance(crtStatus.internal_pool_value)} worth of CRT tokens available for instant bridge!</p>
          <button 
            onClick={() => setShowCRTBridge(true)}
            style={{padding: '8px 16px', backgroundColor: '#f39c12', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer'}}
          >
            Bridge CRT Now
          </button>
        </div>
      )}

      {/* Action Buttons */}
      <div style={{display: 'flex', justifyContent: 'center', gap: '15px', marginBottom: '30px', flexWrap: 'wrap'}}>
        <button onClick={() => setShowDepositModal(true)} style={{padding: '12px 24px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '8px', fontSize: '16px', cursor: 'pointer'}}>
          💳 Deposit (Stripe)
        </button>
        <button onClick={() => setShowWithdrawModal(true)} style={{padding: '12px 24px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '8px', fontSize: '16px', cursor: 'pointer'}}>
          💰 Crypto Withdrawal
        </button>
        <button onClick={() => setShowCRTBridge(true)} style={{padding: '12px 24px', backgroundColor: '#f39c12', color: 'white', border: 'none', borderRadius: '8px', fontSize: '16px', cursor: 'pointer'}}>
          🌉 CRT Bridge
        </button>
      </div>

      {/* Token Balances Grid */}
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px', marginBottom: '30px'}}>
        {Object.entries(balances).map(([token, balance]) => (
          <div key={token} style={{
            padding: '15px', 
            border: '2px solid ' + (token === selectedToken ? '#007bff' : '#e0e0e0'), 
            borderRadius: '10px', 
            textAlign: 'center',
            backgroundColor: token === selectedToken ? '#f8f9ff' : 'white',
            cursor: 'pointer'
          }} onClick={() => setSelectedToken(token)}>
            <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', marginBottom: '8px'}}>
              {getTokenIcon(token)}
              <h4 style={{margin: 0}}>{token}</h4>
            </div>
            <p style={{fontSize: '18px', fontWeight: 'bold', margin: '5px 0'}}>{formatBalance(balance)}</p>
            <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '12px'}}>
              <div>🐷 {formatBalance(savings[token] || 0)}</div>
              <div>🏊‍♂️ {formatBalance(poolAllocation[token] || 0)}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Gaming Section */}
      <div style={{backgroundColor: '#f8f9fa', padding: '30px', borderRadius: '15px', marginBottom: '30px'}}>
        <h2 style={{textAlign: 'center', marginBottom: '20px'}}>🎰 Play Games</h2>
        
        <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '15px', marginBottom: '20px', flexWrap: 'wrap'}}>
          <select value={selectedGame} onChange={(e) => setSelectedGame(e.target.value)} style={{padding: '10px', fontSize: '16px', borderRadius: '5px'}}>
            <option value="blackjack">🃏 Blackjack</option>
            <option value="roulette">🎰 Roulette</option>
            <option value="slots">🎲 Slots</option>
          </select>
          
          <select value={selectedToken} onChange={(e) => setSelectedToken(e.target.value)} style={{padding: '10px', fontSize: '16px', borderRadius: '5px'}}>
            {Object.keys(balances).map(token => (
              <option key={token} value={token}>{token} ({formatBalance(balances[token])})</option>
            ))}
          </select>
          
          <input type="number" value={betAmount} onChange={(e) => setBetAmount(parseFloat(e.target.value))} min="1" max={balances[selectedToken] || 0} style={{padding: '10px', fontSize: '16px', width: '100px', borderRadius: '5px'}} />
          
          <button onClick={playGame} disabled={loading} style={{padding: '12px 24px', fontSize: '18px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer'}}>
            {loading ? 'Playing...' : `🎲 Bet ${betAmount} ${selectedToken}`}
          </button>
        </div>

        {gameResult && (
          <div style={{padding: '20px', border: `2px solid ${gameResult.result === 'win' ? '#28a745' : '#dc3545'}`, borderRadius: '10px', textAlign: 'center'}}>
            <h3>{gameResult.result === 'win' ? '🎉 YOU WON!' : '😔 You Lost - But Your Money is Growing!'}</h3>
            <p><strong>Bet:</strong> {gameResult.bet_amount} {gameResult.bet_token}</p>
            {gameResult.result === 'win' ? (
              <p><strong>Winnings:</strong> {formatBalance(gameResult.winnings)} {gameResult.winnings_token}</p>
            ) : (
              <div>
                <p><strong>🐷 Saved to Piggy Bank:</strong> {formatBalance(gameResult.bet_amount * 0.50)} {gameResult.bet_token}</p>
                <p><strong>🌊 Invested in DeFi Pools:</strong> {formatBalance(gameResult.bet_amount * 0.50)} {gameResult.bet_token}</p>
                <small>Your losses are earning yield in Orca, Raydium & Jupiter!</small>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Deposit Modal */}
      {showDepositModal && (
        <div style={{position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000}}>
          <div style={{backgroundColor: 'white', padding: '30px', borderRadius: '15px', minWidth: '400px'}}>
            <h3>💳 Stripe Deposit Packages</h3>
            <div style={{display: 'flex', flexDirection: 'column', gap: '15px'}}>
              <button onClick={() => initiateDeposit('starter')} style={{padding: '15px', backgroundColor: '#28a745', color: 'white', border: 'none', borderRadius: '8px'}}>
                🚀 Starter - $10 → Get 1,000 tokens
              </button>
              <button onClick={() => initiateDeposit('high_roller')} style={{padding: '15px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '8px'}}>
                💎 High Roller - $50 → Get 5,000 tokens
              </button>
              <button onClick={() => initiateDeposit('whale')} style={{padding: '15px', backgroundColor: '#6f42c1', color: 'white', border: 'none', borderRadius: '8px'}}>
                🐋 Whale - $100 → Get 10,000 tokens
              </button>
              <button onClick={() => setShowDepositModal(false)} style={{padding: '10px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '8px'}}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Withdrawal Modal */}
      {showWithdrawModal && (
        <div style={{position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000}}>
          <div style={{backgroundColor: 'white', padding: '30px', borderRadius: '15px', minWidth: '400px'}}>
            <h3>💰 Crypto Withdrawal</h3>
            
            <div style={{marginBottom: '15px'}}>
              <label>Token:</label>
              <select value={withdrawToken} onChange={(e) => setWithdrawToken(e.target.value)} style={{width: '100%', padding: '10px', marginTop: '5px'}}>
                <option value="USDC">💵 USDC</option>
                <option value="BTC">₿ Bitcoin</option>
                <option value="ETH">⟠ Ethereum</option>
                <option value="SOL">◎ Solana</option>
              </select>
            </div>
            
            <div style={{marginBottom: '15px'}}>
              <label>Amount:</label>
              <input type="number" value={withdrawAmount} onChange={(e) => setWithdrawAmount(parseFloat(e.target.value))} style={{width: '100%', padding: '10px', marginTop: '5px'}} />
            </div>
            
            <div style={{marginBottom: '15px'}}>
              <label>Address:</label>
              <input type="text" value={withdrawAddress} onChange={(e) => setWithdrawAddress(e.target.value)} placeholder="Enter withdrawal address" style={{width: '100%', padding: '10px', marginTop: '5px'}} />
            </div>
            
            <div style={{marginBottom: '20px'}}>
              <label>Network:</label>
              <select value={withdrawNetwork} onChange={(e) => setWithdrawNetwork(e.target.value)} style={{width: '100%', padding: '10px', marginTop: '5px'}}>
                <option value="solana">Solana</option>
                <option value="ethereum">Ethereum</option>
                <option value="bitcoin">Bitcoin</option>
              </select>
            </div>
            
            <div style={{display: 'flex', gap: '10px'}}>
              <button onClick={initiateWithdrawal} style={{flex: 1, padding: '12px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '8px'}}>
                💸 Withdraw
              </button>
              <button onClick={() => setShowWithdrawModal(false)} style={{flex: 1, padding: '12px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '8px'}}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CRT Bridge Modal */}
      {showCRTBridge && (
        <div style={{position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000}}>
          <div style={{backgroundColor: 'white', padding: '30px', borderRadius: '15px', minWidth: '400px'}}>
            <h3>🌉 CRT Bridge System</h3>
            <p style={{color: '#666', marginBottom: '20px'}}>
              Bridge your $140k CRT tokens using our IOU system. Get liquid tokens now, pay back when CRT liquidity is available!
            </p>
            
            <div style={{marginBottom: '15px'}}>
              <label>CRT Amount:</label>
              <input type="number" value={crtAmount} onChange={(e) => setCrtAmount(parseFloat(e.target.value))} max={crtStatus?.internal_pool_value / 0.25} style={{width: '100%', padding: '10px', marginTop: '5px'}} />
              <small>Available: ${formatBalance(crtStatus?.internal_pool_value || 0)} worth</small>
            </div>
            
            <div style={{marginBottom: '20px'}}>
              <label>Get Token:</label>
              <select value={crtDestToken} onChange={(e) => setCrtDestToken(e.target.value)} style={{width: '100%', padding: '10px', marginTop: '5px'}}>
                <option value="USDC">💵 USDC</option>
                <option value="SOL">◎ SOL</option>
                <option value="BTC">₿ BTC</option>
                <option value="ETH">⟠ ETH</option>
              </select>
            </div>
            
            <div style={{backgroundColor: '#e8f5e8', padding: '15px', borderRadius: '8px', marginBottom: '20px'}}>
              <h4>IOU Terms:</h4>
              <ul style={{margin: 0}}>
                <li>Get liquid tokens immediately</li>
                <li>0% interest rate</li>
                <li>Repay when CRT liquidity available</li>
                <li>Your CRT collateral is secure</li>
              </ul>
            </div>
            
            <div style={{display: 'flex', gap: '10px'}}>
              <button onClick={bridgeCRT} style={{flex: 1, padding: '12px', backgroundColor: '#f39c12', color: 'white', border: 'none', borderRadius: '8px'}}>
                🌉 Bridge CRT
              </button>
              <button onClick={() => setShowCRTBridge(false)} style={{flex: 1, padding: '12px', backgroundColor: '#6c757d', color: 'white', border: 'none', borderRadius: '8px'}}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Info Section */}
      <div style={{backgroundColor: '#f8f9fa', padding: '20px', borderRadius: '10px'}}>
        <h3>🏦 Complete Tiger Bank System Features</h3>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px'}}>
          <div>
            <h4>🎰 Multi-Token Gaming</h4>
            <ul>
              <li>7 supported tokens</li>
              <li>Real-time USD values</li>
              <li>Smart loss allocation</li>
            </ul>
          </div>
          <div>
            <h4>💳 Real Payments</h4>
            <ul>
              <li>Stripe deposits</li>
              <li>Crypto withdrawals</li>
              <li>Multiple networks</li>
            </ul>
          </div>
          <div>
            <h4>🌉 CRT Bridge</h4>
            <ul>
              <li>$140k internal pool</li>
              <li>Instant IOU system</li>
              <li>No interest charges</li>
            </ul>
          </div>
          <div>
            <h4>🌊 Real DeFi</h4>
            <ul>
              <li>Orca pools</li>
              <li>Raydium farming</li>
              <li>Jupiter arbitrage</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;