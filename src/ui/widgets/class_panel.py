"""Class management panel (left panel)."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QComboBox, QMessageBox
)

from ...constants.colors_and_styling import Layout
from ...models import load_class, save_class, list_classes, delete_class


class ClassPanel(QWidget):
    """Left panel for class and student management."""
    
    class_changed = Signal(str)  # Emitted when active class changes
    
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
        
        btn_save_class = QPushButton("Save class list")
        btn_save_class.clicked.connect(self._save_class)
        
        class_mgmt_row.addWidget(btn_del_class)
        class_mgmt_row.addWidget(btn_save_class)
        class_mgmt_row.addStretch()
        
        # Student list
        self.student_list = QListWidget()
        # Keep interaction simple: use checkboxes for attendance/removal, not list selection.
        self.student_list.setSelectionMode(QListWidget.NoSelection)
        
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
        if not name:
            return
        
        for student in load_class(name):
            self._add_student_item(student, checked=True)
        
        self.class_changed.emit(name)
    
    def _add_student_item(self, name: str, checked: bool = True):
        """Add a student to the list."""
        item = QListWidgetItem(name)
        item.setFlags(
            item.flags() | Qt.ItemIsUserCheckable | 
            Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled
        )
        item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        self.student_list.addItem(item)
    
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
            idx = self.class_combo.currentIndex()
            self.class_combo.removeItem(idx)
            self.student_list.clear()
    
    def _save_class(self):
        """Save the current class."""
        name = self.class_combo.currentText()
        if not name:
            QMessageBox.warning(self, "No class", "Create/select a class first.")
            return
        
        # Sort students alphabetically by first name before saving (and update UI order)
        self._sort_students_by_first_name()

        students = self.get_all_students()
        save_class(name, students)
        QMessageBox.information(self, "Saved", f"Saved {len(students)} students for '{name}'.")

    def _sort_students_by_first_name(self):
        """Sort the student list by first name (case-insensitive) and update the UI order.

        Preserves each item's checked state. Sorting key is the first whitespace-separated token.
        """
        items = []
        for i in range(self.student_list.count()):
            item = self.student_list.item(i)
            name = item.text().strip()
            checked = (item.checkState() == Qt.Checked)
            items.append((name, checked))

        # Sort by first token (first name), case-insensitive; tie-breaker on full name
        def sort_key(entry):
            name = entry[0]
            first = name.split()[0] if name else ""
            return (first.casefold(), name.casefold())

        items.sort(key=sort_key)

        # Rebuild list to reflect sorted order while preserving check states
        self.student_list.clear()
        for name, checked in items:
            self._add_student_item(name, checked=checked)
    
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
