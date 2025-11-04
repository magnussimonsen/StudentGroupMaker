#!/usr/bin/env python3
"""
Simple script to create a Python virtual environment for Windows development.

This script:
1. Creates a .venv folder 
2. Installs required dependencies
3. That's it!

Usage: python create-python-venv-win.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    print("🐍 Creating Python virtual environment for Windows...")
    
    # Create virtual environment
    print("Creating .venv folder...")
    subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
    
    # Install dependencies
    print("Installing PySide6...")
    venv_python = Path(".venv") / "Scripts" / "python.exe"
    subprocess.run([str(venv_python), "-m", "pip", "install", "PySide6"], check=True)
    
    print("✅ Virtual environment created successfully!")
    print("📝 To use it:")
    print("   1. Activate: .venv\\Scripts\\activate")
    print("   2. Run app: python group-maker.py")
    print("   3. Deactivate: deactivate")

if __name__ == "__main__":
    main()