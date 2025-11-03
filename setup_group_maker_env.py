#!/usr/bin/env python3
"""
Automated environment setup and launcher for group-maker.py

This script does everything needed to run the project:
1. Creates a Python virtual environment (.venv) if it doesn't exist
2. Installs all dependencies from requirements.txt
3. Runs group-maker.py with the correct Python interpreter

Usage examples:
    # Simple run (from project directory)
    python3 setup_group_maker_env.py
    
    # Run from any directory
    python3 setup_group_maker_env.py --project-dir /home/magnus/dev/GroupMakerPull
    
    # Force recreate environment (useful if dependencies are broken)
    python3 setup_group_maker_env.py --force
    
    # Pass arguments to group-maker.py (add -- before them)
    python3 setup_group_maker_env.py -- --help

TIP: For simpler daily use, just run: python3 run-dev.py
"""
from pathlib import Path
import argparse
import subprocess
import sys
import os
import shutil

# Import project configuration
try:
    from config import PROJECT_DIR, GROUP_MAKER_PATH, VENV_DIR_NAME
except ImportError:
    # Fallback if config.py is missing
    print("Warning: config.py not found, using defaults...")
    PROJECT_DIR = Path(__file__).parent.resolve()
    GROUP_MAKER_PATH = PROJECT_DIR / "group-maker.py"
    VENV_DIR_NAME = ".venv"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def run(cmd, env=None):
    """Execute a shell command and print it for visibility."""
    print("RUN:", " ".join(map(str, cmd)))
    subprocess.run(list(map(str, cmd)), check=True, env=env)

def venv_paths(venv_dir: Path):
    """Get the paths to Python and pip inside the virtual environment."""
    if os.name == "nt":  # Windows
        return venv_dir / "Scripts" / "python.exe", venv_dir / "Scripts" / "pip.exe"
    else:  # Linux/Mac
        return venv_dir / "bin" / "python", venv_dir / "bin" / "pip"

def create_venv(venv_dir: Path, python_exe: str, force: bool):
    """
    Create a Python virtual environment.
    
    Args:
        venv_dir: Where to create the venv
        python_exe: Path to Python interpreter to use
        force: If True, delete and recreate existing venv
    """
    # If venv already exists, either skip or delete it
    if venv_dir.exists():
        if force:
            print(f"Deleting existing venv at {venv_dir}...")
            shutil.rmtree(venv_dir)
        else:
            print(f"Virtualenv exists at {venv_dir}; skipping creation.")
            return
    
    # Create the virtual environment
    print(f"Creating virtual environment at {venv_dir}...")
    run([python_exe, "-m", "venv", str(venv_dir)])
    
    # Upgrade pip, setuptools, and wheel inside the venv
    _, pip = venv_paths(venv_dir)
    print("Upgrading pip, setuptools, and wheel...")
    run([str(pip), "install", "--upgrade", "pip", "setuptools", "wheel"])

def install_requirements(pip_path: Path, project_dir: Path):
    """
    Install Python dependencies from requirements files.
    
    Looks for requirements.txt and requirements-dev.txt in the project directory.
    """
    installed = False
    
    # Check for requirements.txt
    req = project_dir / "requirements.txt"
    if req.exists():
        print(f"Installing dependencies from {req}...")
        run([str(pip_path), "install", "-r", str(req)])
        installed = True
    
    # Check for requirements-dev.txt (optional development dependencies)
    dev_req = project_dir / "requirements-dev.txt"
    if dev_req.exists():
        print(f"Installing dev dependencies from {dev_req}...")
        run([str(pip_path), "install", "-r", str(dev_req)])
        installed = True
    
    # If no requirements files found, try editable install
    if not installed:
        if (project_dir / "setup.py").exists() or (project_dir / "pyproject.toml").exists():
            print("No requirements.txt found, installing project as editable...")
            run([str(pip_path), "install", "-e", str(project_dir)])
        else:
            print("No requirements found; skipping dependency installation.")

