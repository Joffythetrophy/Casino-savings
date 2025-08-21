import React, { useState } from 'react';
import Header from './Header';
import HeroSection from './HeroSection';
import FeaturesSection from './FeaturesSection';
import WalletConnectSection from './WalletConnectSection';

const HomePage = () => {
  const [isWalletConnected, setIsWalletConnected] = useState(false);
  const [selectedWallet, setSelectedWallet] = useState(null);

  return (
    <div className="min-h-screen">
      <Header isWalletConnected={isWalletConnected} />
      <main className="pt-20">
        <HeroSection />
        <FeaturesSection />
        <WalletConnectSection 
          onConnect={setIsWalletConnected} 
          onWalletSelect={setSelectedWallet}
          selectedWallet={selectedWallet}
        />
      </main>
    </div>
  );
};

export default HomePage;