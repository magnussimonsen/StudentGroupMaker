"""Class seating organizer with drag-and-drop student assignment."""

import json
from pathlib import Path

from PySide6.QtCore import QByteArray, QMimeData, QStandardPaths, Qt, Signal
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ...models.seating_data import load_seating_charts, save_seating_charts

_STUDENT_MIME_TYPE = "application/x-student-group-maker-seat"
_DEFAULT_ROWS = 5
_DEFAULT_COLUMNS = 6
_MAX_ROWS = 15
_MAX_COLUMNS = 12
_ROW_HEIGHT = 72
_EMPTY_LINE_SCALE = 0.5  # Rows/columns without students are drawn at half size


def _decode_student_mime(mime_data: QMimeData) -> dict | None:
    if not mime_data.hasFormat(_STUDENT_MIME_TYPE):
        return None
    try:
        payload = json.loads(bytes(mime_data.data(_STUDENT_MIME_TYPE)))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict) or not isinstance(payload.get("student_id"), str):
        return None
    return payload


class AvailableStudentsList(QListWidget):
    """List of unseated students; accepts students dragged out of seats."""

    student_returned = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.MoveAction)

    def startDrag(self, supported_actions):
        item = self.currentItem()
        if item is None:
            return
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setData(
            _STUDENT_MIME_TYPE,
            QByteArray(json.dumps({
                "student_id": item.data(Qt.UserRole),
                "source": "available",
            }).encode()),
        )
        drag.setMimeData(mime_data)
        drag.exec(Qt.MoveAction)

    def dragEnterEvent(self, event):
        payload = _decode_student_mime(event.mimeData())
        if payload and payload.get("source") == "seat":
            event.acceptProposedAction()
            return
        event.ignore()

    def dragMoveEvent(self, event):
        self.dragEnterEvent(event)

    def dropEvent(self, event):
        payload = _decode_student_mime(event.mimeData())
        if not payload or payload.get("source") != "seat":
            event.ignore()
            return
        try:
            row, column = int(payload["row"]), int(payload["column"])
        except (KeyError, TypeError, ValueError):
            event.ignore()
            return
        self.student_returned.emit(row, column)
        event.acceptProposedAction()


