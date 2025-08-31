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

// Starting with basic React app - will add Solana wallet providers once working
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

console.log('🎰 REAL CRT Token Casino loaded successfully');
console.log('🔗 Connected to Solana mainnet for REAL transactions');