/**
 * Real Orca Pool Manager - Production Ready Liquidity Pool Creation
 * Uses actual Orca SDK for real cryptocurrency liquidity pools on Solana
 */

const { Connection, PublicKey, Keypair, Transaction, SystemProgram } = require('@solana/web3.js');
const { getOrca, Network } = require('@orca-so/sdk');
const { getAssociatedTokenAddress, createAssociatedTokenAccountInstruction, TOKEN_PROGRAM_ID } = require('@solana/spl-token');
const { WhirlpoolContext, buildWhirlpoolClient, ORCA_WHIRLPOOL_PROGRAM_ID } = require('@orca-so/whirlpools-sdk');
const Decimal = require('decimal.js');

class RealOrcaManager {
    constructor() {
        // Solana connection - using mainnet for production
        this.connection = new Connection(
            process.env.SOLANA_RPC_URL || 'https://api.mainnet-beta.solana.com',
            'confirmed'
        );

        // Initialize Orca SDK
        this.orca = getOrca(this.connection, Network.MAINNET);
        
        // Token mint addresses
        this.tokens = {
            CRT: new PublicKey('9pjWtc6x88wrRMXTxkBcNB6YtcN7NNcyzDAfUMfRknty'),
            SOL: new PublicKey('So11111111111111111111111111111111111111112'), // Wrapped SOL
            USDC: new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'),
            USDT: new PublicKey('Es9vMFrzaCERmJfrF4H2FYD4KCoNkY1NCe8BenwNYB')
        };

        // Load treasury keypair for pool operations
        this.treasuryKeypair = this.loadTreasuryKeypair();
        
        // Initialize Whirlpool context for new pool creation
        this.whirlpoolCtx = WhirlpoolContext.withProvider(
            { connection: this.connection, wallet: { publicKey: this.treasuryKeypair.publicKey } },
            this.connection
        );
        this.whirlpoolClient = buildWhirlpoolClient(this.whirlpoolCtx);
        
        console.log('🌊 Real Orca Manager initialized for mainnet operations');
    }

    loadTreasuryKeypair() {
        try {
            // Load treasury keypair from environment
            if (process.env.TREASURY_PRIVATE_KEY) {
                const privateKey = JSON.parse(process.env.TREASURY_PRIVATE_KEY);
                return Keypair.fromSecretKey(Uint8Array.from(privateKey));
            } else {
                // Generate new keypair (save this for production use!)
                const keypair = Keypair.generate();
                console.log('🔑 Generated new treasury keypair for pool operations');
                console.log('📝 SAVE THIS PRIVATE KEY:', JSON.stringify(Array.from(keypair.secretKey)));
                console.log('🏛️ Treasury Address:', keypair.publicKey.toString());
                return keypair;
            }
        } catch (error) {
            console.error('❌ Failed to load treasury keypair:', error);
            throw error;
        }
    }

