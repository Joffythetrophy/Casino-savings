import React, { useState, useEffect } from 'react';

const USDCToCRTConverter = ({ walletAddress, onBalanceUpdate, backendUrl }) => {
  const [usdcBalance, setUsdcBalance] = useState(0);
  const [estimatedCRT, setEstimatedCRT] = useState(0);
  const [conversionAmount, setConversionAmount] = useState('');
  const [isConverting, setIsConverting] = useState(false);
  const [conversionEstimate, setConversionEstimate] = useState(null);
  const [conversionResults, setConversionResults] = useState([]);
  const [useAllUSDC, setUseAllUSDC] = useState(true);

  useEffect(() => {
    if (walletAddress) {
      fetchUSDCBalance();
    }
  }, [walletAddress]);

  useEffect(() => {
    if (conversionAmount && parseFloat(conversionAmount) > 0) {
      estimateConversion();
    } else {
      setConversionEstimate(null);
    }
  }, [conversionAmount]);

  const fetchUSDCBalance = async () => {
    try {
      const response = await fetch(`${backendUrl}/conversion/current-usdc-balance?wallet_address=${walletAddress}`);
      const data = await response.json();
      
      if (data.success) {
        const balance = data.usdc_balance || 0;
        setUsdcBalance(balance);
        
        if (useAllUSDC && balance > 0) {
          setConversionAmount(balance.toString());
        }
      }
    } catch (error) {
      console.error('Failed to fetch USDC balance:', error);
    }
  };

  const estimateConversion = async () => {
    try {
      const amount = parseFloat(conversionAmount);
      if (amount <= 0) return;

      const response = await fetch(`${backendUrl}/conversion/estimate-usdc-to-crt?usdc_amount=${amount}`);
      const data = await response.json();
      
      if (data.success) {
        setConversionEstimate(data);
        setEstimatedCRT(data.crt_output);
      }
    } catch (error) {
      console.error('Failed to estimate conversion:', error);
    }
  };

  const executeConversion = async () => {
    const amount = useAllUSDC ? null : parseFloat(conversionAmount);
    
    if (!useAllUSDC && (amount <= 0 || amount > usdcBalance)) {
      alert('Invalid conversion amount');
      return;
    }

    setIsConverting(true);
    try {
      const payload = {
        wallet_address: walletAddress
      };
      
      if (!useAllUSDC) {
        payload.usdc_amount = amount;
      }

      const response = await fetch(`${backendUrl}/conversion/usdc-to-crt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      
      if (result.success) {
        const conversionData = result.conversion_result;
        
        alert(`✅ USDC to CRT Conversion Successful!\n` +
              `Converted: ${result.usdc_converted} USDC\n` +
              `Received: ${result.crt_received?.toLocaleString()} CRT\n` +
              `Transaction: ${conversionData.conversion_result?.transaction_hash}`);
        
        // Add to conversion results
        const conversionRecord = {
          ...conversionData,
          conversion_type: result.conversion_type,
          usdc_converted: result.usdc_converted,
          crt_received: result.crt_received,
          timestamp: new Date().toISOString()
        };
        setConversionResults(prev => [conversionRecord, ...prev]);
        
        // Reset form
        setConversionAmount('');
        setConversionEstimate(null);
        setEstimatedCRT(0);
        
        // Update balances
        setTimeout(() => {
          onBalanceUpdate();
          fetchUSDCBalance();
        }, 2000);
      } else {
        alert(`❌ Conversion failed: ${result.error}`);
      }
    } catch (error) {
      console.error('Conversion failed:', error);
      alert('Conversion failed due to network error');
    }
    setIsConverting(false);
  };

  return (
    <div className="usdc-crt-converter">
      <div className="converter-header">
        <h2>💱 USDC to CRT Converter</h2>
        <p>Convert all your USDC back to CRT tokens using real DEX swaps</p>
      </div>

      {/* Current USDC Balance */}
      <div className="balance-display">
        <div className="balance-card">
          <h3>💚 Your USDC Balance</h3>
          <div className="balance-amount">
            {usdcBalance.toLocaleString()} USDC
          </div>
          <div className="balance-usd">
            ≈ ${usdcBalance.toLocaleString()} USD
          </div>
          {usdcBalance > 0 && (
            <div className="potential-crt">
              Can convert to ~{Math.floor(usdcBalance / 0.01).toLocaleString()} CRT
            </div>
          )}
        </div>
        
        <div className="conversion-info">
          <h3>💡 Conversion Details</h3>
          <ul>
            <li><strong>Rate:</strong> ~100 CRT per 1 USDC</li>
            <li><strong>DEX:</strong> Orca (Solana)</li>
            <li><strong>Fee:</strong> ~0.3% + slippage</li>
            <li><strong>Time:</strong> 30-60 seconds</li>
          </ul>
        </div>
      </div>

      {usdcBalance > 0 ? (
        <div className="conversion-form">
          <div className="conversion-options">
            <div className="option-group">
              <label className="conversion-option">
                <input
                  type="radio"
                  checked={useAllUSDC}
                  onChange={() => {
                    setUseAllUSDC(true);
                    setConversionAmount(usdcBalance.toString());
                  }}
                />
                <span className="option-label">
                  🔄 Convert ALL USDC ({usdcBalance.toLocaleString()} USDC)
                </span>
              </label>
              
              <label className="conversion-option">
                <input
                  type="radio"
                  checked={!useAllUSDC}
                  onChange={() => {
                    setUseAllUSDC(false);
                    setConversionAmount('');
                  }}
                />
                <span className="option-label">
                  ⚙️ Convert Specific Amount
                </span>
              </label>
            </div>

            {!useAllUSDC && (
              <div className="amount-input-section">
                <label>USDC Amount to Convert:</label>
                <div className="amount-input-group">
                  <input
                    type="number"
                    value={conversionAmount}
                    onChange={(e) => setConversionAmount(e.target.value)}
                    placeholder="0.00"
                    min="0.01"
                    max={usdcBalance}
                    step="0.01"
                    className="usdc-input"
                  />
                  <span className="currency-label">USDC</span>
                </div>
                <div className="quick-amounts">
                  <button onClick={() => setConversionAmount((usdcBalance * 0.25).toFixed(2))}>25%</button>
                  <button onClick={() => setConversionAmount((usdcBalance * 0.5).toFixed(2))}>50%</button>
                  <button onClick={() => setConversionAmount((usdcBalance * 0.75).toFixed(2))}>75%</button>
                  <button onClick={() => setConversionAmount(usdcBalance.toString())}>100%</button>
                </div>
              </div>
            )}
          </div>

          {/* Conversion Estimate */}
          {conversionEstimate && (
            <div className="conversion-estimate">
              <h4>📊 Conversion Estimate</h4>
              <div className="estimate-details">
                <div className="estimate-row">
                  <span>USDC Input:</span>
                  <span>{conversionEstimate.usdc_input} USDC</span>
                </div>
                <div className="estimate-row">
                  <span>CRT Output:</span>
                  <span className="crt-output">{conversionEstimate.crt_output?.toLocaleString()} CRT</span>
                </div>
                <div className="estimate-row">
                  <span>Exchange Rate:</span>
                  <span>{conversionEstimate.exchange_rate}</span>
                </div>
                <div className="estimate-row">
                  <span>DEX Fee:</span>
                  <span>{conversionEstimate.fees?.dex_fee_percent?.toFixed(2)}% ({conversionEstimate.fees?.dex_fee_amount_crt?.toLocaleString()} CRT)</span>
                </div>
                <div className="estimate-row">
                  <span>Slippage:</span>
                  <span>{conversionEstimate.fees?.slippage_percent?.toFixed(1)}% ({conversionEstimate.fees?.slippage_amount_crt?.toLocaleString()} CRT)</span>
                </div>
                <div className="estimate-row total">
                  <span>Total Fees:</span>
                  <span>{conversionEstimate.total_cost?.total_fees_crt?.toLocaleString()} CRT</span>
                </div>
              </div>

              <div className="dex-info">
                <div className="dex-details">
                  <span>DEX: Orca</span>
                  <span>Network: Solana</span>
                  <span>Time: {conversionEstimate.estimated_time}</span>
                </div>
              </div>
            </div>
          )}

          <button
            className="convert-button"
            onClick={executeConversion}
            disabled={isConverting || (!useAllUSDC && (!conversionAmount || parseFloat(conversionAmount) <= 0))}
          >
            {isConverting ? 
              '💱 Converting USDC to CRT...' : 
              useAllUSDC ? 
                `💱 Convert ALL ${usdcBalance.toLocaleString()} USDC to CRT` :
                `💱 Convert ${conversionAmount || '0'} USDC to CRT`
            }
          </button>
        </div>
      ) : (
        <div className="no-usdc">
          <div className="no-balance-message">
            <h3>💰 No USDC Balance</h3>
            <p>You don't have any USDC to convert to CRT tokens.</p>
            <p>Your USDC balance: {usdcBalance} USDC</p>
          </div>
        </div>
      )}

      {/* Conversion History */}
      {conversionResults.length > 0 && (
        <div className="conversion-history">
          <h3>📊 Recent Conversions</h3>
          <div className="history-list">
            {conversionResults.map((conversion, index) => (
              <div key={index} className="conversion-item">
                <div className="conversion-header">
                  <h4>💱 {conversion.conversion_type?.replace('_', ' ')}</h4>
                  <span className="conversion-status">✅ Completed</span>
                </div>
                
                <div className="conversion-details">
                  <div className="conversion-stat">
                    <span>USDC Converted:</span>
                    <span>{conversion.usdc_converted?.toLocaleString()} USDC</span>
                  </div>
                  <div className="conversion-stat">
                    <span>CRT Received:</span>
                    <span className="crt-received">{conversion.crt_received?.toLocaleString()} CRT</span>
                  </div>
                  <div className="conversion-stat">
                    <span>Exchange Rate:</span>
                    <span>{conversion.exchange_rate}</span>
                  </div>
                  <div className="conversion-stat">
                    <span>DEX Used:</span>
                    <span>{conversion.dex_used}</span>
                  </div>
                </div>

                <div className="conversion-transaction">
                  <a 
                    href={conversion.conversion_result?.explorer_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="view-transaction"
                  >
                    📍 View Transaction
                  </a>
                  <div className="transaction-hash">
                    TX: {conversion.conversion_result?.transaction_hash?.slice(0, 16)}...
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <style jsx>{`
        .usdc-crt-converter {
          max-width: 1000px;
          margin: 0 auto;
          padding: 20px;
        }

        .converter-header {
          text-align: center;
          margin-bottom: 40px;
          padding: 30px;
          background: linear-gradient(135deg, #22c55e, #16a34a);
          color: white;
          border-radius: 15px;
        }

        .balance-display {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 30px;
          margin-bottom: 40px;
        }

        .balance-card {
          background: white;
          padding: 30px;
          border-radius: 15px;
          border: 2px solid #22c55e;
          text-align: center;
        }

        .balance-card h3 {
          color: #22c55e;
          margin-bottom: 20px;
        }

        .balance-amount {
          font-size: 2.5em;
          font-weight: bold;
          color: #16a34a;
          margin: 15px 0;
        }

        .balance-usd {
          font-size: 1.2em;
          color: #666;
          margin-bottom: 15px;
        }

        .potential-crt {
          background: #f0fdf4;
          padding: 10px;
          border-radius: 8px;
          color: #16a34a;
          font-weight: bold;
          font-size: 0.9em;
        }

        .conversion-info {
          background: #f8f9fa;
          padding: 30px;
          border-radius: 15px;
          border: 1px solid #ddd;
        }

        .conversion-info h3 {
          color: #22c55e;
          margin-bottom: 15px;
        }

        .conversion-info ul {
          margin: 0;
          padding-left: 20px;
        }

        .conversion-info li {
          margin-bottom: 8px;
          line-height: 1.5;
        }

        .conversion-form {
          background: white;
          padding: 40px;
          border-radius: 15px;
          border: 2px solid #3b82f6;
          margin-bottom: 40px;
        }

        .conversion-options {
          margin-bottom: 30px;
        }

        .option-group {
          display: flex;
          flex-direction: column;
          gap: 15px;
          margin-bottom: 30px;
        }

        .conversion-option {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 15px;
          border: 2px solid #e5e7eb;
          border-radius: 10px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .conversion-option:hover {
          border-color: #3b82f6;
          background: #f8fafc;
        }

        .conversion-option input[type="radio"]:checked + .option-label {
          color: #3b82f6;
          font-weight: bold;
        }

        .amount-input-section {
          margin-top: 20px;
          padding: 20px;
          background: #f8fafc;
          border-radius: 10px;
        }

        .amount-input-section label {
          display: block;
          margin-bottom: 10px;
          font-weight: bold;
          color: #333;
        }

        .amount-input-group {
          display: flex;
          align-items: center;
          border: 1px solid #ddd;
          border-radius: 8px;
          overflow: hidden;
          margin-bottom: 15px;
        }

        .usdc-input {
          flex: 1;
          padding: 12px;
          border: none;
          font-size: 1.1em;
        }

        .currency-label {
          background: #f8f9fa;
          padding: 12px;
          font-weight: bold;
          color: #22c55e;
          border-left: 1px solid #ddd;
        }

        .quick-amounts {
          display: flex;
          gap: 10px;
        }

        .quick-amounts button {
          padding: 8px 16px;
          border: 1px solid #3b82f6;
          background: white;
          color: #3b82f6;
          border-radius: 5px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .quick-amounts button:hover {
          background: #3b82f6;
          color: white;
        }

        .conversion-estimate {
          background: #eff6ff;
          padding: 25px;
          border-radius: 12px;
          margin: 25px 0;
          border: 1px solid #3b82f6;
        }

        .estimate-details {
          display: flex;
          flex-direction: column;
          gap: 12px;
          margin: 15px 0;
        }

        .estimate-row {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          border-bottom: 1px solid rgba(59, 130, 246, 0.2);
        }

        .estimate-row.total {
          font-weight: bold;
          color: #3b82f6;
          border-bottom: 2px solid #3b82f6;
          margin-top: 10px;
          padding-top: 15px;
        }

        .crt-output {
          font-weight: bold;
          color: #16a34a;
          font-size: 1.1em;
        }

        .dex-info {
          margin-top: 20px;
          padding: 15px;
          background: white;
          border-radius: 8px;
          border: 1px solid #ddd;
        }

        .dex-details {
          display: flex;
          justify-content: space-between;
          font-size: 0.9em;
          color: #666;
        }

        .convert-button {
          width: 100%;
          padding: 18px 30px;
          background: linear-gradient(135deg, #22c55e, #16a34a);
          color: white;
          border: none;
          border-radius: 12px;
          font-size: 1.2em;
          font-weight: bold;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .convert-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(34, 197, 94, 0.4);
        }

        .convert-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .no-usdc {
          text-align: center;
          margin: 40px 0;
        }

        .no-balance-message {
          background: #f8f9fa;
          padding: 40px;
          border-radius: 15px;
          border: 1px solid #ddd;
        }

        .no-balance-message h3 {
          color: #666;
          margin-bottom: 15px;
        }

        .conversion-history {
          background: white;
          padding: 30px;
          border-radius: 15px;
          border: 1px solid #ddd;
        }

        .history-list {
          display: flex;
          flex-direction: column;
          gap: 20px;
          margin-top: 20px;
        }

        .conversion-item {
          background: #f8f9fa;
          padding: 25px;
          border-radius: 12px;
          border: 1px solid #eee;
        }

        .conversion-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .conversion-header h4 {
          margin: 0;
          color: #22c55e;
        }

        .conversion-status {
          background: #16a34a;
          color: white;
          padding: 5px 12px;
          border-radius: 15px;
          font-size: 0.8em;
          font-weight: bold;
        }

        .conversion-details {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
          margin-bottom: 20px;
        }

        .conversion-stat {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }

        .conversion-stat span:first-child {
          font-size: 0.9em;
          color: #666;
        }

        .conversion-stat span:last-child {
          font-weight: bold;
          color: #333;
        }

        .crt-received {
          color: #16a34a !important;
          font-size: 1.1em !important;
        }

        .conversion-transaction {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding-top: 15px;
          border-top: 1px solid #ddd;
        }

        .view-transaction {
          color: #3b82f6;
          text-decoration: none;
          font-weight: bold;
        }

        .view-transaction:hover {
          text-decoration: underline;
        }

        .transaction-hash {
          font-family: monospace;
          font-size: 0.9em;
          color: #666;
        }
      `}</style>
    </div>
  );
};

export default USDCToCRTConverter;