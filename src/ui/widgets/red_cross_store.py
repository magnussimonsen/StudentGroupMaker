"""Red crosses of the active class, shared by the Red Crosses tab and the seating desks.

New crosses are the current ones and the only ones shown and changed on the
seating desks; archived crosses are earlier ones, changed only in the Red Crosses tab.
"""

from datetime import datetime

from PySide6.QtCore import QObject, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QMessageBox, QWidget

from ...models.marks_data import Marks, load_marks, save_marks

RED_CROSS_COLOR = "#e53935"
GREEN_CROSS_COLOR = "#43a047"
ARCHIVED_CROSS_COLOR = "#9e9e9e"  # Readable on both light and dark backgrounds


def confirm_show_red_crosses(parent: QWidget) -> bool:
    """Ask before showing red crosses, since the screen may be projected to the class."""
    reply = QMessageBox.question(
        parent,
        "Show red crosses",
        "Are you sure you want to show the red crosses?\n\n"
        "If the screen is shown on a projector, the class will "
        "see which students have red crosses.",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No,
    )
    return reply == QMessageBox.Yes


def paint_cross(painter: QPainter, rect: QRectF, color: str):
    """Draw a cross filling rect."""
    painter.save()
    painter.setRenderHint(QPainter.Antialiasing)
    pen = QPen(QColor(color), max(1.5, rect.width() / 5))
    pen.setCapStyle(Qt.RoundCap)
    painter.setPen(pen)
    inset = pen.widthF() / 2
    inner = rect.adjusted(inset, inset, -inset, -inset)
    painter.drawLine(inner.topLeft(), inner.bottomRight())
    painter.drawLine(inner.topRight(), inner.bottomLeft())
    painter.restore()


class RedCrossStore(QObject):
    """Loads, changes and saves the red crosses of the currently selected class."""

    roster_changed = Signal()  # Another class or a changed student list
    marks_changed = Signal()  # Crosses added, archived or removed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.class_name = ""
        self.students: dict[str, str] = {}
        self._new: Marks = {}
        self._archived: Marks = {}

    def set_class(self, class_name: str, students: list[dict[str, str]]):
        """Load a class's crosses and drop those of students no longer in it."""
        if class_name != self.class_name:
            try:
                self._new, self._archived = load_marks(class_name) if class_name else ({}, {})
                self.class_name = class_name
            except OSError as error:
                # Keep no class name so the unread crosses are never saved over
                self._new, self._archived = {}, {}
                self.class_name = ""
                QMessageBox.warning(
                    None,
                    "Red crosses could not be loaded",
                    f"The red crosses of '{class_name}' could not be read, so changes "
                    f"to them will not be saved.\n\n{error}",
                )

        self.students = {
            student["id"]: student["name"]
            for student in students
            if isinstance(student, dict)
            and isinstance(student.get("id"), str)
            and isinstance(student.get("name"), str)
        }
        known_new = self._known(self._new)
        known_archived = self._known(self._archived)
        if known_new != self._new or known_archived != self._archived:
            self._new, self._archived = known_new, known_archived
            self._save()
        self.roster_changed.emit()

    def _known(self, marks: Marks) -> Marks:
        return {
            student_id: stamps for student_id, stamps in marks.items()
            if student_id in self.students and stamps
        }

    def count(self, student_id: str | None) -> int:
        """Number of new crosses of a student."""
        return len(self._new.get(student_id, []))

    def archived_count(self, student_id: str | None) -> int:
        return len(self._archived.get(student_id, []))

    def total(self) -> int:
        """Number of new crosses in the class."""
        return sum(len(stamps) for stamps in self._new.values())

    def archived_total(self) -> int:
        return sum(len(stamps) for stamps in self._archived.values())

    def add(self, student_id: str):
        """Give a student a new cross."""
        if student_id not in self.students:
            return
        stamp = datetime.now().isoformat(timespec="seconds")
        self._new.setdefault(student_id, []).append(stamp)
        self._changed()

    def remove_last(self, student_id: str):
        """Remove a student's latest new cross."""
        if self._pop_last(self._new, student_id):
            self._changed()

    def remove_last_archived(self, student_id: str):
        """Remove a student's latest archived cross."""
        if self._pop_last(self._archived, student_id):
            self._changed()

    def archive(self, student_id: str):
        """Move a student's new crosses to the archive, keeping when they were given."""
        stamps = self._new.pop(student_id, None)
        if not stamps:
            return
        self._archived.setdefault(student_id, []).extend(stamps)
        self._changed()

    def archive_all(self):
        """Move every student's new crosses to the archive."""
        if not self._new:
            return
        for student_id, stamps in self._new.items():
            self._archived.setdefault(student_id, []).extend(stamps)
        self._new = {}
        self._changed()

    def reset_new(self):
        self._new = {}
        self._changed()

    def reset_archived(self):
        self._archived = {}
        self._changed()

    @staticmethod
    def _pop_last(marks: Marks, student_id: str) -> bool:
        stamps = marks.get(student_id)
        if not stamps:
            return False
        stamps.pop()
        if not stamps:
            del marks[student_id]
        return True

    def _changed(self):
        self._save()
        self.marks_changed.emit()

    def _save(self):
        if self.class_name:
            save_marks(self.class_name, self._new, self._archived)
