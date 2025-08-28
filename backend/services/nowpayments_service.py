"""
NOWPayments Service for 3-Treasury Casino System
Handles real cryptocurrency withdrawals for DOGE, TRX, USDC with treasury wallet routing
"""

import os
import requests
import hmac
import hashlib
import json
import asyncio
import jwt
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class TreasuryConfig:
    """Configuration for treasury wallets"""
    name: str
    currencies: List[str]
    min_amount: Decimal
    max_amount: Decimal
    priority: int  # 1=highest, 3=lowest

@dataclass
class CurrencyConfig:
    """Configuration for supported cryptocurrencies"""
    code: str
    name: str
    min_withdrawal: Decimal
    network: str
    decimals: int
    fee_estimate: Decimal

class NOWPaymentsService:
    """
    NOWPayments integration for casino dApp with 3-treasury system
    Provides real blockchain withdrawals for DOGE, TRX, USDC
    """
    
    # Treasury wallet configurations
    TREASURIES = {
        'treasury_1_savings': TreasuryConfig(
            name='Savings Treasury',
            currencies=['DOGE', 'TRX', 'USDC'],
            min_amount=Decimal('1'),
            max_amount=Decimal('100000'),
            priority=2
        ),
        'treasury_2_liquidity': TreasuryConfig(
            name='Liquidity Treasury (MAIN)',
            currencies=['DOGE', 'TRX', 'USDC'],
            min_amount=Decimal('1'),
            max_amount=Decimal('1000000'),
            priority=1  # Main treasury
        ),
        'treasury_3_winnings': TreasuryConfig(
            name='Winnings Treasury',
            currencies=['DOGE', 'TRX', 'USDC'],
            min_amount=Decimal('1'),
            max_amount=Decimal('500000'),
            priority=3  # Most active
        )
    }
    
    # Supported currencies
    CURRENCIES = {
        'DOGE': CurrencyConfig(
            code='DOGE',
            name='Dogecoin',
            min_withdrawal=Decimal('10'),
            network='DOGE',
            decimals=8,
            fee_estimate=Decimal('1')
        ),
        'TRX': CurrencyConfig(
            code='TRX', 
            name='Tron',
            min_withdrawal=Decimal('10'),
            network='TRX',
            decimals=6,
            fee_estimate=Decimal('1')
        ),
        'USDC': CurrencyConfig(
            code='USDC',
            name='USD Coin',
            min_withdrawal=Decimal('5'),
            network='ERC20',  # Can also be TRC20
            decimals=6,
            fee_estimate=Decimal('2')
        )
    }
    
    def __init__(self):
        """Initialize NOWPayments service with API credentials"""
        self.api_key = os.getenv('NOWPAYMENTS_API_KEY')
        self.sandbox = os.getenv('NOWPAYMENTS_SANDBOX', 'true').lower() == 'true'
        self.ipn_secret = os.getenv('NOWPAYMENTS_IPN_SECRET')
        
        # API URLs
        if self.sandbox:
            self.base_url = 'https://api-sandbox.nowpayments.io/v1'
        else:
            self.base_url = 'https://api.nowpayments.io/v1'
        
        if not self.api_key:
            raise ValueError("NOWPayments API key not found in environment variables")
            
        logger.info(f"NOWPayments service initialized ({'sandbox' if self.sandbox else 'production'} mode)")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers with authentication"""
        return {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make authenticated API request to NOWPayments"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            if method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                response = requests.get(url, headers=headers, timeout=30)
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"NOWPayments API success: {method} {endpoint}")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"NOWPayments API error: {method} {endpoint} - {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    logger.error(f"Error details: {error_detail}")
                except:
                    logger.error(f"Error response: {e.response.text}")
            raise Exception(f"NOWPayments API request failed: {str(e)}")
    
    async def get_available_currencies(self) -> List[str]:
        """Get list of available currencies"""
        try:
            result = await self._make_request('GET', '/currencies')
            currencies = result.get('currencies', [])
            
            # Filter for supported currencies (convert to uppercase for comparison)
            supported = [curr.upper() for curr in currencies if curr.upper() in self.CURRENCIES.keys()]
            return supported
            
        except Exception as e:
            logger.error(f"Failed to get available currencies: {e}")
            return list(self.CURRENCIES.keys())  # Fallback
    
    async def get_minimum_amount(self, currency_from: str, currency_to: str = None) -> Decimal:
        """Get minimum payment amount for currency"""
        try:
            params = f"?currency_from={currency_from}"
            if currency_to:
                params += f"&currency_to={currency_to}"
            
            result = await self._make_request('GET', f'/min-amount{params}')
            min_amount = result.get('min_amount', 0)
            return Decimal(str(min_amount))
            
        except Exception as e:
            logger.error(f"Failed to get minimum amount: {e}")
            return self.CURRENCIES.get(currency_from, {}).min_withdrawal
    
    def determine_treasury_wallet(self, amount: Decimal, currency: str, 
                                 withdrawal_type: str = 'standard') -> str:
        """
        Determine which treasury wallet to use for withdrawal
        
        Args:
            amount: Withdrawal amount
            currency: Currency code
            withdrawal_type: 'standard', 'high_value', 'winnings', 'savings'
        """
        
        # Treasury selection logic for casino operations
        if withdrawal_type == 'winnings' or amount <= Decimal('1000'):
            return 'treasury_3_winnings'  # Fast, frequent withdrawals
        elif withdrawal_type == 'savings' or amount >= Decimal('50000'):
            return 'treasury_1_savings'   # Large, less frequent
        else:
            return 'treasury_2_liquidity' # Main operational treasury
    
    async def create_payout(self, recipient_address: str, amount: Decimal, 
                           currency: str, user_id: str, treasury_type: str = None) -> Dict[str, Any]:
        """
        Create real cryptocurrency payout using NOWPayments
        
        Args:
            recipient_address: External wallet address
            amount: Amount to withdraw
            currency: Currency code (DOGE, TRX, USDC)
            user_id: User identifier for tracking
            treasury_type: Override treasury selection
        """
        try:
            # Validate currency
            if currency not in self.CURRENCIES:
                raise ValueError(f"Unsupported currency: {currency}")
            
            currency_config = self.CURRENCIES[currency]
            
            # Validate minimum amount
            if amount < currency_config.min_withdrawal:
                raise ValueError(f"Amount below minimum: {currency_config.min_withdrawal} {currency}")
            
            # Determine treasury wallet
            if not treasury_type:
                treasury_type = self.determine_treasury_wallet(amount, currency)
            
            treasury_config = self.TREASURIES[treasury_type]
            logger.info(f"Using {treasury_config.name} for {amount} {currency} withdrawal")
            
            # Create payout request
            payout_data = {
                'ipn_callback_url': f'https://your-domain.com/api/webhooks/nowpayments/payout',
                'withdrawals': [
                    {
                        'address': recipient_address,
                        'currency': currency.lower(),
                        'amount': str(amount),
                        'extra_id': f"casino_withdrawal_{user_id}_{int(datetime.utcnow().timestamp())}"
                    }
                ]
            }
            
            # Execute payout
            result = await self._make_request('POST', '/payout', payout_data)
            
            # Extract payout information
            payout_info = {
                'success': True,
                'payout_id': result.get('id'),
                'status': result.get('status', 'processing'),
                'currency': currency,
                'amount': str(amount),
                'recipient_address': recipient_address,
                'treasury_used': treasury_type,
                'treasury_name': treasury_config.name,
                'created_at': datetime.utcnow().isoformat(),
                'service': 'nowpayments',
                'network': currency_config.network,
                'estimated_fee': str(currency_config.fee_estimate),
                'batch_id': result.get('batch_id'),
                'withdrawals': result.get('withdrawals', [])
            }
            
            # If withdrawals array exists, get transaction details
            if payout_info['withdrawals']:
                first_withdrawal = payout_info['withdrawals'][0]
                payout_info.update({
                    'transaction_hash': first_withdrawal.get('hash'),
                    'blockchain_hash': first_withdrawal.get('hash'),
                    'withdrawal_id': first_withdrawal.get('id'),
                    'verification_url': self._get_verification_url(currency, first_withdrawal.get('hash'))
                })
            
            logger.info(f"NOWPayments payout created: {payout_info['payout_id']}")
            return payout_info
            
        except Exception as e:
            logger.error(f"NOWPayments payout failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'service': 'nowpayments',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _get_verification_url(self, currency: str, tx_hash: str) -> Optional[str]:
        """Get blockchain explorer URL for transaction verification"""
        if not tx_hash:
            return None
        
        explorers = {
            'DOGE': f'https://dogechain.info/tx/{tx_hash}',
            'TRX': f'https://tronscan.org/#/transaction/{tx_hash}',
            'USDC': f'https://etherscan.io/tx/{tx_hash}'  # Assuming ERC-20
        }
        
        return explorers.get(currency)
    
    async def get_payout_status(self, payout_id: str) -> Dict[str, Any]:
        """Get status of NOWPayments payout"""
        try:
            result = await self._make_request('GET', f'/payout/{payout_id}')
            
            return {
                'payout_id': payout_id,
                'status': result.get('status'),
                'created_at': result.get('created_at'),
                'updated_at': result.get('updated_at'),
                'withdrawals': result.get('withdrawals', []),
                'total_amount': result.get('total_amount'),
                'currency': result.get('currency')
            }
            
        except Exception as e:
            logger.error(f"Failed to get payout status: {e}")
            return {'error': str(e)}
    
    async def create_mass_payout(self, withdrawals: List[Dict], currency: str, 
                                treasury_type: str = None) -> Dict[str, Any]:
        """
        Create mass payout for multiple withdrawals (casino batch processing)
        
        Args:
            withdrawals: List of {address, amount, user_id} dicts
            currency: Currency for all withdrawals
            treasury_type: Treasury wallet to use
        """
        try:
            if not treasury_type:
                # Use liquidity treasury for mass payouts
                treasury_type = 'treasury_2_liquidity'
            
            treasury_config = self.TREASURIES[treasury_type]
            
            # Prepare withdrawal array
            withdrawal_array = []
            total_amount = Decimal('0')
            
            for withdrawal in withdrawals:
                amount = Decimal(str(withdrawal['amount']))
                total_amount += amount
                
                withdrawal_array.append({
                    'address': withdrawal['address'],
                    'currency': currency.lower(),
                    'amount': str(amount),
                    'extra_id': f"casino_batch_{withdrawal['user_id']}_{int(datetime.utcnow().timestamp())}"
                })
            
            # Create mass payout
            payout_data = {
                'ipn_callback_url': f'https://your-domain.com/api/webhooks/nowpayments/mass-payout',
                'withdrawals': withdrawal_array
            }
            
            result = await self._make_request('POST', '/payout', payout_data)
            
            return {
                'success': True,
                'batch_id': result.get('id'),
                'status': result.get('status'),
                'currency': currency,
                'total_amount': str(total_amount),
                'withdrawal_count': len(withdrawal_array),
                'treasury_used': treasury_type,
                'treasury_name': treasury_config.name,
                'created_at': datetime.utcnow().isoformat(),
                'withdrawals': result.get('withdrawals', [])
            }
            
        except Exception as e:
            logger.error(f"Mass payout failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def verify_ipn_signature(self, payload: str, signature: str) -> bool:
        """Verify IPN webhook signature from NOWPayments"""
        if not self.ipn_secret:
            logger.warning("IPN secret not configured")
            return True  # Skip validation if not configured
        
        expected_signature = hmac.new(
            self.ipn_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    async def process_ipn_notification(self, ipn_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process IPN notification for payout status updates"""
        try:
            notification_info = {
                'payout_id': ipn_data.get('payout_id'),
                'status': ipn_data.get('status'),
                'currency': ipn_data.get('currency'),
                'amount': ipn_data.get('amount'),
                'hash': ipn_data.get('hash'),
                'address': ipn_data.get('address'),
                'extra_id': ipn_data.get('extra_id'),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Processed IPN notification: {notification_info['payout_id']}")
            return notification_info
            
        except Exception as e:
            logger.error(f"Failed to process IPN: {e}")
            raise Exception(f"IPN processing failed: {str(e)}")
    
    def get_treasury_info(self, treasury_type: str) -> Dict[str, Any]:
        """Get information about a treasury wallet"""
        if treasury_type not in self.TREASURIES:
            raise ValueError(f"Unknown treasury type: {treasury_type}")
        
        treasury = self.TREASURIES[treasury_type]
        return {
            'type': treasury_type,
            'name': treasury.name,
            'currencies': treasury.currencies,
            'min_amount': str(treasury.min_amount),
            'max_amount': str(treasury.max_amount),
            'priority': treasury.priority
        }
    
    def get_currency_info(self, currency: str) -> Dict[str, Any]:
        """Get currency configuration information"""
        if currency not in self.CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}")
        
        config = self.CURRENCIES[currency]
        return {
            'code': config.code,
            'name': config.name,
            'min_withdrawal': str(config.min_withdrawal),
            'network': config.network,
            'decimals': config.decimals,
            'fee_estimate': str(config.fee_estimate)
        }
    
    async def get_account_balance(self) -> Dict[str, Any]:
        """Get NOWPayments account balance (if available in API)"""
        try:
            # Note: This endpoint may not be available in all NOWPayments versions
            result = await self._make_request('GET', '/balance')
            return result
        except Exception as e:
            logger.warning(f"Balance check not available: {e}")
            return {'note': 'Balance information not available via API'}

# Global service instance
nowpayments_service = NOWPaymentsService()