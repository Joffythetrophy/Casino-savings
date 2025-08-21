import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import HomePage from "./components/HomePage";
import GamesPage from "./components/GamesPage";
import SavingsPage from "./components/SavingsPage";
import TradingPage from "./components/TradingPage";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/games" element={<GamesPage />} />
          <Route path="/savings" element={<SavingsPage />} />
          <Route path="/trading" element={<TradingPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;