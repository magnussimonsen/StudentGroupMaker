#!/bin/bash
# Simple build script for Linux
# This installs dependencies and builds the executable

set -e  # Exit on error

echo "========================================"
echo "GroupMaker Build Script for Linux"
echo "========================================"

# Get to project root (parent of dev-scripts)
cd "$(dirname "$0")/.."

# Activate virtual environment if it exists, otherwise create it
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r dev-scripts/requirements.txt

echo "Building executable..."
python dev-scripts/build.py

echo ""
echo "========================================"
echo "Build complete!"
echo "========================================"
echo "Executable: dist/GroupMaker"
echo ""
echo "If the executable is not runnable, do:"
echo "  chmod +x dist/GroupMaker"
echo ""
echo "To run: ./dist/GroupMaker"
