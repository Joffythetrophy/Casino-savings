
#!/usr/bin/env python3
"""
CRT Casino System - Main Startup Script
Comprehensive crypto casino with real blockchain integration
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def install_dependencies():
    """Install required Python packages"""
    try:
        print("🔧 Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    return True

def setup_environment():
    """Setup environment variables"""
    backend_dir = Path("backend")
    env_file = backend_dir / ".env"
    
    if not env_file.exists():
        print("🔧 Creating environment file...")
        env_template = backend_dir / ".env.template"
        if env_template.exists():
            # Copy template to .env
            with open(env_template, 'r') as template:
                content = template.read()
            with open(env_file, 'w') as env:
                env.write(content)
        else:
            # Create basic .env file
            with open(env_file, 'w') as env:
                env.write("""
# Casino Backend Environment Variables
MONGO_URL=mongodb://localhost:27017
DB_NAME=casino_db
JWT_SECRET_KEY=casino_dapp_secret_2024
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_PRIVATE_KEY=your_solana_private_key_here
TRON_PRIVATE_KEY=your_tron_private_key_here
DOGE_PRIVATE_KEY=your_doge_private_key_here
""")
        print("✅ Environment file created!")

def run_backend():
    """Run the casino backend server"""
    try:
        print("🚀 Starting CRT Casino Backend...")
        print("🎰 Features: Multi-currency gaming, Real blockchain transactions, Orca pools")
        print("💎 Supported: CRT, DOGE, TRX, USDC, SOL")
        print("🔗 Real blockchain integration with withdrawal system")
        print("")
        
        os.chdir("backend")
        subprocess.run([sys.executable, "server.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Casino server stopped by user")
    except Exception as e:
        print(f"❌ Error running backend: {e}")

def main():
    """Main startup function"""
    print("🎰 CRT CASINO SYSTEM STARTUP")
    print("=" * 50)
    print("🏛️ Comprehensive Crypto Casino Platform")
    print("💰 Real blockchain transactions & gaming")
    print("🌊 Orca pool integration for liquidity")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Run backend
    run_backend()

if __name__ == "__main__":
    main()
