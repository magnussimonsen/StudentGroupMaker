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


# Storage directories (created when the first file is written into them)
DATA_DIR = Path.home() / f".{APP_NAME}"
CLASSES_DIR = DATA_DIR / "classes"
SEATINGS_DIR = DATA_DIR / "seatings"
MARKS_DIR = DATA_DIR / "marks"

# Characters that are not allowed in file names on Windows
INVALID_FILENAME_CHARACTERS = set('<>:"/\\|?*')
# Device names Windows reserves, even with an extension (e.g. "CON.json")
_RESERVED_FILE_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{digit}" for digit in range(1, 10)),
    *(f"LPT{digit}" for digit in range(1, 10)),
}


def safe_file_name(name: str) -> str:
    """Remove characters that cannot be used in a file name."""
    return "".join(
        c for c in name if c not in INVALID_FILENAME_CHARACTERS and ord(c) >= 32
    ).strip()


def class_name_problem(name: str) -> str | None:
    """Why name cannot be used as a class name on every system, or None if it can."""
    if not name.strip():
        return "Please enter a class name."
    if name != name.strip() or name.endswith("."):
        return "Class names cannot start or end with a space, or end with a period."
    if any(c in INVALID_FILENAME_CHARACTERS or ord(c) < 32 for c in name):
        return 'Class names cannot contain any of < > : " / \\ | ? *'
    if name.split(".")[0].strip().upper() in _RESERVED_FILE_NAMES:
        return f"'{name}' is a reserved name on Windows and cannot be used for a class."
    return None


def same_class_file(first: str, second: str) -> bool:
    """Whether two class names would be stored in the same file.

    Invalid characters are dropped from file names and Windows ignores case,
    so for example "Math101", "math101" and "Math:101" all share one file.
    """
    return safe_file_name(first).casefold() == safe_file_name(second).casefold()


def write_json_to_temporary_file(path: Path, data: object) -> Path:
    """Write JSON to a temporary file next to path and return it, ready to be moved into place."""
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
    return temporary_path


def write_json_atomically(path: Path, data: object) -> None:
    """Write JSON to a temporary file first, so a crash never leaves a half-written file."""
    temporary_path = write_json_to_temporary_file(path, data)
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
    return CLASSES_DIR / f"{safe_file_name(name)}.json"


def seating_path(name: str) -> Path:
    """Get the path to a class seating-layout file."""
    return SEATINGS_DIR / f"{safe_file_name(name)}.json"


def marks_path(name: str) -> Path:
    """Get the path to a class red-cross file."""
    return MARKS_DIR / f"{safe_file_name(name)}.json"


def export_path(filename: str = "plan.txt") -> Path:
    """
    Get default export path.
    
    Args:
        filename: Name of the export file
        
    Returns:
        Full path for export file
    """
    return DATA_DIR / filename
