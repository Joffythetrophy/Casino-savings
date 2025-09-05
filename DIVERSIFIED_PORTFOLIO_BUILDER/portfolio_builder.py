# Diversified Crypto Portfolio Builder
# Bridge your T52M tokens into multiple cryptocurrencies

DIVERSIFIED_PORTFOLIO_OPTIONS = {
    "conservative_starter": {
        "name": "🚀 Conservative Starter Portfolio",
        "total_bridge_amount": 1000000,  # 1M T52M tokens ($100k)
        "allocation": {
            "USDC": 0.40,    # 40% = $40k = 40,000 USDC
            "SOL": 0.25,     # 25% = $25k = 138 SOL
            "ETH": 0.20,     # 20% = $20k = 6.25 ETH  
            "BTC": 0.10,     # 10% = $10k = 0.154 BTC
            "CDT": 0.05      # 5% = $5k = 50,000 CDT
        },
        "description": "Safe diversification with stablecoin base"
    },
    
    "balanced_explorer": {
        "name": "🌟 Balanced Explorer Portfolio", 
        "total_bridge_amount": 5000000,  # 5M T52M tokens ($500k)
        "allocation": {
            "USDC": 0.30,    # 30% = $150k = 150,000 USDC
            "SOL": 0.25,     # 25% = $125k = 694 SOL
            "ETH": 0.20,     # 20% = $100k = 31.25 ETH
            "BTC": 0.15,     # 15% = $75k = 1.15 BTC
            "CDT": 0.10      # 10% = $50k = 500,000 CDT
        },
        "description": "Balanced exposure across major cryptos"
    },
    
    "whale_diversified": {
        "name": "🐋 Whale Diversified Portfolio",
        "total_bridge_amount": 20000000,  # 20M T52M tokens ($2M)
        "allocation": {
            "USDC": 0.25,    # 25% = $500k = 500,000 USDC
            "SOL": 0.25,     # 25% = $500k = 2,777 SOL
            "ETH": 0.20,     # 20% = $400k = 125 ETH
            "BTC": 0.15,     # 15% = $300k = 4.6 BTC
            "CDT": 0.15      # 15% = $300k = 3,000,000 CDT
        },
        "description": "Major crypto whale status across all assets"
    },
    
    "custom_taste_test": {
        "name": "🍽️ Custom Taste Test Portfolio",
        "total_bridge_amount": 2000000,  # 2M T52M tokens ($200k)
        "allocation": {
            "USDC": 0.30,    # 30% = $60k = 60,000 USDC (stable base)
            "SOL": 0.25,     # 25% = $50k = 277 SOL (ecosystem play)
            "ETH": 0.20,     # 20% = $40k = 12.5 ETH (DeFi king)
            "BTC": 0.15,     # 15% = $30k = 0.46 BTC (digital gold)
            "CDT": 0.10      # 10% = $20k = 200,000 CDT (your target)
        },
        "description": "Perfect taste of each major crypto category"
    }
}

def calculate_portfolio_breakdown(portfolio_name: str, t52m_tokens: int, t52m_price: float = 0.10):
    """Calculate exact amounts you'll receive for each crypto"""
    
    if portfolio_name not in DIVERSIFIED_PORTFOLIO_OPTIONS:
        return None
    
    portfolio = DIVERSIFIED_PORTFOLIO_OPTIONS[portfolio_name]
    total_usd_value = t52m_tokens * t52m_price
    
    # Current crypto prices (you'd fetch these from API in real app)
    crypto_prices = {
        "USDC": 1.0,
        "SOL": 180.0,
        "ETH": 3200.0,
        "BTC": 65000.0,
        "CDT": 0.10
    }
    
    breakdown = {
        "portfolio_name": portfolio["name"],
        "total_t52m_bridged": t52m_tokens,
        "total_usd_value": total_usd_value,
        "allocations": {}
    }
    
    for crypto, percentage in portfolio["allocation"].items():
        usd_amount = total_usd_value * percentage
        crypto_amount = usd_amount / crypto_prices[crypto]
        
        breakdown["allocations"][crypto] = {
            "percentage": f"{percentage*100}%",
            "usd_value": usd_amount,
            "crypto_amount": crypto_amount,
            "description": get_crypto_description(crypto)
        }
    
    return breakdown

def get_crypto_description(crypto: str) -> str:
    """Get description of what each crypto represents"""
    descriptions = {
        "USDC": "💵 Stable foundation - your safe harbor",
        "SOL": "⚡ Solana ecosystem - fast & cheap transactions", 
        "ETH": "🔥 DeFi powerhouse - smart contract king",
        "BTC": "🪙 Digital gold - store of value",
        "CDT": "🎨 Creative Dollar - your target investment"
    }
    return descriptions.get(crypto, "🪙 Cryptocurrency")

# Example calculations
if __name__ == "__main__":
    print("🌈 DIVERSIFIED CRYPTO PORTFOLIO OPTIONS")
    print("=" * 50)
    
    # Show all portfolio options
    for portfolio_name, details in DIVERSIFIED_PORTFOLIO_OPTIONS.items():
        print(f"\n{details['name']}")
        print(f"Bridge Amount: {details['total_bridge_amount']:,} T52M tokens")
        print(f"Total Value: ${details['total_bridge_amount'] * 0.10:,.0f}")
        print("Allocation:")
        
        for crypto, percentage in details["allocation"].items():
            usd_amount = details['total_bridge_amount'] * 0.10 * percentage
            print(f"  {crypto}: {percentage*100}% = ${usd_amount:,.0f}")
        
        print(f"Description: {details['description']}")
        print("-" * 40)
    
    # Detailed breakdown example
    print("\n🍽️ DETAILED TASTE TEST BREAKDOWN:")
    breakdown = calculate_portfolio_breakdown("custom_taste_test", 2000000)
    
    for crypto, details in breakdown["allocations"].items():
        print(f"\n{crypto}:")
        print(f"  Amount: {details['crypto_amount']:,.2f} {crypto}")
        print(f"  Value: ${details['usd_value']:,.0f} ({details['percentage']})")
        print(f"  {details['description']}")