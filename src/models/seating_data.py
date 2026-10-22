"""Persistence for class seating layouts."""

import json

from .storage import seating_path, write_json_atomically


def _is_valid_grid(seats: object) -> bool:
    if not isinstance(seats, list) or not seats:
        return False

    width = len(seats[0]) if isinstance(seats[0], list) else 0
    return width > 0 and all(
        isinstance(row, list)
        and len(row) == width
        and all(student is None or isinstance(student, str) for student in row)
        for row in seats
    )


def load_seating_charts(
    name: str,
) -> tuple[dict[str, list[list[str | None]]], str, set[str]] | None:
    """Load a class's named charts, the active chart and the charts drawn front at bottom."""
    path = seating_path(name)
    if not path.exists():
        return None

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Invalid seating layout in {path}")

    charts = data.get("charts")
    active_chart = data.get("active_chart")
    if not isinstance(charts, dict) or not charts:
        raise ValueError(f"Invalid seating layout in {path}")
    if any(
        not isinstance(chart_name, str)
        or not chart_name.strip()
        or not _is_valid_grid(seats)
        for chart_name, seats in charts.items()
    ):
        raise ValueError(f"Invalid seating layout in {path}")
    if not isinstance(active_chart, str) or active_chart not in charts:
        raise ValueError(f"Invalid active seating chart in {path}")

    front_at_bottom = data.get("front_at_bottom")
    if (
        not isinstance(front_at_bottom, list)
        or any(not isinstance(chart_name, str) for chart_name in front_at_bottom)
        or not set(front_at_bottom).issubset(charts)
    ):
        raise ValueError(f"Invalid classroom orientation in {path}")

    return charts, active_chart, set(front_at_bottom)


def save_seating_charts(
    name: str,
    charts: dict[str, list[list[str | None]]],
    active_chart: str,
    front_at_bottom: set[str] | None = None,
) -> None:
    """Save all seating charts for a class and the currently selected chart."""
    write_json_atomically(
        seating_path(name),
        {
            "active_chart": active_chart,
            "charts": charts,
            "front_at_bottom": sorted(front_at_bottom or set()),
        },
    )
