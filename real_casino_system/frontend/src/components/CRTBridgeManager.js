import React, { useState, useEffect } from 'react';

const CRTBridgeManager = ({ walletAddress, crtBalance, onBalanceUpdate, backendUrl }) => {
  const [supportedPairs, setSupportedPairs] = useState({});
  const [selectedBridge, setSelectedBridge] = useState('CRT/SOL');
  const [bridgeValue, setBridgeValue] = useState('10000');
  const [isCreatingBridge, setIsCreatingBridge] = useState(false);
  const [bridgeEstimation, setBridgeEstimation] = useState(null);
  const [bridgeResults, setBridgeResults] = useState([]);
  const [bridgeSummary, setBridgeSummary] = useState(null);

  useEffect(() => {
    if (walletAddress) {
      fetchSupportedPairs();
      fetchBridgeSummary();
    }
  }, [walletAddress]);

  useEffect(() => {
    if (selectedBridge && bridgeValue) {
      estimateBridgeRequirements();
    }
  }, [selectedBridge, bridgeValue]);

  const fetchSupportedPairs = async () => {
    try {
      const response = await fetch(`${backendUrl}/bridge/supported-pairs`);
      const data = await response.json();
      
      if (data.success) {
        setSupportedPairs(data.bridge_pairs);
      }
    } catch (error) {
      console.error('Failed to fetch supported bridge pairs:', error);
    }
  };

  const fetchBridgeSummary = async () => {
    try {
      const response = await fetch(`${backendUrl}/bridge/crt-summary?wallet_address=${walletAddress}`);
      const data = await response.json();
      
      if (data.success) {
        setBridgeSummary(data.bridge_summary);
      }
    } catch (error) {
      console.error('Failed to fetch bridge summary:', error);
    }
  };

  const estimateBridgeRequirements = async () => {
    try {
      const targetValue = parseFloat(bridgeValue);
      if (targetValue <= 0) return;

      const response = await fetch(
        `${backendUrl}/bridge/estimate-requirements?bridge_pair=${selectedBridge}&target_value_usd=${targetValue}`
      );
      const data = await response.json();
      
      if (data.success) {
        setBridgeEstimation(data);
      }
    } catch (error) {
      console.error('Failed to estimate bridge requirements:', error);
    }
  };

  const createBridgePool = async () => {
    const targetValue = parseFloat(bridgeValue);
    
    if (targetValue <= 0) {
      alert('Invalid bridge pool value');
      return;
    }

    if (!bridgeEstimation || bridgeEstimation.required_crt > crtBalance) {
      alert(`Insufficient CRT balance! Need ${bridgeEstimation?.required_crt?.toLocaleString() || 'N/A'} CRT`);
      return;
    }

    setIsCreatingBridge(true);
    try {
      const response = await fetch(`${backendUrl}/bridge/create-crt-bridge-pool`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          wallet_address: walletAddress,
          bridge_pair: selectedBridge,
          target_value_usd: targetValue
        })
      });

      const result = await response.json();
      
      if (result.success) {
        alert(`✅ CRT Bridge Pool Created!\nBridge: ${result.bridge_result.bridge_pool.bridge_address}`);
        
        // Add to bridge results
        const bridgeResult = {
          ...result.bridge_result.bridge_pool,
          created_at: new Date().toISOString(),
          target_value_usd: targetValue,
          bridge_pair: selectedBridge
        };
        setBridgeResults(prev => [bridgeResult, ...prev]);
        
        // Clear form
        setBridgeValue('10000');
        setBridgeEstimation(null);
        
        // Update balance and summary
        setTimeout(() => {
          onBalanceUpdate();
          fetchBridgeSummary();
        }, 2000);
      } else {
        alert(`❌ Bridge pool creation failed: ${result.error}`);
      }
    } catch (error) {
      console.error('Bridge pool creation failed:', error);
      alert('Bridge pool creation failed due to network error');
    }
    setIsCreatingBridge(false);
  };

  const getBridgeIcon = (bridgePair) => {
    switch (bridgePair) {
      case 'CRT/SOL': return '🟣';
      case 'CRT/USDC': return '💚';
      case 'CRT/ETH': return '🔷';
      case 'CRT/BTC': return '🟡';
      default: return '🌉';
    }
  };

  const getBridgeTypeLabel = (bridgeType) => {
    switch (bridgeType) {
      case 'native': return 'Native Bridge';
      case 'stable': return 'Stablecoin Bridge';
      case 'cross_chain': return 'Cross-Chain Bridge';
      case 'wrapped': return 'Wrapped Token Bridge';
      default: return 'Bridge';
    }
  };

  return (
    <div className="crt-bridge-manager">
      <div className="bridge-header">
        <h2>🌉 CRT Bridge Pool Manager</h2>
        <p>Create cross-chain bridge pools to enable CRT token transfers between different blockchains</p>
      </div>

      {/* Bridge Overview */}
      <div className="bridge-overview">
        <div className="overview-card">
          <h3>📊 Your Bridge Pools</h3>
          {bridgeSummary ? (
            <div className="bridge-stats">
              <div className="stat-item">
                <div className="stat-label">Total Bridge Pools:</div>
                <div className="stat-value">{bridgeSummary.summary?.total_bridge_pools || 0}</div>
              </div>
              <div className="stat-item">
                <div className="stat-label">Total Bridge Value:</div>
                <div className="stat-value">${bridgeSummary.summary?.total_bridge_value_usd?.toFixed(2) || '0.00'}</div>
              </div>
              <div className="stat-item">
                <div className="stat-label">Active Bridges:</div>
                <div className="stat-value">{bridgeSummary.summary?.active_bridges?.length || 0}</div>
              </div>
            </div>
          ) : (
            <div className="no-bridges">
              <p>No bridge pools yet. Create your first cross-chain CRT bridge!</p>
            </div>
          )}
        </div>

        <div className="bridge-info">
          <h3>🌉 What are Bridge Pools?</h3>
          <ul>
            <li><strong>Cross-Chain:</strong> Transfer CRT between different blockchains</li>
            <li><strong>Liquidity:</strong> Provide liquidity for cross-chain swaps</li>
            <li><strong>Earn Fees:</strong> Generate income from bridge transactions</li>
            <li><strong>Real Infrastructure:</strong> Actual bridge protocols, not simulations</li>
          </ul>
        </div>
      </div>

      {/* Bridge Creation Form */}
      <div className="bridge-creation-section">
        <h3>🌉 Create CRT Bridge Pool</h3>
        <p>Create a real cross-chain bridge pool to enable CRT transfers</p>
        
        <div className="bridge-creation-form">
          <div className="form-row">
            <div className="form-group">
              <label>Bridge Pair:</label>
              <select 
                value={selectedBridge} 
                onChange={(e) => setSelectedBridge(e.target.value)}
                className="bridge-select"
              >
                {Object.entries(supportedPairs).map(([pair, config]) => (
                  <option key={pair} value={pair}>
                    {getBridgeIcon(pair)} {pair} - {getBridgeTypeLabel(config.bridge_type)}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Bridge Pool Value (USD):</label>
              <div className="value-input-group">
                <span className="currency-symbol">$</span>
                <input
                  type="number"
                  value={bridgeValue}
                  onChange={(e) => setBridgeValue(e.target.value)}
                  min="1000"
                  step="1000"
                  className="bridge-value-input"
                />
              </div>
              <div className="quick-values">
                <button onClick={() => setBridgeValue('10000')}>$10K</button>
                <button onClick={() => setBridgeValue('25000')}>$25K</button>
                <button onClick={() => setBridgeValue('50000')}>$50K</button>
                <button onClick={() => setBridgeValue('100000')}>$100K</button>
              </div>
            </div>
          </div>

          {/* Bridge Estimation */}
          {bridgeEstimation && (
            <div className="bridge-estimation">
              <h4>Bridge Pool Requirements:</h4>
              <div className="estimation-details">
                <div className="estimation-item">
                  <span>Required CRT:</span>
                  <span className={crtBalance >= bridgeEstimation.required_crt ? 'sufficient' : 'insufficient'}>
                    {bridgeEstimation.required_crt?.toLocaleString()} CRT
                  </span>
                </div>
                <div className="estimation-item">
                  <span>Required {bridgeEstimation.quote_currency}:</span>
                  <span>{bridgeEstimation.required_quote?.toFixed(6)} {bridgeEstimation.quote_currency}</span>
                </div>
                <div className="estimation-item">
                  <span>Exchange Rate:</span>
                  <span>1 CRT = {bridgeEstimation.exchange_rate?.toFixed(8)} {bridgeEstimation.quote_currency}</span>
                </div>
                <div className="estimation-item total">
                  <span>Total Pool Value:</span>
                  <span>${bridgeEstimation.target_value_usd?.toLocaleString()}</span>
                </div>
              </div>

              {supportedPairs[selectedBridge] && (
                <div className="bridge-config">
                  <h5>Bridge Configuration:</h5>
                  <div className="config-details">
                    <div>Network: {supportedPairs[selectedBridge].network}</div>
                    <div>Type: {getBridgeTypeLabel(supportedPairs[selectedBridge].bridge_type)}</div>
                    <div>Fee Rate: {(supportedPairs[selectedBridge].fee_rate * 100).toFixed(2)}%</div>
                    <div>Description: {supportedPairs[selectedBridge].description}</div>
                  </div>
                </div>
              )}
            </div>
          )}

          <button
            className="create-bridge-button"
            onClick={createBridgePool}
            disabled={isCreatingBridge || !bridgeEstimation || (bridgeEstimation && bridgeEstimation.required_crt > crtBalance)}
          >
            {isCreatingBridge ? '🌉 Creating Bridge Pool...' : `🌉 Create ${selectedBridge} Bridge Pool`}
          </button>
        </div>
      </div>

      {/* Supported Bridge Pairs */}
      <div className="supported-bridges">
        <h3>🌐 Supported Bridge Pairs</h3>
        <div className="bridges-grid">
          {Object.entries(supportedPairs).map(([pair, config]) => (
            <div key={pair} className="bridge-card">
              <div className="bridge-header-card">
                <span className="bridge-icon">{getBridgeIcon(pair)}</span>
                <h4>{pair}</h4>
                <span className="bridge-type">{getBridgeTypeLabel(config.bridge_type)}</span>
              </div>
              
              <div className="bridge-details">
                <p>{config.description}</p>
                <div className="bridge-stats">
                  <span>Network: {config.network}</span>
                  <span>Fee: {(config.fee_rate * 100).toFixed(2)}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Created Bridge Pools */}
      {bridgeResults.length > 0 && (
        <div className="created-bridges">
          <h3>🌉 Your Bridge Pools</h3>
          <div className="bridges-list">
            {bridgeResults.map((bridge, index) => (
              <div key={index} className="bridge-item">
                <div className="bridge-item-header">
                  <h4>{getBridgeIcon(bridge.bridge_pair)} {bridge.bridge_pair} Bridge</h4>
                  <span className="bridge-status">✅ Active</span>
                </div>
                
                <div className="bridge-item-details">
                  <div className="bridge-stat">
                    <span>Bridge Value:</span>
                    <span>${bridge.target_value_usd?.toLocaleString()}</span>
                  </div>
                  <div className="bridge-stat">
                    <span>Bridge Type:</span>
                    <span>{getBridgeTypeLabel(bridge.bridge_type)}</span>
                  </div>
                  <div className="bridge-stat">
                    <span>Network:</span>
                    <span>{bridge.network}</span>
                  </div>
                  <div className="bridge-stat">
                    <span>Daily Limit:</span>
                    <span>${bridge.daily_transfer_limit?.toLocaleString()}</span>
                  </div>
                </div>

                <div className="bridge-addresses">
                  <div className="address-item">
                    <span>Bridge Address:</span>
                    <code>{bridge.bridge_address?.slice(0, 16)}...{bridge.bridge_address?.slice(-8)}</code>
                  </div>
                  <div className="address-item">
                    <span>Pool Address:</span>
                    <code>{bridge.pool_address?.slice(0, 16)}...{bridge.pool_address?.slice(-8)}</code>
                  </div>
                </div>

                <div className="bridge-actions">
                  <a 
                    href={bridge.explorer_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="view-transaction"
                  >
                    📍 View on Explorer
                  </a>
                  <div className="supported-chains">
                    <span>Supported Chains:</span>
                    <div className="chain-list">
                      {bridge.supported_chains?.map((chain, i) => (
                        <span key={i} className="chain-tag">{chain}</span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <style jsx>{`
        .crt-bridge-manager {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
        }

        .bridge-header {
          text-align: center;
          margin-bottom: 40px;
          padding: 30px;
          background: linear-gradient(135deg, #6a4c93, #9c88ff);
          color: white;
          border-radius: 15px;
        }

        .bridge-overview {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 30px;
          margin-bottom: 40px;
        }

        .overview-card {
          background: white;
          padding: 30px;
          border-radius: 15px;
          border: 2px solid #6a4c93;
        }

        .bridge-stats {
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
          color: #6a4c93;
        }

        .bridge-info {
          background: #f8f9fa;
          padding: 30px;
          border-radius: 15px;
          border: 1px solid #ddd;
        }

        .bridge-info ul {
          margin-top: 15px;
          padding-left: 20px;
        }

        .bridge-info li {
          margin-bottom: 10px;
          line-height: 1.5;
        }

        .bridge-creation-section {
          background: white;
          padding: 40px;
          border-radius: 15px;
          border: 2px solid #9c88ff;
          margin-bottom: 40px;
        }

        .bridge-creation-section h3 {
          color: #6a4c93;
          margin-bottom: 20px;
        }

        .bridge-creation-form {
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

        .bridge-select, .bridge-value-input {
          width: 100%;
          padding: 12px;
          border: 1px solid #ddd;
          border-radius: 8px;
          font-size: 1em;
        }

        .value-input-group {
          display: flex;
          align-items: center;
          border: 1px solid #ddd;
          border-radius: 8px;
          overflow: hidden;
        }

        .currency-symbol {
          background: #f8f9fa;
          padding: 12px;
          font-weight: bold;
          color: #6a4c93;
          border-right: 1px solid #ddd;
        }

        .bridge-value-input {
          border: none;
          flex: 1;
        }

        .quick-values {
          display: flex;
          gap: 10px;
          margin-top: 10px;
        }

        .quick-values button {
          padding: 8px 16px;
          border: 1px solid #6a4c93;
          background: white;
          color: #6a4c93;
          border-radius: 5px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .quick-values button:hover {
          background: #6a4c93;
          color: white;
        }

        .bridge-estimation {
          background: #f0e6ff;
          padding: 20px;
          border-radius: 10px;
          margin: 20px 0;
          border: 1px solid #9c88ff;
        }

        .estimation-details {
          display: flex;
          flex-direction: column;
          gap: 10px;
          margin-top: 15px;
        }

        .estimation-item {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          border-bottom: 1px solid rgba(106, 76, 147, 0.2);
        }

        .estimation-item.total {
          font-weight: bold;
          color: #6a4c93;
          border-bottom: 2px solid #6a4c93;
          margin-top: 10px;
          padding-top: 15px;
        }

        .sufficient {
          color: #28a745;
          font-weight: bold;
        }

        .insufficient {
          color: #dc3545;
          font-weight: bold;
        }

        .bridge-config {
          margin-top: 20px;
          padding: 15px;
          background: white;
          border-radius: 8px;
          border: 1px solid #ddd;
        }

        .config-details {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 10px;
          margin-top: 10px;
          font-size: 0.9em;
        }

        .create-bridge-button {
          width: 100%;
          padding: 15px 30px;
          background: linear-gradient(135deg, #6a4c93, #9c88ff);
          color: white;
          border: none;
          border-radius: 10px;
          font-size: 1.1em;
          font-weight: bold;
          cursor: pointer;
          transition: all 0.3s ease;
          margin-top: 20px;
        }

        .create-bridge-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 5px 15px rgba(106, 76, 147, 0.4);
        }

        .create-bridge-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .supported-bridges {
          margin-bottom: 40px;
        }

        .bridges-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
          margin-top: 20px;
        }

        .bridge-card {
          background: white;
          padding: 25px;
          border-radius: 12px;
          border: 1px solid #ddd;
          transition: all 0.3s ease;
        }

        .bridge-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }

        .bridge-header-card {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 15px;
        }

        .bridge-icon {
          font-size: 1.5em;
        }

        .bridge-card h4 {
          color: #6a4c93;
          margin: 0;
          flex: 1;
        }

        .bridge-type {
          background: #f8f9fa;
          padding: 4px 8px;
          border-radius: 10px;
          font-size: 0.8em;
          color: #666;
        }

        .bridge-stats {
          display: flex;
          gap: 15px;
          margin-top: 10px;
          font-size: 0.9em;
          color: #666;
        }

        .created-bridges {
          background: white;
          padding: 30px;
          border-radius: 15px;
          border: 1px solid #ddd;
        }

        .bridges-list {
          display: flex;
          flex-direction: column;
          gap: 20px;
          margin-top: 20px;
        }

        .bridge-item {
          background: #f8f9fa;
          padding: 25px;
          border-radius: 12px;
          border: 1px solid #eee;
        }

        .bridge-item-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .bridge-item-header h4 {
          margin: 0;
          color: #6a4c93;
        }

        .bridge-status {
          background: #28a745;
          color: white;
          padding: 5px 12px;
          border-radius: 15px;
          font-size: 0.8em;
          font-weight: bold;
        }

        .bridge-item-details {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
          margin-bottom: 20px;
        }

        .bridge-stat {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .bridge-stat span:first-child {
          font-size: 0.9em;
          color: #666;
        }

        .bridge-stat span:last-child {
          font-weight: bold;
          color: #333;
        }

        .bridge-addresses {
          background: white;
          padding: 15px;
          border-radius: 8px;
          margin-bottom: 15px;
        }

        .address-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;
          font-size: 0.9em;
        }

        .address-item code {
          font-family: monospace;
          background: #f8f9fa;
          padding: 4px 8px;
          border-radius: 4px;
          color: #6a4c93;
        }

        .bridge-actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding-top: 15px;
          border-top: 1px solid #ddd;
        }

        .view-transaction {
          color: #6a4c93;
          text-decoration: none;
          font-weight: bold;
        }

        .view-transaction:hover {
          text-decoration: underline;
        }

        .supported-chains {
          display: flex;
          flex-direction: column;
          gap: 5px;
          font-size: 0.9em;
        }

        .chain-list {
          display: flex;
          gap: 5px;
        }

        .chain-tag {
          background: #e9ecef;
          padding: 2px 6px;
          border-radius: 10px;
          font-size: 0.8em;
          color: #666;
        }

        .no-bridges {
          text-align: center;
          color: #666;
          font-style: italic;
        }
      `}</style>
    </div>
  );
};

export default CRTBridgeManager;