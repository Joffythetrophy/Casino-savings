#!/bin/bash
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
