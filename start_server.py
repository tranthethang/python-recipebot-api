#!/usr/bin/env python3
"""
RecipeBot API Server Startup Script
"""

import os
import sys
import uvicorn
from pathlib import Path

def check_environment():
    """Check if required environment variables are set."""
    required_vars = ["OPENROUTER_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Please set these variables or create a .env file")
        print("   Example: export OPENROUTER_API_KEY=your_key_here")
        return False
    
    return True

def main():
    """Start the RecipeBot API server."""
    print("🤖 RecipeBot API Server")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("app/main.py").exists():
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Load environment variables from .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        print("📄 Loading environment variables from .env file")
        from dotenv import load_dotenv
        load_dotenv()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Server configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting server at http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"❤️  Health Check: http://{host}:{port}/health")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()