class SeatingTable(QTableWidget):
    """Seat grid that accepts students from the list or other seats."""

    student_dropped = Signal(dict, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.verticalHeader().show()
        self.horizontalHeader().show()
        self.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        # Column widths are set by _update_column_widths so empty columns can be narrower
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.verticalHeader().setDefaultSectionSize(_ROW_HEIGHT)
        self.verticalHeader().setMinimumSectionSize(int(_ROW_HEIGHT * _EMPTY_LINE_SCALE))
        self.verticalHeader().setMinimumWidth(36)
        self.horizontalHeader().setMinimumSectionSize(24)
        self._empty_columns: set[int] = set()

    def set_empty_lines(self, empty_rows: set[int], empty_columns: set[int]):
        """Shrink rows and columns that have no seated students."""
        for row in range(self.rowCount()):
            scale = _EMPTY_LINE_SCALE if row in empty_rows else 1
            self.setRowHeight(row, int(_ROW_HEIGHT * scale))
        self._empty_columns = set(empty_columns)
        self._update_column_widths()

    def _update_column_widths(self):
        """Fill the available width, giving empty columns a reduced share."""
        columns = self.columnCount()
        if not columns:
            return
        weights = [
            _EMPTY_LINE_SCALE if column in self._empty_columns else 1
            for column in range(columns)
        ]
        unit = self.viewport().width() / sum(weights)
        used = 0
        for column, weight in enumerate(weights):
            width = int(unit * weight)
            if column == columns - 1:
                width = self.viewport().width() - used  # Absorb rounding leftovers
            self.setColumnWidth(column, width)
            used += width

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_column_widths()

    def startDrag(self, supported_actions):
        index = self.currentIndex()
        if not index.isValid():
            return
        item = self.item(index.row(), index.column())
        if item is None or item.data(Qt.UserRole) is None:
            return

        payload = {
            "student_id": item.data(Qt.UserRole),
            "source": "seat",
            "row": index.row(),
            "column": index.column(),
        }
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setData(_STUDENT_MIME_TYPE, QByteArray(json.dumps(payload).encode()))
        drag.setMimeData(mime_data)
        drag.exec(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if _decode_student_mime(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if not _decode_student_mime(event.mimeData()):
            event.ignore()
            return
        index = self.indexAt(event.position().toPoint())
        if index.isValid():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        payload = _decode_student_mime(event.mimeData())
        index = self.indexAt(event.position().toPoint())
        if not payload or not index.isValid():
            event.ignore()
            return
        self.student_dropped.emit(payload, index.row(), index.column())
        event.acceptProposedAction()


class ClassSeatingPanel(QWidget):
    """Available student list and a top-down classroom seating grid."""

    grid_dimensions_changed = Signal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.class_name = ""
        self.students: dict[str, str] = {}
        self.front_at_bottom: set[str] = set()
        self.seats: list[list[str | None]] = [
            [None] * _DEFAULT_COLUMNS for _ in range(_DEFAULT_ROWS)
        ]
        # Start with a default chart so the panel works before any class exists
        self.charts: dict[str, list[list[str | None]]] = {"Seating 1": self.seats}
        self.active_chart = "Seating 1"
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        splitter = QSplitter(Qt.Horizontal, self)

        students_panel = QWidget(splitter)
        students_layout = QVBoxLayout(students_panel)
        students_layout.setContentsMargins(0, 0, 8, 0)
        self.available_students_hint = QLabel(
            "Drag a seated student here to unseat them."
        )
        self.available_students_hint.setWordWrap(True)
        students_layout.addWidget(self.available_students_hint)
        self.available_students = AvailableStudentsList(students_panel)
        self.available_students.student_returned.connect(self._return_student)
        students_layout.addWidget(self.available_students, 1)
        students_panel.setMinimumWidth(180)
        students_panel.setMaximumWidth(320)

        classroom_panel = QWidget(splitter)
        classroom_layout = QVBoxLayout(classroom_panel)
        classroom_layout.setContentsMargins(8, 0, 0, 0)
        self.front_label = QLabel("Front of the classroom", self)
        self.front_label.setAlignment(Qt.AlignCenter)
        self.front_label.setObjectName("frontOfClassroomLabel")
        self.back_label = QLabel("Back of the classroom", self)
        self.back_label.setAlignment(Qt.AlignCenter)
        self.back_label.setObjectName("backOfClassroomLabel")
        classroom_layout.addWidget(self.front_label)
        self.seating_table = SeatingTable(classroom_panel)
        self.seating_table.student_dropped.connect(self._drop_student)
        classroom_layout.addWidget(self.seating_table, 1)
        classroom_layout.addWidget(self.back_label)

        charts_panel = QWidget(splitter)
        charts_layout = QVBoxLayout(charts_panel)
        charts_layout.setContentsMargins(8, 0, 0, 0)
        charts_layout.addWidget(QLabel("Saved seating charts"))
        self.chart_list = QListWidget(charts_panel)
        self.chart_list.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.chart_list.currentItemChanged.connect(self._on_chart_selected)
        self.chart_list.itemChanged.connect(self._rename_chart)
        charts_layout.addWidget(self.chart_list, 1)
        self.new_chart_button = QPushButton("New chart", charts_panel)
        self.new_chart_button.clicked.connect(self._create_chart)
        charts_layout.addWidget(self.new_chart_button)
        self.delete_chart_button = QPushButton("Delete chart", charts_panel)
        self.delete_chart_button.setObjectName("deleteClassButton")
        self.delete_chart_button.clicked.connect(self._delete_chart)
        charts_layout.addWidget(self.delete_chart_button)
        charts_panel.setMinimumWidth(190)
        charts_panel.setMaximumWidth(320)

        splitter.addWidget(students_panel)
        splitter.addWidget(classroom_panel)
        splitter.addWidget(charts_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        layout.addWidget(splitter)

    def set_class(self, class_name: str, students: list[dict[str, str]]):
        """Load a class seating plan and reconcile it with the current roster."""
        if class_name != self.class_name:
            self.class_name = class_name
            saved_charts = load_seating_charts(class_name) if class_name else None
            if saved_charts is None:
                self.charts = {
                    "Seating 1": [
                        [None] * _DEFAULT_COLUMNS for _ in range(_DEFAULT_ROWS)
                    ]
                }
                self.active_chart = "Seating 1"
                self.front_at_bottom = set()
            else:
                self.charts, self.active_chart, self.front_at_bottom = saved_charts
            self.seats = self.charts[self.active_chart]

        previous_charts = {
            chart_name: [row.copy() for row in seats]
            for chart_name, seats in self.charts.items()
        }
        self.students = {
            student["id"]: student["name"]
            for student in students
            if isinstance(student, dict)
            and isinstance(student.get("id"), str)
            and isinstance(student.get("name"), str)
        }
        id_by_name = {
            name: student_id for student_id, name in self.students.items()
        }
        for seats in self.charts.values():
            for row_index, row in enumerate(seats):
                for column_index, student_id in enumerate(row):
                    if student_id not in self.students and student_id in id_by_name:
                        seats[row_index][column_index] = id_by_name[student_id]
            self._reconcile_roster(seats)
        self.seats = self.charts[self.active_chart]
        self._refresh_chart_list()
        if self.class_name and self.charts != previous_charts:
            self._save_charts()
        else:
            self._refresh()

    def _reconcile_roster(self, seats: list[list[str | None]]):
        known_students = set(self.students)
        assigned_students = set()
        for row_index, row in enumerate(seats):
            for column_index, student in enumerate(row):
                if student not in known_students or student in assigned_students:
                    seats[row_index][column_index] = None
                elif student is not None:
                    assigned_students.add(student)

    def _refresh_chart_list(self):
        self.chart_list.blockSignals(True)
        self.chart_list.clear()
        selected_item = None
        for chart_name in self.charts:
            item = QListWidgetItem(chart_name)
            item.setData(Qt.UserRole, chart_name)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.chart_list.addItem(item)
            if chart_name == self.active_chart:
                selected_item = item
        if selected_item is not None:
            self.chart_list.setCurrentItem(selected_item)
        self.chart_list.blockSignals(False)
        self.delete_chart_button.setEnabled(len(self.charts) > 1)
        self._update_front_label_position()
        self._refresh()

    def _save_charts(self):
        if self.class_name:
            save_seating_charts(
                self.class_name,
                self.charts,
                self.active_chart,
                self.front_at_bottom,
            )
        self._refresh()

    def _on_chart_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        if current is None or current.text() not in self.charts:
            return
        self.active_chart = current.text()
        self.seats = self.charts[self.active_chart]
        self._update_front_label_position()
        self._save_charts()

    def _create_chart(self):
        base_name = "Seating chart"
        suffix = 1
        chart_name = f"{base_name} {suffix}"
        while chart_name in self.charts:
            suffix += 1
            chart_name = f"{base_name} {suffix}"

        rows = len(self.seats)
        columns = len(self.seats[0]) if rows else _DEFAULT_COLUMNS
        self.charts[chart_name] = [
            [None] * columns for _ in range(rows or _DEFAULT_ROWS)
        ]
        self.front_at_bottom.discard(chart_name)
        self.active_chart = chart_name
        self.seats = self.charts[chart_name]
        item = QListWidgetItem(chart_name)
        item.setData(Qt.UserRole, chart_name)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.chart_list.addItem(item)
        self.chart_list.setCurrentItem(item)
        self.delete_chart_button.setEnabled(len(self.charts) > 1)
        self._save_charts()

    def _delete_chart(self):
        item = self.chart_list.currentItem()
        if item is None or len(self.charts) <= 1:
            return

        chart_name = item.data(Qt.UserRole)
        if not isinstance(chart_name, str) or chart_name not in self.charts:
            return

        reply = QMessageBox.question(
            self,
            "Delete seating chart",
            f"Delete the seating chart '{chart_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        was_active = chart_name == self.active_chart
        del self.charts[chart_name]
        self.front_at_bottom.discard(chart_name)
        if was_active:
            remaining_names = list(self.charts)
            next_index = min(self.chart_list.row(item), len(remaining_names) - 1)
            self.active_chart = remaining_names[next_index]
            self.seats = self.charts[self.active_chart]

        self.chart_list.blockSignals(True)
        self.chart_list.takeItem(self.chart_list.row(item))
        self.chart_list.setCurrentRow(
            list(self.charts).index(self.active_chart)
        )
        self.chart_list.blockSignals(False)
        self.delete_chart_button.setEnabled(len(self.charts) > 1)
        self._save_charts()

    def _rename_chart(self, item: QListWidgetItem):
        old_name = item.data(Qt.UserRole)
        new_name = item.text().strip()
        if (
            not isinstance(old_name, str)
            or old_name not in self.charts
            or not new_name
            or (new_name != old_name and new_name in self.charts)
        ):
            self.chart_list.blockSignals(True)
            item.setText(old_name if isinstance(old_name, str) else "")
            self.chart_list.blockSignals(False)
            return
        if new_name == old_name:
            if item.text() != new_name:
                self.chart_list.blockSignals(True)
                item.setText(new_name)
                self.chart_list.blockSignals(False)
            return

        charts = {}
        for chart_name, seats in self.charts.items():
            charts[new_name if chart_name == old_name else chart_name] = seats
        self.charts = charts
        item.setData(Qt.UserRole, new_name)
        if old_name in self.front_at_bottom:
            self.front_at_bottom.remove(old_name)
            self.front_at_bottom.add(new_name)
        if self.active_chart == old_name:
            self.active_chart = new_name
            self.seats = self.charts[new_name]
        self._update_front_label_position()
        self._save_charts()

    def _update_front_label_position(self):
        layout = self.seating_table.parentWidget().layout()
        layout.removeWidget(self.front_label)
        layout.removeWidget(self.back_label)
        layout.removeWidget(self.seating_table)
        if self.active_chart in self.front_at_bottom:
            layout.addWidget(self.back_label)
            layout.addWidget(self.seating_table, 1)
            layout.addWidget(self.front_label)
        else:
            layout.addWidget(self.front_label)
            layout.addWidget(self.seating_table, 1)
            layout.addWidget(self.back_label)

    def _refresh(self):
        assigned_students = {
            student_id for row in self.seats for student_id in row
            if student_id is not None
        }
        self.available_students.clear()
        for student_id, student_name in self.students.items():
            if student_id not in assigned_students:
                item = QListWidgetItem(student_name)
                item.setData(Qt.UserRole, student_id)
                self.available_students.addItem(item)

        rows = len(self.seats)
        columns = len(self.seats[0]) if rows else 0
        self.seating_table.setRowCount(rows)
        self.seating_table.setColumnCount(columns)
        self.seating_table.setVerticalHeaderLabels(
            [str(row + 1) for row in range(rows)]
        )
        self.seating_table.setHorizontalHeaderLabels(
            [str(column + 1) for column in range(columns)]
        )
        for row_index, row in enumerate(self.seats):
            for column_index, student_id in enumerate(row):
                student_name = self.students.get(student_id)
                item = QTableWidgetItem(student_name if student_name is not None else "-")
                item.setData(Qt.UserRole, student_id)
                item.setTextAlignment(Qt.AlignCenter)
                flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled
                if student_id is not None:
                    flags |= Qt.ItemIsDragEnabled
                item.setFlags(flags)
                self.seating_table.setItem(row_index, column_index, item)
        empty_rows = {
            row_index for row_index, row in enumerate(self.seats)
            if all(student_id is None for student_id in row)
        }
        empty_columns = {
            column_index for column_index in range(columns)
            if all(row[column_index] is None for row in self.seats)
        }
        self.seating_table.set_empty_lines(empty_rows, empty_columns)
        self.grid_dimensions_changed.emit(rows, columns)

    def _save_and_refresh(self):
        self._reconcile_roster(self.seats)
        self.charts[self.active_chart] = self.seats
        if self.class_name:
            self._save_charts()
        else:
            self._refresh()

    def _drop_student(self, payload: dict, target_row: int, target_column: int):
        student_id = payload["student_id"]
        if student_id not in self.students:
            return

        source = payload.get("source")
        target_student = self.seats[target_row][target_column]
        if source == "available":
            if any(student_id in row for row in self.seats):
                return
            self.seats[target_row][target_column] = student_id
        elif source == "seat":
            try:
                source_row = int(payload["row"])
                source_column = int(payload["column"])
            except (KeyError, TypeError, ValueError):
                return
            if not (
                0 <= source_row < len(self.seats)
                and 0 <= source_column < len(self.seats[source_row])
                and self.seats[source_row][source_column] == student_id
            ):
                return
            if (source_row, source_column) == (target_row, target_column):
                return
            self.seats[source_row][source_column] = target_student
            self.seats[target_row][target_column] = student_id
        else:
            return

        self._save_and_refresh()

    def _return_student(self, row: int, column: int):
        if not (
            0 <= row < len(self.seats)
            and 0 <= column < len(self.seats[row])
            and self.seats[row][column] is not None
        ):
            return
        self.seats[row][column] = None
        self._save_and_refresh()

    def add_row(self):
        if len(self.seats) >= _MAX_ROWS:
            return
        columns = len(self.seats[0]) if self.seats else _DEFAULT_COLUMNS
        self.seats.append([None] * columns)
        self._save_and_refresh()

    def remove_row(self):
        if len(self.seats) <= 1:
            return
        reply = QMessageBox.question(
            self,
            "Remove row",
            "Are you sure you want to remove the last row?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self.seats.pop()
        self._save_and_refresh()

    def add_column(self):
        if not self.seats or len(self.seats[0]) >= _MAX_COLUMNS:
            return
        for row in self.seats:
            row.append(None)
        self._save_and_refresh()

    def remove_column(self):
        if not self.seats or len(self.seats[0]) <= 1:
            return
        reply = QMessageBox.question(
            self,
            "Remove column",
            "Are you sure you want to remove the last column?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        for row in self.seats:
            row.pop()
        self._save_and_refresh()

    def flip_classroom(self):
        """Rotate the seating layout by 180 degrees."""
        self.seats = [list(reversed(row)) for row in reversed(self.seats)]
        if self.active_chart in self.front_at_bottom:
            self.front_at_bottom.remove(self.active_chart)
        else:
            self.front_at_bottom.add(self.active_chart)
        self._update_front_label_position()
        self._save_and_refresh()

    def export_png(self):
        """Save the classroom view (labels and seat grid) as a PNG image."""
        desktop = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        default_name = f"{self.class_name or 'class'} - {self.active_chart}.png"
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export seating as PNG",
            str(Path(desktop or "") / default_name),
            "PNG images (*.png)",
        )
        if not filename:
            return
        if not filename.lower().endswith(".png"):
            filename += ".png"

        # Hide the selection highlight so it doesn't end up in the image
        self.seating_table.clearSelection()
        image = self.seating_table.parentWidget().grab()
        if not image.save(filename, "PNG"):
            QMessageBox.critical(self, "Export failed", f"Could not save:\n{filename}")
            return
        QMessageBox.information(self, "Seating exported", f"Saved to:\n{filename}")
