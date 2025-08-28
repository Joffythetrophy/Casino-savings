import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Toaster } from "./components/ui/toaster";
import Header from "./components/Header";
import HeroSection from "./components/HeroSection";
import CasinoLobby from "./components/CasinoLobby";
import SavingsPage from "./components/SavingsPage";
import TradingPage from "./components/TradingPage";
import WalletManager from "./components/WalletManager";
import PremiumDashboard from "./components/PremiumDashboard";
import AdminControlPanel from "./components/AdminControlPanel";
import ConversionHistoryTracker from "./components/ConversionHistoryTracker";
import StreamlinedGamingDashboard from "./components/StreamlinedGamingDashboard";
import MillionaireCasinoInterface from "./components/MillionaireCasinoInterface";
import SimplifiedCasinoInterface from "./components/SimplifiedCasinoInterface";
import { AuthProvider, useAuth, AuthModal } from "./components/UserAuth";

function AppContent() {
  const { user, isAuthenticated, loading } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [userBalance, setUserBalance] = useState(null);

  // Fetch user balance when authenticated
  useEffect(() => {
    const fetchBalance = async () => {
      if (isAuthenticated && user?.wallet_address) {
        try {
          const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
          const response = await fetch(`${backendUrl}/api/wallet/${user.wallet_address}`);
          if (response.ok) {
            const data = await response.json();
            if (data.success && data.wallet) {
              setUserBalance(data.wallet);
            }
          }
        } catch (error) {
          console.error('Error fetching balance:', error);
        }
      }
    };

    fetchBalance();
    // Refresh balance every 10 seconds
    const interval = setInterval(fetchBalance, 10000);
    return () => clearInterval(interval);
  }, [isAuthenticated, user?.wallet_address]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <Router>
        <Header />
        {!isAuthenticated ? (
          <>
            <Routes>
              <Route path="/" element={
                <div className="flex items-center justify-center min-h-[80vh]">
                  <div className="text-center">
                    <h1 className="text-4xl font-bold text-white mb-4">Welcome to Casino Savings</h1>
                    <p className="text-gray-300 mb-8">Login or create an account to start playing and saving</p>
                    <button 
                      onClick={() => setShowAuthModal(true)}
                      className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-black font-bold py-3 px-8 rounded-lg text-lg hover:from-yellow-300 hover:to-yellow-500 transition-all"
                    >
                      Get Started
                    </button>
                  </div>
                </div>
              } />
              <Route path="/wallet" element={
                <div className="flex items-center justify-center min-h-[80vh]">
                  <div className="text-center">
                    <h1 className="text-4xl font-bold text-white mb-4">Authentication Required</h1>
                    <p className="text-gray-300 mb-8">Please login to access your wallet</p>
                    <button 
                      onClick={() => setShowAuthModal(true)}
                      className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-black font-bold py-3 px-8 rounded-lg text-lg hover:from-yellow-300 hover:to-yellow-500 transition-all"
                    >
                      Login
                    </button>
                  </div>
                </div>
              } />
              <Route path="/savings" element={
                <div className="flex items-center justify-center min-h-[80vh]">
                  <div className="text-center">
                    <h1 className="text-4xl font-bold text-white mb-4">Authentication Required</h1>
                    <p className="text-gray-300 mb-8">Please login to access your savings</p>
                    <button 
                      onClick={() => setShowAuthModal(true)}
                      className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-black font-bold py-3 px-8 rounded-lg text-lg hover:from-yellow-300 hover:to-yellow-500 transition-all"
                    >
                      Login
                    </button>
                  </div>
                </div>
              } />
              <Route path="*" element={
                <div className="flex items-center justify-center min-h-[80vh]">
                  <div className="text-center">
                    <h1 className="text-4xl font-bold text-white mb-4">Welcome to Casino Savings</h1>
                    <p className="text-gray-300 mb-8">Login or create an account to start playing and saving</p>
                    <button 
                      onClick={() => setShowAuthModal(true)}
                      className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-black font-bold py-3 px-8 rounded-lg text-lg hover:from-yellow-300 hover:to-yellow-500 transition-all"
                    >
                      Get Started
                    </button>
                  </div>
                </div>
              } />
            </Routes>
            <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
          </>
        ) : (
          <Routes>
            <Route path="/" element={<SimplifiedCasinoInterface />} />
            <Route path="/games" element={<SimplifiedCasinoInterface />} />
            <Route path="/savings" element={<SavingsPage />} />
            <Route path="/trading" element={<TradingPage />} />
            <Route path="/wallet" element={<WalletManager />} />
            <Route path="/dashboard" element={<PremiumDashboard onNavigate={(section) => window.location.href = `/${section}`} />} />
            <Route path="/admin" element={<AdminControlPanel />} />
            <Route path="/history" element={<ConversionHistoryTracker />} />
          </Routes>
        )}
      </Router>
      <Toaster />
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;