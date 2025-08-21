import React from 'react';
import { Shield, TrendingUp, Zap } from 'lucide-react';

const FeatureCard = ({ icon: Icon, title, description }) => {
  return (
    <div className="group relative bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 hover:border-yellow-400/30 transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-yellow-400/20">
      {/* Background Glow */}
      <div className="absolute inset-0 bg-gradient-to-br from-yellow-400/5 to-purple-600/5 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
      
      {/* Content */}
      <div className="relative z-10 text-center">
        {/* Icon */}
        <div className="w-16 h-16 mx-auto mb-6 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-2xl flex items-center justify-center group-hover:rotate-12 transition-transform duration-500">
          <Icon className="w-8 h-8 text-black" />
        </div>
        
        {/* Title */}
        <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-yellow-400 transition-colors duration-300">
          {title}
        </h3>
        
        {/* Description */}
        <p className="text-gray-300 leading-relaxed group-hover:text-gray-200 transition-colors duration-300">
          {description}
        </p>
      </div>
    </div>
  );
};

const FeaturesSection = () => {
  const features = [
    {
      icon: Shield,
      title: "No KYC Required",
      description: "Start playing instantly with just your crypto wallet"
    },
    {
      icon: TrendingUp,
      title: "Auto Savings",
      description: "Every loss goes into your personal savings account"
    },
    {
      icon: Zap,
      title: "Instant Payouts",
      description: "Withdraw winnings to your spending wallet anytime"
    }
  ];

  return (
    <section className="py-20 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <FeatureCard 
              key={index}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;