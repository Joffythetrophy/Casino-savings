
# 🎰 CRT Casino System

A comprehensive cryptocurrency casino platform with real blockchain integration, supporting multiple currencies and advanced gaming features.

## 🌟 Features

### 🎮 Gaming Platform
- **Multi-Currency Support**: CRT, DOGE, TRX, USDC, SOL
- **6 Casino Games**: Slots, Roulette, Dice, Plinko, Keno, Mines
- **Real Blockchain Transactions**: All deposits and withdrawals use actual blockchain
- **Auto-Play System**: Advanced automation with stop-loss and profit targets

### 🔗 Blockchain Integration
- **Solana Integration**: CRT token and USDC management
- **Multi-Chain Support**: TRON, Dogecoin, Solana
- **Real Withdrawals**: Actual cryptocurrency transfers to external wallets
- **Orca Pool Integration**: Liquidity provision and DEX functionality

### 💰 Financial Features
- **Real-Time Conversion**: Between all supported currencies
- **Savings Vault**: Non-custodial savings with yield generation
- **Treasury Management**: Smart contract-backed withdrawal system
- **Pool Funding**: Automatic liquidity pool funding from game losses

### 🔐 Security & Auth
- **Username/Password Auth**: Traditional login system
- **Wallet Authentication**: Blockchain signature verification
- **Trust Wallet SWIFT**: Account abstraction support
- **Multi-Signature Treasury**: Enhanced security for large amounts

## 🚀 Quick Start

### Backend (API Server)
```bash
# Start the casino backend
python main.py
```

### Frontend (React App)
```bash
# Start the casino frontend
python start_frontend.py
```

## 🏗️ Architecture

### Backend Components
- **FastAPI Server**: High-performance async API
- **MongoDB Database**: User accounts and transaction history
- **Blockchain Managers**: Real blockchain integration
- **Treasury System**: Smart contract withdrawal backing
- **Authentication**: JWT + wallet signature verification

### Frontend Components
- **React Dashboard**: Modern gaming interface
- **Game Components**: Individual casino games
- **Wallet Manager**: Multi-currency balance management
- **Admin Panel**: Treasury and pool management

## 🎯 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/challenge` - Wallet challenge
- `POST /api/auth/verify` - Verify wallet signature

### Gaming
- `POST /api/games/bet` - Place casino bet
- `GET /api/games/history/{wallet}` - Game history

### Wallet Management
- `GET /api/wallet/{address}` - Get wallet info
- `POST /api/wallet/deposit` - Deposit funds
- `POST /api/wallet/withdraw` - Withdraw funds
- `POST /api/wallet/convert` - Convert currencies

### Blockchain
- `GET /api/wallet/balance/{currency}` - Real blockchain balance
- `GET /api/blockchain/balances` - All balances

### Orca Pools
- `POST /api/orca/add-liquidity` - Add liquidity to pools
- `GET /api/dex/pools` - Get pool information
- `POST /api/pools/fund-with-user-balance` - Fund pools from balance

## 🔧 Configuration

### Environment Variables (backend/.env)
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=casino_db
JWT_SECRET_KEY=casino_dapp_secret_2024
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_PRIVATE_KEY=your_solana_private_key
TRON_PRIVATE_KEY=your_tron_private_key
DOGE_PRIVATE_KEY=your_doge_private_key
```

### Frontend Environment (frontend/.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
REACT_APP_CASINO_NAME=CRT Casino
```

## 💎 Supported Currencies

| Currency | Network | Use Case |
|----------|---------|----------|
| CRT | Solana | Primary casino token |
| USDC | Solana | Stable currency for large bets |
| SOL | Solana | Transaction fees and liquidity |
| DOGE | Dogecoin | Community favorite |
| TRX | TRON | Fast, low-cost transactions |

## 🎲 Games Available

1. **Diamond Slots** - Classic slot machine with multipliers
2. **VIP Roulette** - European roulette with crypto betting
3. **Crypto Dice** - Provably fair dice rolling
4. **Million Plinko** - High-volatility Plinko with huge multipliers
5. **Luxury Keno** - Number selection game with jackpots
6. **Diamond Mines** - Minesweeper-style risk game

## 🏦 Treasury System

The casino uses a sophisticated treasury system:
- **Smart Contract Backing**: All withdrawals backed by on-chain treasury
- **Liquidity Management**: Automatic pool funding from game losses
- **Multi-Signature Security**: Enhanced protection for large amounts
- **Real-Time Monitoring**: Continuous balance and health monitoring

## 🌊 Orca Integration

- **Automatic Pool Funding**: 50% of game losses fund real Orca pools
- **Liquidity Provision**: Users can add liquidity from winnings
- **DEX Functionality**: Token swapping and price discovery
- **Real Blockchain Transactions**: All pool operations use actual Solana

## 🔒 Security Features

- **Real Blockchain Verification**: All transactions verified on-chain
- **Multi-Layer Authentication**: Username/password + wallet signatures
- **Treasury Protection**: Smart contract limits and monitoring
- **Audit Trail**: Complete transaction history and logging

## 📱 Frontend Features

- **Responsive Design**: Works on desktop and mobile
- **Real-Time Updates**: Live balance and game updates
- **Multi-Currency Display**: All supported currencies
- **Game Statistics**: Detailed win/loss tracking
- **Auto-Play**: Advanced automation features

## 🚀 Deployment

The system is designed for production deployment with:
- **Docker Support**: Containerized deployment
- **Environment Configuration**: Separate dev/prod configs
- **Database Migration**: Automated setup scripts
- **Health Monitoring**: Built-in health checks

## 🎯 Admin Features

- **Treasury Management**: Monitor and control treasury
- **User Management**: View and manage user accounts
- **Pool Administration**: Control liquidity pools
- **Transaction Monitoring**: Real-time transaction tracking
- **Emergency Controls**: Pause/resume functionality

## 💡 Getting Started as a User

1. **Register**: Create account with username/password
2. **Connect Wallet**: Link your crypto wallet
3. **Deposit**: Add cryptocurrency to your casino account
4. **Play Games**: Choose from 6 different casino games
5. **Withdraw**: Transfer winnings to external wallet

## 🔧 For Developers

The system is built with modern technologies:
- **Backend**: Python 3.8+, FastAPI, MongoDB
- **Frontend**: React 18, TailwindCSS, Lucide Icons
- **Blockchain**: Solana Web3.js, TRON API, Dogecoin RPC
- **Authentication**: JWT, bcrypt, wallet signatures

## 📈 Roadmap

- [ ] Mobile app development
- [ ] Additional casino games
- [ ] Cross-chain bridge integration
- [ ] Advanced analytics dashboard
- [ ] Social features and tournaments

---

**🎰 Ready to play? Start the casino and experience real crypto gaming!**
