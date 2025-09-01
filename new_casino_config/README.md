# Casino Savings System

A full-stack casino application with real games, betting, and savings features.

## Quick Deploy to Render

1. **Create new GitHub repository**
2. **Copy these files to your new repo:**
   ```
   casino-savings/
   ├── backend/          (from real_casino_system/backend/)
   ├── frontend/         (from real_casino_system/frontend/) 
   ├── render.yaml       (deployment config)
   └── README.md         (this file)
   ```

3. **Connect to Render:**
   - Go to [render.com](https://render.com)
   - Connect your GitHub repo
   - Render will auto-detect the `render.yaml` and deploy both services

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

### Frontend  
```bash
cd frontend
npm install
npm start
```

## Environment Variables

Copy `.env.example` to `.env` and update with your values:
- `MONGO_URL`: Your MongoDB connection string
- `JWT_SECRET`: Random secret key for authentication
- `REACT_APP_BACKEND_URL`: Backend API URL

## Features

- 🎰 **Casino Games**: Blackjack, Roulette, Slots
- 💰 **Real Betting**: USDC/SOL/CRT token support  
- 🏦 **Savings System**: Automated loss allocation to DeFi pools
- 🔐 **Wallet Integration**: Phantom, Trust Wallet support
- 📱 **Responsive Design**: Works on mobile and desktop

## Support

For deployment issues, check the Render logs or create an issue in this repository.