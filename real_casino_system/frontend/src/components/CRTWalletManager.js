import React, { useState, useEffect } from 'react';

const CRTWalletManager = ({ walletAddress, crtBalance, onBalanceUpdate, backendUrl, isConnected, onConnect }) => {
  const [allBalances, setAllBalances] = useState({});
  const [withdrawalAddress, setWithdrawalAddress] = useState('');
  const [withdrawalAmount, setWithdrawalAmount] = useState('');
  const [isWithdrawing, setIsWithdrawing] = useState(false);
  const [walletInput, setWalletInput] = useState('');
  const [isLoadingBalance, setIsLoadingBalance] = useState(false);
  const [transactionHistory, setTransactionHistory] = useState([]);

  // Your known CRT wallet address for easy connection
  const KNOWN_CRT_WALLET = 'DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq';

  useEffect(() => {
    if (isConnected && walletAddress) {
      fetchAllBalances();
    }
  }, [isConnected, walletAddress]);

  const fetchAllBalances = async () => {
    setIsLoadingBalance(true);
    try {
      const response = await fetch(`${backendUrl}/wallet/all-balances?wallet_address=${walletAddress}`);
      const data = await response.json();
      
      if (data.success) {
        setAllBalances(data.balances);
      }
    } catch (error) {
      console.error('Failed to fetch all balances:', error);
    }
    setIsLoadingBalance(false);
  };

  const connectWallet = async () => {
    const addressToConnect = walletInput || KNOWN_CRT_WALLET;
    
    if (!addressToConnect) {
      alert('Please enter a wallet address');
      return;
    }

    setIsLoadingBalance(true);
    try {
      // Verify wallet has CRT balance
      const response = await fetch(`${backendUrl}/wallet/crt-balance?wallet_address=${addressToConnect}`);
      const data = await response.json();
      
      if (data.success) {
        onConnect(addressToConnect);
        setWalletInput('');
      } else {
        alert(`Could not connect to wallet: ${data.error}`);
      }
    } catch (error) {
      console.error('Wallet connection failed:', error);
      alert('Wallet connection failed');
    }
    setIsLoadingBalance(false);
  };

  const executeWithdrawal = async () => {
    if (!withdrawalAddress || !withdrawalAmount) {
      alert('Please enter withdrawal address and amount');
      return;
    }

    const amount = parseFloat(withdrawalAmount);
    if (amount <= 0 || amount > crtBalance) {
      alert('Invalid withdrawal amount');
      return;
    }

    setIsWithdrawing(true);
    try {
      const response = await fetch(`${backendUrl}/wallet/withdraw-crt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          from_address: walletAddress,
          to_address: withdrawalAddress,
          amount: amount
        })
      });

      const result = await response.json();
      
      if (result.success) {
        alert(`✅ Withdrawal successful!\nTransaction: ${result.withdrawal_result.transaction_hash}`);
        setWithdrawalAddress('');
        setWithdrawalAmount('');
        
        // Add to transaction history
        const transaction = {
          type: 'withdrawal',
          amount: amount,
          currency: 'CRT',
          to_address: withdrawalAddress,
          transaction_hash: result.withdrawal_result.transaction_hash,
          timestamp: new Date().toISOString(),
          status: 'completed'
        };
        setTransactionHistory(prev => [transaction, ...prev]);
        
        // Update balance
        setTimeout(onBalanceUpdate, 2000);
      } else {
        alert(`❌ Withdrawal failed: ${result.error}`);
      }
    } catch (error) {
      console.error('Withdrawal failed:', error);
      alert('Withdrawal failed due to network error');
    }
    setIsWithdrawing(false);
  };

  if (!isConnected) {
    return (
      <div className="wallet-connection">
        <div className="connection-card">
          <h2>🎰 Connect Your CRT Wallet</h2>
          <p>Connect your Solana wallet containing CRT tokens to start playing!</p>
          
          <div className="quick-connect">
            <h3>Quick Connect (Your Known Wallet):</h3>
            <div className="known-wallet">
              <code>{KNOWN_CRT_WALLET}</code>
              <button 
                className="connect-button"
                onClick={connectWallet}
                disabled={isLoadingBalance}
              >
                {isLoadingBalance ? '🔄 Connecting...' : '🔗 Connect'}
              </button>
            </div>
          </div>

          <div className="manual-connect">
            <h3>Or Enter Different Wallet:</h3>
            <div className="wallet-input-group">
              <input
                type="text"
                placeholder="Enter Solana wallet address..."
                value={walletInput}
                onChange={(e) => setWalletInput(e.target.value)}
                className="wallet-input"
              />
              <button 
                className="connect-button"
                onClick={connectWallet}
                disabled={isLoadingBalance || !walletInput}
              >
                {isLoadingBalance ? '🔄 Connecting...' : '🔗 Connect'}
              </button>
            </div>
          </div>

          <div className="wallet-info">
            <h3>What happens when you connect:</h3>
            <ul>
              <li>✅ View your REAL CRT token balance</li>
              <li>✅ Bet with your actual CRT tokens</li>
              <li>✅ Create real savings from gaming losses</li>
              <li>✅ Withdraw CRT to any Solana wallet</li>
              <li>❌ No access to your private keys</li>
            </ul>
          </div>

          <div className="security-note">
            <p><strong>🔒 Security:</strong> This is read-only access to check your balance. We never access your private keys.</p>
          </div>
        </div>

        <style jsx>{`
          .wallet-connection {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 500px;
            padding: 20px;
          }

          .connection-card {
            max-width: 600px;
            padding: 40px;
            background: white;
            border-radius: 15px;
            border: 2px solid #4caf50;
            text-align: center;
          }

          .quick-connect, .manual-connect {
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
          }

          .known-wallet {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-top: 15px;
          }

          .known-wallet code {
            flex: 1;
            padding: 10px;
            background: #e9ecef;
            border-radius: 5px;
            font-size: 0.9em;
            word-break: break-all;
          }

          .wallet-input-group {
            display: flex;
            gap: 10px;
            margin-top: 15px;
          }

          .wallet-input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1em;
          }

          .connect-button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #4caf50, #45a049);
            color: white;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
          }

          .connect-button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
          }

          .connect-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
          }

          .wallet-info {
            text-align: left;
            margin: 30px 0;
          }

          .wallet-info ul {
            list-style: none;
            padding: 0;
          }

          .wallet-info li {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
          }

          .security-note {
            margin-top: 30px;
            padding: 15px;
            background: #e8f5e8;
            border-radius: 8px;
            font-size: 0.9em;
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="crt-wallet-manager">
      <div className="wallet-header">
        <h2>👛 Your CRT Wallet</h2>
        <div className="wallet-address">
          <span className="address-label">Connected:</span>
          <code className="address-value">{walletAddress}</code>
        </div>
      </div>

      {/* Balance Overview */}
      <div className="balance-overview">
        <div className="primary-balance">
          <h3>💎 CRT Balance</h3>
          <div className="balance-amount">
            {isLoadingBalance ? '🔄 Loading...' : `${crtBalance.toLocaleString()} CRT`}
          </div>
          <div className="balance-usd">
            ≈ ${(crtBalance * 0.01).toLocaleString()} USD
          </div>
          <button onClick={onBalanceUpdate} className="refresh-button">
            🔄 Refresh Balance
          </button>
        </div>

        {/* Other Token Balances */}
        <div className="other-balances">
          <h3>🪙 Other Tokens</h3>
          <div className="balance-list">
            {Object.entries(allBalances).map(([currency, balance]) => {
              if (currency === 'CRT' || currency === 'wallet_address' || currency === 'network' || currency === 'source' || currency === 'last_updated') return null;
              return (
                <div key={currency} className="balance-item">
                  <span className="currency">{currency}:</span>
                  <span className="amount">{balance?.toFixed(6) || '0.000000'}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Withdrawal Section */}
      <div className="withdrawal-section">
        <h3>💸 Withdraw CRT Tokens</h3>
        <div className="withdrawal-form">
          <div className="form-group">
            <label>Destination Wallet Address:</label>
            <input
              type="text"
              value={withdrawalAddress}
              onChange={(e) => setWithdrawalAddress(e.target.value)}
              placeholder="Enter Solana wallet address..."
              className="address-input"
            />
          </div>

          <div className="form-group">
            <label>Amount to Withdraw:</label>
            <div className="amount-input-group">
              <input
                type="number"
                value={withdrawalAmount}
                onChange={(e) => setWithdrawalAmount(e.target.value)}
                placeholder="0"
                min="1000"
                max={crtBalance}
                step="1000"
                className="amount-input"
              />
              <span className="currency-label">CRT</span>
            </div>
            <div className="quick-amounts">
              <button onClick={() => setWithdrawalAmount('10000')}>10K</button>
              <button onClick={() => setWithdrawalAmount('100000')}>100K</button>
              <button onClick={() => setWithdrawalAmount('1000000')}>1M</button>
              <button onClick={() => setWithdrawalAmount(Math.floor(crtBalance * 0.1).toString())}>10%</button>
              <button onClick={() => setWithdrawalAmount(Math.floor(crtBalance * 0.25).toString())}>25%</button>
            </div>
          </div>

          <div className="withdrawal-info">
            <p><strong>⚠️ Important:</strong></p>
            <ul>
              <li>Minimum withdrawal: 1,000 CRT</li>
              <li>Daily limit: 10,000,000 CRT</li>
              <li>This will create a REAL blockchain transaction</li>
              <li>Transaction fees will be deducted from your SOL balance</li>
            </ul>
          </div>

          <button
            className="withdraw-button"
            onClick={executeWithdrawal}
            disabled={isWithdrawing || !withdrawalAddress || !withdrawalAmount || parseFloat(withdrawalAmount) > crtBalance}
          >
            {isWithdrawing ? '💸 Processing Withdrawal...' : `💸 Withdraw ${withdrawalAmount || '0'} CRT`}
          </button>
        </div>
      </div>

      {/* Transaction History */}
      {transactionHistory.length > 0 && (
        <div className="transaction-history">
          <h3>📊 Recent Transactions</h3>
          <div className="history-list">
            {transactionHistory.map((tx, index) => (
              <div key={index} className="transaction-item">
                <div className="tx-type">{tx.type.toUpperCase()}</div>
                <div className="tx-amount">{tx.amount.toLocaleString()} {tx.currency}</div>
                <div className="tx-address">To: {tx.to_address.slice(0, 8)}...{tx.to_address.slice(-8)}</div>
                <div className="tx-hash">
                  <a href={`https://explorer.solana.com/tx/${tx.transaction_hash}`} target="_blank" rel="noopener noreferrer">
                    View on Explorer
                  </a>
                </div>
                <div className="tx-status">{tx.status}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <style jsx>{`
        .crt-wallet-manager {
          max-width: 1000px;
          margin: 0 auto;
          padding: 20px;
        }

        .wallet-header {
          background: linear-gradient(135deg, #1a5f1a, #2d8f2d);
          color: white;
          padding: 30px;
          border-radius: 15px;
          margin-bottom: 30px;
        }

        .wallet-header h2 {
          margin: 0 0 15px 0;
          font-size: 1.8em;
        }

        .wallet-address {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 0.9em;
        }

        .address-value {
          background: rgba(255, 255, 255, 0.2);
          padding: 8px 12px;
          border-radius: 5px;
          font-family: monospace;
        }

        .balance-overview {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 30px;
          margin-bottom: 40px;
        }

        .primary-balance {
          background: linear-gradient(135deg, #f8f9fa, #e9ecef);
          padding: 30px;
          border-radius: 15px;
          text-align: center;
          border: 2px solid #4caf50;
        }

        .balance-amount {
          font-size: 2.5em;
          font-weight: bold;
          color: #2d8f2d;
          margin: 15px 0;
        }

        .balance-usd {
          font-size: 1.2em;
          color: #666;
          margin-bottom: 20px;
        }

        .refresh-button {
          padding: 10px 20px;
          background: #4caf50;
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .refresh-button:hover {
          background: #45a049;
          transform: translateY(-2px);
        }

        .other-balances {
          background: #f8f9fa;
          padding: 30px;
          border-radius: 15px;
          border: 1px solid #ddd;
        }

        .balance-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
          margin-top: 15px;
        }

        .balance-item {
          display: flex;
          justify-content: space-between;
          padding: 10px;
          background: white;
          border-radius: 5px;
          border: 1px solid #eee;
        }

        .withdrawal-section {
          background: white;
          padding: 30px;
          border-radius: 15px;
          border: 2px solid #ff6b35;
          margin-bottom: 30px;
        }

        .withdrawal-section h3 {
          color: #ff6b35;
          margin-bottom: 25px;
        }

        .withdrawal-form {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }

        .form-group label {
          display: block;
          margin-bottom: 8px;
          font-weight: bold;
          color: #333;
        }

        .address-input, .amount-input {
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
          border: 1px solid #4caf50;
          background: white;
          color: #4caf50;
          border-radius: 5px;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .quick-amounts button:hover {
          background: #4caf50;
          color: white;
        }

        .withdrawal-info {
          background: #fff3cd;
          padding: 15px;
          border-radius: 8px;
          border: 1px solid #ffeaa7;
        }

        .withdrawal-info ul {
          margin: 10px 0 0 20px;
        }

        .withdraw-button {
          padding: 15px 30px;
          background: linear-gradient(135deg, #ff6b35, #f0932b);
          color: white;
          border: none;
          border-radius: 10px;
          font-size: 1.1em;
          font-weight: bold;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .withdraw-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 5px 15px rgba(255, 107, 53, 0.4);
        }

        .withdraw-button:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .transaction-history {
          background: white;
          padding: 30px;
          border-radius: 15px;
          border: 1px solid #ddd;
        }

        .history-list {
          display: flex;
          flex-direction: column;
          gap: 15px;
          margin-top: 20px;
        }

        .transaction-item {
          display: grid;
          grid-template-columns: 1fr 1fr 2fr 1fr 1fr;
          gap: 15px;
          padding: 15px;
          background: #f8f9fa;
          border-radius: 8px;
          border: 1px solid #eee;
          align-items: center;
          font-size: 0.9em;
        }

        .tx-type {
          font-weight: bold;
          color: #ff6b35;
        }

        .tx-amount {
          font-weight: bold;
          color: #4caf50;
        }

        .tx-hash a {
          color: #007bff;
          text-decoration: none;
          font-size: 0.8em;
        }

        .tx-hash a:hover {
          text-decoration: underline;
        }

        .tx-status {
          color: #28a745;
          font-weight: bold;
          text-transform: uppercase;
          font-size: 0.8em;
        }
      `}</style>
    </div>
  );
};

export default CRTWalletManager;