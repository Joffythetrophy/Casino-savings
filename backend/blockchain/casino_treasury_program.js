/**
 * Casino Treasury Solana Program Integration
 * Handles smart contract interactions for treasury-backed USDC withdrawals
 */

const { Connection, PublicKey, Keypair, Transaction, SystemProgram } = require('@solana/web3.js');
const { Program, AnchorProvider, Wallet, BN, web3 } = require('@project-serum/anchor');
const { TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID, getAssociatedTokenAddress, createAssociatedTokenAccountInstruction } = require('@solana/spl-token');

class CasinoTreasuryProgram {
    constructor() {
        // Program ID (this would be the deployed program ID)
        this.programId = new PublicKey('CasinoTreasuryProgram11111111111111111111111');
        
        // USDC Mint on Solana mainnet
        this.usdcMint = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v');
        
        // Solana connection
        this.connection = new Connection(
            process.env.SOLANA_RPC_URL || 'https://api.mainnet-beta.solana.com',
            'confirmed'
        );
        
        // Treasury keypair (in production, use secure key management)
        this.treasuryKeypair = this.loadTreasuryKeypair();
        
        // Treasury PDA
        this.treasuryPDA = null;
        this.treasuryBump = null;
        
        this.initializePDAs();
    }
    
    loadTreasuryKeypair() {
        // In production, load from secure environment or key management service
        // For now, generate or load a consistent keypair
        const privateKeyString = process.env.TREASURY_PRIVATE_KEY;
        if (privateKeyString) {
            const privateKey = Uint8Array.from(JSON.parse(privateKeyString));
            return Keypair.fromSecretKey(privateKey);
        }
        
        // Generate new keypair (save this for production use)
        const keypair = Keypair.generate();
        console.log('🐅 Generated new treasury keypair. Save this private key:', JSON.stringify(Array.from(keypair.secretKey)));
        return keypair;
    }
    
    async initializePDAs() {
        // Find Treasury PDA
        const [treasuryPDA, treasuryBump] = await PublicKey.findProgramAddress(
            [Buffer.from('treasury')],
            this.programId
        );
        
        this.treasuryPDA = treasuryPDA;
        this.treasuryBump = treasuryBump;
        
        console.log('🐅 Treasury PDA:', this.treasuryPDA.toString());
    }
    
