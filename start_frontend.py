
#!/usr/bin/env python3
"""
Start the React frontend for the casino
"""

import os
import subprocess
import sys
from pathlib import Path

def start_frontend():
    """Start the React frontend"""
    try:
        print("🎮 Starting Casino Frontend...")
        print("🌐 React-based casino interface")
        print("🎲 Games: Slots, Roulette, Dice, Plinko, Keno, Mines")
        print("")
        
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            print("❌ Frontend directory not found!")
            return
        
        os.chdir("frontend")
        
        # Check if node_modules exists, if not install dependencies
        if not Path("node_modules").exists():
            print("📦 Installing frontend dependencies...")
            subprocess.run(["npm", "install"], check=True)
        
        # Start the development server
        print("🚀 Starting React development server...")
        subprocess.run(["npm", "start"], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped by user")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        print("💡 Make sure Node.js and npm are installed")

if __name__ == "__main__":
    start_frontend()
