import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// Solana wallet adapter imports for REAL wallet connections
import { ConnectionProvider, WalletProvider } from '@solana/wallet-adapter-react';
import { WalletAdapterNetwork } from '@solana/wallet-adapter-base';
import { 
    PhantomWalletAdapter,
    SolflareWalletAdapter,
    TorusWalletAdapter,
    LedgerWalletAdapter,
} from '@solana/wallet-adapter-wallets';
import { WalletModalProvider } from '@solana/wallet-adapter-react-ui';
import { clusterApiUrl } from '@solana/web3.js';

// Import wallet adapter CSS for styling
import '@solana/wallet-adapter-react-ui/styles.css';

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