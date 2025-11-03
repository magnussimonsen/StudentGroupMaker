#!/usr/bin/env python3
"""
Simple launcher for group-maker.py using the project's virtual environment.

This script:
1. Checks if .venv exists (if not, tells you to run setup_group_maker_env.py first)
2. Uses the venv's Python to run group-maker.py
3. Passes any command-line arguments through to group-maker.py

Usage:
    python3 run-dev.py
    python3 run-dev.py --some-flag --another-arg
"""
import sys
import subprocess
from pathlib import Path

# Import project configuration
try:
    from config import PROJECT_DIR, GROUP_MAKER_PATH, VENV_DIR_NAME
except ImportError:
    # Fallback if config.py is missing (assume we're in dev-scripts)
    print("Warning: config.py not found, using defaults...")
    PROJECT_DIR = Path(__file__).parent.parent.resolve()
    GROUP_MAKER_PATH = PROJECT_DIR / "group-maker.py"
    VENV_DIR_NAME = ".venv"

# Determine paths (works on Windows, Linux, and Mac)
VENV_DIR = PROJECT_DIR / VENV_DIR_NAME
def main():
    # Check if venv exists (cross-platform)
    if sys.platform == "win32":
        venv_python = VENV_DIR / "Scripts" / "python.exe"
    else:
        venv_python = VENV_DIR / "bin" / "python"
    
    if not venv_python.exists():
        print(f"ERROR: Virtual environment not found at {VENV_DIR}")
        print(f"Please run: python3 setup_group_maker_env.py")
        sys.exit(1)
    
    # Check if group-maker.py exists
    if not GROUP_MAKER_PATH.exists():
        print(f"ERROR: {GROUP_MAKER_PATH} not found")
        sys.exit(1)
    
    # Run group-maker.py with the venv's Python, forwarding all arguments
    cmd = [str(venv_python), str(GROUP_MAKER_PATH)] + sys.argv[1:]
    print(f"Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(130)

if __name__ == "__main__":
    main()