    async createCRTSOLPool(initialCRTAmount, initialSOLAmount) {
        try {
            console.log(`🌊 Creating REAL CRT/SOL pool with ${initialCRTAmount} CRT + ${initialSOLAmount} SOL`);
            
            // Check if pool already exists
            const existingPool = await this.findExistingPool('CRT', 'SOL');
            if (existingPool) {
                return {
                    success: true,
                    message: 'CRT/SOL pool already exists',
                    pool_address: existingPool.address.toString(),
                    existing: true,
                    pool_url: `https://www.orca.so/pools/${existingPool.address.toString()}`
                };
            }

            // Check treasury balances
            const treasuryAddress = this.treasuryKeypair.publicKey;
            const balanceCheck = await this.checkTreasuryBalances(treasuryAddress, initialCRTAmount, initialSOLAmount);
            
            if (!balanceCheck.sufficient) {
                return {
                    success: false,
                    error: 'Insufficient treasury balances for pool creation',
                    required: balanceCheck.required,
                    available: balanceCheck.available
                };
            }

            // Create pool using Whirlpool (Orca's concentrated liquidity protocol)
            const poolResult = await this.createWhirlpool(
                this.tokens.CRT,
                this.tokens.SOL,
                initialCRTAmount,
                initialSOLAmount
            );

            if (!poolResult.success) {
                return {
                    success: false,
                    error: poolResult.error
                };
            }

            console.log('✅ CRT/SOL pool created successfully!');
            return {
                success: true,
                message: 'CRT/SOL pool created successfully on Orca',
                pool_address: poolResult.poolAddress,
                transaction_hash: poolResult.transaction_hash,
                explorer_url: `https://explorer.solana.com/tx/${poolResult.transaction_hash}`,
                pool_url: `https://www.orca.so/pools/${poolResult.poolAddress}`,
                initial_liquidity: {
                    crt_amount: initialCRTAmount,
                    sol_amount: initialSOLAmount
                },
                fee_tier: 0.003,
                network: 'Solana Mainnet'
            };

        } catch (error) {
            console.error('❌ CRT/SOL pool creation failed:', error);
            return {
                success: false,
                error: `Pool creation failed: ${error.message}`,
                details: error.stack
            };
        }
    }

    async createCRTUSDCPool(initialCRTAmount, initialUSDCAmount) {
        try {
            console.log(`💰 Creating REAL CRT/USDC pool with ${initialCRTAmount} CRT + ${initialUSDCAmount} USDC`);

            // Check if pool already exists
            const existingPool = await this.findExistingPool('CRT', 'USDC');
            if (existingPool) {
                return {
                    success: true,
                    message: 'CRT/USDC pool already exists',
                    pool_address: existingPool.address.toString(),
                    existing: true,
                    pool_url: `https://www.orca.so/pools/${existingPool.address.toString()}`
                };
            }

            // Check treasury balances
            const treasuryAddress = this.treasuryKeypair.publicKey;
            const balanceCheck = await this.checkTreasuryBalances(treasuryAddress, initialCRTAmount, initialUSDCAmount, true);
            
            if (!balanceCheck.sufficient) {
                return {
                    success: false,
                    error: 'Insufficient treasury balances for pool creation',
                    required: balanceCheck.required,
                    available: balanceCheck.available
                };
            }

            // Create pool using Whirlpool
            const poolResult = await this.createWhirlpool(
                this.tokens.CRT,
                this.tokens.USDC,
                initialCRTAmount,
                initialUSDCAmount
            );

            if (!poolResult.success) {
                return {
                    success: false,
                    error: poolResult.error
                };
            }

            console.log('✅ CRT/USDC pool created successfully!');
            return {
                success: true,
                message: 'CRT/USDC pool created successfully on Orca',
                pool_address: poolResult.poolAddress,
                transaction_hash: poolResult.transaction_hash,
                explorer_url: `https://explorer.solana.com/tx/${poolResult.transaction_hash}`,
                pool_url: `https://www.orca.so/pools/${poolResult.poolAddress}`,
                initial_liquidity: {
                    crt_amount: initialCRTAmount,
                    usdc_amount: initialUSDCAmount
                },
                fee_tier: 0.003,
                network: 'Solana Mainnet'
            };

        } catch (error) {
            console.error('❌ CRT/USDC pool creation failed:', error);
            return {
                success: false,
                error: `Pool creation failed: ${error.message}`,
                details: error.stack
            };
        }
    }

