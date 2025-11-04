"""Main application window."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QMessageBox, QDialog, QPushButton
)
from PySide6.QtCore import Qt

from ..constants import APP_NAME, VERSION, REPOSITORY
from ..core import schedule_groups, schedule_quality
from .widgets import ClassPanel, ControlsPanel, OutputPanel
from .dialogs import show_about_dialog


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {VERSION}")
        self.resize(1200, 700)
        
        # Store the last generated schedule for matrix display
        self.last_schedule = None
        
        self._setup_ui()
        self._setup_menu()
    
    def _setup_ui(self):
        """Set up the main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        
        # Create splitter with left and right panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel (class management)
        self.class_panel = ClassPanel()
        self.class_panel.class_changed.connect(self._on_class_changed)
        
        # Right side container
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Controls panel (now at top)
        self.controls_panel = ControlsPanel()
        self.controls_panel.generate_requested.connect(self._generate_groups)
        
        # Output panel (below controls)
        self.output_panel = OutputPanel()
        
        # Add controls and output to right side vertically
        right_layout.addWidget(self.controls_panel)
        right_layout.addWidget(self.output_panel, 1)
        
        # Add panels to splitter
        splitter.addWidget(self.class_panel)
        splitter.addWidget(right_widget)
        
        # Set initial splitter sizes (30% left, 70% right)
        splitter.setSizes([500, 700])
        
        layout.addWidget(splitter, 1)
        
        # Bottom bar for student actions (spans entire width)
        self._create_student_actions_bar(layout)
    
    def _create_student_actions_bar(self, parent_layout):
        """Create the bottom action bar for student management."""
        from PySide6.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QLabel
        
        students_row = QHBoxLayout()
        
        self.student_input = QLineEdit()
        self.student_input.setPlaceholderText("Add student…")
        
        btn_add_student = QPushButton("Add")
        btn_add_student.clicked.connect(self._add_student)
        
        btn_remove_selected = QPushButton("Remove selected")
        btn_remove_selected.clicked.connect(self._remove_selected)
        
        btn_all = QPushButton("Check all")
        btn_all.clicked.connect(self._check_all)
        
        btn_none = QPushButton("Uncheck all")
        btn_none.clicked.connect(self._uncheck_all)
        
        students_row.addWidget(QLabel("Student actions:"))
        students_row.addWidget(self.student_input, 2)
        students_row.addWidget(btn_add_student)
        students_row.addWidget(btn_remove_selected)
        students_row.addWidget(btn_all)
        students_row.addWidget(btn_none)
        students_row.addStretch()
        
        parent_layout.addLayout(students_row)
    
    def _add_student(self):
        """Add a student via the bottom bar."""
        self.class_panel.add_student_from_input(self.student_input.text())
        self.student_input.clear()
    
    def _remove_selected(self):
        """Remove selected students via the bottom bar."""
        self.class_panel.remove_selected_students()
    
    def _check_all(self):
        """Check all students via the bottom bar."""
        self.class_panel.check_all_students()
    
    def _uncheck_all(self):
        """Uncheck all students via the bottom bar."""
        self.class_panel.uncheck_all_students()
    
    def _setup_menu(self):
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        light_action = view_menu.addAction("Light Mode")
        light_action.triggered.connect(lambda: self._set_theme("light"))
        
        dark_action = view_menu.addAction("Dark Mode")
        dark_action.triggered.connect(lambda: self._set_theme("dark"))
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = help_menu.addAction("About GroupMaker")
        about_action.triggered.connect(lambda: show_about_dialog(self))
        
        repo_action = help_menu.addAction("View Repository at GitHub")
        repo_action.triggered.connect(self._open_repository)
        
        # Font Size menu (to the right of Help)
        font_menu = menubar.addMenu("Font Size")
        
        # Add font size options as actions
        for size in ["8", "9", "10", "11", "12", "14", "16", "18", "20", "24"]:
            action = font_menu.addAction(f"{size}pt")
            action.triggered.connect(lambda checked, s=size: self._on_font_size_changed(int(s)))
    
    def _on_class_changed(self, name: str):
        """Handle class selection change."""
        # Clear output when switching classes
        self.output_panel.clear()
    
    def _on_font_size_changed(self, size: int):
        """Handle font size change - applies globally to entire application."""
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QFont
        
        # Set application-wide font
        font = QFont()
        font.setPointSize(size)
        QApplication.instance().setFont(font)
        
        # Also explicitly update output panel
        self.output_panel.set_font_size(size)
    
    def _generate_groups(self, students_per_group: int, num_groups: int, 
                        num_rounds: int, seed: int):
        """Generate groups based on current settings."""
        present = self.class_panel.get_present_students()
        
        if not present:
            QMessageBox.warning(self, "No students", "No students are checked as present.")
            return
        
        # Generate the schedule
        schedule = schedule_groups(
            students=present,
            n_groups=num_groups,
            rounds=num_rounds,
            seed=seed
        )
        
        # Store for matrix display
        self.last_schedule = schedule
        
        # Calculate quality - returns (overall_pct, per_round_pct, counts)
        overall_pct, per_round_pct, counts = schedule_quality(schedule)
        
        # Format output
        lines = []
        lines.append(f"Class: {self.class_panel.get_current_class_name()}")
        lines.append(f"Students: {len(present)}")
        lines.append(f"Groups per round: {num_groups}")
        lines.append(f"Students per group: {students_per_group}")
        lines.append(f"Rounds: {num_rounds}")
        lines.append(f"Quality: {overall_pct:.1f}% of new pairs")
        lines.append(f"Random seed: {seed}")
        lines.append("")
        
        for round_idx, round_groups in enumerate(schedule, start=1):
            lines.append(f"Round {round_idx}:")
            for group_idx, group in enumerate(round_groups, start=1):
                members = ", ".join(group)
                lines.append(f"  Group {group_idx}: {members}")
            lines.append("")
        
        output = "\n".join(lines)
        self.output_panel.set_text(output)
    
    def _open_repository(self):
        """Open the repository in a web browser."""
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl(REPOSITORY))
    
    def _set_theme(self, theme: str):
        """Set the application theme (light or dark mode)."""
        from PySide6.QtWidgets import QApplication
        from PySide6.QtGui import QPalette, QColor
        from PySide6.QtCore import Qt
        
        app = QApplication.instance()
        
        if theme == "dark":
            # Dark mode colors
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            app.setPalette(palette)
            
            # Add specific styles for dropdown menus (comboboxes) and menu bar
            dark_style = """
            QComboBox {
                background-color: #353535;
                color: white;
                border: 1px solid #555555;
                padding: 4px;
                border-radius: 3px;
            }
            QComboBox:hover {
                border: 1px solid #777777;
            }
            QComboBox::drop-down {
                background-color: #353535;
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #353535;
                color: white;
                selection-background-color: #2a82da;
                selection-color: black;
                border: 1px solid #555555;
            }
            QComboBox QAbstractItemView::item {
                padding: 4px;
                background-color: #353535;
                color: white;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #2a82da;
                color: black;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #404040;
                color: white;
            }
            
            QMenuBar {
                background-color: #353535;
                color: white;
                border-bottom: 1px solid #555555;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
            }
            QMenuBar::item:selected {
                background-color: #404040;
            }
            QMenuBar::item:pressed {
                background-color: #2a82da;
            }
            
            QMenu {
                background-color: #353535;
                color: white;
                border: 1px solid #555555;
            }
            QMenu::item {
                padding: 6px 20px;
                background-color: transparent;
            }
            QMenu::item:selected {
                background-color: #2a82da;
                color: black;
            }
            QMenu::item:hover {
                background-color: #404040;
            }
            QMenu::separator {
                height: 1px;
                background-color: #555555;
                margin: 2px 0px;
            }
            """
            app.setStyleSheet(dark_style)
        else:
            # Light mode - reset to default
            app.setPalette(app.style().standardPalette())
            app.setStyleSheet("")  # Clear any custom styles
    
    # Methods used by controls panel
    def get_output_text(self) -> str:
        """Get the current output text."""
        return self.output_panel.get_text()
    
    def get_current_class_name(self) -> str:
        """Get the current class name."""
        return self.class_panel.get_current_class_name()
    
    def get_last_schedule(self) -> list[list[list[str]]] | None:
        """Get the last generated schedule."""
        return self.last_schedule
    
    def show_cooccurrence_matrix(self):
        """Show co-occurrence matrix of student pairings."""
        if not self.last_schedule:
            QMessageBox.information(
                self,
                "No Schedule",
                "Please generate a group schedule first."
            )
            return
        
        from ..core.visualization import build_pair_matrix, create_heatmap_figure
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        
        names, matrix = build_pair_matrix(self.last_schedule)
        
        # Create dialog to display matrix
        dialog = QDialog(self)
        dialog.setWindowTitle("Student Co-occurrence Matrix")
        dialog.resize(900, 800)
        
        layout = QVBoxLayout()
        
        # Create and add matplotlib figure
        fig = create_heatmap_figure(names, matrix)
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        
        # Add close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()

        """Get the current class name."""
        return self.class_panel.get_current_class_name()
