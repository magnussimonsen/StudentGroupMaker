"""Import and export complete class data bundles."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .class_data import list_classes, load_class_records
from .seating_data import load_seating_charts
from .storage import class_path, seating_path

_BUNDLE_FORMAT = "student-group-maker-classes"
_BUNDLE_VERSION = 1
_INVALID_FILENAME_CHARACTERS = set('<>:"/\\|?*')


def _read_class_data(name: str) -> list[dict[str, str]]:
    path = class_path(name)
    if not path.exists():
        raise ValueError(f"Class data for '{name}' could not be found.")
    try:
        raw_data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Class data for '{name}' could not be read: {error}") from error

    students = raw_data.get("students") if isinstance(raw_data, dict) else raw_data
    if not isinstance(students, list):
        raise ValueError(f"Class data for '{name}' has an invalid student list.")
    for student in students:
        if isinstance(student, dict):
            if not isinstance(student.get("name"), str):
                raise ValueError(f"Class '{name}' contains an invalid student record.")
        elif isinstance(student, list):
            if not student or not isinstance(student[0], str):
                raise ValueError(f"Class '{name}' contains an invalid student record.")
        elif not isinstance(student, str):
            raise ValueError(f"Class '{name}' contains an invalid student record.")

    return load_class_records(name)


def _export_seating(name: str, students: list[dict[str, str]]) -> dict[str, Any] | None:
    saved = load_seating_charts(name)
    if saved is None:
        return None

    charts, active_chart, front_at_bottom = saved
    id_by_name: dict[str, str | None] = {}
    for student in students:
        student_name = student["name"]
        id_by_name[student_name] = (
            student["id"] if student_name not in id_by_name else None
        )

    student_ids = {student["id"] for student in students}
    exported_charts: dict[str, list[list[str | None]]] = {}
    for chart_name, grid in charts.items():
        assigned: set[str] = set()
        exported_grid: list[list[str | None]] = []
        for row in grid:
            exported_row = []
            for seat in row:
                if seat is None:
                    exported_row.append(None)
                    continue
                student_id = seat if seat in student_ids else id_by_name.get(seat)
                if student_id is None or student_id in assigned:
                    raise ValueError(
                        f"Seating chart '{chart_name}' in class '{name}' "
                        "contains an invalid or duplicate student assignment."
                    )
                assigned.add(student_id)
                exported_row.append(student_id)
            exported_grid.append(exported_row)
        exported_charts[chart_name] = exported_grid

    return {
        "charts": exported_charts,
        "active_chart": active_chart,
        "front_at_bottom": sorted(front_at_bottom),
    }


def _write_json_atomically(path: Path, data: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(data, temporary_file, ensure_ascii=False, indent=2)
            temporary_file.write("\n")
        return temporary_path
    except OSError:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise


def export_classes(names: list[str], destination: Path) -> None:
    """Write selected classes and all their seating charts to one JSON file."""
    if not names:
        raise ValueError("Select at least one class to export.")

    classes = []
    for name in names:
        students = _read_class_data(name)
        classes.append(
            {
                "name": name,
                "students": students,
                "seating": _export_seating(name, students),
            }
        )

    bundle = {
        "format": _BUNDLE_FORMAT,
        "version": _BUNDLE_VERSION,
        "classes": classes,
    }
    temporary_path = _write_json_atomically(destination, bundle)
    try:
        temporary_path.replace(destination)
    except OSError:
        temporary_path.unlink(missing_ok=True)
        raise


def _validate_class_name(name: object) -> str:
    if not isinstance(name, str):
        raise ValueError("The import file contains a class with an invalid name.")
    normalized = name.strip()
    if (
        not normalized
        or normalized[-1] in " ."
        or any(character in _INVALID_FILENAME_CHARACTERS for character in normalized)
        or any(ord(character) < 32 for character in normalized)
    ):
        raise ValueError(f"The imported class name '{name}' is not valid on this system.")
    return normalized


def _validate_imported_students(students: object, class_name: str) -> list[dict[str, str]]:
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
        records.append({"id": student_id, "name": normalized_name})
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


def _get_available_class_name(
    original_name: str, reserved_names: set[str]
) -> str:
    candidate = original_name
    suffix = 2
    while (
        candidate.casefold() in reserved_names
        or class_path(candidate).exists()
        or seating_path(candidate).exists()
    ):
        candidate = f"{original_name}_{suffix}"
        suffix += 1
    reserved_names.add(candidate.casefold())
    return candidate


def import_classes(source: Path) -> list[tuple[str, str]]:
    """Validate and import a bundle, renaming classes that already exist."""
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
        validated_classes.append((class_name, students, seating))

    reserved_names = {name.casefold() for name in list_classes()}
    imports = []
    staged_files: list[tuple[Path, Path]] = []
    created_targets: list[Path] = []
    try:
        for original_name, students, seating in validated_classes:
            imported_name = _get_available_class_name(original_name, reserved_names)
            class_file = class_path(imported_name)
            staged_files.append(
                (
                    _write_json_atomically(class_file, {"students": students}),
                    class_file,
                )
            )
            if seating is not None:
                seating_file = seating_path(imported_name)
                staged_files.append(
                    (
                        _write_json_atomically(seating_file, seating),
                        seating_file,
                    )
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
