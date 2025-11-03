# Building GroupMaker for Linux

This document explains how to build a standalone Linux executable for GroupMaker.

## Quick Start

```bash
# Simple one-command build (from project root):
./dev-scripts/build.sh

# Or use the wrapper:
./build-wrapper.sh

# Or build manually:
.venv/bin/python dev-scripts/build.py
```

## What Gets Created

- **`dist/GroupMaker`** - Single executable file (~65 MB)
- No Python installation needed on target systems!
- All dependencies are bundled inside

## Detailed Build Process

### Option 1: Using the build.sh script (Recommended)

```bash
cd /home/magnus/dev/GroupMakerPull
./dev-scripts/build.sh
```

This script:
1. Creates/activates virtual environment
2. Installs all dependencies from dev-scripts/requirements.txt
3. Runs PyInstaller
4. Creates `dist/GroupMaker` executable

### Option 2: Manual build

```bash
# 1. Set up environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r dev-scripts/requirements.txt

# 3. Build executable
python dev-scripts/build.py
```

## Running the Executable

```bash
# Make it executable (if not already)
chmod +x dist/GroupMaker

# Run it
./dist/GroupMaker
```

## Distribution

To distribute your application:

1. **Copy the executable**:
   ```bash
   cp dist/GroupMaker ~/Desktop/
   ```

2. **Send to others**: Just send the single `GroupMaker` file
   - No Python needed on their system
   - No dependencies to install
   - Just run it!

3. **Optional - Create installer/package**:
   ```bash
   # Create a tar.gz archive
   cd dist
   tar -czf GroupMaker-linux-x64.tar.gz GroupMaker
   ```

## Troubleshooting

### Missing Libraries Warning

If you see warnings about missing `.so` files during build:
```
WARNING: Library not found: could not resolve 'libxcb-*.so'
```

Install these packages on your build system:
```bash
sudo apt install libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
                 libxcb-keysyms1 libxcb-render-util0
```

**Note**: These warnings usually don't prevent the app from running on most Linux systems.

### Build Fails

If the build fails:

1. **Clean and rebuild**:
   ```bash
   rm -rf build/ dist/ *.spec
   .venv/bin/python dev-scripts/build.py
   ```

2. **Update PyInstaller**:
   ```bash
   pip install --upgrade pyinstaller
   ```

3. **Check Python version**: Requires Python 3.8+

## Build Options

Edit `dev-scripts/build.py` to customize:

```python
cmd = [
    sys.executable,
    "-m", "PyInstaller",
    "--onefile",              # Single file (current)
    # "--onedir",             # Folder with files (alternative)
    "--name=GroupMaker",
    "--clean",
    "--noconfirm",
    str(GROUP_MAKER_PATH)
]
```

### `--onefile` vs `--onedir`

- **`--onefile`** (current): 
  - Single executable file
  - Slower startup (extracts to temp)
  - Easier to distribute
  
- **`--onedir`**: 
  - Folder with executable + libraries
  - Faster startup
  - Distribute entire folder

## File Sizes

- **Executable**: ~65 MB
- **Compressed (tar.gz)**: ~25 MB

The size includes:
- Python runtime
- PySide6 (Qt framework)
- All application code

## Cross-Platform Notes

This build process creates **Linux executables only**.

For other platforms:
- **Windows**: Run the same `build.py` on Windows
- **macOS**: Run the same `build.py` on macOS

PyInstaller creates platform-specific executables, so build on the target platform.

## Advanced: Reduce Size

To create a smaller executable:

1. **Use `--onedir` instead** (creates folder but faster/smaller)
2. **Exclude unused Qt modules** in `dev-scripts/build.py`:
   ```python
   "--exclude-module=PySide6.QtWebEngine",
   "--exclude-module=PySide6.Qt3D",
   ```
3. **Strip debug symbols**:
   ```bash
   strip dist/GroupMaker
   ```

## Continuous Integration

For automated builds, use the build script:

```bash
#!/bin/bash
# CI build script
python3 -m venv .venv
source .venv/bin/activate
pip install -r dev-scripts/requirements.txt
python dev-scripts/build.py
# Upload dist/GroupMaker to releases
```

## Summary

**To build**: `./dev-scripts/build.sh`  
**Result**: `dist/GroupMaker`  
**To run**: `./dist/GroupMaker`  
**To distribute**: Send the `GroupMaker` file  

**For development**: `./run-dev.sh` or `python3 dev-scripts/run-dev.py`

That's it! 🎉
