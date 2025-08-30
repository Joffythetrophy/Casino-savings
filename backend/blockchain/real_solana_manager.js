/**
 * Real Solana Manager - Actual Blockchain Transactions
 * This replaces the mock/simulation system with real Solana operations
 */

const { Connection, PublicKey, Keypair, Transaction, SystemProgram, sendAndConfirmTransaction } = require('@solana/web3.js');
const { Token, TOKEN_PROGRAM_ID, getOrCreateAssociatedTokenAccount, transfer, createTransferInstruction } = require('@solana/spl-token');

class RealSolanaManager {
    constructor() {
        // Solana RPC connection
        this.connection = new Connection(
            process.env.SOLANA_RPC_URL || 'https://api.mainnet-beta.solana.com',
            'confirmed'
        );
        
        // Token mint addresses  
        this.tokens = {
            USDC: new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'),
            CRT: new PublicKey('9pjWtc6x88wrRMXTxkBcNB6YtcN7NNcyzDAfUMfRknty'),
            SOL: new PublicKey('So11111111111111111111111111111111111111112') // Wrapped SOL
        };
        
        console.log('🔗 Real Solana Manager initialized for mainnet operations');
    }
    
    async sendTransaction({ toAddress, amount, currency, fromPrivateKey }) {
        try {
            console.log(`🚀 Executing REAL ${currency} transaction: ${amount} to ${toAddress}`);
            
            if (!fromPrivateKey) {
                throw new Error('Hot wallet private key not configured');
            }
            
            // Create keypair from private key
            const fromKeypair = Keypair.fromSecretKey(
                Buffer.from(fromPrivateKey, 'base64')
            );
            
            const toPublicKey = new PublicKey(toAddress);
            
            if (currency === 'SOL') {
                return await this.sendSOL(fromKeypair, toPublicKey, amount);
            } else if (currency === 'USDC') {
                return await this.sendSPLToken(fromKeypair, toPublicKey, amount, this.tokens.USDC, 6);
            } else if (currency === 'CRT') {
                return await this.sendSPLToken(fromKeypair, toPublicKey, amount, this.tokens.CRT, 9);
            } else {
                throw new Error(`Unsupported currency: ${currency}`);
            }
            
        } catch (error) {
            console.error(`❌ Real ${currency} transaction failed:`, error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    async sendSOL(fromKeypair, toPublicKey, amount) {
        try {
            const lamports = amount * 1e9; // Convert SOL to lamports
            
            const transaction = new Transaction().add(
                SystemProgram.transfer({
                    fromPubkey: fromKeypair.publicKey,
                    toPubkey: toPublicKey,
                    lamports: lamports
                })
            );
            
            const signature = await sendAndConfirmTransaction(
                this.connection,
                transaction,
                [fromKeypair],
                { commitment: 'confirmed' }
            );
            
            console.log(`✅ SOL transaction confirmed: ${signature}`);
            
            return {
                success: true,
                transaction_hash: signature,
                amount: amount,
                currency: 'SOL',
                blockchain: 'Solana'
            };
            
        } catch (error) {
            throw new Error(`SOL transfer failed: ${error.message}`);
        }
    }
    
    async sendSPLToken(fromKeypair, toPublicKey, amount, mintAddress, decimals) {
        try {
            // Get or create associated token accounts
            const fromTokenAccount = await getOrCreateAssociatedTokenAccount(
                this.connection,
                fromKeypair,
                mintAddress,
                fromKeypair.publicKey
            );
            
            const toTokenAccount = await getOrCreateAssociatedTokenAccount(
                this.connection,
                fromKeypair, // Payer
                mintAddress,
                toPublicKey
            );
            
            // Calculate amount with decimals
            const transferAmount = amount * Math.pow(10, decimals);
            
            const transaction = new Transaction().add(
                createTransferInstruction(
                    fromTokenAccount.address,
                    toTokenAccount.address,
                    fromKeypair.publicKey,
                    transferAmount,
                    [],
                    TOKEN_PROGRAM_ID
                )
            );
            
            const signature = await sendAndConfirmTransaction(
                this.connection,
                transaction,
                [fromKeypair],
                { commitment: 'confirmed' }
            );
            
            console.log(`✅ SPL Token transaction confirmed: ${signature}`);
            
            return {
                success: true,
                transaction_hash: signature,
                amount: amount,
                mint_address: mintAddress.toString(),
                blockchain: 'Solana'
            };
            
        } catch (error) {
            throw new Error(`SPL Token transfer failed: ${error.message}`);
        }
    }
    
    async getBalance(address, currency = 'SOL') {
        try {
            const publicKey = new PublicKey(address);
            
            if (currency === 'SOL') {
                const balance = await this.connection.getBalance(publicKey);
                return {
                    success: true,
                    balance: balance / 1e9, // Convert lamports to SOL
                    currency: 'SOL'
                };
            } else {
                // SPL Token balance would require token account lookup
                return {
                    success: false,
                    error: "SPL token balance lookup not implemented"
                };
            }
            
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
}

module.exports = RealSolanaManager;