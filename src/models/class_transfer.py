"""Import and export complete class data bundles."""

from __future__ import annotations

import base64
import binascii
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from .class_data import list_classes, load_class_records
from .marks_data import Marks, load_marks, marks_file_data
from .seating_data import load_seating_charts
from .storage import (
    class_name_problem,
    class_path,
    marks_path,
    seating_path,
    student_photo_path,
    write_bytes_to_temporary_file,
    write_json_atomically,
    write_json_to_temporary_file,
)

_BUNDLE_FORMAT = "student-group-maker-classes"
_BUNDLE_VERSION = 1
_PHOTO_SUFFIXES = {".bmp", ".gif", ".jpeg", ".jpg", ".png", ".webp"}


def _export_students(name: str) -> list[dict[str, str]]:
    if not class_path(name).exists():
        raise ValueError(f"Class data for '{name}' could not be found.")
    # Checked like an import, so every exported file can be imported again
    records = _validate_imported_students(
        load_class_records(name), name, allow_local_photo=True
    )
    exported = []
    for record in records:
        student = {"id": record["id"], "name": record["name"]}
        photo = record.get("photo")
        if photo:
            photo_path = student_photo_path(photo)
            try:
                photo_data = photo_path.read_bytes()
            except OSError as error:
                raise ValueError(
                    f"The photo for '{record['name']}' in '{name}' could not be read: "
                    f"{error}"
                ) from error
            student["photo_data"] = base64.b64encode(photo_data).decode("ascii")
            student["photo_suffix"] = photo_path.suffix.lower()
        exported.append(student)
    return exported


def _export_seating(name: str, students: list[dict[str, str]]) -> dict[str, Any] | None:
    saved = load_seating_charts(name)
    if saved is None:
        return None
    charts, active_chart, front_at_bottom = saved
    return _validate_imported_seating(
        {
            "charts": charts,
            "active_chart": active_chart,
            "front_at_bottom": sorted(front_at_bottom),
        },
        students,
        name,
    )


def _export_red_crosses(name: str, students: list[dict[str, str]]) -> dict[str, Marks]:
    student_ids = {student["id"] for student in students}
    new, archived = load_marks(name)
    # Crosses of students who have left the class are dropped, as when the class is opened
    return _validate_imported_red_crosses(
        {
            kind: {
                student_id: stamps for student_id, stamps in marks.items()
                if student_id in student_ids
            }
            for kind, marks in (("new", new), ("archived", archived))
        },
        students,
        name,
    )


def export_classes(
    names: list[str], destination: Path, include_red_crosses: bool = False
) -> None:
    """Write selected classes and all their seating charts to one JSON file.

    Red crosses are only included when asked for, since the file may be shared.
    """
    if not names:
        raise ValueError("Select at least one class to export.")

    classes = []
    for name in names:
        students = _export_students(name)
        classes.append(
            {
                "name": name,
                "students": students,
                "seating": _export_seating(name, students),
                "red_crosses": (
                    _export_red_crosses(name, students) if include_red_crosses else None
                ),
            }
        )

    bundle = {
        "format": _BUNDLE_FORMAT,
        "version": _BUNDLE_VERSION,
        "classes": classes,
    }
    write_json_atomically(destination, bundle)


def _validate_class_name(name: object) -> str:
    if not isinstance(name, str):
        raise ValueError("The import file contains a class with an invalid name.")
    normalized = name.strip()
    problem = class_name_problem(normalized)
    if problem is not None:
        raise ValueError(f"The imported class name '{name}' cannot be used. {problem}")
    return normalized


