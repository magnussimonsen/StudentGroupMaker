#!/bin/bash
# Convenience wrapper to build the executable using PyInstaller and GroupMaker.spec
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v pyinstaller >/dev/null 2>&1; then
	echo "PyInstaller not found. Installing into current environment..."
	python3 -m pip install --upgrade pip
	python3 -m pip install pyinstaller
fi

echo "Building executable with PyInstaller (GroupMaker.spec)..."
pyinstaller GroupMaker.spec

if [ -f "dist/GroupMaker" ]; then
	echo "Build complete: dist/GroupMaker"
else
	echo "ERROR: Build did not produce dist/GroupMaker"
	exit 1
fi
