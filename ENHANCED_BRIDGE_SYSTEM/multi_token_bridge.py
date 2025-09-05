# Enhanced Multi-Token Bridge System for All Your Tokens

# YOUR TOKEN PORTFOLIO CONFIGURATION
YOUR_TOKEN_ASSETS = {
    "CRT": {
        "address": "CRTtoken1111111111111111111111111111111111",
        "symbol": "CRT",
        "name": "Casino Revenue Token", 
        "decimals": 9,
        "your_balance": 560000,  # Your actual CRT balance
        "current_price": 0.25,   # $0.25 per CRT
        "total_value_usd": 140000,  # $140k total value
        "logo": "💎"
    },
    "TOKEN_21M": {
        "address": "3ZP9KAKwJTMbhcbJdiaLvLXAgkmKVoAeNMQ6wNavjupx",  # Your 21M supply token
        "symbol": "T21M",
        "name": "Tiger Token 21M Supply",
        "decimals": 9, 
        "total_supply": 21000000,
        "your_balance": 0,  # You'll need to specify your actual balance
        "current_price": 0.0,  # You'll need to set estimated price
        "total_value_usd": 0,  # Will calculate based on your balance * price
        "logo": "🔥"
    },
    "TOKEN_52M": {
        "address": "6MPSpfXcbYaZNLczhu53Q9MaqTHPa1B7BRGJSmiU17f4",  # Your 52M supply token  
        "symbol": "T52M",
        "name": "Tiger Token 52M Supply",
        "decimals": 9,
        "total_supply": 52000000,
        "your_balance": 0,  # You'll need to specify your actual balance
        "current_price": 0.0,  # You'll need to set estimated price
        "total_value_usd": 0,  # Will calculate based on your balance * price
        "logo": "⚡"
    }
}

# BRIDGEABLE DESTINATION TOKENS
BRIDGE_DESTINATIONS = {
    "USDC": {
        "address": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "symbol": "USDC",
        "name": "USD Coin",
        "decimals": 6,
        "current_price": 1.0,
        "logo": "💵"
    },
    "SOL": {
        "address": "So11111111111111111111111111111111111111112",
        "symbol": "SOL", 
        "name": "Solana",
        "decimals": 9,
        "current_price": 180.0,
        "logo": "◎"
    },
    "BTC": {
        "address": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E",
        "symbol": "BTC",
        "name": "Wrapped Bitcoin",
        "decimals": 6,
        "current_price": 65000.0,
        "logo": "₿"
    },
    "ETH": {
        "address": "7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs", 
        "symbol": "ETH",
        "name": "Wrapped Ethereum",
        "decimals": 8,
        "current_price": 3200.0,
        "logo": "⟠"
    }
}