def _validate_imported_students(
    students: object, class_name: str, allow_local_photo: bool = False
) -> list[dict[str, str]]:
    if not isinstance(students, list):
        raise ValueError(f"Class '{class_name}' has an invalid student list.")

    records: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    seen_names: set[str] = set()
    for student in students:
        if not isinstance(student, dict):
            raise ValueError(f"Class '{class_name}' contains an invalid student record.")
        student_id = student.get("id")
        student_name = student.get("name")
        photo_data = student.get("photo_data")
        photo_suffix = student.get("photo_suffix")
        photo = student.get("photo")
        if (
            not isinstance(student_id, str)
            or not student_id
            or not isinstance(student_name, str)
            or not student_name.strip()
        ):
            raise ValueError(f"Class '{class_name}' contains an invalid student record.")
        normalized_name = student_name.strip()
        if student_id in seen_ids or normalized_name.casefold() in seen_names:
            raise ValueError(
                f"Class '{class_name}' contains duplicate student IDs or names."
            )
        seen_ids.add(student_id)
        seen_names.add(normalized_name.casefold())
        record = {"id": student_id, "name": normalized_name}
        if allow_local_photo and photo is not None:
            if (
                not isinstance(photo, str)
                or Path(photo).name != photo
                or Path(photo).suffix.lower() not in _PHOTO_SUFFIXES
            ):
                raise ValueError(f"Class '{class_name}' contains an invalid photo.")
            record["photo"] = photo
        if photo_data is not None or photo_suffix is not None:
            if (
                not isinstance(photo_data, str)
                or not isinstance(photo_suffix, str)
                or photo_suffix.lower() not in _PHOTO_SUFFIXES
            ):
                raise ValueError(f"Class '{class_name}' contains invalid photo data.")
            try:
                base64.b64decode(photo_data, validate=True)
            except (binascii.Error, ValueError) as error:
                raise ValueError(
                    f"Class '{class_name}' contains invalid photo data."
                ) from error
            record["photo_data"] = photo_data
            record["photo_suffix"] = photo_suffix.lower()
        if photo is not None and not allow_local_photo:
            raise ValueError(f"Class '{class_name}' contains an unsupported photo path.")
        records.append(record)
    return records


def _validate_imported_seating(
    seating: object, students: list[dict[str, str]], class_name: str
) -> dict[str, Any] | None:
    if seating is None:
        return None
    if not isinstance(seating, dict):
        raise ValueError(f"Class '{class_name}' has invalid seating data.")

    charts = seating.get("charts")
    active_chart = seating.get("active_chart")
    front_at_bottom = seating.get("front_at_bottom")
    if (
        not isinstance(charts, dict)
        or not charts
        or not isinstance(active_chart, str)
        or active_chart not in charts
        or not isinstance(front_at_bottom, list)
        or any(not isinstance(chart_name, str) for chart_name in front_at_bottom)
        or not set(front_at_bottom).issubset(charts)
    ):
        raise ValueError(f"Class '{class_name}' has invalid seating data.")

    student_ids = {student["id"] for student in students}
    validated_charts: dict[str, list[list[str | None]]] = {}
    for chart_name, grid in charts.items():
        if not isinstance(chart_name, str) or not chart_name.strip():
            raise ValueError(f"Class '{class_name}' has an invalid chart name.")
        if (
            not isinstance(grid, list)
            or not grid
            or not isinstance(grid[0], list)
            or not grid[0]
        ):
            raise ValueError(f"Seating chart '{chart_name}' in '{class_name}' is invalid.")

        width = len(grid[0])
        assigned: set[str] = set()
        validated_grid = []
        for row in grid:
            if not isinstance(row, list) or len(row) != width:
                raise ValueError(
                    f"Seating chart '{chart_name}' in '{class_name}' is invalid."
                )
            validated_row: list[str | None] = []
            for student_id in row:
                if student_id is not None and (
                    not isinstance(student_id, str)
                    or student_id not in student_ids
                    or student_id in assigned
                ):
                    raise ValueError(
                        f"Seating chart '{chart_name}' in '{class_name}' "
                        "contains an invalid or duplicate student assignment."
                    )
                if student_id is not None:
                    assigned.add(student_id)
                validated_row.append(student_id)
            validated_grid.append(validated_row)
        validated_charts[chart_name] = validated_grid

    return {
        "charts": validated_charts,
        "active_chart": active_chart,
        "front_at_bottom": sorted(set(front_at_bottom)),
    }


