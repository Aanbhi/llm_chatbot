#!/usr/bin/env python3
"""
AI ChatBot Pro - Launcher Script
Run this script to start the application with optimal settings
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'openai', 
        'pillow',
        'pypdf2',
        'chardet'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Please install requirements:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_api_key():
    """Check if OpenAI API key is set"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OpenAI API key not found!")
        print("🔑 Please set your API key:")
        print("   export OPENAI_API_KEY='your_api_key_here'")
        print("   Or create a .env file with OPENAI_API_KEY=your_key")
        return False
    
    if api_key.startswith('sk-'):
        print("✅ OpenAI API key found")
        return True
    else:
        print("⚠️  API key format seems incorrect (should start with 'sk-')")
        return False

def main():
    """Main launcher function"""
    print("🤖 AI ChatBot Pro - Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path('app.py').exists():
        print("❌ app.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    print("📋 Checking requirements...")
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check API key
    api_key_ok = check_api_key()
    
    print("\n🚀 Starting AI ChatBot Pro...")
    print("📱 The app will open at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the application\n")
    
    if not api_key_ok:
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("👋 Setup your API key and try again!")
            sys.exit(1)
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', 'app.py',
            '--server.port', '5000',
            '--server.address', '0.0.0.0',
            '--server.headless', 'true'
        ])
    except KeyboardInterrupt:
        print("\n👋 AI ChatBot Pro stopped. Thanks for using it!")
    except Exception as e:
        print(f"\n❌ Error running application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()