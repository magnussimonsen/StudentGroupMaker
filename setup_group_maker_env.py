#!/usr/bin/env python3
"""
Automated environment setup for an existing project that uses group-maker.py.

Usage examples (from any directory):

    # create venv inside the project and run group-maker.py
    python3 setup_group_maker_env.py --project-dir /home/magnus/dev/GroupMakerPull

    # force recreate venv and overwrite .env if .env.example exists
    python3 setup_group_maker_env.py -p /home/magnus/dev/GroupMakerPull --force

    # pass arguments to group-maker.py (prefix with --)
    python3 setup_group_maker_env.py -p /home/magnus/dev/GroupMakerPull -- --help

Notes:
- This script will create a virtual environment (default: .venv inside project),
    install requirements from requirements.txt or requirements-dev.txt, copy .env.example
    to .env (unless .env exists), optionally install pre-commit, then run group-maker.py.
- The default group-maker path used by this repo is:
        /home/magnus/dev/GroupMakerPull/group-maker.py

When forwarding arguments to group-maker.py, put a "--" before them so this script
does not try to parse them. Example: `...setup_group_maker_env.py -- --myflag value`.
"""
from pathlib import Path
import argparse
import subprocess
import sys
import os
import shutil

def run(cmd, env=None):
    print("RUN:", " ".join(map(str, cmd)))
    subprocess.run(list(map(str, cmd)), check=True, env=env)

def venv_paths(venv_dir: Path):
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe", venv_dir / "Scripts" / "pip.exe"
    return venv_dir / "bin" / "python", venv_dir / "bin" / "pip"

def create_venv(venv_dir: Path, python_exe: str, force: bool):
    if venv_dir.exists():
        if force:
            shutil.rmtree(venv_dir)
        else:
            print(f"Virtualenv exists at {venv_dir}; skipping creation.")
            return
    run([python_exe, "-m", "venv", str(venv_dir)])
    _, pip = venv_paths(venv_dir)
    run([str(pip), "install", "--upgrade", "pip", "setuptools", "wheel"])

def install_requirements(pip_path: Path, project_dir: Path):
    installed = False
    req = project_dir / "requirements.txt"
    dev_req = project_dir / "requirements-dev.txt"
    if req.exists():
        run([str(pip_path), "install", "-r", str(req)])
        installed = True
    if dev_req.exists():
        run([str(pip_path), "install", "-r", str(dev_req)])
        installed = True
    if not installed:
        # Fallback to editable install if project is installable
        if (project_dir / "setup.py").exists() or (project_dir / "pyproject.toml").exists():
            run([str(pip_path), "install", "-e", str(project_dir)])
        else:
            print("No requirements found; skipping dependency installation.")

def run_group_maker(py_path: Path, project_dir: Path, group_maker: str, extra_args):
    # Accept either an absolute path or a path relative to project_dir
    gm_path = Path(group_maker)
    if not gm_path.is_absolute():
        gm_path = (project_dir / group_maker)
    gm_path = gm_path.resolve()
    if not gm_path.exists():
        raise FileNotFoundError(f"{group_maker} not found (resolved to {gm_path})")
    cmd = [str(py_path), str(gm_path)] + (extra_args or [])
    run(cmd, env=os.environ)

def install_precommit(py_path: Path, pip_path: Path, project_dir: Path):
    if (project_dir / ".pre-commit-config.yaml").exists():
        run([str(pip_path), "install", "pre-commit"])
        run([str(py_path), "-m", "pre_commit", "install"], env=os.environ)

def copy_env_example(project_dir: Path, force: bool):
    example = project_dir / ".env.example"
    dest = project_dir / ".env"
    if example.exists():
        if dest.exists() and not force:
            print(".env exists; skipping .env.example copy.")
            return
        shutil.copy2(example, dest)
        print("Created .env from .env.example")

def main():
    p = argparse.ArgumentParser(description="Setup development environment and run group-maker.py")
    p.add_argument("--project-dir", "-p", type=Path, default=Path.cwd(), help="Project root directory")
    p.add_argument("--venv", "-v", type=Path, default=Path(".venv"), help="Virtualenv directory (relative to project-dir)")
    # Default follows the user's project path to avoid manual edits each run
    p.add_argument("--group-maker", "-g", type=str, default="/home/magnus/dev/GroupMakerPull/group-maker.py", help="Path to group-maker.py (absolute or relative to project-dir)")
    p.add_argument("--force", "-f", action="store_true", help="Overwrite existing venv and .env")
    p.add_argument("gm_args", nargs=argparse.REMAINDER, help="Arguments forwarded to group-maker.py (prefix with --)")
    args = p.parse_args()

    project_dir = args.project_dir.resolve()
    venv_dir = (project_dir / args.venv).resolve() if not args.venv.is_absolute() else args.venv.resolve()
    python_exe = sys.executable

    try:
        create_venv(venv_dir, python_exe, args.force)
        py_path, pip_path = venv_paths(venv_dir)
        install_requirements(Path(pip_path), project_dir)
        copy_env_example(project_dir, args.force)
        install_precommit(Path(py_path), Path(pip_path), project_dir)
        # forward gm args (strip leading "--" if argparse left it)
        extra = [a for a in args.gm_args if a != "--"]
        run_group_maker(Path(py_path), project_dir, args.group_maker, extra)
    except subprocess.CalledProcessError as e:
        print("Command failed:", e)
        sys.exit(1)
    except Exception as e:
        print("Error:", e)
        sys.exit(2)
    print("Setup complete.")

if __name__ == "__main__":
    main()