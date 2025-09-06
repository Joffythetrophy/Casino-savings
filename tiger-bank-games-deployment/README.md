# 🐅 Tiger Bank Games - Development Fund System

**Live Demo:** Your Railway URL will appear here after deployment

## 💰 Portfolio Overview
- **Total Value:** $12.922M
- **Tokens:** USDC, DOGE, TRX, CRT, T52M, ETH, BTC, CDT
- **Development Fund:** $500K instant withdrawal capability

## 🚀 Features
- **$500K Development Fund Withdrawals** - Instant access to your external wallets
- **CDT Bridge Integration** - Direct & IOU bridging for all tokens
- **Admin Override Controls** - Complete owner control over all transactions
- **Multi-Token Portfolio** - Real-time balance tracking across 8 cryptocurrencies

## 🔧 Admin Access
- **Master Key:** `TIGER_BANK_ADMIN_2024`
- **Emergency Withdrawal:** `/api/admin/override-transaction`
- **Price Control:** `/api/admin/set-prices`
- **System Status:** `/api/admin/system-status`

## 🏦 External Wallets (Pre-configured)
- **ETH/USDC:** `0xaA94Fe949f6734e228c13C9Fc25D1eBCd994bffD`
- **BTC:** `bc1qv489kvy26f4y87murvs39xfq7jv06m4gkth578a5zcw6h6ud038sr99trc`

## 📊 Key API Endpoints
- `GET /api/user/user123/portfolio` - Portfolio overview
- `POST /api/withdraw/preset?preset_id=testing_fund_500k` - $500K withdrawal
- `GET /api/cdt/pricing` - CDT bridge pricing
- `POST /api/cdt/bridge` - Token to CDT bridging

## 🚂 Railway Deployment Instructions

1. **Upload to GitHub:**
   - Create new repository
   - Upload all these files
   - Commit and push

2. **Deploy to Railway:**
   - Go to https://railway.app
   - Login with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-deploy!

3. **Access Your System:**
   - Use the Railway URL provided
   - Your $12.9M portfolio will be live
   - All admin controls ready to use

---
**Deployed on Railway** | **Owner:** Tiger Bank Games System