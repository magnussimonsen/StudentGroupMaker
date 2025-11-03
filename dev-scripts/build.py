#!/usr/bin/env python3
"""
Build script for GroupMaker - Creates a standalone executable for Linux

This script uses PyInstaller to package the application into a single
executable file that can run on Linux systems without Python installed.

Usage:
    # From within the virtual environment:
    python3 build.py
    
    # Or use the venv's Python directly:
    .venv/bin/python build.py

Output:
    - dist/GroupMaker (standalone executable)

Note: Make sure PyInstaller is installed in your venv first!
      Run: pip install pyinstaller
"""
import subprocess
import sys
from pathlib import Path

# Import project configuration
try:
    from config import PROJECT_DIR, GROUP_MAKER_PATH
except ImportError:
    # Fallback: assume we're in dev-scripts folder
    PROJECT_DIR = Path(__file__).parent.parent.resolve()
    GROUP_MAKER_PATH = PROJECT_DIR / "group-maker.py"

def main():
    print("=" * 70)
    print("Building GroupMaker for Linux")
    print("=" * 70)
    print(f"Python: {sys.executable}")
    print(f"Version: {sys.version}")
    
    # Check if PyInstaller is installed
    try:
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ PyInstaller {result.stdout.strip()} found")
        else:
            raise ImportError("PyInstaller not found")
    except Exception:
        print("\n✗ PyInstaller not found in current environment!")
        print("\nPlease install it first:")
        print("  pip install pyinstaller")
        print("\nOr run the full setup:")
        print("  python3 setup_group_maker_env.py --force")
        sys.exit(1)
    
    # Build directory
    build_dir = PROJECT_DIR / "build"
    dist_dir = PROJECT_DIR / "dist"
    
    print(f"\nSource file: {GROUP_MAKER_PATH}")
    print(f"Output directory: {dist_dir}")
    
    # PyInstaller command with hidden imports for modular structure
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile",              # Single executable file
        "--name=GroupMaker",      # Output name
        "--clean",                # Clean cache
        "--noconfirm",            # Overwrite without asking
        # Ensure all src modules are included
        "--hidden-import=src.main",
        "--hidden-import=src.core.grouping",
        "--hidden-import=src.core.quality",
        "--hidden-import=src.core.visualization",
        "--hidden-import=src.models.storage",
        "--hidden-import=src.models.class_data",
        "--hidden-import=src.ui.main_window",
        "--hidden-import=src.ui.widgets.class_panel",
        "--hidden-import=src.ui.widgets.controls_panel",
        "--hidden-import=src.ui.widgets.output_panel",
        "--hidden-import=src.ui.dialogs.about_dialog",
        "--hidden-import=src.constants.app_info",
        "--hidden-import=src.constants.license",
        "--hidden-import=src.utils.validators",
        # Matplotlib and dependencies
        "--hidden-import=matplotlib",
        "--hidden-import=matplotlib.pyplot",
        "--hidden-import=matplotlib.backends.backend_qt5agg",
        "--hidden-import=numpy",
        str(GROUP_MAKER_PATH)
    ]
    
    print("\n" + "=" * 70)
    print("Running PyInstaller...")
    print("Command:", " ".join(cmd))
    print("=" * 70 + "\n")
    
    try:
        subprocess.run(cmd, check=True, cwd=PROJECT_DIR)
        
        executable = dist_dir / "GroupMaker"
        
        # Make executable on Unix systems
        if sys.platform != "win32":
            import stat
            executable.chmod(executable.stat().st_mode | stat.S_IEXEC)
        
        print("\n" + "=" * 70)
        print("✅ BUILD SUCCESSFUL!")
        print("=" * 70)
        print(f"\nExecutable created: {executable}")
        print(f"Size: {executable.stat().st_size / 1024 / 1024:.1f} MB")
        
        print("\nTo run the application:")
        print(f"  {executable}")
        
        print("\nTo distribute:")
        print(f"  - Copy {executable} to target system")
        print("  - No Python installation needed on target!")
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 70)
        print("❌ BUILD FAILED!")
        print("=" * 70)
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