def run_group_maker(py_path: Path, project_dir: Path, group_maker: str, extra_args):
    """
    Run the group-maker.py script using the virtual environment's Python.
    
    Args:
        py_path: Path to Python in the venv
        project_dir: Project root directory
        group_maker: Path to group-maker.py (absolute or relative to project_dir)
        extra_args: Additional command-line arguments to pass to group-maker.py
    """
    # Figure out the full path to group-maker.py
    gm_path = Path(group_maker)
    if not gm_path.is_absolute():
        gm_path = (project_dir / group_maker)
    gm_path = gm_path.resolve()
    
    # Make sure it exists
    if not gm_path.exists():
        raise FileNotFoundError(f"{group_maker} not found (resolved to {gm_path})")
    
    # Run it with the venv's Python
    print(f"\nLaunching {gm_path}...")
    cmd = [str(py_path), str(gm_path)] + (extra_args or [])
    run(cmd, env=os.environ)


# ============================================================================
# OPTIONAL FEATURES (not needed for basic setup)
# ============================================================================

def install_precommit(py_path: Path, pip_path: Path, project_dir: Path):
    """Install pre-commit hooks if .pre-commit-config.yaml exists."""
    if (project_dir / ".pre-commit-config.yaml").exists():
        print("Installing pre-commit hooks...")
        run([str(pip_path), "install", "pre-commit"])
        run([str(py_path), "-m", "pre_commit", "install"], env=os.environ)

def copy_env_example(project_dir: Path, force: bool):
    """Copy .env.example to .env if it exists and .env doesn't."""
    example = project_dir / ".env.example"
    dest = project_dir / ".env"
    if example.exists():
        if dest.exists() and not force:
            print(".env exists; skipping .env.example copy.")
            return
        shutil.copy2(example, dest)
        print("Created .env from .env.example")

# ============================================================================
# MAIN SCRIPT
# ============================================================================



def main():
    # ========================================================================
    # Parse command-line arguments
    # ========================================================================
    p = argparse.ArgumentParser(
        description="Setup development environment and run group-maker.py",
        epilog="TIP: For daily use, just run 'python3 run-dev.py' instead!"
    )
    p.add_argument(
        "--project-dir", "-p", 
        type=Path, 
        default=PROJECT_DIR,  # Now uses config.py
        help="Project root directory (default: from config.py)"
    )
    p.add_argument(
        "--venv", "-v", 
        type=Path, 
        default=Path(VENV_DIR_NAME),  # Now uses config.py
        help=f"Virtualenv directory name (default: {VENV_DIR_NAME})"
    )
    p.add_argument(
        "--group-maker", "-g", 
        type=str, 
        default=str(GROUP_MAKER_PATH),  # Now uses config.py
        help="Path to group-maker.py (from config.py)"
    )
    p.add_argument(
        "--force", "-f", 
        action="store_true", 
        help="Recreate venv and overwrite .env"
    )
    p.add_argument(
        "gm_args", 
        nargs=argparse.REMAINDER, 
        help="Arguments to pass to group-maker.py (prefix with --)"
    )
    args = p.parse_args()

    # ========================================================================
    # Determine paths
    # ========================================================================
    project_dir = args.project_dir.resolve()
    venv_dir = (project_dir / args.venv).resolve() if not args.venv.is_absolute() else args.venv.resolve()
    python_exe = sys.executable

    print(f"\n{'='*70}")
    print(f"Project Directory: {project_dir}")
    print(f"Virtual Environment: {venv_dir}")
    print(f"{'='*70}\n")

    # ========================================================================
    # Main setup and execution
    # ========================================================================
    try:
        # Step 1: Create virtual environment
        create_venv(venv_dir, python_exe, args.force)
        
        # Step 2: Get paths to Python and pip in the venv
        py_path, pip_path = venv_paths(venv_dir)
        
        # Step 3: Install dependencies
        install_requirements(Path(pip_path), project_dir)
        
        # Step 4: Optional setup (env files, pre-commit)
        copy_env_example(project_dir, args.force)
        install_precommit(Path(py_path), Path(pip_path), project_dir)
        
        # Step 5: Run group-maker.py
        # Remove the "--" separator if argparse left it in
        extra = [a for a in args.gm_args if a != "--"]
        run_group_maker(Path(py_path), project_dir, args.group_maker, extra)
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Command failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(2)
    
    print("\n✅ Setup complete.")


if __name__ == "__main__":
    main()