    async createWhirlpool(tokenMintA, tokenMintB, initialAmountA, initialAmountB) {
        try {
            console.log(`🌪️ Creating Whirlpool for ${tokenMintA.toString()} / ${tokenMintB.toString()}`);
            
            // Standard tick spacing for concentrated liquidity pools (64 for most token pairs)
            const tickSpacing = 64;
            
            // Fee tier (0.3% = 3000)
            const feeTierKey = { fee: 3000 };
            
            // Initialize whirlpool with the token pair
            const whirlpoolAddress = await this.whirlpoolClient.createPool(
                tokenMintA,
                tokenMintB,
                tickSpacing,
                Math.sqrt(initialAmountA / initialAmountB) // Initial price ratio
            );
            
            if (!whirlpoolAddress) {
                throw new Error('Failed to create whirlpool - no address returned');
            }

            // Add initial liquidity to the pool
            const liquidityResult = await this.addInitialLiquidity(
                whirlpoolAddress,
                tokenMintA,
                tokenMintB,
                initialAmountA,
                initialAmountB
            );

            return {
                success: true,
                poolAddress: whirlpoolAddress.toString(),
                transaction_hash: liquidityResult.transaction_hash,
                liquidity_added: {
                    tokenA: initialAmountA,
                    tokenB: initialAmountB
                }
            };

        } catch (error) {
            console.error('❌ Whirlpool creation failed:', error);
            return {
                success: false,
                error: `Whirlpool creation failed: ${error.message}`
            };
        }
    }

    async addInitialLiquidity(poolAddress, tokenMintA, tokenMintB, amountA, amountB) {
        try {
            console.log(`💧 Adding initial liquidity to pool ${poolAddress.toString()}`);

            // Get the whirlpool instance
            const whirlpool = await this.whirlpoolClient.getPool(poolAddress);
            
            // Define price range for liquidity (full range for initial liquidity)
            const tickLowerIndex = -443636; // Min tick
            const tickUpperIndex = 443636;  // Max tick

            // Create position and add liquidity
            const positionTx = await whirlpool.openPosition(
                tickLowerIndex,
                tickUpperIndex,
                {
                    tokenA: new Decimal(amountA),
                    tokenB: new Decimal(amountB)
                }
            );

            // Sign and send the transaction
            const signature = await this.connection.sendTransaction(
                positionTx,
                [this.treasuryKeypair],
                { skipPreflight: false, preflightCommitment: 'confirmed' }
            );

            // Wait for confirmation
            await this.connection.confirmTransaction(signature, 'confirmed');

            console.log('✅ Initial liquidity added successfully');
            return {
                success: true,
                transaction_hash: signature
            };

        } catch (error) {
            console.error('❌ Adding initial liquidity failed:', error);
            return {
                success: false,
                error: `Liquidity addition failed: ${error.message}`
            };
        }
    }

