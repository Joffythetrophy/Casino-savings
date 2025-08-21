# Casino Savings - API Contracts & Implementation Plan

## API Endpoints

### Authentication & Wallet
- `POST /api/auth/connect` - Connect wallet (Phantom, Solflare, etc.)
- `POST /api/auth/disconnect` - Disconnect wallet
- `GET /api/auth/status` - Check connection status

### User Profile
- `GET /api/user/profile` - Get user profile and balances
- `PUT /api/user/profile` - Update user settings
- `GET /api/user/transactions` - Get transaction history

### Cryptocurrency Integration
- `GET /api/crypto/balances` - Get current balances for CRT, DOGE, TRX
- `POST /api/crypto/deposit` - Deposit crypto to gaming wallet
- `POST /api/crypto/withdraw` - Withdraw crypto from savings
- `GET /api/crypto/prices` - Get current market prices

### Gaming
- `POST /api/games/dice/play` - Play dice game
- `POST /api/games/blackjack/play` - Play blackjack
- `GET /api/games/history` - Get gaming history

### Savings
- `GET /api/savings/balance` - Get current savings balance
- `GET /api/savings/history` - Get savings transaction history
- `POST /api/savings/withdraw` - Withdraw from savings

### Trading (AI)
- `GET /api/trading/status` - Get AI trading status
- `POST /api/trading/enable` - Enable AI trading
- `GET /api/trading/performance` - Get trading performance

## Database Models

### User
```python
class User:
    id: ObjectId
    wallet_address: str
    wallet_type: str  # phantom, solflare, etc
    created_at: datetime
    settings: dict
    is_active: bool
```

### UserBalance
```python
class UserBalance:
    user_id: ObjectId
    currency: str  # CRT, DOGE, TRX, SOL
    gaming_balance: Decimal
    savings_balance: Decimal
    total_deposited: Decimal
    total_withdrawn: Decimal
    updated_at: datetime
```

### Transaction
```python
class Transaction:
    id: ObjectId
    user_id: ObjectId
    type: str  # deposit, withdrawal, game_loss, game_win, savings_transfer
    currency: str
    amount: Decimal
    from_balance: str  # gaming, savings
    to_balance: str
    tx_hash: str  # blockchain transaction hash
    status: str  # pending, completed, failed
    created_at: datetime
```

### GameSession
```python
class GameSession:
    id: ObjectId
    user_id: ObjectId
    game_type: str  # dice, blackjack
    currency: str
    bet_amount: Decimal
    result: str  # win, loss
    payout_amount: Decimal
    savings_contribution: Decimal
    created_at: datetime
```

## Blockchain Integration Requirements

### Solana (CRT Token)
- Use `@solana/web3.js` and `@solana/spl-token`
- CRT Token contract address: [To be provided]
- Handle SPL token transfers
- Real-time balance checking

### Dogecoin Integration
- Use Dogecoin API or RPC node
- Handle DOGE transfers
- Multi-sig wallet setup for security

### Tron (TRX) Integration  
- Use TronWeb library
- Handle TRX and TRC-20 token transfers
- Energy/bandwidth management

## Frontend Integration Changes

### Mock Data to Replace
1. **WalletConnectSection**: Replace mock wallet connection with real Web3 integration
2. **User Balances**: Replace hardcoded "0.00" values with real blockchain balances
3. **Transaction History**: Replace empty states with real transaction data
4. **Game Results**: Connect to real smart contracts for provably fair gaming

### Real Wallet Integration
- Phantom wallet adapter for Solana
- MetaMask for Ethereum/DOGE
- TronLink for Tron
- Real transaction signing and broadcasting

## Implementation Steps

1. **Install blockchain dependencies**
2. **Setup wallet adapters and blockchain clients**
3. **Create database models and API endpoints**
4. **Implement real wallet connection**
5. **Add cryptocurrency balance checking**
6. **Create provably fair gaming contracts**
7. **Implement auto-savings mechanism**
8. **Add AI trading functionality**
9. **Frontend integration with real backend**
10. **Testing and security audit**

## Security Considerations
- Never store private keys
- Use secure wallet adapters
- Implement proper transaction validation
- Rate limiting for API endpoints
- Multi-signature wallets for large amounts