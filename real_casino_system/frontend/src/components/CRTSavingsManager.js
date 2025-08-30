import React, { useState, useEffect } from 'react';

const CRTSavingsManager = ({ walletAddress, crtBalance, onBalanceUpdate, backendUrl }) => {
  const [savingsSummary, setSavingsSummary] = useState(null);
  const [poolAmount, setPoolAmount] = useState('100000');
  const [poolType, setPoolType] = useState('CRT/SOL');
  const [isCreatingPool, setIsCreatingPool] = useState(false);
  const [savingsHistory, setSavingsHistory] = useState([]);
  const [poolResults, setPoolResults] = useState([]);

  useEffect(() => {
    if (walletAddress) {
      fetchSavingsSummary();
    }
  }, [walletAddress]);

  const fetchSavingsSummary = async () => {
    try {
      const response = await fetch(`${backendUrl}/savings/crt-summary?wallet_address=${walletAddress}`);
      const data = await response.json();
      
      if (data.success) {
        setSavingsSummary(data.savings_summary);
      }
    } catch (error) {
      console.error('Failed to fetch savings summary:', error);
    }
  };

  const createSavingsPool = async () => {
    const amount = parseFloat(poolAmount);
    
    if (amount <= 0 || amount > crtBalance) {
      alert('Invalid pool amount');
      return;
    }

    setIsCreatingPool(true);
    try {
      const response = await fetch(`${backendUrl}/savings/create-crt-pool`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: walletAddress,
          crt_amount: amount,
          pool_type: poolType
        })
      });

      const result = await response.json();
      
      if (result.success) {
        alert(`✅ CRT Savings Pool Created!\nPool: ${result.pool_result.pool_address}`);
        
        // Add to pool results
        const poolResult = {
          ...result.pool_result,
          created_at: new Date().toISOString(),
          crt_amount: amount,
          pool_type: poolType
        };
        setPoolResults(prev => [poolResult, ...prev]);
        
        // Clear form
        setPoolAmount('100000');
        
        // Update balance and summary
        setTimeout(() => {
          onBalanceUpdate();
          fetchSavingsSummary();
        }, 2000);
      } else {
        alert(`❌ Pool creation failed: ${result.error}`);
      }
    } catch (error) {
      console.error('Pool creation failed:', error);
      alert('Pool creation failed due to network error');
    }
    setIsCreatingPool(false);
  };

  const calculatePoolValue = () => {
    const amount = parseFloat(poolAmount) || 0;
    const crtValue = amount * 0.01; // $0.01 per CRT
    
    if (poolType === 'CRT/SOL') {
      const solValue = crtValue / 240; // $240 per SOL
      return {
        crt_amount: amount,
        sol_amount: solValue,
        total_usd: crtValue * 2 // Both sides of the pool
      };
    } else if (poolType === 'CRT/USDC') {
      return {
        crt_amount: amount,
        usdc_amount: crtValue,
        total_usd: crtValue * 2 // Both sides of the pool
      };
    }
    return null;
  };

  const poolValue = calculatePoolValue();

  return (
    <div className="crt-savings-manager">
      <div className="savings-header">
        <h2>💰 CRT Savings System</h2>
        <p>Convert your CRT tokens into real cryptocurrency investments and liquidity pools</p>
      </div>

      {/* Savings Overview */}
      <div className="savings-overview">
        <div className="overview-card">
          <h3>📊 Your CRT Savings</h3>
          {savingsSummary ? (
            <div className="savings-stats">
              <div className="stat-item">
                <div className="stat-label">Total Saved:</div>
                <div className="stat-value">{savingsSummary.summary?.total_saved?.toLocaleString() || '0'} CRT</div>
              </div>
              <div className="stat-item">
                <div className="stat-label">Active Positions:</div>
                <div className="stat-value">{savingsSummary.summary?.active_positions?.length || 0}</div>
              </div>
              <div className="stat-item">
                <div className="stat-label">Total Earnings:</div>
                <div className="stat-value">${savingsSummary.summary?.total_earnings?.toFixed(2) || '0.00'}</div>
              </div>
            </div>
          ) : (
            <div className="no-savings">
              <p>No savings positions yet. Start betting to create automatic savings!</p>
            </div>
          )}
        </div>

        <div className="savings-info">
          <h3>🎰 How Savings Work</h3>
          <ul>
            <li><strong>Automatic:</strong> 50% of casino losses become savings</li>
            <li><strong>Real Pools:</strong> Creates actual DEX liquidity pools</li>
            <li><strong>Earn Yield:</strong> Generate returns from DeFi protocols</li>
            <li><strong>Compound:</strong> Reinvest earnings automatically</li>
          </ul>
        </div>
      </div>

      {/* Manual Pool Creation */}
      <div className="manual-pool-section">
        <h3>🏊‍♂️ Create CRT Liquidity Pool</h3>
        <p>Manually create a liquidity pool with your CRT tokens to earn trading fees</p>
        
        <div className="pool-creation-form">
          <div className="form-row">
            <div className="form-group">
              <label>Pool Type:</label>
              <select 
                value={poolType} 
                onChange={(e) => setPoolType(e.target.value)}
                className="pool-type-select"
              >
                <option value="CRT/SOL">CRT/SOL Pool</option>
                <option value="CRT/USDC">CRT/USDC Pool</option>
              </select>
            </div>

            <div className="form-group">
              <label>CRT Amount:</label>
              <div className="amount-input-group">
                <input
                  type="number"
                  value={poolAmount}
                  onChange={(e) => setPoolAmount(e.target.value)}
                  min="10000"
                  max={crtBalance}
                  step="10000"
                  className="pool-amount-input"
                />
                <span className="currency-label">CRT</span>
              </div>
              <div className="quick-amounts">
                <button onClick={() => setPoolAmount('100000')}>100K</button>
                <button onClick={() => setPoolAmount('500000')}>500K</button>
                <button onClick={() => setPoolAmount('1000000')}>1M</button>
                <button onClick={() => setPoolAmount('5000000')}>5M</button>
                <button onClick={() => setPoolAmount(Math.floor(crtBalance * 0.1).toString())}>10%</button>
              </div>
            </div>
          </div>

          {poolValue && (
            <div className="pool-preview">
              <h4>Pool Preview:</h4>
              <div className="preview-details">
                <div className="preview-item">
                  <span>CRT Contribution:</span>
                  <span>{poolValue.crt_amount.toLocaleString()} CRT</span>
                </div>
                {poolType === 'CRT/SOL' && (
                  <div className="preview-item">
                    <span>SOL Required:</span>
                    <span>{poolValue.sol_amount.toFixed(6)} SOL</span>
                  </div>
                )}
                {poolType === 'CRT/USDC' && (
                  <div className="preview-item">
                    <span>USDC Required:</span>
                    <span>{poolValue.usdc_amount.toFixed(2)} USDC</span>
                  </div>
                )}
                <div className="preview-item total">
                  <span>Total Pool Value:</span>
                  <span>${poolValue.total_usd.toFixed(2)}</span>
                </div>
              </div>
            </div>
          )}

          <button
            className="create-pool-button"
            onClick={createSavingsPool}
            disabled={isCreatingPool || !poolAmount || parseFloat(poolAmount) > crtBalance}
          >
            {isCreatingPool ? '🏊‍♂️ Creating Pool...' : `🏊‍♂️ Create ${poolType} Pool`}
          </button>
        </div>
      </div>

      {/* Savings Strategies */}
      <div className="savings-strategies">
        <h3>📈 Available Savings Strategies</h3>
        <div className="strategy-grid">
          <div className="strategy-card">
            <h4>🏊‍♂️ DEX Liquidity Pools</h4>
            <p>Create real liquidity pools on Orca DEX to earn trading fees</p>
            <div className="strategy-stats">
              <span>APR: 15-25%</span>
              <span>Risk: Medium</span>
            </div>
          </div>

          <div className="strategy-card">
            <h4>🌱 Yield Farming</h4>
            <p>Stake CRT tokens in DeFi protocols for consistent returns</p>
            <div className="strategy-stats">
              <span>APY: 8-12%</span>
              <span>Risk: Low</span>
            </div>
          </div>

          <div className="strategy-card">
            <h4>📊 Compound Interest</h4>
            <p>Lend CRT tokens to earn daily compound interest</p>
            <div className="strategy-stats">
              <span>APY: 5-8%</span>
              <span>Risk: Very Low</span>
            </div>
          </div>
        </div>
      </div>

      {/* Created Pools */}
      {poolResults.length > 0 && (
        <div className="created-pools">
          <h3>🏊‍♂️ Your Liquidity Pools</h3>
          <div className="pools-list">
            {poolResults.map((pool, index) => (
              <div key={index} className="pool-item">
                <div className="pool-header">
                  <h4>{pool.pool_type} Pool</h4>
                  <span className="pool-status">✅ Active</span>
                </div>
                
                <div className="pool-details">
                  <div className="pool-stat">
                    <span>CRT Amount:</span>
                    <span>{pool.crt_amount?.toLocaleString()} CRT</span>
                  </div>
                  <div className="pool-stat">
                    <span>LP Tokens:</span>
                    <span>{pool.lp_tokens_received?.toLocaleString()}</span>
                  </div>
                  <div className="pool-stat">
                    <span>Est. APR:</span>
                    <span>{pool.apr_estimate}%</span>
                  </div>
                </div>

                <div className="pool-actions">
                  <a 
                    href={pool.explorer_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="view-transaction"
                  >
                    📍 View on Explorer
                  </a>
                  <div className="pool-address">
                    Pool: {pool.pool_address?.slice(0, 8)}...{pool.pool_address?.slice(-8)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <style jsx>{`
        .crt-savings-manager {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
        }

        .savings-header {
          text-align: center;
          margin-bottom: 40px;
          padding: 30px;
          background: linear-gradient(135deg, #2d8f2d, #1a5f1a);
          color: white;
          border-radius: 15px;
        }

        .savings-overview {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 30px;
          margin-bottom: 40px;
        }

        .overview-card {
          background: white;
          padding: 30px;
          border-radius: 15px;
          border: 2px solid #4caf50;
        }

        .savings-stats {
          display: flex;
          flex-direction: column;
          gap: 15px;
          margin-top: 20px;
        }

        .stat-item {
          display: flex;
          justify-content: space-between;
          padding: 10px;
          background: #f8f9fa;
          border-radius: 8px;
        }

        .stat-value {
          font-weight: bold;
          color: #2d8f2d;
        }

        .savings-info {
          background: #f8f9fa;
          padding: 30px;
          border-radius: 15px;
          border: 1px solid #ddd;
        }

        .savings-info ul {
          margin-top: 15px;
          padding-left: 20px;
        }

        .savings-info li {
          margin-bottom: 10px;
          line-height: 1.5;
        }

        .manual-pool-section {
          background: white;
          padding: 40px;
          border-radius: 15px;
          border: 2px solid #3498db;
          margin-bottom: 40px;
        }

        .manual-pool-section h3 {
          color: #3498db;
          margin-bottom: 20px;
        }

        .pool-creation-form {
          margin-top: 30px;
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 30px;
          margin-bottom: 30px;
        }

        .form-group label {
          display: block;
          margin-bottom: 8px;
          font-weight: bold;
          color: #333;
        }

        .pool-type-select, .pool-amount-input {
          width: 100%;
          padding: 12px;
          border: 1px solid #ddd;
          border-radius: 8px;
          font-size: 1em;
        }

        .amount-input-group {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .currency-label {
          font-weight: bold;
          color: #4caf50;
        }

        .quick-amounts {
          display: flex;
          gap: 10px;
          margin-top: 10px;
        }

        .quick-amounts button {
          padding: 8px 16px;
          border: 1px solid #3498db;
          background: white;
          color: #3498db;
          border-radius: 5px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .quick-amounts button:hover {
          background: #3498db;
          color: white;
        }

        .pool-preview {
          background: #e8f4f8;
          padding: 20px;
          border-radius: 10px;
          margin: 20px 0;
          border: 1px solid #3498db;
        }

        .preview-details {
          display: flex;
          flex-direction: column;
          gap: 10px;
          margin-top: 15px;
        }

        .preview-item {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          border-bottom: 1px solid rgba(52, 152, 219, 0.2);
        }

        .preview-item.total {
          font-weight: bold;
          color: #3498db;
          border-bottom: 2px solid #3498db;
          margin-top: 10px;
          padding-top: 15px;
        }

        .create-pool-button {
          width: 100%;
          padding: 15px 30px;
          background: linear-gradient(135deg, #3498db, #2980b9);
          color: white;
          border: none;
          border-radius: 10px;
          font-size: 1.1em;
          font-weight: bold;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .create-pool-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
        }

        .create-pool-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .savings-strategies {
          margin-bottom: 40px;
        }

        .strategy-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
          margin-top: 20px;
        }

        .strategy-card {
          background: white;
          padding: 25px;
          border-radius: 12px;
          border: 1px solid #ddd;
          transition: all 0.3s ease;
        }

        .strategy-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }

        .strategy-card h4 {
          color: #2d8f2d;
          margin-bottom: 10px;
        }

        .strategy-stats {
          display: flex;
          gap: 15px;
          margin-top: 15px;
          font-size: 0.9em;
        }

        .strategy-stats span {
          background: #f8f9fa;
          padding: 5px 10px;
          border-radius: 15px;
          font-weight: bold;
        }

        .created-pools {
          background: white;
          padding: 30px;
          border-radius: 15px;
          border: 1px solid #ddd;
        }

        .pools-list {
          display: flex;
          flex-direction: column;
          gap: 20px;
          margin-top: 20px;
        }

        .pool-item {
          background: #f8f9fa;
          padding: 25px;
          border-radius: 12px;
          border: 1px solid #eee;
        }

        .pool-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .pool-header h4 {
          margin: 0;
          color: #3498db;
        }

        .pool-status {
          background: #28a745;
          color: white;
          padding: 5px 12px;
          border-radius: 15px;
          font-size: 0.8em;
          font-weight: bold;
        }

        .pool-details {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 15px;
          margin-bottom: 20px;
        }

        .pool-stat {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .pool-stat span:first-child {
          font-size: 0.9em;
          color: #666;
        }

        .pool-stat span:last-child {
          font-weight: bold;
          color: #333;
        }

        .pool-actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding-top: 15px;
          border-top: 1px solid #ddd;
        }

        .view-transaction {
          color: #3498db;
          text-decoration: none;
          font-weight: bold;
        }

        .view-transaction:hover {
          text-decoration: underline;
        }

        .pool-address {
          font-family: monospace;
          font-size: 0.9em;
          color: #666;
        }

        .no-savings {
          text-align: center;
          color: #666;
          font-style: italic;
        }
      `}</style>
    </div>
  );
};

export default CRTSavingsManager;