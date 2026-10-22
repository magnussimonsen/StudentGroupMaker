"""Persistence for red crosses given to students.

Each student has new crosses (the current period, shown on the seating desks)
and archived crosses (earlier periods, kept safe from everyday changes).
"""

import json

from .storage import backup_damaged_file, marks_path, write_json_atomically

# {student_id: [ISO timestamps of when each cross was given]}
Marks = dict[str, list[str]]


def _read_marks(data: object, key: str) -> Marks:
    marks = data.get(key) if isinstance(data, dict) else None
    if not isinstance(marks, dict):
        return {}
    return {
        student_id: [stamp for stamp in stamps if isinstance(stamp, str)]
        for student_id, stamps in marks.items()
        if isinstance(student_id, str) and isinstance(stamps, list)
    }


def load_marks(name: str) -> tuple[Marks, Marks]:
    """Load the (new, archived) red crosses of a class.

    Raises OSError if the file cannot be read. A damaged file is moved aside
    and no crosses are returned, so the next save cannot overwrite it.
    """
    path = marks_path(name)
    if not path.exists():
        return {}, {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        backup_damaged_file(path)
        return {}, {}

    return _read_marks(data, "new"), _read_marks(data, "archived")


def marks_file_data(new: Marks, archived: Marks) -> dict[str, Marks]:
    """The contents of a red-cross file, leaving out students without any crosses."""
    return {
        "new": {student_id: stamps for student_id, stamps in new.items() if stamps},
        "archived": {
            student_id: stamps for student_id, stamps in archived.items() if stamps
        },
    }


def save_marks(name: str, new: Marks, archived: Marks) -> None:
    """Save the red crosses of a class."""
    write_json_atomically(marks_path(name), marks_file_data(new, archived))