def _validate_imported_red_crosses(
    red_crosses: object, students: list[dict[str, str]], class_name: str
) -> dict[str, Marks] | None:
    if red_crosses is None:
        return None
    invalid = ValueError(f"Class '{class_name}' has invalid red crosses.")
    if not isinstance(red_crosses, dict) or set(red_crosses) != {"new", "archived"}:
        raise invalid

    student_ids = {student["id"] for student in students}
    validated: dict[str, Marks] = {}
    for kind in ("new", "archived"):
        marks = red_crosses[kind]
        if not isinstance(marks, dict):
            raise invalid
        for student_id, stamps in marks.items():
            if student_id not in student_ids or not isinstance(stamps, list):
                raise invalid
            for stamp in stamps:
                try:
                    datetime.fromisoformat(stamp)
                except (TypeError, ValueError):
                    raise invalid from None
        validated[kind] = {student_id: list(stamps) for student_id, stamps in marks.items()}
    return marks_file_data(validated["new"], validated["archived"])


def _get_available_class_name(
    original_name: str, reserved_names: set[str]
) -> str:
    candidate = original_name
    suffix = 2
    while (
        candidate.casefold() in reserved_names
        or class_path(candidate).exists()
        or seating_path(candidate).exists()
        or marks_path(candidate).exists()
    ):
        candidate = f"{original_name}_{suffix}"
        suffix += 1
    reserved_names.add(candidate.casefold())
    return candidate


def import_classes(source: Path) -> list[tuple[str, str]]:
    """Validate and import a bundle, renaming classes that already exist.

    Imports seating charts, and red crosses when the bundle includes them.
    """
    try:
        bundle = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"The selected file could not be read as JSON: {error}") from error

    if (
        not isinstance(bundle, dict)
        or bundle.get("format") != _BUNDLE_FORMAT
        or bundle.get("version") != _BUNDLE_VERSION
        or not isinstance(bundle.get("classes"), list)
        or not bundle["classes"]
    ):
        raise ValueError(
            "This is not a supported GroupMaker class export file."
        )

    validated_classes = []
    source_names: set[str] = set()
    for class_data in bundle["classes"]:
        if not isinstance(class_data, dict):
            raise ValueError("The import file contains an invalid class entry.")
        class_name = _validate_class_name(class_data.get("name"))
        if class_name.casefold() in source_names:
            raise ValueError(f"The import file contains duplicate class '{class_name}'.")
        source_names.add(class_name.casefold())
        students = _validate_imported_students(
            class_data.get("students"), class_name
        )
        seating = _validate_imported_seating(
            class_data.get("seating"), students, class_name
        )
        red_crosses = _validate_imported_red_crosses(
            class_data.get("red_crosses"), students, class_name
        )
        validated_classes.append((class_name, students, seating, red_crosses))

    reserved_names = {name.casefold() for name in list_classes()}
    imports = []
    staged_files: list[tuple[Path, Path]] = []
    created_targets: list[Path] = []
    try:
        for original_name, students, seating, red_crosses in validated_classes:
            imported_name = _get_available_class_name(original_name, reserved_names)
            imported_students = []
            for student in students:
                imported_student = {"id": student["id"], "name": student["name"]}
                photo_data = student.get("photo_data")
                if photo_data is not None:
                    suffix = student["photo_suffix"]
                    photo_filename = f"{uuid4().hex}{suffix}"
                    target_photo = student_photo_path(photo_filename)
                    staged_files.append(
                        (
                            write_bytes_to_temporary_file(
                                target_photo, base64.b64decode(photo_data, validate=True)
                            ),
                            target_photo,
                        )
                    )
                    imported_student["photo"] = photo_filename
                imported_students.append(imported_student)
            for target_file, data in (
                (class_path(imported_name), {"students": imported_students}),
                (seating_path(imported_name), seating),
                (marks_path(imported_name), red_crosses),
            ):
                if data is not None:
                    staged_files.append(
                        (write_json_to_temporary_file(target_file, data), target_file)
                    )
            imports.append((original_name, imported_name))

        for staged_path, target_path in staged_files:
            os.rename(staged_path, target_path)
            created_targets.append(target_path)
    except OSError:
        for staged_path, _ in staged_files:
            staged_path.unlink(missing_ok=True)
        for target_path in created_targets:
            target_path.unlink(missing_ok=True)
        raise

    return imports
