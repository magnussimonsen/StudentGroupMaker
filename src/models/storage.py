"""
Storage paths and file operations.

This module handles all file system operations for the application.
"""
from pathlib import Path

from ..constants import APP_NAME


# Storage directories
DATA_DIR = Path.home() / f".{APP_NAME}"
CLASSES_DIR = DATA_DIR / "classes"
SEATINGS_DIR = DATA_DIR / "seatings"

# Ensure directories exist
CLASSES_DIR.mkdir(parents=True, exist_ok=True)
SEATINGS_DIR.mkdir(parents=True, exist_ok=True)


def class_path(name: str) -> Path:
    """
    Get the file path for a class data file.
    
    Args:
        name: Class name
        
    Returns:
        Path to the class JSON file
    """
    # Sanitize filename - remove invalid characters
    safe = "".join(c for c in name if c not in r'<>:"/\|?*').strip()
    return CLASSES_DIR / f"{safe}.json"


def seating_path(name: str) -> Path:
    """Get the path to a class seating-layout file."""
    safe = "".join(c for c in name if c not in r'<>:"/\|?*').strip()
    return SEATINGS_DIR / f"{safe}.json"


def export_path(filename: str = "plan.txt") -> Path:
    """
    Get default export path.
    
    Args:
        filename: Name of the export file
        
    Returns:
        Full path for export file
    """
    return DATA_DIR / filename