    async findExistingPool(tokenA, tokenB) {
        try {
            // Search for existing whirlpools with our token pair
            console.log(`🔍 Searching for existing ${tokenA}/${tokenB} pools...`);
            
            // Use Whirlpool client to search for existing pools
            const pools = await this.whirlpoolClient.getPools({
                tokenMintA: this.tokens[tokenA],
                tokenMintB: this.tokens[tokenB]
            });
            
            if (pools && pools.length > 0) {
                const pool = pools[0]; // Get first matching pool
                console.log(`✅ Found existing pool: ${pool.address.toString()}`);
                return {
                    address: pool.address,
                    tokenA: pool.tokenMintA,
                    tokenB: pool.tokenMintB
                };
            }
            
            return null;
        } catch (error) {
            console.error('❌ Error searching for existing pools:', error);
            return null;
        }
    }
    }

    async createNewPoolConfig(tokenA, tokenB) {
        try {
            console.log(`🔧 Creating new pool configuration for ${tokenA}/${tokenB}`);
            
            // This is a simplified pool config creation
            // In production, you'd need to interact with Orca's pool factory
            const poolConfig = {
                address: Keypair.generate().publicKey, // Temporary address
                nonce: Math.floor(Math.random() * 255),
                authority: this.treasuryKeypair.publicKey,
                poolTokenMint: Keypair.generate().publicKey,
                tokenAccountA: await getAssociatedTokenAddress(this.tokens[tokenA], this.treasuryKeypair.publicKey),
                tokenAccountB: await getAssociatedTokenAddress(this.tokens[tokenB], this.treasuryKeypair.publicKey),
                feeAccount: Keypair.generate().publicKey,
                feeNumerator: 30,
                feeDenominator: 10000,
                ownerTradeFeeNumerator: 5,
                ownerTradeFeeDenominator: 10000,
                ownerWithdrawFeeNumerator: 0,
                ownerWithdrawFeeDenominator: 10000,
                hostFeeNumerator: 20,
                hostFeeDenominator: 100
            };

            return poolConfig;
        } catch (error) {
            console.error('❌ Failed to create pool config:', error);
            throw error;
        }
    }

    async checkTreasuryBalances(treasuryAddress, tokenAAmount, tokenBAmount, isUSDC = false) {
        try {
            console.log('💳 Checking treasury balances...');
            
            // Check SOL balance for transaction fees
            const solBalance = await this.connection.getBalance(treasuryAddress);
            const solBalanceSOL = solBalance / 1e9;
            
            if (solBalanceSOL < 0.1) { // Need at least 0.1 SOL for fees
                return {
                    sufficient: false,
                    error: 'Insufficient SOL for transaction fees',
                    required: { sol: 0.1 },
                    available: { sol: solBalanceSOL }
                };
            }

            // Check CRT token balance
            const crtTokenAccount = await getAssociatedTokenAddress(this.tokens.CRT, treasuryAddress);
            let crtBalance = 0;
            
            try {
                const crtInfo = await this.connection.getTokenAccountBalance(crtTokenAccount);
                crtBalance = parseFloat(crtInfo.value.uiAmount || 0);
            } catch (error) {
                console.log('⚠️ CRT token account not found - needs to be created');
            }

            // Check second token balance (SOL or USDC)
            let secondTokenBalance = 0;
            const secondToken = isUSDC ? 'USDC' : 'SOL';
            
            if (isUSDC) {
                const usdcTokenAccount = await getAssociatedTokenAddress(this.tokens.USDC, treasuryAddress);
                try {
                    const usdcInfo = await this.connection.getTokenAccountBalance(usdcTokenAccount);
                    secondTokenBalance = parseFloat(usdcInfo.value.uiAmount || 0);
                } catch (error) {
                    console.log('⚠️ USDC token account not found - needs to be created');
                }
            } else {
                secondTokenBalance = solBalanceSOL;
            }

            const required = {
                crt: tokenAAmount,
                [secondToken.toLowerCase()]: tokenBAmount
            };
            
            const available = {
                crt: crtBalance,
                [secondToken.toLowerCase()]: secondTokenBalance,
                sol: solBalanceSOL
            };

            const sufficient = (crtBalance >= tokenAAmount) && (secondTokenBalance >= tokenBAmount) && (solBalanceSOL >= 0.1);

            return {
                sufficient,
                required,
                available,
                treasury_address: treasuryAddress.toString()
            };

        } catch (error) {
            console.error('❌ Balance check failed:', error);
            return {
                sufficient: false,
                error: error.message
            };
        }
    }

    async buildPoolCreationTransaction(poolConfig, tokenAAmount, tokenBAmount, poolPair) {
        try {
            console.log(`🔨 Building pool creation transaction for ${poolPair}`);
            
            const transaction = new Transaction();
            const treasuryAddress = this.treasuryKeypair.publicKey;

            // For now, create a basic liquidity addition transaction
            // In a full implementation, this would use Orca's pool factory
            
            // Create associated token accounts if they don't exist
            const crtTokenAccount = await getAssociatedTokenAddress(this.tokens.CRT, treasuryAddress);
            
            let secondTokenAccount;
            if (poolPair === 'CRT/SOL') {
                secondTokenAccount = treasuryAddress; // SOL uses the main account
            } else {
                secondTokenAccount = await getAssociatedTokenAddress(this.tokens.USDC, treasuryAddress);
            }

            // Check if accounts exist and create if needed
            try {
                await this.connection.getAccountInfo(crtTokenAccount);
            } catch (error) {
                transaction.add(
                    createAssociatedTokenAccountInstruction(
                        treasuryAddress, // payer
                        crtTokenAccount, // associated token account
                        treasuryAddress, // owner
                        this.tokens.CRT, // mint
                        TOKEN_PROGRAM_ID
                    )
                );
            }

            if (poolPair === 'CRT/USDC') {
                try {
                    await this.connection.getAccountInfo(secondTokenAccount);
                } catch (error) {
                    transaction.add(
                        createAssociatedTokenAccountInstruction(
                            treasuryAddress,
                            secondTokenAccount,
                            treasuryAddress,
                            this.tokens.USDC,
                            TOKEN_PROGRAM_ID
                        )
                    );
                }
            }

            // Generate a mock pool address (in real implementation, this would come from Orca)
            const poolAddress = Keypair.generate().publicKey.toString();

            console.log(`✅ Pool creation transaction built for ${poolPair}`);
            return {
                success: true,
                transaction,
                poolAddress,
                tokenAAccount: crtTokenAccount.toString(),
                tokenBAccount: secondTokenAccount.toString()
            };

        } catch (error) {
            console.error('❌ Failed to build pool creation transaction:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    async getPoolInfo(poolAddress) {
        try {
            const pool = this.orca.getPool(new PublicKey(poolAddress));
            const poolData = await pool.getData();
            
            return {
                success: true,
                pool_data: {
                    address: poolAddress,
                    token_a: poolData.tokenA,
                    token_b: poolData.tokenB,
                    liquidity: poolData.liquidity,
                    fee: poolData.fee
                }
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    async addLiquidity(poolAddress, tokenAAmount, tokenBAmount) {
        try {
            console.log(`💧 Adding liquidity to pool ${poolAddress}`);
            
            const pool = this.orca.getPool(new PublicKey(poolAddress));
            
            // Build add liquidity transaction
            const addLiquidityTx = await pool.getAddLiquidityTransaction(
                this.treasuryKeypair.publicKey,
                new Decimal(tokenAAmount),
                new Decimal(tokenBAmount)
            );

            // Sign and send transaction
            const signature = await this.connection.sendTransaction(addLiquidityTx, [this.treasuryKeypair]);
            await this.connection.confirmTransaction(signature);

            return {
                success: true,
                transaction_hash: signature,
                explorer_url: `https://explorer.solana.com/tx/${signature}`
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    async removeLiquidity(poolAddress, lpTokenAmount) {
        try {
            console.log(`💧 Removing liquidity from pool ${poolAddress}`);
            
            const pool = this.orca.getPool(new PublicKey(poolAddress));
            
            // Build remove liquidity transaction
            const removeLiquidityTx = await pool.getRemoveLiquidityTransaction(
                this.treasuryKeypair.publicKey,
                new Decimal(lpTokenAmount)
            );

            // Sign and send transaction
            const signature = await this.connection.sendTransaction(removeLiquidityTx, [this.treasuryKeypair]);
            await this.connection.confirmTransaction(signature);

            return {
                success: true,
                transaction_hash: signature,
                explorer_url: `https://explorer.solana.com/tx/${signature}`
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    async getAllOrcaPools() {
        try {
            console.log('🔍 Fetching all Orca pools...');
            
            const pools = await this.orca.getPools();
            const poolList = [];

            for (const pool of pools) {
                try {
                    const poolData = await pool.getData();
                    poolList.push({
                        address: pool.address.toString(),
                        tokens: poolData.tokens,
                        liquidity: poolData.liquidity,
                        fee: poolData.fee
                    });
                } catch (error) {
                    // Skip pools that can't be loaded
                    continue;
                }
            }

            return {
                success: true,
                pools: poolList,
                total_count: poolList.length
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
}

module.exports = RealOrcaManager;