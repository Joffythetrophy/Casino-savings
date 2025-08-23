import React, { useState } from "react";
import "./App.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Toaster } from "./components/ui/toaster";
import Header from "./components/Header";
import HeroSection from "./components/HeroSection";
import CasinoLobby from "./components/CasinoLobby";
import SavingsPage from "./components/SavingsPage";
import TradingPage from "./components/TradingPage";
import WalletManager from "./components/WalletManager";
import { AuthProvider, useAuth, AuthModal } from "./components/UserAuth";

function AppContent() {
  const { isAuthenticated, loading } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
        <Router>
          <Header />
        </Router>
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
        <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
        <Toaster />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      <Router>
        <Header />
        <Routes>
          <Route path="/" element={
            <>
              <HeroSection />
              <CasinoLobby />
            </>
          } />
          <Route path="/savings" element={<SavingsPage />} />
          <Route path="/trading" element={<TradingPage />} />
          <Route path="/wallet" element={<WalletManager />} />
        </Routes>
        <Toaster />
      </Router>
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