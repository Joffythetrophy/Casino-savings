"""
Treasury Address Configuration
User's real treasury wallet addresses for different cryptocurrencies
"""

# User's Real Treasury Addresses - Updated with actual wallet addresses
TREASURY_ADDRESSES = {
    "USDC": {
        "address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
        "network": "Solana",
        "description": "Solana USDC Treasury Wallet",
        "currency_type": "SPL Token"
    },
    "TRON": {
        "address": "TJkna9XCi5noxE7hsEo6jz6et6c3B7zE9o", 
        "network": "TRON",
        "description": "TRON Treasury Wallet",
        "currency_type": "Native TRX"
    },
    "DOGE": {
        "address": "DNmtdukSPBf1PTqVQ9z8GGSJjpR8JqAimQ",
        "network": "Dogecoin", 
        "description": "Dogecoin Treasury Wallet",
        "currency_type": "Native DOGE"
    },
    "SOL": {
        "address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
        "network": "Solana",
        "description": "Solana Native Treasury Wallet", 
        "currency_type": "Native SOL"
    },
    "CRT": {
        "address": "DwK4nUM8TKWAxEBKTG6mWA6PBRDHFPA3beLB18pwCekq",
        "network": "Solana",
        "description": "CRT Token Treasury Wallet",
        "currency_type": "SPL Token"
    }
}

def get_treasury_address(currency: str) -> dict:
    """Get treasury address configuration for a specific currency"""
    currency_upper = currency.upper()
    if currency_upper == "TRX":
        currency_upper = "TRON"
    
    return TREASURY_ADDRESSES.get(currency_upper, {})

def get_all_treasury_addresses() -> dict:
    """Get all treasury addresses"""
    return TREASURY_ADDRESSES

def validate_treasury_addresses():
    """Validate all treasury addresses are properly configured"""
    results = {}
    
    for currency, config in TREASURY_ADDRESSES.items():
        address = config.get("address")
        network = config.get("network")
        
        results[currency] = {
            "address": address,
            "network": network,
            "configured": bool(address and network),
            "address_length": len(address) if address else 0
        }
    
    return results