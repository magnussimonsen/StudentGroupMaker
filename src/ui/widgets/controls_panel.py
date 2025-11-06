"""Controls panel (right panel)."""

from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QSpinBox, QPushButton, QComboBox, QMessageBox, QFileDialog
)
from PySide6.QtGui import QFont

from ...constants.colors_and_styling import Layout
from ...models import export_plan, DATA_DIR
from ...constants.start_values import (
    DEFAULT_STUDENTS_PER_GROUP, 
    DEFAULT_NUM_GROUPS, 
    DEFAULT_NUM_ROUNDS
)


class ControlsPanel(QWidget):
    """Right panel for group generation controls."""
    
    generate_requested = Signal(int, int, int, int)  # students, groups, rounds, seed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Use minimal margins
        layout.setSpacing(5)  # Use standard spacing
        
        # First row: spinboxes
        spinbox_row = QHBoxLayout()
        
        spinbox_row.addWidget(QLabel("Students/group:"))
        self.num_students = QSpinBox()
        self.num_students.setRange(2, 99)
        self.num_students.setValue(DEFAULT_STUDENTS_PER_GROUP)
        spinbox_row.addWidget(self.num_students)
        
        spinbox_row.addSpacing(10)
        
        spinbox_row.addWidget(QLabel("Groups:"))
        self.num_groups = QSpinBox()
        self.num_groups.setRange(1, 99)
        self.num_groups.setValue(DEFAULT_NUM_GROUPS)
        spinbox_row.addWidget(self.num_groups)
        
        spinbox_row.addSpacing(10)
        
        spinbox_row.addWidget(QLabel("Rounds:"))
        self.num_rounds = QSpinBox()
        self.num_rounds.setRange(1, 99)
        self.num_rounds.setValue(DEFAULT_NUM_ROUNDS)
        spinbox_row.addWidget(self.num_rounds)
        
        spinbox_row.addSpacing(10)
        
        spinbox_row.addWidget(QLabel("Seed (0 = random):"))
        self.random_seed = QSpinBox()
        self.random_seed.setRange(0, 999999)
        self.random_seed.setValue(0)
        # Help users understand that 0 means totally random
        self.random_seed.setToolTip("0 = totally random; any other number reproduces the same grouping")
        # Show a friendly label when at the minimum value
        self.random_seed.setSpecialValueText("Random")
        spinbox_row.addWidget(self.random_seed)
        
        spinbox_row.addStretch()
        
        # Second row: buttons
        button_row = QHBoxLayout()
        
        btn_generate = QPushButton("Generate groups")
        btn_generate.clicked.connect(self._on_generate)
        button_row.addWidget(btn_generate)
        
        button_row.addSpacing(20)
        
        btn_export = QPushButton("Export plan as file")
        btn_export.clicked.connect(self._on_export)
        button_row.addWidget(btn_export)
        
        button_row.addSpacing(20)
        
        btn_matrix = QPushButton("Show Co-occurrence Heatmap")
        btn_matrix.clicked.connect(self._on_show_matrix)
        button_row.addWidget(btn_matrix)
        
        button_row.addStretch()
        
        layout.addLayout(spinbox_row)
        layout.addLayout(button_row)
    
    def _on_generate(self):
        """Emit signal to generate groups."""
        students = self.num_students.value()
        groups = self.num_groups.value()
        rounds = self.num_rounds.value()
        seed = self.random_seed.value()
        self.generate_requested.emit(students, groups, rounds, seed)
    
    def _on_export(self):
        """Export the current plan to a text file."""
        # This method is now handled directly in the main window
        pass
    
    def _on_show_matrix(self):
        """Show the co-occurrence matrix."""
        # This method is now handled directly in the main window  
        pass
