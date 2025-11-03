"""
Project configuration - paths and settings

Edit this file to match your local setup.
This works on both Windows and Linux/Mac.

NOTE: This config file is in dev-scripts/ folder, but paths
      point to the parent directory (project root).
"""
from pathlib import Path

# ============================================================================
# PROJECT PATHS
# ============================================================================

# Project root directory (parent of dev-scripts folder)
PROJECT_DIR = Path(__file__).parent.parent.resolve()

# Path to the main application script
GROUP_MAKER_PATH = PROJECT_DIR / "group-maker.py"

# Virtual environment directory name (in project root)
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
