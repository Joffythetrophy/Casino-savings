"""
Real Blockchain Configuration
All networks and endpoints for REAL cryptocurrency operations
"""

import os
from typing import Dict, Any

class RealBlockchainConfig:
    """Configuration for real blockchain networks"""
    
    # Solana Configuration
    SOLANA_RPC_ENDPOINT = os.getenv('SOLANA_RPC_ENDPOINT', 'https://api.mainnet-beta.solana.com')
    SOLANA_WEBSOCKET_ENDPOINT = os.getenv('SOLANA_WS_ENDPOINT', 'wss://api.mainnet-beta.solana.com')
    
    # Ethereum Configuration  
    ETHEREUM_RPC_ENDPOINT = os.getenv('ETHEREUM_RPC_ENDPOINT', 'https://mainnet.infura.io/v3/')
    ETHEREUM_CHAIN_ID = 1
    
    # Bitcoin/DOGE Configuration
    BITCOIN_RPC_ENDPOINT = os.getenv('BITCOIN_RPC_ENDPOINT', 'https://blockstream.info/api')
    DOGECOIN_RPC_ENDPOINT = os.getenv('DOGECOIN_RPC_ENDPOINT', 'https://dogechain.info/api/v1')
    
    # TRON Configuration
    TRON_RPC_ENDPOINT = os.getenv('TRON_RPC_ENDPOINT', 'https://api.trongrid.io')
    
    # Token Addresses (Real contracts only)
    TOKEN_ADDRESSES = {
        'solana': {
            'USDC': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            'CRT': '9pjWtc6x88wrRMXTxkBcNB6YtcN7NNcyzDAfUMfRknty',  # Your custom token
            'SOL': 'So11111111111111111111111111111111111111112'
        },
        'ethereum': {
            'USDC': '0xA0b86a33E6441c05b1dF5E7b87d0b2c03bC4F6D0',
            'ETH': '0x0000000000000000000000000000000000000000'
        },
        'tron': {
            'USDT': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',
            'TRX': 'T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb'
        }
    }
    
    # DEX Integration
    DEX_PROTOCOLS = {
        'solana': {
            'orca': {
                'program_id': '9W959DqEETiGZocYWCQPaJ6sD0dILjWJgYzs5sVBs1v5',
                'pools_api': 'https://api.orca.so/v1/pools',
                'swap_api': 'https://api.orca.so/v1/swap'
            }
        },
        'ethereum': {
            'uniswap_v3': {
                'router': '0xE592427A0AEce92De3Edee1F18E0157C05861564',
                'factory': '0x1F98431c8aD98523631AE4a59f267346ea31F984'
            }
        }
    }
    
    # Casino Configuration
    CASINO_CONFIG = {
        'min_bet_amounts': {
            'SOL': 0.001,
            'USDC': 0.1,
            'CRT': 100,
            'ETH': 0.0001,
            'DOGE': 1.0,
            'TRX': 1.0
        },
        'max_bet_amounts': {
            'SOL': 10.0,
            'USDC': 1000.0,
            'CRT': 1000000,
            'ETH': 1.0,
            'DOGE': 100000,
            'TRX': 10000
        },
        'house_edge': 0.02,  # 2% house edge
        'savings_allocation': 0.5  # 50% of losses go to savings
    }
    
    # Real Withdrawal Limits
    WITHDRAWAL_LIMITS = {
        'daily_limits': {
            'SOL': 100.0,
            'USDC': 10000.0,
            'CRT': 10000000,
            'ETH': 10.0,
            'DOGE': 1000000,
            'TRX': 100000
        },
        'min_withdrawal': {
            'SOL': 0.01,
            'USDC': 1.0,
            'CRT': 1000,
            'ETH': 0.001,
            'DOGE': 10.0,
            'TRX': 10.0
        }
    }

# Global config instance
blockchain_config = RealBlockchainConfig()