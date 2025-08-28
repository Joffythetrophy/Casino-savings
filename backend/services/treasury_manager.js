/**
 * Treasury Manager Service
 * Manages smart contract treasury operations and withdrawal backing
 */

const CasinoTreasuryProgram = require('../blockchain/casino_treasury_program');
const { PublicKey, Keypair } = require('@solana/web3.js');

class TreasuryManager {
    constructor() {
        this.treasuryProgram = new CasinoTreasuryProgram();
        this.isInitialized = false;
        
        // Treasury configuration
        this.config = {
            minTreasuryBalance: 50000, // Keep minimum 50,000 USDC in treasury
            maxWithdrawalPerTransaction: 10000, // Max 10,000 USDC per withdrawal
            maxDailyWithdrawals: 100000, // Max 100,000 USDC per day
            autoFundingThreshold: 100000, // Auto-fund when below this amount
            emergencyPauseThreshold: 25000 // Emergency pause when below this
        };
        
        this.dailyWithdrawalTracker = {
            date: new Date().toDateString(),
            totalWithdrawn: 0
        };
    }
    
    async initialize() {
        try {
            console.log('🐅 Initializing Treasury Manager...');
            
            // Initialize the treasury program if not already done
            const initResult = await this.treasuryProgram.initializeTreasury(
                this.treasuryProgram.treasuryKeypair.publicKey,
                this.config.maxDailyWithdrawals,
                this.config.minTreasuryBalance
            );
            
            if (initResult.success) {
                this.isInitialized = true;
                console.log('🐅 Treasury Manager initialized successfully');
                
                // Check initial treasury balance
                await this.checkTreasuryHealth();
                
                return { success: true, treasury: initResult };
            } else {
                console.error('❌ Treasury initialization failed:', initResult.error);
                return { success: false, error: initResult.error };
            }
            
        } catch (error) {
            console.error('❌ Treasury Manager initialization error:', error);
            return { success: false, error: error.message };
        }
    }
    
    async fundTreasury(amount) {
        try {
            console.log(`🐅 Funding treasury with ${amount} USDC...`);
            
            // In production, this would use a designated funding account
            const fundingKeypair = this.treasuryProgram.treasuryKeypair; // Simplified for demo
            
            const result = await this.treasuryProgram.fundTreasury(amount, fundingKeypair);
            
            if (result.success) {
                console.log(`🐅 Treasury funded successfully: ${amount} USDC`);
                
                // Log funding event
                await this.logTreasuryEvent('funding', {
                    amount,
                    signature: result.signature,
                    newBalance: result.treasuryBalance
                });
            }
            
            return result;
            
        } catch (error) {
            console.error('❌ Treasury funding error:', error);
            return { success: false, error: error.message };
        }
    }
    
    async processWithdrawal(userWallet, amount, withdrawalType = 'Winnings') {
        try {
            console.log(`🐅 Processing withdrawal: ${amount} USDC for ${userWallet}`);
            
            // Reset daily tracker if new day
            this.resetDailyTrackerIfNeeded();
            
            // Validate withdrawal
            const validation = await this.validateWithdrawal(userWallet, amount, withdrawalType);
            if (!validation.valid) {
                return {
                    success: false,
                    error: validation.reason,
                    code: 'VALIDATION_FAILED'
                };
            }
            
            // Step 1: Authorize withdrawal through smart contract
            const userPublicKey = new PublicKey(userWallet);
            const authResult = await this.treasuryProgram.authorizeWithdrawal(
                userPublicKey,
                amount,
                withdrawalType
            );
            
            if (!authResult.success) {
                return {
                    success: false,
                    error: 'Failed to authorize withdrawal',
                    details: authResult.error,
                    code: 'AUTHORIZATION_FAILED'
                };
            }
            
            // Step 2: Execute withdrawal (in production, user would sign this)
            // For demo, we'll simulate user execution
            const userKeypair = Keypair.generate(); // In production, user provides signature
            const executeResult = await this.treasuryProgram.executeWithdrawal(
                userKeypair,
                authResult.authorizationAccount
            );
            
            if (executeResult.success) {
                // Update daily withdrawal tracking
                this.dailyWithdrawalTracker.totalWithdrawn += amount;
                
                // Log withdrawal event
                await this.logTreasuryEvent('withdrawal', {
                    userWallet,
                    amount,
                    withdrawalType,
                    authorizationSignature: authResult.signature,
                    executionSignature: executeResult.signature,
                    explorerUrl: executeResult.explorerUrl
                });
                
                // Check if treasury needs refunding
                await this.checkTreasuryHealth();
                
                return {
                    success: true,
                    withdrawal: {
                        amount,
                        userWallet,
                        withdrawalType,
                        authorizationSignature: authResult.signature,
                        executionSignature: executeResult.signature,
                        explorerUrl: executeResult.explorerUrl,
                        timestamp: new Date().toISOString()
                    }
                };
            } else {
                return {
                    success: false,
                    error: 'Failed to execute withdrawal',
                    details: executeResult.error,
                    code: 'EXECUTION_FAILED'
                };
            }
            
        } catch (error) {
            console.error('❌ Withdrawal processing error:', error);
            return {
                success: false,
                error: error.message,
                code: 'PROCESSING_ERROR'
            };
        }
    }
    
