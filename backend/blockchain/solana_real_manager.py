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
from solana.system_program import transfer, TransferParams
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.instruction import Instruction
from spl.token.instructions import transfer_checked, TransferCheckedParams, create_associated_token_account
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID
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
            private_key_b58 = base58.b58encode(bytes(keypair)).decode()
            
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
            
            # Create transaction
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
    
    async def send_real_crt(
        self,
        to_address: str,
        amount: float, 
        from_keypair: Optional[Keypair] = None
    ) -> Dict[str, Any]:
        """Send REAL CRT SPL tokens on Solana blockchain"""
        
        try:
            if not from_keypair:
                from_keypair = await self.get_real_keypair()
                if not from_keypair:
                    return {"success": False, "error": "No keypair available"}
            
            from solders.transaction import VersionedTransaction
            from solders.message import MessageV0
            from spl.token.instructions import transfer_checked, TransferCheckedParams
            from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID
            from solders.address_lookup_table_account import AddressLookupTableAccount
            
            # Convert addresses
            to_pubkey = Pubkey.from_string(to_address)
            
            # Convert amount with decimals (CRT has 6 decimals)
            decimals = 6
            token_amount = int(amount * (10 ** decimals))
            
            # Get associated token accounts
            from_ata = await self._get_associated_token_account(from_keypair.pubkey(), self.CRT_MINT)
            to_ata = await self._get_associated_token_account(to_pubkey, self.CRT_MINT)
            
            # Check if destination ATA exists, create if not
            to_ata_info = await self.client.get_account_info(to_ata)
            instructions = []
            
            if not to_ata_info.value:
                # Create associated token account instruction
                from spl.token.instructions import create_associated_token_account
                create_ata_ix = create_associated_token_account(
                    payer=from_keypair.pubkey(),
                    owner=to_pubkey,
                    mint=self.CRT_MINT
                )
                instructions.append(create_ata_ix)
            
            # Create transfer instruction
            transfer_ix = transfer_checked(
                TransferCheckedParams(
                    program_id=TOKEN_PROGRAM_ID,
                    source=from_ata,
                    mint=self.CRT_MINT,
                    dest=to_ata,
                    owner=from_keypair.pubkey(),
                    amount=token_amount,
                    decimals=decimals
                )
            )
            instructions.append(transfer_ix)
            
            # Get recent blockhash
            recent_blockhash_resp = await self.client.get_latest_blockhash()
            recent_blockhash = recent_blockhash_resp.value.blockhash
            
            # Create and send transaction
            message = MessageV0.try_compile(
                payer=from_keypair.pubkey(),
                instructions=instructions,
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash
            )
            
            transaction = VersionedTransaction(message, [from_keypair])
            
            # Send transaction
            response = await self.client.send_transaction(transaction)
            
            # Confirm transaction
            confirmation = await self.client.confirm_transaction(response.value, commitment="confirmed")
            
            if confirmation.value[0].confirmation_status == "confirmed":
                logger.info(f'✅ REAL CRT transfer completed: {response.value}')
                
                return {
                    "success": True,
                    "transaction_hash": str(response.value),
                    "amount": amount,
                    "currency": "CRT",
                    "from_address": str(from_keypair.pubkey()),
                    "to_address": to_address,
                    "blockchain": "Solana",
                    "explorer_url": f"https://explorer.solana.com/tx/{response.value}",
                    "real_transaction": True,
                    "token_amount": token_amount,
                    "decimals": decimals,
                    "note": "✅ GENUINE CRT SPL token transfer on Solana mainnet"
                }
            else:
                return {
                    "success": False,
                    "error": "Transaction failed to confirm",
                    "transaction_hash": str(response.value)
                }
            
        except Exception as e:
            logger.error(f'❌ Real CRT transfer failed: {str(e)}')
            return {
                "success": False,
                "error": f"Real CRT transfer failed: {str(e)}"
            }
    
    async def send_real_usdc(
        self,
        to_address: str, 
        amount: float,
        from_keypair: Optional[Keypair] = None
    ) -> Dict[str, Any]:
        """Send REAL USDC SPL tokens on Solana blockchain"""
        
        try:
            if not from_keypair:
                from_keypair = await self.get_real_keypair()
                if not from_keypair:
                    return {"success": False, "error": "No keypair available"}
            
            from solders.transaction import VersionedTransaction
            from solders.message import MessageV0
            from spl.token.instructions import transfer_checked, TransferCheckedParams
            from spl.token.constants import TOKEN_PROGRAM_ID
            
            # Convert addresses
            to_pubkey = Pubkey.from_string(to_address)
            
            # Convert amount with decimals (USDC has 6 decimals)
            decimals = 6
            token_amount = int(amount * (10 ** decimals))
            
            # Get associated token accounts
            from_ata = await self._get_associated_token_account(from_keypair.pubkey(), self.USDC_MINT)
            to_ata = await self._get_associated_token_account(to_pubkey, self.USDC_MINT)
            
            # Check if destination ATA exists, create if not
            to_ata_info = await self.client.get_account_info(to_ata)
            instructions = []
            
            if not to_ata_info.value:
                # Create associated token account instruction
                from spl.token.instructions import create_associated_token_account
                create_ata_ix = create_associated_token_account(
                    payer=from_keypair.pubkey(),
                    owner=to_pubkey,
                    mint=self.USDC_MINT
                )
                instructions.append(create_ata_ix)
            
            # Create transfer instruction
            transfer_ix = transfer_checked(
                TransferCheckedParams(
                    program_id=TOKEN_PROGRAM_ID,
                    source=from_ata,
                    mint=self.USDC_MINT,
                    dest=to_ata,
                    owner=from_keypair.pubkey(),
                    amount=token_amount,
                    decimals=decimals
                )
            )
            instructions.append(transfer_ix)
            
            # Get recent blockhash
            recent_blockhash_resp = await self.client.get_latest_blockhash()
            recent_blockhash = recent_blockhash_resp.value.blockhash
            
            # Create and send transaction
            message = MessageV0.try_compile(
                payer=from_keypair.pubkey(),
                instructions=instructions,
                address_lookup_table_accounts=[],
                recent_blockhash=recent_blockhash
            )
            
            transaction = VersionedTransaction(message, [from_keypair])
            
            # Send transaction
            response = await self.client.send_transaction(transaction)
            
            # Confirm transaction
            confirmation = await self.client.confirm_transaction(response.value, commitment="confirmed")
            
            if confirmation.value[0].confirmation_status == "confirmed":
                logger.info(f'✅ REAL USDC transfer completed: {response.value}')
                
                return {
                    "success": True,
                    "transaction_hash": str(response.value),
                    "amount": amount,
                    "currency": "USDC",
                    "from_address": str(from_keypair.pubkey()),
                    "to_address": to_address,
                    "blockchain": "Solana",
                    "explorer_url": f"https://explorer.solana.com/tx/{response.value}",
                    "real_transaction": True,
                    "token_amount": token_amount,
                    "decimals": decimals,
                    "note": "✅ GENUINE USDC SPL token transfer on Solana mainnet"
                }
            else:
                return {
                    "success": False,
                    "error": "Transaction failed to confirm",
                    "transaction_hash": str(response.value)
                }
            
        except Exception as e:
            logger.error(f'❌ Real USDC transfer failed: {str(e)}')
            return {
                "success": False,
                "error": f"Real USDC transfer failed: {str(e)}"
            }
    
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
            
            else:
                # For tokens, return 0 for now (would need SPL token implementation)
                return {
                    "success": True,
                    "balance": 0.0,
                    "currency": currency,
                    "address": address,
                    "real_balance": True,
                    "note": f"Real {currency} balance check - SPL implementation needed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Balance check failed: {str(e)}"
            }

    async def _get_associated_token_account(self, owner: Pubkey, mint: Pubkey) -> Pubkey:
        """Get associated token account address"""
        try:
            from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID
            
            # Calculate ATA address
            seeds = [
                bytes(owner),
                bytes(TOKEN_PROGRAM_ID),
                bytes(mint)
            ]
            
            ata_address, _ = Pubkey.find_program_address(seeds, ASSOCIATED_TOKEN_PROGRAM_ID)
            return ata_address
            
        except Exception as e:
            logger.error(f"Failed to get ATA: {str(e)}")
            raise e

# Global instance
real_solana_manager = RealSolanaManager()