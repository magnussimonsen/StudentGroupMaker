"""
Storage paths and file operations.

This module handles all file system operations for the application.
"""
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

from ..constants import APP_NAME


# Storage directories
DATA_DIR = Path.home() / f".{APP_NAME}"
CLASSES_DIR = DATA_DIR / "classes"
SEATINGS_DIR = DATA_DIR / "seatings"
MARKS_DIR = DATA_DIR / "marks"

# Ensure directories exist
CLASSES_DIR.mkdir(parents=True, exist_ok=True)
SEATINGS_DIR.mkdir(parents=True, exist_ok=True)
MARKS_DIR.mkdir(parents=True, exist_ok=True)

# Characters that are not allowed in file names on Windows
INVALID_FILENAME_CHARACTERS = set('<>:"/\\|?*')


def _safe_name(name: str) -> str:
    """Remove characters that cannot be used in a file name."""
    return "".join(c for c in name if c not in INVALID_FILENAME_CHARACTERS).strip()


def same_class_file(first: str, second: str) -> bool:
    """Whether two class names would be stored in the same file.

    Invalid characters are dropped from file names and Windows ignores case,
    so for example "Math101", "math101" and "Math:101" all share one file.
    """
    return _safe_name(first).casefold() == _safe_name(second).casefold()


def write_json_atomically(path: Path, data: object) -> None:
    """Write JSON to a temporary file first, so a crash never leaves a half-written file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temporary_file:
        temporary_path = Path(temporary_file.name)
        try:
            json.dump(data, temporary_file, ensure_ascii=False, indent=2)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        except BaseException:
            temporary_file.close()
            temporary_path.unlink(missing_ok=True)
            raise
    try:
        os.replace(temporary_path, path)
    except OSError:
        temporary_path.unlink(missing_ok=True)
        raise


def backup_damaged_file(path: Path) -> Path:
    """Move an unreadable data file aside, so it is kept instead of overwritten."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(f"{path.stem}.damaged-{stamp}{path.suffix}")
    path.replace(backup)
    return backup


def class_path(name: str) -> Path:
    """
    Get the file path for a class data file.
    
    Args:
        name: Class name
        
    Returns:
        Path to the class JSON file
    """
    return CLASSES_DIR / f"{_safe_name(name)}.json"


def seating_path(name: str) -> Path:
    """Get the path to a class seating-layout file."""
    return SEATINGS_DIR / f"{_safe_name(name)}.json"


def marks_path(name: str) -> Path:
    """Get the path to a class red-cross file."""
    return MARKS_DIR / f"{_safe_name(name)}.json"


def export_path(filename: str = "plan.txt") -> Path:
    """
    Get default export path.
    
    Args:
        filename: Name of the export file
        
    Returns:
        Full path for export file
    """
    return DATA_DIR / filename
