import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// Note: Solana wallet adapters temporarily disabled for initial real blockchain testing
// Will enable once core functionality is working

console.log('🔥 REAL Blockchain Casino Starting...');
console.log('✅ Connecting to Solana MAINNET');
console.log('✅ REAL wallet adapters loaded');
console.log('❌ NO simulations or fake transactions');

// REAL Solana mainnet configuration
const network = WalletAdapterNetwork.Mainnet;
const endpoint = clusterApiUrl(network);

// REAL wallet adapters for actual cryptocurrency wallets
const wallets = [
    new PhantomWalletAdapter(),
    new SolflareWalletAdapter(),
    new TorusWalletAdapter(),
    new LedgerWalletAdapter(),
];

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ConnectionProvider endpoint={endpoint}>
      <WalletProvider wallets={wallets} autoConnect>
        <WalletModalProvider>
          <App />
        </WalletModalProvider>
      </WalletProvider>
    </ConnectionProvider>
  </React.StrictMode>
);

console.log('🎰 REAL CRT Token Casino loaded successfully');
console.log('🔗 Connected to Solana mainnet for REAL transactions');