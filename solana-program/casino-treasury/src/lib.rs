use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer, Mint};
use anchor_spl::associated_token::AssociatedToken;

declare_id!("CasinoTreasuryProgram11111111111111111111111");

#[program]
pub mod casino_treasury {
    use super::*;

    /// Initialize the casino treasury program
    pub fn initialize_treasury(
        ctx: Context<InitializeTreasury>,
        treasury_authority: Pubkey,
        withdrawal_limit_per_day: u64,
        min_treasury_balance: u64,
    ) -> Result<()> {
        let treasury = &mut ctx.accounts.treasury;
        
        treasury.authority = treasury_authority;
        treasury.total_deposits = 0;
        treasury.total_withdrawals = 0;
        treasury.withdrawal_limit_per_day = withdrawal_limit_per_day;
        treasury.min_treasury_balance = min_treasury_balance;
        treasury.is_active = true;
        treasury.created_at = Clock::get()?.unix_timestamp;
        treasury.last_update = Clock::get()?.unix_timestamp;
        
        msg!("🐅 Treasury initialized with authority: {}", treasury_authority);
        Ok(())
    }

    /// Deposit USDC to the treasury
    pub fn deposit_to_treasury(
        ctx: Context<DepositToTreasury>,
        amount: u64,
    ) -> Result<()> {
        let treasury = &mut ctx.accounts.treasury;
        
        require!(treasury.is_active, TreasuryError::TreasuryInactive);
        require!(amount > 0, TreasuryError::InvalidAmount);

        // Transfer USDC from user to treasury
        let cpi_accounts = Transfer {
            from: ctx.accounts.user_usdc_account.to_account_info(),
            to: ctx.accounts.treasury_usdc_account.to_account_info(),
            authority: ctx.accounts.user.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);
        
        token::transfer(cpi_ctx, amount)?;

        // Update treasury stats
        treasury.total_deposits = treasury.total_deposits.checked_add(amount)
            .ok_or(TreasuryError::MathOverflow)?;
        treasury.last_update = Clock::get()?.unix_timestamp;

        // Record deposit
        let deposit_record = &mut ctx.accounts.deposit_record;
        deposit_record.user = ctx.accounts.user.key();
        deposit_record.amount = amount;
        deposit_record.timestamp = Clock::get()?.unix_timestamp;
        deposit_record.transaction_type = TransactionType::Deposit;

        msg!("🐅 Deposited {} USDC to treasury by {}", amount, ctx.accounts.user.key());
        Ok(())
    }

    /// Authorize a withdrawal from the treasury (gaming winnings)
    pub fn authorize_withdrawal(
        ctx: Context<AuthorizeWithdrawal>,
        user: Pubkey,
        amount: u64,
        withdrawal_type: WithdrawalType,
    ) -> Result<()> {
        let treasury = &mut ctx.accounts.treasury;
        
        require!(treasury.is_active, TreasuryError::TreasuryInactive);
        require!(amount > 0, TreasuryError::InvalidAmount);
        
        // Only authorized casino program can authorize withdrawals
        require!(
            ctx.accounts.casino_authority.key() == treasury.authority,
            TreasuryError::UnauthorizedWithdrawal
        );

        let current_treasury_balance = ctx.accounts.treasury_usdc_account.amount;
        
        // Ensure treasury has sufficient funds
        require!(
            current_treasury_balance >= amount + treasury.min_treasury_balance,
            TreasuryError::InsufficientTreasuryFunds
        );

        // Create withdrawal authorization
        let withdrawal_auth = &mut ctx.accounts.withdrawal_authorization;
        withdrawal_auth.user = user;
        withdrawal_auth.amount = amount;
        withdrawal_auth.withdrawal_type = withdrawal_type;
        withdrawal_auth.authorized_by = ctx.accounts.casino_authority.key();
        withdrawal_auth.authorized_at = Clock::get()?.unix_timestamp;
        withdrawal_auth.expires_at = Clock::get()?.unix_timestamp + 3600; // 1 hour expiry
        withdrawal_auth.is_executed = false;

        msg!("🐅 Withdrawal authorized: {} USDC for user {}", amount, user);
        Ok(())
    }

