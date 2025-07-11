#!/usr/bin/env python3
"""
ParkIT Platform Backend Server
Run this script to start the FastAPI server with automatic reload.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    """Run the FastAPI server."""
    print("🚀 Starting ParkIT Platform Backend...")
    print("📍 Backend directory:", backend_dir)
    
    # Check if .env file exists
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("⚠️  Warning: .env file not found. Using default configuration.")
        print("💡 Copy env.example to .env and configure your settings.")
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(backend_dir / "app")],
        log_level="info"
    )

if __name__ == "__main__":
    main() 