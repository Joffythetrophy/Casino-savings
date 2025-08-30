import React, { useState, useEffect } from 'react';
import './App.css';

// Real CRT Casino Components
import CRTWalletManager from './components/CRTWalletManager';
import CRTCasinoInterface from './components/CRTCasinoInterface';
import CRTSavingsManager from './components/CRTSavingsManager';
import RealSystemStatus from './components/RealSystemStatus';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8002/api';

function App() {
  const [walletAddress, setWalletAddress] = useState('');
  const [crtBalance, setCrtBalance] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [currentView, setCurrentView] = useState('casino');
  const [systemStatus, setSystemStatus] = useState(null);

  // Load wallet from localStorage on startup
  useEffect(() => {
    const savedWallet = localStorage.getItem('crt_wallet_address');
    if (savedWallet) {
      setWalletAddress(savedWallet);
      setIsConnected(true);
      fetchCRTBalance(savedWallet);
    }
    
    fetchSystemStatus();
  }, []);

  const fetchCRTBalance = async (address) => {
    try {
      const response = await fetch(`${BACKEND_URL}/wallet/crt-balance?wallet_address=${address}`);
      const data = await response.json();
      
      if (data.success) {
        setCrtBalance(data.crt_balance);
      }
    } catch (error) {
      console.error('Failed to fetch CRT balance:', error);
    }
  };

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/system/status`);
      const data = await response.json();
      
      if (data.success) {
        setSystemStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };

  const connectWallet = (address) => {
    setWalletAddress(address);
    setIsConnected(true);
    localStorage.setItem('crt_wallet_address', address);
    fetchCRTBalance(address);
  };

  const disconnectWallet = () => {
    setWalletAddress('');
    setCrtBalance(0);
    setIsConnected(false);
    localStorage.removeItem('crt_wallet_address');
  };

  const refreshBalance = () => {
    if (walletAddress) {
      fetchCRTBalance(walletAddress);
    }
  };

  return (
    <div className="App">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">
            🎰 Real Casino Savings System
          </h1>
          <div className="header-info">
            <span className="crt-focus">CRT Token Casino</span>
            {systemStatus && (
              <span className="system-status">
                {systemStatus.features.real_cryptocurrency_betting ? '✅ REAL' : '❌ FAKE'}
              </span>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="main-nav">
          <button
            className={`nav-button ${currentView === 'casino' ? 'active' : ''}`}
            onClick={() => setCurrentView('casino')}
          >
            🎰 Casino
          </button>
          <button
            className={`nav-button ${currentView === 'savings' ? 'active' : ''}`}
            onClick={() => setCurrentView('savings')}
          >
            💰 Savings
          </button>
          <button
            className={`nav-button ${currentView === 'wallet' ? 'active' : ''}`}
            onClick={() => setCurrentView('wallet')}
          >
            👛 Wallet
          </button>
          <button
            className={`nav-button ${currentView === 'status' ? 'active' : ''}`}
            onClick={() => setCurrentView('status')}
          >
            📊 Status
          </button>
        </nav>

        {/* Wallet Connection Status */}
        <div className="wallet-status">
          {isConnected ? (
            <div className="connected-wallet">
              <div className="wallet-info">
                <span className="wallet-address">
                  {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}
                </span>
                <span className="crt-balance">
                  {crtBalance.toLocaleString()} CRT
                </span>
              </div>
              <button className="refresh-btn" onClick={refreshBalance}>
                🔄
              </button>
              <button className="disconnect-btn" onClick={disconnectWallet}>
                ❌
              </button>
            </div>
          ) : (
            <div className="no-wallet">
              <span>No CRT Wallet Connected</span>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {!isConnected ? (
          <div className="welcome-screen">
            <div className="welcome-card">
              <h2>🎰 Welcome to Real Casino Savings</h2>
              <p>
                A real cryptocurrency casino that uses your <strong>CRT tokens</strong> for:
              </p>
              <ul className="feature-list">
                <li>✅ Real CRT token betting</li>
                <li>✅ Real blockchain transactions</li>  
                <li>✅ Real savings from gaming losses</li>
                <li>✅ Real DEX pool creation</li>
                <li>❌ No fake balances or simulations</li>
              </ul>
              
              <div className="connect-section">
                <h3>Connect Your CRT Wallet</h3>
                <CRTWalletManager 
                  onConnect={connectWallet}
                  backendUrl={BACKEND_URL}
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="app-views">
            {currentView === 'casino' && (
              <CRTCasinoInterface
                walletAddress={walletAddress}
                crtBalance={crtBalance}
                onBalanceUpdate={refreshBalance}
                backendUrl={BACKEND_URL}
              />
            )}
            
            {currentView === 'savings' && (
              <CRTSavingsManager
                walletAddress={walletAddress}
                crtBalance={crtBalance}
                onBalanceUpdate={refreshBalance}
                backendUrl={BACKEND_URL}
              />
            )}
            
            {currentView === 'wallet' && (
              <CRTWalletManager
                walletAddress={walletAddress}
                crtBalance={crtBalance}
                onBalanceUpdate={refreshBalance}
                backendUrl={BACKEND_URL}
                isConnected={true}
              />
            )}
            
            {currentView === 'status' && (
              <RealSystemStatus
                systemStatus={systemStatus}
                backendUrl={BACKEND_URL}
              />
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>
          🔥 Real Casino Savings System - Built for CRT Token Integration
        </p>
        <p>
          ✅ Real Cryptocurrency • ❌ No Simulations • 🔗 Solana Blockchain
        </p>
      </footer>
    </div>
  );
}

export default App;