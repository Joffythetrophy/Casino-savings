"""
RAILWAY DEPLOYMENT SETUP
Step-by-step guide to deploy your blockchain casino on Railway
"""

import os
import json

def create_railway_config():
    """Create Railway deployment configuration"""
    
    print("🚂 RAILWAY DEPLOYMENT SETUP")
    print("=" * 60)
    print("🎯 Platform: Railway.app (Best for blockchain apps)")
    print("💰 Cost: $5/month for hobby plan")
    print("⚡ Deploy time: 5 minutes")
    print("=" * 60)
    
    # Create railway.json config
    railway_config = {
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "numReplicas": 1,
            "restartPolicyType": "ON_FAILURE"
        }
    }
    
    print("\n📁 CREATING DEPLOYMENT FILES:")
    print("-" * 40)
    
    # 1. Railway config
    with open('/app/railway.json', 'w') as f:
        json.dump(railway_config, f, indent=2)
    print("✅ Created railway.json")
    
    # 2. Environment variables template
    env_template = '''# Railway Environment Variables Template
# Copy these to your Railway project settings

# Database
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/casino_db
DB_NAME=casino_production

# NOWPayments (for real crypto withdrawals)
NOWPAYMENTS_API_KEY=your_nowpayments_key
NOWPAYMENTS_PUBLIC_KEY=your_public_key
NOWPAYMENTS_SANDBOX=false

# Security
JWT_SECRET=your_super_secret_jwt_key_for_production
CRYPTO_SECRET_KEY=your_encryption_key

# Frontend URL (Railway will provide this)
REACT_APP_BACKEND_URL=https://your-casino-production.railway.app

# Blockchain RPC endpoints
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
ETHEREUM_RPC_URL=https://mainnet.infura.io/v3/your_key

# Debug
DEBUG=false
NODE_ENV=production
'''
    
    with open('/app/railway_env_template.txt', 'w') as f:
        f.write(env_template)
    print("✅ Created environment variables template")
    
    # 3. Deployment script
    deploy_script = '''#!/bin/bash
# Railway Deployment Script

echo "🚂 Deploying Blockchain Casino to Railway..."

# Install Railway CLI (if not installed)
if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "Please login to Railway:"
railway login

# Create new project
echo "Creating Railway project..."
railway create

# Link to existing project (if already created)
# railway link [project-id]

# Set environment variables
echo "Setting up environment variables..."
echo "Go to Railway dashboard and add the variables from railway_env_template.txt"

# Deploy
echo "Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "🎰 Your blockchain casino is now live!"
'''
    
    with open('/app/deploy_to_railway.sh', 'w') as f:
        f.write(deploy_script)
    os.chmod('/app/deploy_to_railway.sh', 0o755)
    print("✅ Created deployment script")
    
    return railway_config

def create_dockerfile():
    """Create optimized Dockerfile for Railway"""
    
    # Backend Dockerfile
    backend_dockerfile = '''FROM python:3.11-slim

WORKDIR /app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Expose port
EXPOSE 8001

# Start backend
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
'''
    
    with open('/app/backend/Dockerfile', 'w') as f:
        f.write(backend_dockerfile)
    print("✅ Created backend Dockerfile")
    
    # Frontend Dockerfile  
    frontend_dockerfile = '''FROM node:18-alpine

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./
COPY frontend/yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy frontend code
COPY frontend/ .

# Build the app
RUN yarn build

# Install serve to run the built app
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Start frontend
CMD ["serve", "-s", "build", "-l", "3000"]
'''
    
    with open('/app/frontend/Dockerfile', 'w') as f:
        f.write(frontend_dockerfile)
    print("✅ Created frontend Dockerfile")

def print_deployment_steps():
    """Print step-by-step deployment instructions"""
    
    print(f"\n🎯 RAILWAY DEPLOYMENT STEPS:")
    print("=" * 60)
    
    steps = [
        {
            "step": 1,
            "title": "Create Railway Account",
            "action": "Go to railway.app and sign up with GitHub",
            "time": "2 minutes"
        },
        {
            "step": 2, 
            "title": "Push Code to GitHub",
            "action": "Push your casino code to a GitHub repository",
            "time": "1 minute"
        },
        {
            "step": 3,
            "title": "Create Railway Project", 
            "action": "Connect your GitHub repo to Railway",
            "time": "1 minute"
        },
        {
            "step": 4,
            "title": "Add Environment Variables",
            "action": "Copy variables from railway_env_template.txt to Railway dashboard",
            "time": "3 minutes"
        },
        {
            "step": 5,
            "title": "Deploy", 
            "action": "Railway automatically deploys your casino",
            "time": "5 minutes"
        },
        {
            "step": 6,
            "title": "Test Blockchain Features",
            "action": "Verify crypto transfers work on live site",
            "time": "10 minutes"
        }
    ]
    
    for step in steps:
        print(f"\n{step['step']}. 📋 {step['title']} ({step['time']})")
        print(f"   → {step['action']}")
    
    print(f"\n🚀 TOTAL TIME: ~15-20 minutes")
    print(f"💰 COST: $5/month")
    print(f"🎰 RESULT: Live blockchain casino with real crypto transfers!")

if __name__ == "__main__":
    config = create_railway_config()
    create_dockerfile()
    print_deployment_steps()
    
    print(f"\n🔥 READY TO DEPLOY!")
    print("Files created:")
    print("  ✅ railway.json")
    print("  ✅ railway_env_template.txt") 
    print("  ✅ deploy_to_railway.sh")
    print("  ✅ Dockerfiles")
    print(f"\nNext: Follow the deployment steps above!")