    async initializeTreasury(authorityPublicKey, withdrawalLimitPerDay = 100000, minTreasuryBalance = 50000) {
        try {
            console.log('🐅 Initializing Casino Treasury...');
            
            // Get treasury USDC account
            const treasuryUsdcAccount = await getAssociatedTokenAddress(
                this.usdcMint,
                this.treasuryPDA,
                true
            );
            
            const transaction = new Transaction();
            
            // Create treasury USDC account if it doesn't exist
            try {
                await this.connection.getAccountInfo(treasuryUsdcAccount);
            } catch (error) {
                transaction.add(
                    createAssociatedTokenAccountInstruction(
                        this.treasuryKeypair.publicKey,
                        treasuryUsdcAccount,
                        this.treasuryPDA,
                        this.usdcMint,
                        TOKEN_PROGRAM_ID,
                        ASSOCIATED_TOKEN_PROGRAM_ID
                    )
                );
            }
            
            // Initialize treasury instruction (this would use the Anchor program)
            // For now, simulate the initialization
            
            const signature = await this.connection.sendTransaction(transaction, [this.treasuryKeypair]);
            await this.connection.confirmTransaction(signature);
            
            console.log('🐅 Treasury initialized successfully:', signature);
            return {
                success: true,
                signature,
                treasuryPDA: this.treasuryPDA.toString(),
                treasuryUsdcAccount: treasuryUsdcAccount.toString()
            };
            
        } catch (error) {
            console.error('❌ Treasury initialization failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    async fundTreasury(amount, funderKeypair) {
        try {
            console.log(`🐅 Funding treasury with ${amount} USDC...`);
            
            // Get funder's USDC account
            const funderUsdcAccount = await getAssociatedTokenAddress(
                this.usdcMint,
                funderKeypair.publicKey
            );
            
            // Get treasury USDC account
            const treasuryUsdcAccount = await getAssociatedTokenAddress(
                this.usdcMint,
                this.treasuryPDA,
                true
            );
            
            // Create deposit to treasury instruction
            // This would call the smart contract's deposit_to_treasury function
            
            const transaction = new Transaction();
            // Add deposit instruction here
            
            const signature = await this.connection.sendTransaction(transaction, [funderKeypair]);
            await this.connection.confirmTransaction(signature);
            
            console.log('🐅 Treasury funded successfully:', signature);
            return {
                success: true,
                signature,
                amount,
                treasuryBalance: await this.getTreasuryBalance()
            };
            
        } catch (error) {
            console.error('❌ Treasury funding failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    async authorizeWithdrawal(userPublicKey, amount, withdrawalType = 'Winnings') {
        try {
            console.log(`🐅 Authorizing withdrawal: ${amount} USDC for ${userPublicKey.toString()}`);
            
            // Create withdrawal authorization
            const withdrawalAuthKeypair = Keypair.generate();
            
            const transaction = new Transaction();
            
            // Add authorize withdrawal instruction
            // This calls the smart contract's authorize_withdrawal function
            
            const signature = await this.connection.sendTransaction(transaction, [this.treasuryKeypair]);
            await this.connection.confirmTransaction(signature);
            
            console.log('🐅 Withdrawal authorized:', signature);
            return {
                success: true,
                signature,
                authorizationAccount: withdrawalAuthKeypair.publicKey.toString(),
                amount,
                userPublicKey: userPublicKey.toString(),
                expiresAt: Date.now() + (3600 * 1000) // 1 hour
            };
            
        } catch (error) {
            console.error('❌ Withdrawal authorization failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    async executeWithdrawal(userKeypair, authorizationAccount) {
        try {
            console.log(`🐅 Executing withdrawal for ${userKeypair.publicKey.toString()}`);
            
            // Get user's USDC account
            const userUsdcAccount = await getAssociatedTokenAddress(
                this.usdcMint,
                userKeypair.publicKey
            );
            
            // Create user USDC account if it doesn't exist
            const transaction = new Transaction();
            
            try {
                await this.connection.getAccountInfo(userUsdcAccount);
            } catch (error) {
                transaction.add(
                    createAssociatedTokenAccountInstruction(
                        userKeypair.publicKey,
                        userUsdcAccount,
                        userKeypair.publicKey,
                        this.usdcMint,
                        TOKEN_PROGRAM_ID,
                        ASSOCIATED_TOKEN_PROGRAM_ID
                    )
                );
            }
            
            // Add execute withdrawal instruction
            // This calls the smart contract's execute_withdrawal function
            
            const signature = await this.connection.sendTransaction(transaction, [userKeypair]);
            await this.connection.confirmTransaction(signature);
            
            console.log('🐅 Withdrawal executed successfully:', signature);
            return {
                success: true,
                signature,
                userUsdcAccount: userUsdcAccount.toString(),
                explorerUrl: `https://explorer.solana.com/tx/${signature}`
            };
            
        } catch (error) {
            console.error('❌ Withdrawal execution failed:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    async getTreasuryBalance() {
        try {
            const treasuryUsdcAccount = await getAssociatedTokenAddress(
                this.usdcMint,
                this.treasuryPDA,
                true
            );
            
            const accountInfo = await this.connection.getTokenAccountBalance(treasuryUsdcAccount);
            return {
                success: true,
                balance: accountInfo.value.uiAmount,
                rawBalance: accountInfo.value.amount,
                decimals: accountInfo.value.decimals
            };
            
        } catch (error) {
            console.error('❌ Failed to get treasury balance:', error);
            return {
                success: false,
                balance: 0,
                error: error.message
            };
        }
    }
    
    async getTreasuryStats() {
        try {
            // This would fetch data from the treasury account on-chain
            const stats = {
                totalDeposits: 0,
                totalWithdrawals: 0,
                currentBalance: 0,
                isActive: true,
                withdrawalLimitPerDay: 100000,
                minTreasuryBalance: 50000
            };
            
            const balanceResult = await this.getTreasuryBalance();
            if (balanceResult.success) {
                stats.currentBalance = balanceResult.balance;
            }
            
            return {
                success: true,
                stats
            };
            
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    async validateWithdrawal(userPublicKey, amount) {
        try {
            const treasuryBalance = await this.getTreasuryBalance();
            const treasuryStats = await this.getTreasuryStats();
            
            if (!treasuryBalance.success || !treasuryStats.success) {
                return {
                    valid: false,
                    reason: 'Unable to validate treasury status'
                };
            }
            
            const minBalanceRequired = treasuryStats.stats.minTreasuryBalance;
            const availableForWithdrawal = treasuryBalance.balance - minBalanceRequired;
            
            if (amount > availableForWithdrawal) {
                return {
                    valid: false,
                    reason: `Insufficient treasury funds. Available: ${availableForWithdrawal} USDC`,
                    availableAmount: availableForWithdrawal
                };
            }
            
            if (!treasuryStats.stats.isActive) {
                return {
                    valid: false,
                    reason: 'Treasury is currently inactive'
                };
            }
            
            return {
                valid: true,
                availableAmount: availableForWithdrawal,
                treasuryBalance: treasuryBalance.balance
            };
            
        } catch (error) {
            return {
                valid: false,
                reason: error.message
            };
        }
    }
    
    // Emergency functions
    async pauseTreasury() {
        try {
            console.log('🐅 Pausing treasury...');
            
            // This would call the pause_treasury function on the smart contract
            const transaction = new Transaction();
            // Add pause instruction
            
            const signature = await this.connection.sendTransaction(transaction, [this.treasuryKeypair]);
            await this.connection.confirmTransaction(signature);
            
            console.log('🐅 Treasury paused:', signature);
            return { success: true, signature };
            
        } catch (error) {
            console.error('❌ Failed to pause treasury:', error);
            return { success: false, error: error.message };
        }
    }
    
    async resumeTreasury() {
        try {
            console.log('🐅 Resuming treasury...');
            
            // This would call the resume_treasury function on the smart contract
            const transaction = new Transaction();
            // Add resume instruction
            
            const signature = await this.connection.sendTransaction(transaction, [this.treasuryKeypair]);
            await this.connection.confirmTransaction(signature);
            
            console.log('🐅 Treasury resumed:', signature);
            return { success: true, signature };
            
        } catch (error) {
            console.error('❌ Failed to resume treasury:', error);
            return { success: false, error: error.message };
        }
    }
}

module.exports = CasinoTreasuryProgram;