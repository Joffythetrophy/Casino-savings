"""
CoinPayments Service for Real Blockchain Transfers
Handles deposits, withdrawals, and transaction management for DOGE, TRX, and USDC
"""

import os
import hmac
import hashlib
import requests
import json
import asyncio
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CurrencyConfig:
    """Configuration for supported cryptocurrencies"""
    name: str
    code: str
    confirmations_required: int
    min_deposit: Decimal
    min_withdrawal: Decimal
    network: str
    precision: int
    withdrawal_fee: Decimal

class CoinPaymentsService:
    """CoinPayments API service for real blockchain transfers"""
    
    # Supported currencies configuration
    CURRENCIES = {
        'DOGE': CurrencyConfig(
            name='Dogecoin',
            code='DOGE',
            confirmations_required=6,
            min_deposit=Decimal('1.0'),
            min_withdrawal=Decimal('10.0'),
            network='DOGE',
            precision=8,
            withdrawal_fee=Decimal('1.0')
        ),
        'TRX': CurrencyConfig(
            name='Tron',
            code='TRX',
            confirmations_required=20,
            min_deposit=Decimal('1.0'),
            min_withdrawal=Decimal('10.0'),
            network='TRX',
            precision=6,
            withdrawal_fee=Decimal('1.0')
        ),
        'USDC': CurrencyConfig(
            name='USD Coin',
            code='USDC',
            confirmations_required=12,
            min_deposit=Decimal('1.0'),
            min_withdrawal=Decimal('5.0'),
            network='ERC20',
            precision=6,
            withdrawal_fee=Decimal('2.0')
        )
    }
    
    def __init__(self):
        """Initialize CoinPayments service with API credentials"""
        self.public_key = os.getenv('COINPAYMENTS_PUBLIC_KEY')
        self.private_key = os.getenv('COINPAYMENTS_PRIVATE_KEY')
        self.merchant_id = os.getenv('COINPAYMENTS_MERCHANT_ID')
        self.ipn_secret = os.getenv('COINPAYMENTS_IPN_SECRET')
        self.api_url = 'https://www.coinpayments.net/api.php'
        
        if not all([self.public_key, self.private_key]):
            raise ValueError("CoinPayments API credentials not found in environment variables")
            
        logger.info("CoinPayments service initialized successfully")
    
    def _generate_signature(self, post_data: str) -> str:
        """Generate HMAC-SHA512 signature for API authentication"""
        return hmac.new(
            self.private_key.encode('utf-8'),
            post_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
    
    async def _make_request(self, params: Dict[str, Any], retries: int = 3) -> Dict[str, Any]:
        """Make authenticated API request to CoinPayments with retry logic"""
        # Add required fields
        params.update({
            'version': 1,
            'key': self.public_key,
            'format': 'json'
        })
        
        # Generate POST data string
        post_data = '&'.join([f"{k}={v}" for k, v in params.items()])
        
        # Generate signature
        signature = self._generate_signature(post_data)
        
        # Set headers
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'HMAC': signature
        }
        
        for attempt in range(retries):
            try:
                response = requests.post(
                    self.api_url,
                    data=post_data,
                    headers=headers,
                    timeout=30
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Check for API errors
                if result.get('error') != 'ok':
                    error_msg = result.get('error', 'Unknown error')
                    logger.error(f"CoinPayments API error: {error_msg}")
                    raise Exception(f"CoinPayments API error: {error_msg}")
                
                logger.info(f"CoinPayments API request successful: {params.get('cmd')}")
                return result
                
            except Exception as e:
                if attempt == retries - 1:
                    logger.error(f"CoinPayments API request failed after {retries} attempts: {str(e)}")
                    raise Exception(f"CoinPayments API request failed: {str(e)}")
                
                # Wait before retry with exponential backoff
                await asyncio.sleep(2 ** attempt)
        
        return {}
    
    async def generate_deposit_address(self, user_id: str, currency: str) -> Dict[str, Any]:
        """Generate deposit address for user and currency"""
        if currency not in self.CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}")
        
        # Create IPN URL for deposit notifications
        ipn_url = f"https://your-domain.com/api/webhooks/coinpayments/deposit"
        
        params = {
            'cmd': 'get_callback_address',
            'currency': currency,
            'ipn_url': ipn_url
        }
        
        try:
            response = await self._make_request(params)
            result = response.get('result', {})
            
            address_info = {
                'address': result.get('address'),
                'currency': currency,
                'network': self.CURRENCIES[currency].network,
                'qr_code_url': f"https://chart.googleapis.com/chart?chs=200x200&cht=qr&chl={result.get('address')}",
                'min_deposit': str(self.CURRENCIES[currency].min_deposit),
                'confirmations_needed': self.CURRENCIES[currency].confirmations_required,
                'pubkey': result.get('pubkey', ''),
                'created_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated deposit address for {user_id}: {currency} - {result.get('address')}")
            return address_info
            
        except Exception as e:
            logger.error(f"Failed to generate deposit address for {user_id}, {currency}: {str(e)}")
            raise Exception(f"Failed to generate deposit address: {str(e)}")
    
    async def create_withdrawal(self, user_id: str, currency: str, amount: Decimal, 
                               destination_address: str, auto_confirm: bool = False) -> Dict[str, Any]:
        """Create withdrawal transaction to external address"""
        if currency not in self.CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}")
        
        currency_config = self.CURRENCIES[currency]
        
        # Validate minimum withdrawal amount
        if amount < currency_config.min_withdrawal:
            raise ValueError(f"Amount below minimum withdrawal: {currency_config.min_withdrawal} {currency}")
        
        # Calculate amount including fee
        total_amount = amount + currency_config.withdrawal_fee
        
        params = {
            'cmd': 'create_withdrawal',
            'currency': currency,
            'amount': str(amount),
            'address': destination_address,
            'auto_confirm': 1 if auto_confirm else 0,
            'ipn_url': f"https://your-domain.com/api/webhooks/coinpayments/withdrawal"
        }
        
        try:
            response = await self._make_request(params)
            result = response.get('result', {})
            
            withdrawal_info = {
                'withdrawal_id': result.get('id'),
                'currency': currency,
                'amount': str(amount),
                'fee': str(currency_config.withdrawal_fee),
                'total_amount': str(total_amount),
                'destination_address': destination_address,
                'status': result.get('status', 0),  # 0=pending, 1=sent
                'created_at': datetime.utcnow().isoformat(),
                'network': currency_config.network
            }
            
            logger.info(f"Created withdrawal for {user_id}: {amount} {currency} to {destination_address}")
            return withdrawal_info
            
        except Exception as e:
            logger.error(f"Failed to create withdrawal for {user_id}: {str(e)}")
            raise Exception(f"Failed to create withdrawal: {str(e)}")
    
    async def get_transaction_info(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction information by ID"""
        params = {
            'cmd': 'get_tx_info',
            'txid': transaction_id
        }
        
        try:
            response = await self._make_request(params)
            result = response.get('result', {})
            
            transaction_info = {
                'transaction_id': transaction_id,
                'time_created': result.get('time_created'),
                'time_expires': result.get('time_expires'),
                'status': result.get('status'),
                'status_text': result.get('status_text'),
                'currency': result.get('coin'),
                'amount': result.get('amount'),
                'fee': result.get('fee'),
                'net_amount': result.get('net'),
                'confirms_needed': result.get('confirms_needed'),
                'recv_confirms': result.get('recv_confirms'),
                'payment_address': result.get('payment_address')
            }
            
            return transaction_info
            
        except Exception as e:
            logger.error(f"Failed to get transaction info for {transaction_id}: {str(e)}")
            raise Exception(f"Failed to get transaction info: {str(e)}")
    
    async def get_account_balances(self) -> Dict[str, Any]:
        """Get CoinPayments account balances for all currencies"""
        params = {
            'cmd': 'balances'
        }
        
        try:
            response = await self._make_request(params)
            result = response.get('result', {})
            
            # Filter for supported currencies only
            filtered_balances = {}
            for currency in self.CURRENCIES.keys():
                if currency in result:
                    balance_info = result[currency]
                    filtered_balances[currency] = {
                        'balance': balance_info.get('balance', '0'),
                        'balance_pending': balance_info.get('balance_pending', '0'),
                        'available': str(Decimal(balance_info.get('balance', '0')) - Decimal(balance_info.get('balance_pending', '0')))
                    }
            
            return {
                'balances': filtered_balances,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get account balances: {str(e)}")
            raise Exception(f"Failed to get account balances: {str(e)}")
    
    def verify_ipn_signature(self, ipn_data: str, signature: str) -> bool:
        """Verify IPN signature for webhook validation"""
        if not self.ipn_secret:
            logger.warning("IPN secret not configured, skipping signature verification")
            return True
        
        expected_signature = hmac.new(
            self.ipn_secret.encode('utf-8'),
            ipn_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        is_valid = hmac.compare_digest(expected_signature, signature)
        if not is_valid:
            logger.warning("Invalid IPN signature received")
        
        return is_valid
    
    async def process_deposit_notification(self, ipn_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process deposit IPN notification"""
        try:
            deposit_info = {
                'transaction_id': ipn_data.get('txn_id'),
                'deposit_id': ipn_data.get('deposit_id'),
                'currency': ipn_data.get('currency'),
                'amount': ipn_data.get('amount'),
                'fee': ipn_data.get('fee'),
                'net_amount': ipn_data.get('net'),
                'address': ipn_data.get('address'),
                'status': int(ipn_data.get('status', 0)),
                'status_text': ipn_data.get('status_text'),
                'confirmations': int(ipn_data.get('confirms', 0)),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Processed deposit notification: {deposit_info['transaction_id']}")
            return deposit_info
            
        except Exception as e:
            logger.error(f"Failed to process deposit notification: {str(e)}")
            raise Exception(f"Failed to process deposit notification: {str(e)}")
    
    async def process_withdrawal_notification(self, ipn_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process withdrawal IPN notification"""
        try:
            withdrawal_info = {
                'withdrawal_id': ipn_data.get('id'),
                'transaction_id': ipn_data.get('txn_id'),
                'currency': ipn_data.get('currency'),
                'amount': ipn_data.get('amount'),
                'fee': ipn_data.get('fee'),
                'status': int(ipn_data.get('status', 0)),
                'status_text': ipn_data.get('status_text'),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Processed withdrawal notification: {withdrawal_info['withdrawal_id']}")
            return withdrawal_info
            
        except Exception as e:
            logger.error(f"Failed to process withdrawal notification: {str(e)}")
            raise Exception(f"Failed to process withdrawal notification: {str(e)}")
    
    def get_currency_info(self, currency: str) -> Dict[str, Any]:
        """Get currency configuration information"""
        if currency not in self.CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency}")
        
        config = self.CURRENCIES[currency]
        return {
            'name': config.name,
            'code': config.code,
            'network': config.network,
            'min_deposit': str(config.min_deposit),
            'min_withdrawal': str(config.min_withdrawal),
            'withdrawal_fee': str(config.withdrawal_fee),
            'confirmations_required': config.confirmations_required,
            'precision': config.precision
        }

# Global service instance
coinpayments_service = CoinPaymentsService()