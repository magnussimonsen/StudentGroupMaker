"""
Class and student data management.

This module handles loading, saving, and managing class/student data.
"""
from __future__ import annotations
import json
from pathlib import Path
from uuid import uuid4

from .storage import class_path, marks_path, seating_path, write_json_atomically, CLASSES_DIR
from ..constants import DEFAULT_STUDENTS, DEFAULT_MATH102_STUDENTS


def load_class_records(name: str) -> list[dict[str, str]]:
    """Load students with their stable IDs.

    Raises OSError if the file cannot be read and ValueError if it is damaged,
    so callers never mistake an unreadable class for an empty one.
    """
    path = class_path(name)
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        raise ValueError(f"The student list of '{name}' is damaged: {error}") from error

    students = data.get("students") if isinstance(data, dict) else None
    if not isinstance(students, list):
        raise ValueError(f"The student list of '{name}' is damaged.")

    records = []
    seen_ids = set()
    for student in students:
        student_id = student.get("id") if isinstance(student, dict) else None
        student_name = student.get("name") if isinstance(student, dict) else None
        if (
            not isinstance(student_id, str)
            or not student_id
            or student_id in seen_ids
            or not isinstance(student_name, str)
            or not student_name.strip()
        ):
            raise ValueError(f"The student list of '{name}' contains an invalid student.")
        seen_ids.add(student_id)
        records.append({"id": student_id, "name": student_name.strip()})
    return records


def save_class_records(name: str, students: list[dict[str, str]]) -> None:
    """Save student records without changing their stable IDs."""
    write_json_atomically(class_path(name), {"students": students})


def save_class(name: str, students: list[str]) -> None:
    """
    Save student list for a class.
    
    Args:
        name: Class name
        students: List of student names
    """
    save_class_records(
        name,
        [{"id": uuid4().hex, "name": student} for student in students],
    )


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
        for related_file in (seating_path(name), marks_path(name)):
            if related_file.exists():
                related_file.unlink()
        return True
    return False


# Built-in sample classes; they are always available and cannot be deleted
SAMPLE_CLASSES = {
    "Math101": DEFAULT_STUDENTS,
    "Math102": DEFAULT_MATH102_STUDENTS,
}


def create_default_class() -> None:
    """Create the built-in sample classes if they do not already exist."""
    existing_classes = list_classes()
    for name, students in SAMPLE_CLASSES.items():
        if name not in existing_classes:
            save_class(name, students)


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
