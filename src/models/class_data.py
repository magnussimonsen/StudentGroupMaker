"""
Class and student data management.

This module handles loading, saving, and managing class/student data.
"""
from __future__ import annotations
import json
from pathlib import Path

from .storage import class_path, CLASSES_DIR
from ..constants import DEFAULT_STUDENTS


def load_class(name: str) -> list[str]:
    """
    Load student list for a class.
    
    Args:
        name: Class name
        
    Returns:
        List of student names
    """
    p = class_path(name)
    if not p.exists():
        return []
    
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        # Accept legacy shapes: either list[str] or [[name, present], ...]
        if data and isinstance(data[0], list):
            return [row[0] for row in data]
        return list(map(str, data))
    except Exception:
        return []


def save_class(name: str, students: list[str]) -> None:
    """
    Save student list for a class.
    
    Args:
        name: Class name
        students: List of student names
    """
    p = class_path(name)
    p.write_text(json.dumps(students, ensure_ascii=False, indent=2), encoding="utf-8")


def list_classes() -> list[str]:
    """
    Get list of all saved classes.
    
    Returns:
        Sorted list of class names
    """
    return sorted([p.stem for p in CLASSES_DIR.glob("*.json")])


def delete_class(name: str) -> bool:
    """
    Delete a class file.
    
    Args:
        name: Class name to delete
        
    Returns:
        True if deleted, False if file didn't exist
    """
    p = class_path(name)
    if p.exists():
        p.unlink()
        return True
    return False


def create_default_class() -> None:
    """Create a default sample class if Math101 doesn't exist."""
    existing_classes = list_classes()
    if "Math101" not in existing_classes:
        save_class("Math101", DEFAULT_STUDENTS)


def export_plan(filename: str, class_name: str, rounds: list[list[list[str]]]) -> None:
    """
    Export a group plan to a text file.
    
    Args:
        filename: Path to save file
        class_name: Name of the class
        rounds: List of rounds (each round is a list of groups)
    """
    lines = []
    lines.append(f"Class: {class_name}\n")
    
    for r, groups in enumerate(rounds, start=1):
        lines.append(f"-------- Round {r} --------\n")
        for i, g in enumerate(groups, start=1):
            lines.append(f"Group {i}: {', '.join(g)}\n")
        lines.append("\n")
    
    Path(filename).write_text("".join(lines), encoding="utf-8")
