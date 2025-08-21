import React, { useState } from 'react';
import { Wallet, CheckCircle } from 'lucide-react';

const WalletButton = ({ name, icon, isSelected, onClick, isConnected }) => {
  return (
    <button
      onClick={() => onClick(name)}
      className={`relative group w-full p-4 rounded-xl border-2 transition-all duration-300 ${
        isSelected 
          ? 'border-yellow-400 bg-yellow-400/10' 
          : 'border-white/20 bg-white/5 hover:border-yellow-400/50 hover:bg-white/10'
      }`}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center">
            <span className="text-sm font-bold text-black">{icon}</span>
          </div>
          <span className="font-medium text-white">{name}</span>
        </div>
        {isConnected && (
          <CheckCircle className="w-5 h-5 text-green-400" />
        )}
      </div>
    </button>
  );
};

const WalletConnectSection = ({ onConnect, onWalletSelect, selectedWallet }) => {
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectedWallet, setConnectedWallet] = useState(null);

  const wallets = [
    { name: 'Phantom', icon: '👻' },
    { name: 'Solflare', icon: '🔥' },
    { name: 'Backpack', icon: '🎒' },
    { name: 'MetaMask', icon: '🦊' }
  ];

  const handleWalletSelect = (walletName) => {
    onWalletSelect(walletName);
  };

  const handleConnect = async () => {
    if (!selectedWallet) return;
    
    setIsConnecting(true);
    
    // Simulate wallet connection
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setConnectedWallet(selectedWallet);
    onConnect(true);
    setIsConnecting(false);
  };

  return (
    <section className="py-20 px-6">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-2xl flex items-center justify-center">
            <Wallet className="w-10 h-10 text-black" />
          </div>
          <h2 className="text-4xl font-bold text-white mb-4">Connect Your Wallet</h2>
          <p className="text-gray-300 text-lg">Choose your preferred wallet to get started</p>
        </div>

        {/* Wallet Options */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          {wallets.map((wallet) => (
            <WalletButton
              key={wallet.name}
              name={wallet.name}
              icon={wallet.icon}
              isSelected={selectedWallet === wallet.name}
              onClick={handleWalletSelect}
              isConnected={connectedWallet === wallet.name}
            />
          ))}
        </div>

        {/* Connect Button */}
        <div className="text-center">
          <button
            onClick={handleConnect}
            disabled={!selectedWallet || isConnecting || connectedWallet}
            className={`px-12 py-4 rounded-xl font-bold text-lg transition-all duration-300 ${
              !selectedWallet || connectedWallet
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : isConnecting
                ? 'bg-yellow-500 text-black cursor-wait'
                : 'bg-gradient-to-r from-yellow-400 to-yellow-600 text-black hover:from-yellow-300 hover:to-yellow-500 hover:scale-105 hover:shadow-lg hover:shadow-yellow-400/30'
            }`}
          >
            {connectedWallet ? 'Connected!' : isConnecting ? 'Connecting...' : 'Connect Wallet'}
          </button>
          
          <p className="text-gray-400 text-sm mt-4">
            Supported networks: Solana, Ethereum, BSC, Polygon, Avalanche
          </p>
        </div>
      </div>
    </section>
  );
};

export default WalletConnectSection;