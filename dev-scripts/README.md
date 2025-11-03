# Development Scripts

This folder contains all development, build, and environment setup scripts for GroupMaker.

## Files

### Core Scripts

- **`run-dev.py`** - Launch the application using the virtual environment
  ```bash
  python3 dev-scripts/run-dev.py
  # Or from root: ./run-dev.sh
  ```

- **`setup_group_maker_env.py`** - Full environment setup (creates venv, installs deps, runs app)
  ```bash
  python3 dev-scripts/setup_group_maker_env.py
  ```

- **`build.py`** - Build standalone executable with PyInstaller
  ```bash
  .venv/bin/python dev-scripts/build.py
  ```

- **`build.sh`** - Bash wrapper for complete build process
  ```bash
  ./dev-scripts/build.sh
  # Or from root: ./build-wrapper.sh
  ```

### Configuration

- **`config.py`** - Project paths and settings (PROJECT_DIR, GROUP_MAKER_PATH, etc.)
- **`requirements.txt`** - Python dependencies (PySide6, PyInstaller)

## Quick Reference

### Development Workflow

```bash
# First time setup
python3 dev-scripts/setup_group_maker_env.py

# Daily development
./run-dev.sh
# or
python3 dev-scripts/run-dev.py
```

### Building Executables

```bash
# Build for distribution
./dev-scripts/build.sh
# Creates: dist/GroupMaker

# Or manually
.venv/bin/python dev-scripts/build.py
```

### Environment Management

```bash
# Force recreate environment
python3 dev-scripts/setup_group_maker_env.py --force

# Install/update dependencies
source .venv/bin/activate
pip install -r dev-scripts/requirements.txt
```

## Root Directory Wrappers

For convenience, wrapper scripts exist in the project root:

- `run-dev.sh` → calls `dev-scripts/run-dev.py`
- `build-wrapper.sh` → calls `dev-scripts/build.sh`

These let you run scripts without `cd`-ing into dev-scripts.

## Why This Structure?

Organizing dev scripts in a dedicated folder:
- ✅ Keeps project root clean
- ✅ Separates development tools from application code
- ✅ Makes it clear what's for development vs distribution
- ✅ Easier to exclude from builds/packaging
- ✅ All configuration in one place

## Customizing Paths

Edit `dev-scripts/config.py` to change:
- Project directory location
- Application script path
- Virtual environment name

The config automatically detects the project root (parent of dev-scripts).

## Cross-Platform Notes

All Python scripts work on Windows, Linux, and macOS.

Shell scripts (`.sh`) are for Linux/Mac. On Windows, run the Python scripts directly:
```cmd
python dev-scripts\run-dev.py
python dev-scripts\build.py
```
