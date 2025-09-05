import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || '';

function App() {
  const [portfolio, setPortfolio] = useState(null);
  const [tokensSummary, setTokensSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showBridgeModal, setShowBridgeModal] = useState(false);
  
  // Bridge state
  const [sourceToken, setSourceToken] = useState('USDC');
  const [destToken, setDestToken] = useState('CDT');
  const [bridgeAmount, setBridgeAmount] = useState(1000);

  useEffect(() => {
    fetchPortfolio();
    fetchTokensSummary();
  }, []);

  const fetchPortfolio = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/user/user123/portfolio`);
      setPortfolio(response.data);
    } catch (error) {
      console.error('Error fetching portfolio:', error);
    }
  };

  const fetchTokensSummary = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/tokens/summary`);
      setTokensSummary(response.data);
    } catch (error) {
      console.error('Error fetching tokens summary:', error);
    }
  };

  const executeBridge = async () => {
    if (!portfolio?.tokens[sourceToken]) {
      alert('Source token not available');
      return;
    }

    if (bridgeAmount > portfolio.tokens[sourceToken].balance) {
      alert('Insufficient balance');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/tokens/bridge`, {
        source_token: sourceToken,
        amount: bridgeAmount,
        destination_token: destToken,
        user_wallet: 'your_wallet_address'
      });
      
      alert(`Bridge Success: ${response.data.message}`);
      setShowBridgeModal(false);
      fetchPortfolio();
      fetchTokensSummary();
    } catch (error) {
      alert('Bridge failed: ' + (error.response?.data?.detail || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  const formatBalance = (amount, decimals = 2) => {
    return amount ? amount.toLocaleString(undefined, { 
      minimumFractionDigits: decimals, 
      maximumFractionDigits: decimals 
    }) : '0.00';
  };

  const getTokensBySource = (source) => {
    if (!portfolio?.tokens) return {};
    return Object.fromEntries(
      Object.entries(portfolio.tokens).filter(([_, token]) => token.source === source)
    );
  };

  return (
    <div style={{padding: '20px', fontFamily: 'Arial', maxWidth: '1200px', margin: '0 auto'}}>
      {/* Header */}
      <header style={{textAlign: 'center', marginBottom: '30px'}}>
        <h1 style={{
          background: 'linear-gradient(45deg, #ff6b35, #f7931e)', 
          WebkitBackgroundClip: 'text', 
          WebkitTextFillColor: 'transparent', 
          fontSize: '3em',
          margin: '0'
        }}>
          🐅 TIGER BANK GAMES 🎮
        </h1>
        <p style={{fontSize: '18px', color: '#666', margin: '10px 0'}}>
          Your Complete Converted Portfolio System
        </p>
        
        {portfolio && (
          <div style={{
            backgroundColor: '#f8f9fa', 
            padding: '20px', 
            borderRadius: '15px', 
            margin: '20px 0',
            border: '3px solid #28a745'
          }}>
            <h2 style={{color: '#28a745', margin: '0 0 10px 0'}}>
              💰 TOTAL PORTFOLIO VALUE: ${formatBalance(portfolio.total_value_usd)}
            </h2>
            <p style={{color: '#666', margin: '0'}}>
              Complete access to your converted crypto holdings + T52M supply
            </p>
          </div>
        )}
      </header>

      {/* Action Buttons */}
      <div style={{display: 'flex', justifyContent: 'center', gap: '15px', marginBottom: '30px', flexWrap: 'wrap'}}>
        <button 
          onClick={() => setShowBridgeModal(true)}
          style={{
            padding: '15px 30px', 
            backgroundColor: '#007bff', 
            color: 'white', 
            border: 'none', 
            borderRadius: '10px', 
            fontSize: '18px', 
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          🌉 Bridge Tokens
        </button>
      </div>

      {/* Token Categories */}
      {tokensSummary && (
        <div style={{marginBottom: '30px'}}>
          
          {/* Converted Portfolio Section */}
          <div style={{marginBottom: '30px'}}>
            <h2 style={{color: '#28a745', borderBottom: '2px solid #28a745', paddingBottom: '10px'}}>
              💎 Your Converted Portfolio (${formatBalance(tokensSummary.converted_portfolio.total_value_usd)})
            </h2>
            <p style={{color: '#666', marginBottom: '20px'}}>
              {tokensSummary.converted_portfolio.description}
            </p>
            
            <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px'}}>
              {Object.entries(tokensSummary.converted_portfolio.tokens).map(([symbol, token]) => (
                <div key={symbol} style={{
                  padding: '20px',
                  border: '3px solid #28a745',
                  borderRadius: '15px',
                  backgroundColor: '#f8fff8',
                  textAlign: 'center'
                }}>
                  <div style={{fontSize: '32px', marginBottom: '10px'}}>{token.logo}</div>
                  <h3 style={{margin: '0 0 10px 0', color: '#28a745'}}>{symbol}</h3>
                  <p style={{margin: '5px 0', fontSize: '20px', fontWeight: 'bold'}}>
                    {formatBalance(token.balance)} {symbol}
                  </p>
                  <p style={{margin: '5px 0', color: '#666'}}>
                    ${formatBalance(token.value_usd)}
                  </p>
                  <p style={{margin: '0', fontSize: '14px', color: '#888'}}>
                    {token.name}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Current Holdings Section */}
          <div style={{marginBottom: '30px'}}>
            <h2 style={{color: '#007bff', borderBottom: '2px solid #007bff', paddingBottom: '10px'}}>
              🔥 Current Holdings (${formatBalance(tokensSummary.current_holdings.total_value_usd)})
            </h2>
            <p style={{color: '#666', marginBottom: '20px'}}>
              {tokensSummary.current_holdings.description}
            </p>
            
            <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px'}}>
              {Object.entries(tokensSummary.current_holdings.tokens).map(([symbol, token]) => (
                <div key={symbol} style={{
                  padding: '20px',
                  border: '3px solid #007bff',
                  borderRadius: '15px',
                  backgroundColor: '#f8f9ff',
                  textAlign: 'center'
                }}>
                  <div style={{fontSize: '32px', marginBottom: '10px'}}>{token.logo}</div>
                  <h3 style={{margin: '0 0 10px 0', color: '#007bff'}}>{symbol}</h3>
                  <p style={{margin: '5px 0', fontSize: '20px', fontWeight: 'bold'}}>
                    {formatBalance(token.balance)} {symbol}
                  </p>
                  <p style={{margin: '5px 0', color: '#666'}}>
                    ${formatBalance(token.value_usd)}
                  </p>
                  <p style={{margin: '0', fontSize: '14px', color: '#888'}}>
                    {token.name}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Purchase Targets Section */}
          <div style={{marginBottom: '30px'}}>
            <h2 style={{color: '#f39c12', borderBottom: '2px solid #f39c12', paddingBottom: '10px'}}>
              🎯 Purchase Targets
            </h2>
            <p style={{color: '#666', marginBottom: '20px'}}>
              Tokens you want to acquire using your portfolio
            </p>
            
            <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px'}}>
              {Object.entries(tokensSummary.purchase_targets.tokens).map(([symbol, token]) => (
                <div key={symbol} style={{
                  padding: '20px',
                  border: '3px solid #f39c12',
                  borderRadius: '15px',
                  backgroundColor: '#fffbf0',
                  textAlign: 'center'
                }}>
                  <div style={{fontSize: '32px', marginBottom: '10px'}}>{token.logo}</div>
                  <h3 style={{margin: '0 0 10px 0', color: '#f39c12'}}>{symbol}</h3>
                  <p style={{margin: '5px 0', fontSize: '18px', fontWeight: 'bold', color: '#f39c12'}}>
                    TARGET: $0.10 per token
                  </p>
                  <p style={{margin: '0', fontSize: '14px', color: '#888'}}>
                    {token.name}
                  </p>
                  <button 
                    onClick={() => {setDestToken(symbol); setShowBridgeModal(true);}}
                    style={{
                      marginTop: '10px',
                      padding: '8px 16px',
                      backgroundColor: '#f39c12',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      cursor: 'pointer'
                    }}
                  >
                    Buy {symbol}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Bridge Modal */}
      {showBridgeModal && portfolio && (
        <div style={{
          position: 'fixed', 
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white', 
            padding: '30px', 
            borderRadius: '15px', 
            minWidth: '500px',
            maxHeight: '80vh',
            overflow: 'auto'
          }}>
            <h3>🌉 Bridge Your Tokens</h3>
            <p style={{color: '#666', marginBottom: '20px'}}>
              Convert between any of your tokens instantly
            </p>
            
            <div style={{marginBottom: '20px'}}>
              <label style={{display: 'block', marginBottom: '8px', fontWeight: 'bold'}}>From Token:</label>
              <select 
                value={sourceToken} 
                onChange={(e) => setSourceToken(e.target.value)}
                style={{
                  width: '100%', 
                  padding: '12px', 
                  fontSize: '16px',
                  borderRadius: '8px',
                  border: '2px solid #ddd'
                }}
              >
                {portfolio.tokens && Object.entries(portfolio.tokens)
                  .filter(([_, token]) => token.balance > 0)
                  .map(([symbol, token]) => (
                  <option key={symbol} value={symbol}>
                    {symbol} - {formatBalance(token.balance)} available (${formatBalance(token.value_usd)})
                  </option>
                ))}
              </select>
            </div>
            
            <div style={{marginBottom: '20px'}}>
              <label style={{display: 'block', marginBottom: '8px', fontWeight: 'bold'}}>To Token:</label>
              <select 
                value={destToken} 
                onChange={(e) => setDestToken(e.target.value)}
                style={{
                  width: '100%', 
                  padding: '12px', 
                  fontSize: '16px',
                  borderRadius: '8px',
                  border: '2px solid #ddd'
                }}
              >
                <option value="CDT">🎨 CDT - Creative Dollar Token</option>
                <option value="USDC">💵 USDC - USD Coin</option>
                <option value="DOGE">🐕 DOGE - Dogecoin</option>
                <option value="TRX">⚡ TRX - TRON</option>
                <option value="CRT">💎 CRT - Casino Revenue Token</option>
                <option value="T52M">🔥 T52M - Tiger Token</option>
              </select>
            </div>
            
            <div style={{marginBottom: '20px'}}>
              <label style={{display: 'block', marginBottom: '8px', fontWeight: 'bold'}}>Amount:</label>
              <input
                type="number"
                value={bridgeAmount}
                onChange={(e) => setBridgeAmount(parseFloat(e.target.value))}
                max={portfolio.tokens[sourceToken]?.balance || 0}
                style={{
                  width: '100%', 
                  padding: '12px', 
                  fontSize: '16px',
                  borderRadius: '8px',
                  border: '2px solid #ddd'
                }}
              />
              <small style={{color: '#666'}}>
                Available: {formatBalance(portfolio.tokens[sourceToken]?.balance || 0)} {sourceToken}
              </small>
            </div>
            
            {bridgeAmount > 0 && portfolio.tokens[sourceToken] && (
              <div style={{
                backgroundColor: '#f8f9fa', 
                padding: '15px', 
                borderRadius: '8px', 
                marginBottom: '20px'
              }}>
                <h4>📊 Bridge Preview:</h4>
                <p>
                  <strong>Convert:</strong> {formatBalance(bridgeAmount)} {sourceToken}
                </p>
                <p>
                  <strong>USD Value:</strong> ${formatBalance(bridgeAmount * portfolio.tokens[sourceToken].price_usd)}
                </p>
                <p>
                  <strong>You'll Get:</strong> ~{formatBalance((bridgeAmount * portfolio.tokens[sourceToken].price_usd) / (destToken === 'CDT' ? 0.10 : 1))} {destToken}
                </p>
              </div>
            )}
            
            <div style={{display: 'flex', gap: '15px'}}>
              <button 
                onClick={executeBridge}
                disabled={loading || bridgeAmount <= 0}
                style={{
                  flex: 1, 
                  padding: '15px', 
                  backgroundColor: loading ? '#ccc' : '#007bff', 
                  color: 'white', 
                  border: 'none', 
                  borderRadius: '8px',
                  fontSize: '16px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontWeight: 'bold'
                }}
              >
                {loading ? 'Processing...' : `🌉 Execute Bridge`}
              </button>
              <button 
                onClick={() => setShowBridgeModal(false)}
                style={{
                  flex: 1, 
                  padding: '15px', 
                  backgroundColor: '#6c757d', 
                  color: 'white', 
                  border: 'none', 
                  borderRadius: '8px',
                  fontSize: '16px',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Portfolio Summary */}
      <div style={{
        backgroundColor: '#f8f9fa', 
        padding: '30px', 
        borderRadius: '15px',
        marginTop: '30px'
      }}>
        <h3>🏦 Your Complete Tiger Bank System</h3>
        <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px'}}>
          <div>
            <h4>💎 Converted Assets</h4>
            <ul style={{margin: 0, fontSize: '14px'}}>
              <li>319,000 USDC</li>
              <li>13,000,000 DOGE</li>
              <li>3,900,000 TRX</li>
              <li>21,000,000 CRT</li>
            </ul>
          </div>
          <div>
            <h4>🔥 Current Holdings</h4>
            <ul style={{margin: 0, fontSize: '14px'}}>
              <li>52,000,000 T52M</li>
              <li>Full token supply</li>
              <li>Bridge to any crypto</li>
            </ul>
          </div>
          <div>
            <h4>🎯 Purchase Power</h4>
            <ul style={{margin: 0, fontSize: '14px'}}>
              <li>Bridge to CDT</li>
              <li>Instant conversions</li>
              <li>No liquidity limits</li>
            </ul>
          </div>
          <div>
            <h4>🌉 Bridge System</h4>
            <ul style={{margin: 0, fontSize: '14px'}}>
              <li>Any token to any token</li>
              <li>Real-time rates</li>
              <li>Instant execution</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;