import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import CasinoLobby from "./components/CasinoLobby";
import SavingsPage from "./components/SavingsPage";
import WalletManager from "./components/WalletManager";
import { Toaster } from "./components/ui/toaster";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<CasinoLobby />} />
          <Route path="/savings" element={<SavingsPage />} />
          <Route path="/wallet" element={<WalletManager />} />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;