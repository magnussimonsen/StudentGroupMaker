"""Class management panel (left panel)."""

from PySide6.QtCore import Qt, Signal
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
        
        self.new_class_name = QLineEdit()
        self.new_class_name.setPlaceholderText("New class name…")
        
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
        self.student_list.setSelectionMode(QListWidget.ExtendedSelection)
        
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
        
        students = self.get_all_students()
        save_class(name, students)
        QMessageBox.information(self, "Saved", f"Saved {len(students)} students for '{name}'.")
    
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
    
    def remove_selected_students(self):
        """Remove selected students (public method for bottom bar)."""
        for item in self.student_list.selectedItems():
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
