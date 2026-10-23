"""Class and student management: the class selector, student list and their actions."""

from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImageReader
from PySide6.QtWidgets import (
    QWidget, QLineEdit, QListWidget, QListWidgetItem, QComboBox, QMessageBox,
    QFileDialog,
)

from ...models import (
    load_class_records, save_class, save_class_records, list_classes, delete_class,
)
from ...models.class_data import replace_student_photo
from ...models.class_data import SAMPLE_CLASSES
from ...models.storage import class_name_problem, same_class_file


class ClassPanel(QWidget):
    """Left panel for class and student management."""
    
    class_changed = Signal(str)  # Emitted when active class changes
    students_changed = Signal(str, list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set when the current class file could not be read; blocks saving over it
        self._roster_unavailable = False
        self._setup_ui()
        self._load_initial_class()
    
    def _setup_ui(self):
        """Create the class selector, new class field and student list.

        MainWindow places these widgets on its pages; the panel itself is never shown.
        """
        self.class_combo = QComboBox()
        self.class_combo.addItems(list_classes())
        self.class_combo.currentTextChanged.connect(self._on_class_changed)

        self.new_class_name = QLineEdit()
        self.new_class_name.setPlaceholderText("New class name…")
        self.new_class_name.setMinimumWidth(180)  # Set minimum width in pixels

        self.student_list = QListWidget()
        # Checkboxes mark attendance and identify students to remove.
        self.student_list.setSelectionMode(QListWidget.NoSelection)
        self.student_list.itemChanged.connect(self._on_student_item_changed)
    
    def _load_initial_class(self):
        """Load the first class if any exist."""
        if self.class_combo.count() > 0:
            self._on_class_changed(self.class_combo.currentText())
    
    def _on_class_changed(self, name: str):
        """Handle class selection change."""
        self.student_list.clear()
        try:
            students = load_class_records(name) if name else []
        except (OSError, ValueError) as error:
            # Publish no class at all, so the other tabs neither show nor save
            # this class's seating and red crosses against an empty roster.
            self._roster_unavailable = True
            self.student_list.setEnabled(False)
            QMessageBox.warning(
                self,
                "Class could not be loaded",
                f"The student list of '{name}' could not be read, so the class "
                f"is shown as read-only and nothing will be saved.\n\n{error}",
            )
            self.class_changed.emit(name)
            self.students_changed.emit("", [])
            return

        self._roster_unavailable = False
        self.student_list.setEnabled(True)
        for student in students:
            self._add_student_item(
                student["name"],
                checked=True,
                student_id=student["id"],
                photo=student.get("photo"),
            )
        self.class_changed.emit(name)
        self.students_changed.emit(name, self.get_student_records())

    def _can_edit_roster(self) -> bool:
        """Warn and refuse when the current class could not be loaded."""
        if self._roster_unavailable:
            QMessageBox.warning(
                self,
                "Class is read-only",
                "This class could not be loaded, so its student list cannot be changed.",
            )
        return not self._roster_unavailable

    def _add_student_item(
        self,
        name: str,
        checked: bool = True,
        student_id: str | None = None,
        photo: str | None = None,
    ):
        """Add a student to the list."""
        item = QListWidgetItem(name)
        item.setFlags(
            item.flags() | Qt.ItemIsUserCheckable | 
            Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled
        )
        item.setData(Qt.UserRole, student_id or uuid4().hex)
        item.setData(Qt.UserRole + 1, name)
        if photo:
            item.setData(Qt.UserRole + 2, photo)
        item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        self.student_list.addItem(item)

    def _on_student_item_changed(self, item: QListWidgetItem):
        """Save valid student-name edits while ignoring checkbox changes."""
        previous_name = item.data(Qt.UserRole + 1)
        new_name = item.text().strip()
        if new_name == previous_name:
            return

        # Ignore case like the class import does, or the class could be exported
        # but not imported again
        existing_names = {
            self.student_list.item(index).text().strip().casefold()
            for index in range(self.student_list.count())
            if self.student_list.item(index) is not item
        }
        if not new_name or new_name.casefold() in existing_names:
            self.student_list.blockSignals(True)
            item.setText(previous_name)
            self.student_list.blockSignals(False)
            QMessageBox.warning(
                self,
                "Student name",
                "Student names must be non-empty and unique within the class.",
            )
            return

        self.student_list.blockSignals(True)
        item.setText(new_name)
        item.setData(Qt.UserRole + 1, new_name)
        self.student_list.blockSignals(False)
        class_name = self.class_combo.currentText()
        if class_name and isinstance(previous_name, str):
            self._auto_save_class()
    
    def _add_class(self):
        """Add a new class."""
        name = self.new_class_name.text().strip()
        problem = class_name_problem(name)
        if problem is not None:
            QMessageBox.warning(self, "Class name", problem)
            return

        # Compare the way the files are named, or the new class would overwrite
        # an existing one that differs only in case (e.g. "math101" vs "Math101").
        existing = next(
            (
                self.class_combo.itemText(i)
                for i in range(self.class_combo.count())
                if same_class_file(self.class_combo.itemText(i), name)
            ),
            None,
        )
        if existing is not None:
            QMessageBox.information(
                self, "Exists", f"The class '{existing}' already exists."
            )
        else:
            try:
                save_class(name, [])
            except OSError as error:
                QMessageBox.critical(
                    self, "Class not saved", f"The class '{name}' could not be saved.\n\n{error}"
                )
                return
            self.class_combo.addItem(name)
            self.class_combo.setCurrentText(name)
        
        self.new_class_name.clear()
    
    def _delete_class(self):
        """Delete the current class."""
        name = self.class_combo.currentText()
        if not name:
            return
        if name in SAMPLE_CLASSES:
            QMessageBox.information(
                self,
                "Sample class",
                f"'{name}' is a sample class and cannot be deleted.",
            )
            return

        reply = QMessageBox.question(
            self, "Delete class",
            f"Delete class '{name}'? This removes its JSON file."
        )
        
        if reply == QMessageBox.Yes:
            try:
                delete_class(name)
            except OSError as error:
                QMessageBox.critical(
                    self, "Class not deleted", f"The class '{name}' could not be deleted.\n\n{error}"
                )
                # Show what is left on disk: the class stays if its file is still there
                self.refresh_classes(name)
                return
            # Removing the item selects the next class (or none), which reloads
            # the student list and notifies the other tabs via _on_class_changed.
            idx = self.class_combo.currentIndex()
            self.class_combo.removeItem(idx)
    
    def _auto_save_class(self):
        """Silently save the current class after its student list changes."""
        name = self.class_combo.currentText()
        if not name or self._roster_unavailable:
            return
        
        # Sort students alphabetically by first name before saving (and update UI order)
        self._sort_students_by_first_name()
        students = self.get_student_records()
        try:
            save_class_records(name, students)
        except OSError as error:
            QMessageBox.critical(
                self,
                "Student list not saved",
                f"The student list of '{name}' could not be saved, so the change "
                f"has been undone.\n\n{error}",
            )
            # Reload the saved list, so the other tabs never act on an unsaved roster
            # (e.g. drop the seats and red crosses of a student who was not removed)
            self._on_class_changed(name)
            return
        self.students_changed.emit(name, students)

    def _sort_students_by_first_name(self):
        """Sort the student list by first name (case-insensitive) and update the UI order.

        Preserves each item's checked state. Sorting key is the first whitespace-separated token.
        """
        items = []
        for i in range(self.student_list.count()):
            item = self.student_list.item(i)
            name = item.text().strip()
            checked = (item.checkState() == Qt.Checked)
            student_id = item.data(Qt.UserRole)
            photo = item.data(Qt.UserRole + 2)
            items.append((name, checked, student_id, photo))

        # Sort by first token (first name), case-insensitive; tie-breaker on full name
        def sort_key(entry):
            name = entry[0]
            first = name.split()[0] if name else ""
            return (first.casefold(), name.casefold())

        items.sort(key=sort_key)

        # Rebuild list to reflect sorted order while preserving check states
        self.student_list.clear()
        for name, checked, student_id, photo in items:
            self._add_student_item(
                name, checked=checked, student_id=student_id, photo=photo
            )
    
    def add_student_from_input(self, name: str):
        """Add a student from external input (e.g., bottom bar)."""
        name = name.strip()
        if not name or not self._can_edit_roster():
            return
        
        existing = self._find_student(name)
        if existing is not None:
            QMessageBox.information(self, "Duplicate", f"'{existing}' is already in the list.")
        else:
            self._add_student_item(name, checked=True)
            self._auto_save_class()

    def _find_student(self, name: str) -> str | None:
        """The student whose name matches name ignoring case, as the class import does."""
        return next(
            (student for student in self.get_all_students()
             if student.casefold() == name.casefold()),
            None,
        )

    def remove_checked_students(self):
        """Remove checked students after confirming."""
        if not self._can_edit_roster():
            return
        # In list order, so the confirmation lists them as shown
        checked_items = [
            self.student_list.item(index)
            for index in range(self.student_list.count())
            if self.student_list.item(index).checkState() == Qt.Checked
        ]

        if not checked_items:
            QMessageBox.information(
                self,
                "No students checked",
                "Check the students you want to remove, then try again."
            )
            return

        # Build confirmation message with student names
        if len(checked_items) == 1:
            student_name = checked_items[0].text()
            message = f"Are you sure you want to remove '{student_name}'?"
        else:
            student_names = [item.text() for item in checked_items]
            names_list = "', '".join(student_names)
            message = f"Are you sure you want to remove these {len(checked_items)} students:\n'{names_list}'?"
        
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Remove student" if len(checked_items) == 1 else "Remove students",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for item in checked_items:
                self.student_list.takeItem(self.student_list.row(item))
            self._auto_save_class()

    def add_or_change_checked_student_photo(self):
        """Choose and save a photo for exactly one checked student."""
        if not self._can_edit_roster():
            return
        checked_items = [
            self.student_list.item(index)
            for index in range(self.student_list.count())
            if self.student_list.item(index).checkState() == Qt.Checked
        ]
        if len(checked_items) != 1:
            QMessageBox.information(
                self,
                "Select one student",
                "Check only one student to add or change their photo.",
            )
            return

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Choose student photo",
            "",
            "Image files (*.bmp *.gif *.jpeg *.jpg *.png *.webp)",
        )
        if not filename:
            return
        reader = QImageReader(filename)
        if not reader.canRead() or reader.read().isNull():
            QMessageBox.warning(
                self, "Invalid photo", "The selected file could not be read as an image."
            )
            return

        item = checked_items[0]
        try:
            photo, cleanup_error = replace_student_photo(
                self.class_combo.currentText(),
                item.data(Qt.UserRole),
                Path(filename),
            )
        except (OSError, ValueError) as error:
            QMessageBox.critical(self, "Photo not saved", str(error))
            return

        item.setData(Qt.UserRole + 2, photo)
        self.students_changed.emit(
            self.class_combo.currentText(), self.get_student_records()
        )
        if cleanup_error is not None:
            QMessageBox.warning(
                self,
                "Photo changed",
                "The new photo was saved, but the previous photo file could not "
                f"be removed.\n\n{cleanup_error}",
            )
    
    def check_all_students(self):
        """Check all students (public method for bottom bar)."""
        for i in range(self.student_list.count()):
            self.student_list.item(i).setCheckState(Qt.Checked)
    
    def uncheck_all_students(self):
        """Uncheck all students (public method for bottom bar)."""
        for i in range(self.student_list.count()):
            self.student_list.item(i).setCheckState(Qt.Unchecked)
    
    def get_all_students(self) -> list[str]:
        """Get all students (checked and unchecked)."""
        return [self.student_list.item(i).text() for i in range(self.student_list.count())]

    def get_student_records(self) -> list[dict[str, str]]:
        """Get student IDs and names for identity-aware features."""
        students = []
        for i in range(self.student_list.count()):
            item = self.student_list.item(i)
            student = {
                "id": item.data(Qt.UserRole),
                "name": item.text(),
            }
            photo = item.data(Qt.UserRole + 2)
            if photo:
                student["photo"] = photo
            students.append(student)
        return students
    
    def get_present_students(self) -> list[str]:
        """Get only checked (present) students."""
        students = []
        for i in range(self.student_list.count()):
            item = self.student_list.item(i)
            if item.checkState() == Qt.Checked:
                students.append(item.text())
        return students
    
    def get_current_class_name(self) -> str:
        """Get the currently selected class name."""
        return self.class_combo.currentText()

    def refresh_classes(self, select_name: str | None = None):
        """Reload class names after an import and publish the selected roster."""
        current_name = select_name or self.class_combo.currentText()
        self.class_combo.blockSignals(True)
        self.class_combo.clear()
        self.class_combo.addItems(list_classes())
        index = self.class_combo.findText(current_name)
        if index >= 0:
            self.class_combo.setCurrentIndex(index)
        elif self.class_combo.count():
            self.class_combo.setCurrentIndex(0)
        self.class_combo.blockSignals(False)
        self._on_class_changed(self.class_combo.currentText())
