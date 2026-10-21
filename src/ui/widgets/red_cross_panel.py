"""Red Crosses tab: give, archive and remove red crosses and list every student's crosses."""

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QColor, QFontMetrics
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .flow_layout import FlowLayout, make_group
from .red_cross_store import ARCHIVED_CROSS_COLOR, RED_CROSS_COLOR, RedCrossStore

(
    _NAME_COLUMN,
    _ADD_COLUMN,
    _ARCHIVE_COLUMN,
    _REMOVE_NEW_COLUMN,
    _REMOVE_ARCHIVED_COLUMN,
    _NEW_COLUMN,
    _ARCHIVED_COLUMN,
    _TOTAL_COLUMN,
) = range(8)
_ROW_PADDING = 8  # Room for the buttons' vertical padding and border (3px + 1px each side)


class RedCrossPanel(QWidget):
    """One row per student with buttons for their new and archived red crosses."""

    def __init__(self, red_crosses: RedCrossStore, parent=None):
        super().__init__(parent)
        self.red_crosses = red_crosses
        # Student ID of each table row, in roster order
        self._row_students: list[str] = []
        self._setup_ui()
        red_crosses.roster_changed.connect(self._rebuild_table)
        red_crosses.marks_changed.connect(self._update_marks)
        self._rebuild_table()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        # Same margins as the toolbar rows on the other pages
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        controls_row = FlowLayout(spacing=10)
        # Class selector (the combo box is moved in here by MainWindow._set_mode)
        self.class_group = make_group(QLabel("Class:"))
        controls_row.addWidget(self.class_group)
        self.archive_all_button = QPushButton("Archive all new crosses")
        self.archive_all_button.setObjectName("generateButton")  # Styled green in the stylesheet
        self.archive_all_button.setToolTip("Move every student's new crosses to the archive")
        self.archive_all_button.clicked.connect(self.red_crosses.archive_all)
        controls_row.addWidget(self.archive_all_button)
        self.reset_new_button = QPushButton("Reset all new crosses")
        self.reset_new_button.setObjectName("deleteClassButton")  # Styled red in the stylesheet
        self.reset_new_button.clicked.connect(self._reset_new)
        controls_row.addWidget(self.reset_new_button)
        self.reset_archived_button = QPushButton("Reset all archived crosses")
        self.reset_archived_button.setObjectName("deleteClassButton")
        self.reset_archived_button.clicked.connect(self._reset_archived)
        controls_row.addWidget(self.reset_archived_button)
        controls_widget = QWidget()
        controls_widget.setLayout(controls_row)
        layout.addWidget(controls_widget)

        hint = QLabel(
            "New red crosses can also be given in Class Seating: "
            "click a green cross on a student's desk to turn it red. "
            "Archived crosses are not shown there."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.table = QTableWidget(0, 8, self)
        self.table.setHorizontalHeaderLabels(
            ["Student", "", "", "", "", "New crosses", "Archived crosses", "Total"]
        )
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self._update_row_height()
        header = self.table.horizontalHeader()
        for column in range(self.table.columnCount()):
            header.setSectionResizeMode(column, QHeaderView.ResizeToContents)
        for column in (_NEW_COLUMN, _ARCHIVED_COLUMN):
            header.setSectionResizeMode(column, QHeaderView.Stretch)
        layout.addWidget(self.table, 1)

    def changeEvent(self, event):
        if event.type() == QEvent.FontChange:
            self._update_row_height()
        super().changeEvent(event)

    def _update_row_height(self):
        """Keep rows just tall enough for the text and the buttons."""
        height = QFontMetrics(self.table.font()).height() + _ROW_PADDING
        self.table.verticalHeader().setDefaultSectionSize(height)

    def _rebuild_table(self):
        self._row_students = list(self.red_crosses.students)
        self.table.setRowCount(len(self._row_students))
        for row, student_id in enumerate(self._row_students):
            name_item = QTableWidgetItem(self.red_crosses.students[student_id])
            self.table.setItem(row, _NAME_COLUMN, name_item)

            for column, label, tooltip, action in (
                (_ADD_COLUMN, "Add new cross", "Give a new red cross",
                 self.red_crosses.add),
                (_ARCHIVE_COLUMN, "Archive new crosses",
                 "Move this student's new crosses to the archive",
                 self.red_crosses.archive),
                (_REMOVE_NEW_COLUMN, "Remove new cross", "Remove the latest new cross",
                 self.red_crosses.remove_last),
                (_REMOVE_ARCHIVED_COLUMN, "Remove archived cross",
                 "Remove the latest archived cross",
                 self._remove_archived),
            ):
                button = QPushButton(label)
                button.setToolTip(tooltip)
                button.clicked.connect(lambda _checked, a=action, s=student_id: a(s))
                self.table.setCellWidget(row, column, button)

            for column, color in (
                (_NEW_COLUMN, RED_CROSS_COLOR),
                (_ARCHIVED_COLUMN, ARCHIVED_CROSS_COLOR),
            ):
                crosses_item = QTableWidgetItem()
                crosses_item.setForeground(QColor(color))
                self.table.setItem(row, column, crosses_item)

            total_item = QTableWidgetItem()
            total_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, _TOTAL_COLUMN, total_item)
        self._update_marks()

    def _update_marks(self):
        """Refresh the crosses without recreating the buttons (one may be mid-click)."""
        for row, student_id in enumerate(self._row_students):
            new = self.red_crosses.count(student_id)
            archived = self.red_crosses.archived_count(student_id)
            self.table.item(row, _NEW_COLUMN).setText(" ".join(["✖"] * new))
            self.table.item(row, _ARCHIVED_COLUMN).setText(" ".join(["✖"] * archived))
            self.table.item(row, _TOTAL_COLUMN).setText(str(new + archived))
            self.table.cellWidget(row, _ARCHIVE_COLUMN).setEnabled(new > 0)
            self.table.cellWidget(row, _REMOVE_NEW_COLUMN).setEnabled(new > 0)
            self.table.cellWidget(row, _REMOVE_ARCHIVED_COLUMN).setEnabled(archived > 0)
        self.archive_all_button.setEnabled(self.red_crosses.total() > 0)
        self.reset_new_button.setEnabled(self.red_crosses.total() > 0)
        self.reset_archived_button.setEnabled(self.red_crosses.archived_total() > 0)

    def _remove_archived(self, student_id: str):
        """Ask first, since the archive is meant to keep earlier crosses safe."""
        name = self.red_crosses.students.get(student_id, "this student")
        reply = QMessageBox.question(
            self,
            "Remove archived cross",
            f"Remove the latest archived red cross of {name}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.red_crosses.remove_last_archived(student_id)

    def _reset_new(self):
        if self._confirm_reset("new", self.red_crosses.total()):
            self.red_crosses.reset_new()

    def _reset_archived(self):
        if self._confirm_reset("archived", self.red_crosses.archived_total()):
            self.red_crosses.reset_archived()

    def _confirm_reset(self, kind: str, count: int) -> bool:
        class_name = self.red_crosses.class_name or "this class"
        reply = QMessageBox.warning(
            self,
            f"Reset all {kind} crosses",
            f"Are you sure you want to remove all {count} {kind} red "
            f"cross(es) in {class_name}?\nThis cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        return reply == QMessageBox.Yes
