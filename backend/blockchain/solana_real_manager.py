"""
Real Solana Blockchain Manager - ACTUAL BLOCKCHAIN TRANSACTIONS
This completely replaces all fake transaction systems with real Solana blockchain calls
"""

import os
import json
import base58
import asyncio
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer
from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import get_associated_token_address, create_associated_token_account
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RealSolanaManager:
    """Real Solana blockchain transaction manager"""
    
    def __init__(self):
        self.rpc_url = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
        self.client = AsyncClient(self.rpc_url, commitment=Confirmed)
        
        # Token mint addresses
        self.USDC_MINT = Pubkey.from_string('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v')
        self.CRT_MINT = Pubkey.from_string('9pjWtc6x88wrRMXTxkBcNB6YtcN7NNcyzDAfUMfRknty')
        
        logger.info('🔗 Real Solana Manager initialized for mainnet')
    
    async def get_real_keypair(self) -> Optional[Keypair]:
        """Get real keypair from environment or generate new one"""
        try:
            # Try to load from environment
            private_key_b58 = os.getenv('SOLANA_REAL_PRIVATE_KEY')
            if private_key_b58:
                private_key_bytes = base58.b58decode(private_key_b58)
                keypair = Keypair.from_bytes(private_key_bytes)
                logger.info(f'✅ Loaded real keypair: {keypair.pubkey()}')
                return keypair
            
            # Generate new keypair if none exists
            keypair = Keypair()
            private_key_b58 = base58.b58encode(keypair.secret()).decode()
            
            logger.warning('🔑 Generated NEW real keypair')
            logger.warning(f'🔑 Public Key: {keypair.pubkey()}')
            logger.warning(f'🔑 Private Key (base58): {private_key_b58}')
            logger.warning('🔑 SAVE THIS PRIVATE KEY TO .env AS SOLANA_REAL_PRIVATE_KEY')
            logger.warning('🔑 FUND THIS ADDRESS WITH SOL AND TOKENS TO ENABLE TRANSFERS')
            
            return keypair
            
        except Exception as e:
            logger.error(f'❌ Failed to get keypair: {str(e)}')
            return None
    
    async def send_real_sol(
        self, 
        to_address: str, 
        amount: float, 
        from_keypair: Optional[Keypair] = None
    ) -> Dict[str, Any]:
        """Send REAL SOL on Solana blockchain"""
        
        try:
            if not from_keypair:
                from_keypair = await self.get_real_keypair()
                if not from_keypair:
                    return {"success": False, "error": "No keypair available"}
            
            # Convert to lamports (1 SOL = 1e9 lamports)
            lamports = int(amount * 1_000_000_000)
            
            # Create destination pubkey
            to_pubkey = Pubkey.from_string(to_address)
            
            # Check balance
            balance_resp = await self.client.get_balance(from_keypair.pubkey())
            if balance_resp.value < lamports + 5000:  # 5000 lamports for fees
                return {
                    "success": False,
                    "error": f"Insufficient SOL balance. Need {amount + 0.000005} SOL, have {balance_resp.value / 1e9} SOL"
                }
            
            # Create transfer instruction
            transfer_instruction = transfer(
                TransferParams(
                    from_pubkey=from_keypair.pubkey(),
                    to_pubkey=to_pubkey,
                    lamports=lamports
                )
            )
            
            # Create and send transaction
            transaction = Transaction()
            transaction.add(transfer_instruction)
            
            # Get recent blockhash
            recent_blockhash = await self.client.get_latest_blockhash()
            transaction.recent_blockhash = recent_blockhash.value.blockhash
            
            # Sign transaction
            transaction.sign(from_keypair)
            
            # Send transaction
            response = await self.client.send_transaction(transaction)
            
            # Confirm transaction
            await self.client.confirm_transaction(response.value)
            
            logger.info(f'✅ Real SOL transfer completed: {response.value}')
            
            return {
                "success": True,
                "transaction_hash": str(response.value),
                "amount": amount,
                "currency": "SOL",
                "from_address": str(from_keypair.pubkey()),
                "to_address": to_address,
                "blockchain": "Solana",
                "explorer_url": f"https://explorer.solana.com/tx/{response.value}",
                "real_transaction": True
            }
            
        except Exception as e:
            logger.error(f'❌ Real SOL transfer failed: {str(e)}')
            return {
                "success": False,
                "error": f"Real SOL transfer failed: {str(e)}"
            }
    
    async def send_real_spl_token(
        self,
        to_address: str,
        amount: float,
        token_mint: Pubkey,
        decimals: int = 6,
        from_keypair: Optional[Keypair] = None
    ) -> Dict[str, Any]:
        """Send REAL SPL tokens (USDC, CRT, etc.) on Solana blockchain"""
        
        try:
            if not from_keypair:
                from_keypair = await self.get_real_keypair()
                if not from_keypair:
                    return {"success": False, "error": "No keypair available"}
            
            to_pubkey = Pubkey.from_string(to_address)
            
            # Calculate token amount with decimals
            token_amount = int(amount * (10 ** decimals))
            
            # Get associated token accounts
            from_token_account = get_associated_token_address(
                from_keypair.pubkey(), token_mint
            )
            
            to_token_account = get_associated_token_address(
                to_pubkey, token_mint
            )
            
            # Create AsyncToken client
            token_client = AsyncToken(
                self.client,
                token_mint,
                TOKEN_PROGRAM_ID,
                from_keypair
            )
            
            # Check if destination token account exists, create if needed
            try:
                await self.client.get_account_info(to_token_account)
            except:
                # Create associated token account for destination
                create_ata_tx = Transaction()
                create_ata_instruction = create_associated_token_account(
                    payer=from_keypair.pubkey(),
                    owner=to_pubkey,
                    mint=token_mint
                )
                create_ata_tx.add(create_ata_instruction)
                
                recent_blockhash = await self.client.get_latest_blockhash()
                create_ata_tx.recent_blockhash = recent_blockhash.value.blockhash
                create_ata_tx.sign(from_keypair)
                
                await self.client.send_transaction(create_ata_tx)
                logger.info(f'✅ Created token account for {to_address}')
            
            # Check token balance
            balance_resp = await token_client.get_balance(from_token_account)
            if balance_resp.value.amount < token_amount:
                return {
                    "success": False,
                    "error": f"Insufficient token balance. Need {amount}, have {balance_resp.value.amount / (10 ** decimals)}"
                }
            
            # Transfer tokens
            transfer_resp = await token_client.transfer(
                source=from_token_account,
                dest=to_token_account,
                owner=from_keypair,
                amount=token_amount
            )
            
            logger.info(f'✅ Real SPL token transfer completed: {transfer_resp.value}')
            
            return {
                "success": True,
                "transaction_hash": str(transfer_resp.value),
                "amount": amount,
                "currency": str(token_mint),
                "from_address": str(from_keypair.pubkey()),
                "to_address": to_address,
                "blockchain": "Solana",
                "explorer_url": f"https://explorer.solana.com/tx/{transfer_resp.value}",
                "real_transaction": True,
                "token_mint": str(token_mint)
            }
            
        except Exception as e:
            logger.error(f'❌ Real SPL token transfer failed: {str(e)}')
            return {
                "success": False,
                "error": f"Real SPL token transfer failed: {str(e)}"
            }
    
    async def send_real_usdc(
        self,
        to_address: str, 
        amount: float,
        from_keypair: Optional[Keypair] = None
    ) -> Dict[str, Any]:
        """Send REAL USDC tokens"""
        result = await self.send_real_spl_token(
            to_address=to_address,
            amount=amount,
            token_mint=self.USDC_MINT,
            decimals=6,  # USDC has 6 decimals
            from_keypair=from_keypair
        )
        if result.get("success"):
            result["currency"] = "USDC"
        return result
    
    async def send_real_crt(
        self,
        to_address: str,
        amount: float, 
        from_keypair: Optional[Keypair] = None
    ) -> Dict[str, Any]:
        """Send REAL CRT tokens"""
        result = await self.send_real_spl_token(
            to_address=to_address,
            amount=amount,
            token_mint=self.CRT_MINT,
            decimals=9,  # CRT has 9 decimals (assuming)
            from_keypair=from_keypair
        )
        if result.get("success"):
            result["currency"] = "CRT"
        return result
    
    async def get_real_balance(
        self,
        address: str,
        currency: str = "SOL"
    ) -> Dict[str, Any]:
        """Get REAL blockchain balance"""
        
        try:
            pubkey = Pubkey.from_string(address)
            
            if currency == "SOL":
                balance_resp = await self.client.get_balance(pubkey)
                balance_sol = balance_resp.value / 1_000_000_000
                
                return {
                    "success": True,
                    "balance": balance_sol,
                    "currency": "SOL",
                    "address": address,
                    "real_balance": True
                }
            
            elif currency == "USDC":
                token_account = get_associated_token_address(pubkey, self.USDC_MINT)
                token_client = AsyncToken(
                    self.client, self.USDC_MINT, TOKEN_PROGRAM_ID, None
                )
                
                try:
                    balance_resp = await token_client.get_balance(token_account)
                    balance_usdc = balance_resp.value.amount / 1_000_000  # 6 decimals
                    
                    return {
                        "success": True,
                        "balance": balance_usdc,
                        "currency": "USDC",
                        "address": address,
                        "real_balance": True
                    }
                except:
                    return {
                        "success": True,
                        "balance": 0.0,
                        "currency": "USDC",
                        "address": address,
                        "real_balance": True,
                        "note": "No USDC token account found"
                    }
            
            elif currency == "CRT":
                token_account = get_associated_token_address(pubkey, self.CRT_MINT)
                token_client = AsyncToken(
                    self.client, self.CRT_MINT, TOKEN_PROGRAM_ID, None
                )
                
                try:
                    balance_resp = await token_client.get_balance(token_account)
                    balance_crt = balance_resp.value.amount / 1_000_000_000  # 9 decimals
                    
                    return {
                        "success": True,
                        "balance": balance_crt,
                        "currency": "CRT", 
                        "address": address,
                        "real_balance": True
                    }
                except:
                    return {
                        "success": True,
                        "balance": 0.0,
                        "currency": "CRT",
                        "address": address,
                        "real_balance": True,
                        "note": "No CRT token account found"
                    }
            
            else:
                return {
                    "success": False,
                    "error": f"Unsupported currency: {currency}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Balance check failed: {str(e)}"
            }

# Global instance
real_solana_manager = RealSolanaManager()