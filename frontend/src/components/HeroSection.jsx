import React from 'react';

const HeroSection = () => {
  return (
    <section className="relative py-24 px-6">
      <div className="max-w-4xl mx-auto text-center">
        {/* Main Heading */}
        <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold mb-6 bg-gradient-to-r from-yellow-300 via-yellow-400 to-yellow-600 bg-clip-text text-transparent leading-tight">
          Casino Savings
        </h1>
        
        {/* Subheading */}
        <h2 className="text-2xl md:text-3xl font-semibold text-gray-200 mb-8">
          The casino where losing means saving
        </h2>
        
        {/* Description */}
        <p className="text-lg md:text-xl text-gray-300 leading-relaxed max-w-2xl mx-auto">
          Play your favorite casino games while automatically building your savings. Every loss contributes to your personal savings vault.
        </p>
        
        {/* Decorative elements */}
        <div className="absolute top-1/2 left-10 w-20 h-20 bg-yellow-400/10 rounded-full blur-xl"></div>
        <div className="absolute top-1/3 right-10 w-32 h-32 bg-purple-400/10 rounded-full blur-2xl"></div>
      </section>
    );
  };

export default HeroSection;