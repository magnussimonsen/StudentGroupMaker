"""Class management panel (left panel)."""

from uuid import uuid4

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QComboBox, QMessageBox
)

from ...constants.colors_and_styling import Layout
from ...models import (
    load_class_records, save_class, save_class_records, list_classes, delete_class,
)


class ClassPanel(QWidget):
    """Left panel for class and student management."""
    
    class_changed = Signal(str)  # Emitted when active class changes
    students_changed = Signal(str, list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_initial_class()
    
    def _setup_ui(self):
        """Set up the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Use minimal margins
        layout.setSpacing(5)  # Use standard spacing
        
        # Class selection row
        classes_row = QHBoxLayout()
        self.class_combo = QComboBox()
        self.class_combo.addItems(list_classes())
        self.class_combo.currentTextChanged.connect(self._on_class_changed)
        
        # Set minimum width based on font size (like rem/em in CSS)
        # fm = QFontMetrics(self.class_combo.font())
        # char_width = fm.averageCharWidth()
        # self.class_combo.setMinimumWidth(char_width * 15)  # ~15 characters wide
        self.class_combo.setMinimumWidth(100)  # Set minimum width in pixels

        
        self.new_class_name = QLineEdit()
        self.new_class_name.setPlaceholderText("New class name…")
        
        # Set minimum width based on font size (like rem/em in CSS)
        # fm = QFontMetrics(self.new_class_name.font())
        # char_width = fm.averageCharWidth()
        # self.new_class_name.setMinimumWidth(char_width * 20)  # ~20 characters wide
        self.new_class_name.setMinimumWidth(180)  # Set minimum width in pixels

        btn_add_class = QPushButton("Add class")
        btn_add_class.clicked.connect(self._add_class)
        
        classes_row.addWidget(QLabel("Class:"))
        classes_row.addWidget(self.class_combo, 2)
        classes_row.addWidget(self.new_class_name, 2)
        classes_row.addWidget(btn_add_class)
        
        # Class management buttons
        class_mgmt_row = QHBoxLayout()
        btn_del_class = QPushButton("Delete class")
        btn_del_class.clicked.connect(self._delete_class)
        
        class_mgmt_row.addWidget(btn_del_class)
        class_mgmt_row.addStretch()
        
        # Student list
        self.student_list = QListWidget()
        # Keep interaction simple: use checkboxes for attendance/removal, not list selection.
        self.student_list.setSelectionMode(QListWidget.NoSelection)
        self.student_list.itemChanged.connect(self._on_student_item_changed)
        
        # Add to main layout
        layout.addLayout(classes_row)
        layout.addLayout(class_mgmt_row)
        layout.addWidget(QLabel("Students in class:"))
        layout.addWidget(self.student_list, 1)
    
    def _load_initial_class(self):
        """Load the first class if any exist."""
        if self.class_combo.count() > 0:
            self._on_class_changed(self.class_combo.currentText())
    
    def _on_class_changed(self, name: str):
        """Handle class selection change."""
        self.student_list.clear()
        if name:
            for student in load_class_records(name):
                self._add_student_item(
                    student["name"],
                    checked=True,
                    student_id=student["id"],
                )
        self.class_changed.emit(name)
        self.students_changed.emit(name, self.get_student_records())

    def _add_student_item(
        self, name: str, checked: bool = True, student_id: str | None = None
    ):
        """Add a student to the list."""
        item = QListWidgetItem(name)
        item.setFlags(
            item.flags() | Qt.ItemIsUserCheckable | 
            Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled
        )
        item.setData(Qt.UserRole, student_id or uuid4().hex)
        item.setData(Qt.UserRole + 1, name)
        item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        self.student_list.addItem(item)

    def _on_student_item_changed(self, item: QListWidgetItem):
        """Save valid student-name edits while ignoring checkbox changes."""
        previous_name = item.data(Qt.UserRole + 1)
        new_name = item.text().strip()
        if new_name == previous_name:
            return

        existing_names = {
            self.student_list.item(index).text().strip()
            for index in range(self.student_list.count())
            if self.student_list.item(index) is not item
        }
        if not new_name or new_name in existing_names:
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
        if not name:
            QMessageBox.warning(self, "Class name", "Please enter a class name.")
            return
        
        existing = [self.class_combo.itemText(i) for i in range(self.class_combo.count())]
        if name in existing:
            QMessageBox.information(self, "Exists", "That class already exists.")
        else:
            save_class(name, [])
            self.class_combo.addItem(name)
            self.class_combo.setCurrentText(name)
        
        self.new_class_name.clear()
    
    def _delete_class(self):
        """Delete the current class."""
        name = self.class_combo.currentText()
        if not name:
            return
        
        reply = QMessageBox.question(
            self, "Delete class",
            f"Delete class '{name}'? This removes its JSON file."
        )
        
        if reply == QMessageBox.Yes:
            delete_class(name)
            # Removing the item selects the next class (or none), which reloads
            # the student list and notifies the other tabs via _on_class_changed.
            idx = self.class_combo.currentIndex()
            self.class_combo.removeItem(idx)
    
    def _auto_save_class(self):
        """Silently save the current class after its student list changes."""
        name = self.class_combo.currentText()
        if not name:
            return
        
        # Sort students alphabetically by first name before saving (and update UI order)
        self._sort_students_by_first_name()
        students = self.get_student_records()
        save_class_records(name, students)
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
            items.append((name, checked, student_id))

        # Sort by first token (first name), case-insensitive; tie-breaker on full name
        def sort_key(entry):
            name = entry[0]
            first = name.split()[0] if name else ""
            return (first.casefold(), name.casefold())

        items.sort(key=sort_key)

        # Rebuild list to reflect sorted order while preserving check states
        self.student_list.clear()
        for name, checked, student_id in items:
            self._add_student_item(name, checked=checked, student_id=student_id)
    
    def _add_student(self):
        """Add a student to the list."""
        name = self.student_input.text().strip()
        if not name:
            return
        
        existing = self.get_all_students()
        if name in existing:
            QMessageBox.information(self, "Duplicate", f"'{name}' is already in the list.")
        else:
            self._add_student_item(name, checked=True)
            self._auto_save_class()
        
        self.student_input.clear()
    
    def add_student_from_input(self, name: str):
        """Add a student from external input (e.g., bottom bar)."""
        name = name.strip()
        if not name:
            return
        
        existing = self.get_all_students()
        if name in existing:
            QMessageBox.information(self, "Duplicate", f"'{name}' is already in the list.")
        else:
            self._add_student_item(name, checked=True)
            self._auto_save_class()
    
    def remove_checked_students(self):
        """Remove checked students (public method for bottom bar)."""
        checked_items = [
            self.student_list.item(i)
            for i in range(self.student_list.count())
            if self.student_list.item(i).checkState() == Qt.Checked
        ]

        if not checked_items:
            QMessageBox.information(
                self,
                "No students checked",
                "Check one or more students to remove."
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
        return [
            {
                "id": self.student_list.item(i).data(Qt.UserRole),
                "name": self.student_list.item(i).text(),
            }
            for i in range(self.student_list.count())
        ]
    
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