    /// Execute an authorized withdrawal
    pub fn execute_withdrawal(
        ctx: Context<ExecuteWithdrawal>,
    ) -> Result<()> {
        let treasury = &mut ctx.accounts.treasury;
        let withdrawal_auth = &mut ctx.accounts.withdrawal_authorization;
        
        require!(treasury.is_active, TreasuryError::TreasuryInactive);
        require!(!withdrawal_auth.is_executed, TreasuryError::WithdrawalAlreadyExecuted);
        require!(
            withdrawal_auth.user == ctx.accounts.user.key(),
            TreasuryError::UnauthorizedUser
        );
        
        let current_time = Clock::get()?.unix_timestamp;
        require!(
            current_time <= withdrawal_auth.expires_at,
            TreasuryError::WithdrawalExpired
        );

        // Execute the transfer
        let treasury_key = treasury.key();
        let seeds = &[
            b"treasury".as_ref(),
            treasury_key.as_ref(),
            &[ctx.bumps.treasury],
        ];
        let signer = &[&seeds[..]];

        let cpi_accounts = Transfer {
            from: ctx.accounts.treasury_usdc_account.to_account_info(),
            to: ctx.accounts.user_usdc_account.to_account_info(),
            authority: treasury.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new_with_signer(cpi_program, cpi_accounts, signer);
        
        token::transfer(cpi_ctx, withdrawal_auth.amount)?;

        // Update records
        withdrawal_auth.is_executed = true;
        withdrawal_auth.executed_at = current_time;
        
        treasury.total_withdrawals = treasury.total_withdrawals.checked_add(withdrawal_auth.amount)
            .ok_or(TreasuryError::MathOverflow)?;
        treasury.last_update = current_time;

        // Record withdrawal
        let withdrawal_record = &mut ctx.accounts.withdrawal_record;
        withdrawal_record.user = ctx.accounts.user.key();
        withdrawal_record.amount = withdrawal_auth.amount;
        withdrawal_record.timestamp = current_time;
        withdrawal_record.transaction_type = TransactionType::Withdrawal;
        withdrawal_record.withdrawal_type = withdrawal_auth.withdrawal_type;

        msg!("🐅 Withdrawal executed: {} USDC to user {}", withdrawal_auth.amount, ctx.accounts.user.key());
        Ok(())
    }

    /// Emergency pause the treasury
    pub fn pause_treasury(ctx: Context<PauseTreasury>) -> Result<()> {
        let treasury = &mut ctx.accounts.treasury;
        
        require!(
            ctx.accounts.authority.key() == treasury.authority,
            TreasuryError::UnauthorizedAuthority
        );

        treasury.is_active = false;
        treasury.last_update = Clock::get()?.unix_timestamp;

        msg!("🐅 Treasury paused by authority");
        Ok(())
    }

    /// Resume treasury operations
    pub fn resume_treasury(ctx: Context<ResumeTreasury>) -> Result<()> {
        let treasury = &mut ctx.accounts.treasury;
        
        require!(
            ctx.accounts.authority.key() == treasury.authority,
            TreasuryError::UnauthorizedAuthority
        );

        treasury.is_active = true;
        treasury.last_update = Clock::get()?.unix_timestamp;

        msg!("🐅 Treasury resumed by authority");
        Ok(())
    }

    /// Update treasury settings
    pub fn update_treasury_settings(
        ctx: Context<UpdateTreasurySettings>,
        new_withdrawal_limit: Option<u64>,
        new_min_balance: Option<u64>,
    ) -> Result<()> {
        let treasury = &mut ctx.accounts.treasury;
        
        require!(
            ctx.accounts.authority.key() == treasury.authority,
            TreasuryError::UnauthorizedAuthority
        );

        if let Some(limit) = new_withdrawal_limit {
            treasury.withdrawal_limit_per_day = limit;
        }

        if let Some(min_balance) = new_min_balance {
            treasury.min_treasury_balance = min_balance;
        }

        treasury.last_update = Clock::get()?.unix_timestamp;

        msg!("🐅 Treasury settings updated");
        Ok(())
    }
}

#[derive(Accounts)]
pub struct InitializeTreasury<'info> {
    #[account(
        init,
        payer = payer,
        space = Treasury::LEN,
        seeds = [b"treasury"],
        bump
    )]
    pub treasury: Account<'info, Treasury>,
    
    #[account(
        init,
        payer = payer,
        associated_token::mint = usdc_mint,
        associated_token::authority = treasury,
    )]
    pub treasury_usdc_account: Account<'info, TokenAccount>,
    
    pub usdc_mint: Account<'info, Mint>,
    
    #[account(mut)]
    pub payer: Signer<'info>,
    
    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
}

