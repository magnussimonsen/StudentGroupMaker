"""
Project configuration - paths and settings

Edit this file to match your local setup.
This works on both Windows and Linux/Mac.
"""
from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================

# Auto-detect project directory (where this config.py file lives)
PROJECT_DIR = Path(__file__).parent.resolve()

# Path to the main application script
GROUP_MAKER_PATH = PROJECT_DIR / "group-maker.py"

# Virtual environment directory name
VENV_DIR_NAME = ".venv"

# ============================================================================
# NOTES FOR DIFFERENT OPERATING SYSTEMS
# ============================================================================
# This configuration works on:
# - Windows (Path objects handle backslashes automatically)
# - Linux/Mac (Path objects use forward slashes)
# - WSL (Windows Subsystem for Linux)
#
# You don't need to change anything - Path() handles OS differences!
