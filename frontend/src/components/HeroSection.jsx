import React from 'react';

const HeroSection = () => {
  return (
    <section className="relative py-24 px-6">
      <div className="max-w-4xl mx-auto text-center">
        {/* Main Heading */}
        <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold mb-6 bg-gradient-to-r from-casino-green-300 via-emerald-casino-400 to-casino-green-500 bg-clip-text text-transparent leading-tight glow-green">
          🐅 CRT Tiger Casino 🐅
        </h1>
        
        {/* Subheading */}
        <h2 className="text-2xl md:text-3xl font-semibold text-casino-green-200 mb-8">
          Hunt the Fortune • Save the Winnings
        </h2>
        
        {/* Description */}
        <p className="text-lg md:text-xl text-casino-green-100 leading-relaxed max-w-2xl mx-auto mb-12">
          Join the hunt in our premium casino where every play builds your treasure. Tiger-powered gaming with smart savings technology.
        </p>
        
        {/* CTA Button */}
        <button className="btn-primary px-12 py-4 text-xl font-bold rounded-xl shadow-lg glow-green transform hover:scale-105 transition-all duration-300">
          🐅 Start Hunting Fortune 🐅
        </button>
        
        {/* Decorative elements */}
        <div className="absolute top-1/2 left-10 w-20 h-20 bg-casino-green-400/20 rounded-full blur-xl pulse-green"></div>
        <div className="absolute top-1/3 right-10 w-32 h-32 bg-emerald-casino-400/15 rounded-full blur-2xl pulse-green"></div>
        <div className="absolute bottom-1/4 left-1/4 w-16 h-16 bg-casino-green-500/10 rounded-full blur-lg"></div>
      </div>
    </section>
  );
};

export default HeroSection;