#[derive(Accounts)]
pub struct DepositToTreasury<'info> {
    #[account(
        mut,
        seeds = [b"treasury"],
        bump
    )]
    pub treasury: Account<'info, Treasury>,
    
    #[account(mut)]
    pub treasury_usdc_account: Account<'info, TokenAccount>,
    
    #[account(mut)]
    pub user_usdc_account: Account<'info, TokenAccount>,
    
    #[account(
        init,
        payer = user,
        space = TransactionRecord::LEN,
    )]
    pub deposit_record: Account<'info, TransactionRecord>,
    
    #[account(mut)]
    pub user: Signer<'info>,
    
    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct AuthorizeWithdrawal<'info> {
    #[account(
        mut,
        seeds = [b"treasury"],
        bump
    )]
    pub treasury: Account<'info, Treasury>,
    
    #[account(mut)]
    pub treasury_usdc_account: Account<'info, TokenAccount>,
    
    #[account(
        init,
        payer = casino_authority,
        space = WithdrawalAuthorization::LEN,
    )]
    pub withdrawal_authorization: Account<'info, WithdrawalAuthorization>,
    
    #[account(mut)]
    pub casino_authority: Signer<'info>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ExecuteWithdrawal<'info> {
    #[account(
        mut,
        seeds = [b"treasury"],
        bump
    )]
    pub treasury: Account<'info, Treasury>,
    
    #[account(mut)]
    pub treasury_usdc_account: Account<'info, TokenAccount>,
    
    #[account(mut)]
    pub user_usdc_account: Account<'info, TokenAccount>,
    
    #[account(mut)]
    pub withdrawal_authorization: Account<'info, WithdrawalAuthorization>,
    
    #[account(
        init,
        payer = user,
        space = TransactionRecord::LEN,
    )]
    pub withdrawal_record: Account<'info, TransactionRecord>,
    
    #[account(mut)]
    pub user: Signer<'info>,
    
    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct PauseTreasury<'info> {
    #[account(mut)]
    pub treasury: Account<'info, Treasury>,
    
    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct ResumeTreasury<'info> {
    #[account(mut)]
    pub treasury: Account<'info, Treasury>,
    
    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct UpdateTreasurySettings<'info> {
    #[account(mut)]
    pub treasury: Account<'info, Treasury>,
    
    pub authority: Signer<'info>,
}

#[account]
pub struct Treasury {
    pub authority: Pubkey,
    pub total_deposits: u64,
    pub total_withdrawals: u64,
    pub withdrawal_limit_per_day: u64,
    pub min_treasury_balance: u64,
    pub is_active: bool,
    pub created_at: i64,
    pub last_update: i64,
}

impl Treasury {
    pub const LEN: usize = 32 + 8 + 8 + 8 + 8 + 1 + 8 + 8 + 8; // padding
}

#[account]
pub struct WithdrawalAuthorization {
    pub user: Pubkey,
    pub amount: u64,
    pub withdrawal_type: WithdrawalType,
    pub authorized_by: Pubkey,
    pub authorized_at: i64,
    pub expires_at: i64,
    pub executed_at: i64,
    pub is_executed: bool,
}

impl WithdrawalAuthorization {
    pub const LEN: usize = 32 + 8 + 1 + 32 + 8 + 8 + 8 + 1 + 8; // padding
}

#[account]
pub struct TransactionRecord {
    pub user: Pubkey,
    pub amount: u64,
    pub timestamp: i64,
    pub transaction_type: TransactionType,
    pub withdrawal_type: WithdrawalType,
}

impl TransactionRecord {
    pub const LEN: usize = 32 + 8 + 8 + 1 + 1 + 8; // padding
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq)]
pub enum WithdrawalType {
    Winnings,
    Savings,
    Liquidity,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq)]
pub enum TransactionType {
    Deposit,
    Withdrawal,
}

#[error_code]
pub enum TreasuryError {
    #[msg("Treasury is currently inactive")]
    TreasuryInactive,
    
    #[msg("Invalid amount specified")]
    InvalidAmount,
    
    #[msg("Insufficient treasury funds for withdrawal")]
    InsufficientTreasuryFunds,
    
    #[msg("Unauthorized withdrawal attempt")]
    UnauthorizedWithdrawal,
    
    #[msg("Unauthorized user for this withdrawal")]
    UnauthorizedUser,
    
    #[msg("Withdrawal has already been executed")]
    WithdrawalAlreadyExecuted,
    
    #[msg("Withdrawal authorization has expired")]
    WithdrawalExpired,
    
    #[msg("Unauthorized authority")]
    UnauthorizedAuthority,
    
    #[msg("Mathematical overflow occurred")]
    MathOverflow,
}