    async validateWithdrawal(userWallet, amount, withdrawalType) {
        try {
            // Basic validations
            if (amount <= 0) {
                return { valid: false, reason: 'Invalid withdrawal amount' };
            }
            
            if (amount > this.config.maxWithdrawalPerTransaction) {
                return {
                    valid: false,
                    reason: `Withdrawal exceeds maximum limit: ${this.config.maxWithdrawalPerTransaction} USDC`
                };
            }
            
            // Check daily withdrawal limits
            this.resetDailyTrackerIfNeeded();
            const remainingDailyLimit = this.config.maxDailyWithdrawals - this.dailyWithdrawalTracker.totalWithdrawn;
            
            if (amount > remainingDailyLimit) {
                return {
                    valid: false,
                    reason: `Withdrawal exceeds daily limit. Remaining: ${remainingDailyLimit} USDC`
                };
            }
            
            // Validate through smart contract
            const contractValidation = await this.treasuryProgram.validateWithdrawal(
                new PublicKey(userWallet),
                amount
            );
            
            return contractValidation;
            
        } catch (error) {
            return {
                valid: false,
                reason: `Validation error: ${error.message}`
            };
        }
    }
    
    async checkTreasuryHealth() {
        try {
            const balance = await this.treasuryProgram.getTreasuryBalance();
            const stats = await this.treasuryProgram.getTreasuryStats();
            
            if (!balance.success || !stats.success) {
                console.error('❌ Failed to check treasury health');
                return { healthy: false, error: 'Unable to fetch treasury status' };
            }
            
            const currentBalance = balance.balance;
            
            console.log(`🐅 Treasury Health Check - Balance: ${currentBalance} USDC`);
            
            // Emergency pause if balance too low
            if (currentBalance < this.config.emergencyPauseThreshold) {
                console.log('🚨 EMERGENCY: Treasury balance critically low, pausing operations');
                await this.treasuryProgram.pauseTreasury();
                
                return {
                    healthy: false,
                    status: 'EMERGENCY_PAUSED',
                    currentBalance,
                    threshold: this.config.emergencyPauseThreshold
                };
            }
            
            // Auto-funding trigger
            if (currentBalance < this.config.autoFundingThreshold) {
                console.log('⚠️ Treasury balance low, triggering auto-funding');
                
                const fundingAmount = this.config.autoFundingThreshold * 2; // Fund to 2x threshold
                await this.requestTreasuryFunding(fundingAmount);
                
                return {
                    healthy: true,
                    status: 'AUTO_FUNDING_TRIGGERED',
                    currentBalance,
                    fundingRequested: fundingAmount
                };
            }
            
            return {
                healthy: true,
                status: 'HEALTHY',
                currentBalance,
                stats: stats.stats
            };
            
        } catch (error) {
            console.error('❌ Treasury health check error:', error);
            return { healthy: false, error: error.message };
        }
    }
    
    async requestTreasuryFunding(amount) {
        try {
            console.log(`🐅 Requesting treasury funding: ${amount} USDC`);
            
            // In production, this would:
            // 1. Send alerts to treasury managers
            // 2. Trigger automated funding from reserves
            // 3. Create funding requests in admin dashboard
            
            // For now, simulate auto-funding
            const fundingResult = await this.fundTreasury(amount);
            
            if (fundingResult.success) {
                console.log(`🐅 Auto-funding successful: ${amount} USDC`);
                return { success: true, amount, signature: fundingResult.signature };
            } else {
                console.error('❌ Auto-funding failed:', fundingResult.error);
                return { success: false, error: fundingResult.error };
            }
            
        } catch (error) {
            console.error('❌ Treasury funding request error:', error);
            return { success: false, error: error.message };
        }
    }
    
    async getTreasuryStatus() {
        try {
            const balance = await this.treasuryProgram.getTreasuryBalance();
            const stats = await this.treasuryProgram.getTreasuryStats();
            const health = await this.checkTreasuryHealth();
            
            return {
                success: true,
                status: {
                    balance: balance.success ? balance.balance : 0,
                    stats: stats.success ? stats.stats : null,
                    health: health,
                    dailyWithdrawals: this.dailyWithdrawalTracker,
                    config: this.config,
                    isInitialized: this.isInitialized
                }
            };
            
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    resetDailyTrackerIfNeeded() {
        const today = new Date().toDateString();
        if (this.dailyWithdrawalTracker.date !== today) {
            this.dailyWithdrawalTracker = {
                date: today,
                totalWithdrawn: 0
            };
        }
    }
    
    async logTreasuryEvent(eventType, data) {
        try {
            const logEntry = {
                timestamp: new Date().toISOString(),
                eventType,
                data,
                treasuryPDA: this.treasuryProgram.treasuryPDA?.toString()
            };
            
            console.log('🐅 Treasury Event:', JSON.stringify(logEntry, null, 2));
            
            // In production, store in database or monitoring system
            
        } catch (error) {
            console.error('❌ Failed to log treasury event:', error);
        }
    }
    
    // Emergency controls
    async emergencyPause() {
        try {
            console.log('🚨 EMERGENCY PAUSE initiated');
            const result = await this.treasuryProgram.pauseTreasury();
            
            if (result.success) {
                await this.logTreasuryEvent('emergency_pause', {
                    signature: result.signature,
                    initiatedBy: 'system'
                });
            }
            
            return result;
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    async emergencyResume() {
        try {
            console.log('🐅 EMERGENCY RESUME initiated');
            const result = await this.treasuryProgram.resumeTreasury();
            
            if (result.success) {
                await this.logTreasuryEvent('emergency_resume', {
                    signature: result.signature,
                    initiatedBy: 'admin'
                });
            }
            
            return result;
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
}

// Global treasury manager instance
const treasuryManager = new TreasuryManager();

module.exports = {
    TreasuryManager,
    treasuryManager
};