class MultiTokenBridge:
    def __init__(self):
        self.bridge_requests = []
        self.iou_records = []
        self.total_ious_issued = 0
    
    def calculate_bridge_value(self, source_token: str, amount: float) -> dict:
        """Calculate USD value and destination amounts for bridge"""
        
        if source_token not in YOUR_TOKEN_ASSETS:
            raise ValueError(f"Token {source_token} not available for bridging")
            
        token_info = YOUR_TOKEN_ASSETS[source_token]
        
        if amount > token_info["your_balance"]:
            raise ValueError(f"Insufficient balance. Available: {token_info['your_balance']}")
        
        # Calculate USD value
        usd_value = amount * token_info["current_price"]
        
        # Calculate destination amounts for all possible tokens
        destination_amounts = {}
        for dest_symbol, dest_info in BRIDGE_DESTINATIONS.items():
            destination_amounts[dest_symbol] = usd_value / dest_info["current_price"]
        
        return {
            "source_token": source_token,
            "source_amount": amount,
            "usd_value": usd_value,
            "destination_amounts": destination_amounts,
            "available_balance": token_info["your_balance"]
        }
    
    def create_bridge_request(self, 
                            source_token: str,
                            amount: float, 
                            destination_token: str,
                            user_wallet: str,
                            use_iou: bool = True) -> dict:
        """Create bridge request with IOU system"""
        
        # Validate and calculate
        bridge_calc = self.calculate_bridge_value(source_token, amount)
        
        if destination_token not in BRIDGE_DESTINATIONS:
            raise ValueError(f"Destination token {destination_token} not supported")
        
        destination_amount = bridge_calc["destination_amounts"][destination_token]
        
        # Create bridge request
        bridge_id = f"multi_bridge_{len(self.bridge_requests)}"
        
        bridge_request = {
            "bridge_id": bridge_id,
            "source_token": source_token,
            "source_amount": amount,
            "source_value_usd": bridge_calc["usd_value"],
            "destination_token": destination_token,
            "destination_amount": destination_amount,
            "user_wallet": user_wallet,
            "status": "iou_issued" if use_iou else "pending_liquidity",
            "created_at": "2024-01-01T00:00:00Z",
            "iou_active": use_iou
        }
        
        if use_iou:
            # Create IOU record
            iou_record = {
                "iou_id": f"iou_{len(self.iou_records)}",
                "bridge_id": bridge_id,
                "collateral_token": source_token,
                "collateral_amount": amount,
                "collateral_value_usd": bridge_calc["usd_value"],
                "issued_token": destination_token,
                "issued_amount": destination_amount,
                "interest_rate": 0.0,  # No interest
                "repayment_terms": "Repay when source token liquidity available",
                "status": "active"
            }
            
            bridge_request["iou_details"] = iou_record
            self.iou_records.append(iou_record)
            self.total_ious_issued += bridge_calc["usd_value"]
            
            # Update available balance (reserved as collateral)
            YOUR_TOKEN_ASSETS[source_token]["your_balance"] -= amount
        
        self.bridge_requests.append(bridge_request)
        return bridge_request
    
    def get_portfolio_summary(self) -> dict:
        """Get complete portfolio summary including bridge potential"""
        
        total_portfolio_value = 0
        token_breakdown = {}
        
        for token_symbol, token_info in YOUR_TOKEN_ASSETS.items():
            token_value = token_info["your_balance"] * token_info["current_price"]
            total_portfolio_value += token_value
            
            token_breakdown[token_symbol] = {
                "balance": token_info["your_balance"],
                "price": token_info["current_price"],
                "value_usd": token_value,
                "total_supply": token_info.get("total_supply", "N/A"),
                "bridgeable": token_value > 0
            }
        
        return {
            "total_portfolio_value_usd": total_portfolio_value,
            "total_ious_issued_usd": self.total_ious_issued,
            "available_to_bridge_usd": total_portfolio_value - self.total_ious_issued,
            "tokens": token_breakdown,
            "active_bridge_requests": len([r for r in self.bridge_requests if r["status"] == "iou_issued"]),
            "bridge_destinations": list(BRIDGE_DESTINATIONS.keys())
        }
    
    def get_bridge_opportunities(self) -> dict:
        """Show what you can bridge right now"""
        
        opportunities = {}
        
        for token_symbol, token_info in YOUR_TOKEN_ASSETS.items():
            if token_info["your_balance"] > 0 and token_info["current_price"] > 0:
                
                # Calculate max bridge amounts for each destination
                max_usd_value = token_info["your_balance"] * token_info["current_price"]
                
                destination_options = {}
                for dest_symbol, dest_info in BRIDGE_DESTINATIONS.items():
                    max_dest_amount = max_usd_value / dest_info["current_price"]
                    destination_options[dest_symbol] = {
                        "max_amount": max_dest_amount,
                        "value_usd": max_usd_value,
                        "example_bridge": {
                            "source": f"Bridge 50% = {token_info['your_balance'] * 0.5:,.0f} {token_symbol}",
                            "get": f"Get {max_dest_amount * 0.5:,.2f} {dest_symbol}",
                            "value": f"${max_usd_value * 0.5:,.2f}"
                        }
                    }
                
                opportunities[token_symbol] = {
                    "available_balance": token_info["your_balance"],
                    "token_price": token_info["current_price"],
                    "max_bridge_value_usd": max_usd_value,
                    "destinations": destination_options
                }
        
        return opportunities

# Example usage and testing
if __name__ == "__main__":
    
    # Initialize bridge system
    bridge = MultiTokenBridge()
    
    # YOU NEED TO UPDATE THESE WITH YOUR ACTUAL BALANCES:
    # Set your actual token balances
    YOUR_TOKEN_ASSETS["TOKEN_21M"]["your_balance"] = 1000000  # Example: 1M tokens
    YOUR_TOKEN_ASSETS["TOKEN_21M"]["current_price"] = 0.10    # Example: $0.10 per token
    YOUR_TOKEN_ASSETS["TOKEN_21M"]["total_value_usd"] = 100000  # $100k value
    
    YOUR_TOKEN_ASSETS["TOKEN_52M"]["your_balance"] = 2000000  # Example: 2M tokens  
    YOUR_TOKEN_ASSETS["TOKEN_52M"]["current_price"] = 0.05    # Example: $0.05 per token
    YOUR_TOKEN_ASSETS["TOKEN_52M"]["total_value_usd"] = 100000  # $100k value
    
    # Show your complete portfolio
    portfolio = bridge.get_portfolio_summary()
    print("🏦 YOUR COMPLETE TOKEN PORTFOLIO:")
    print(f"Total Value: ${portfolio['total_portfolio_value_usd']:,.2f}")
    
    for token, details in portfolio['tokens'].items():
        print(f"{token}: {details['balance']:,.0f} tokens = ${details['value_usd']:,.2f}")
    
    # Show bridge opportunities  
    opportunities = bridge.get_bridge_opportunities()
    print("\n🌉 BRIDGE OPPORTUNITIES:")
    
    for source_token, options in opportunities.items():
        print(f"\n{source_token} (${options['max_bridge_value_usd']:,.2f} max):")
        for dest_token, dest_info in options['destinations'].items():
            example = dest_info['example_bridge']
            print(f"  → {dest_token}: {example['source']} → {example['get']}")
    
    # Example bridge transaction
    print("\n🔥 EXAMPLE BRIDGE TRANSACTION:")
    bridge_result = bridge.create_bridge_request(
        source_token="CRT",
        amount=200000,  # Bridge 200k CRT
        destination_token="USDC", 
        user_wallet="your_wallet_address",
        use_iou=True
    )
    
    print(f"Bridged: {bridge_result['source_amount']:,.0f} {bridge_result['source_token']}")
    print(f"Got: {bridge_result['destination_amount']:,.2f} {bridge_result['destination_token']}")
    print(f"Value: ${bridge_result['source_value_usd']:,.2f}")
    print(f"Status: {bridge_result['status']}")