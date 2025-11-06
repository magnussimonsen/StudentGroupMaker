"""Main application window."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QMessageBox, QDialog, QPushButton, QLabel
)
from PySide6.QtCore import Qt

from ..constants import APP_NAME, VERSION, REPOSITORY
from ..constants.colors_and_styling import (
    DARK_STYLESHEET, LIGHT_STYLESHEET, DarkTheme, Layout,
    get_dark_stylesheet, get_light_stylesheet
)
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
        
        # Track current theme state
        self.current_theme = "light"
        
        self._setup_ui()
        self._setup_menu()
        
        # Initialize with light theme styling
        self._set_theme("light")
    
    def _setup_ui(self):
        """Set up the main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)  # Use standard margins
        layout.setSpacing(10)  # Use standard spacing
        
        # Create separate panels to extract controls from
        self.class_panel = ClassPanel()
        self.class_panel.class_changed.connect(self._on_class_changed)
        self.controls_panel = ControlsPanel()
        self.controls_panel.generate_requested.connect(self._generate_groups)
        
        # Row 2: Main controls row
        controls_row = QHBoxLayout()
        controls_row.setSpacing(10)  # Use standard spacing
        
        # Class selector and new class controls
        controls_row.addWidget(QLabel("Class:"))
        controls_row.addWidget(self.class_panel.class_combo)
        controls_row.addWidget(self.class_panel.new_class_name)
        
        # Create new add class button since we need to extract it
        self.add_class_btn = QPushButton("Add class")
        self.add_class_btn.clicked.connect(self.class_panel._add_class)
        controls_row.addWidget(self.add_class_btn)
        
        # Add separator
        controls_row.addSpacing(20)  # Use standard section spacing
        
        # Students per group selector
        controls_row.addWidget(QLabel("Students/group:"))
        controls_row.addWidget(self.controls_panel.num_students)
        
        # Groups selector
        controls_row.addWidget(QLabel("Groups:"))
        controls_row.addWidget(self.controls_panel.num_groups)
        
        # Rounds selector  
        controls_row.addWidget(QLabel("Rounds:"))
        controls_row.addWidget(self.controls_panel.num_rounds)
        
        # Seed selector
        controls_row.addWidget(QLabel("Seed:"))
        controls_row.addWidget(self.controls_panel.random_seed)
        
        controls_row.addStretch()  # Push everything to the left
        layout.addLayout(controls_row)
        
        # Row 3: Action buttons row
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(10)  # Use standard spacing
        
        # Create new buttons since we need to extract them from panels
        self.delete_class_btn = QPushButton("Delete class")
        self.delete_class_btn.clicked.connect(self.class_panel._delete_class)
        buttons_row.addWidget(self.delete_class_btn)
        
        self.save_class_btn = QPushButton("Save class list")
        self.save_class_btn.clicked.connect(self.class_panel._save_class)
        buttons_row.addWidget(self.save_class_btn)
        
        self.generate_btn = QPushButton("Generate groups")
        self.generate_btn.clicked.connect(self._on_generate_clicked)
        buttons_row.addWidget(self.generate_btn)
        
        self.export_btn = QPushButton("Export plan as file")
        self.export_btn.clicked.connect(self._on_export_clicked)
        buttons_row.addWidget(self.export_btn)
        
        self.heatmap_btn = QPushButton("Show Co-occurrence Heatmap")
        self.heatmap_btn.clicked.connect(self._on_heatmap_clicked)
        buttons_row.addWidget(self.heatmap_btn)
        
        buttons_row.addStretch()  # Push everything to the left
        layout.addLayout(buttons_row)
        
        # Row 4: Main panels (horizontal splitter)
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side: Student list from class panel
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("Students:"))
        left_layout.addWidget(self.class_panel.student_list)
        
        # Right side: Output panel
        self.output_panel = OutputPanel()
        
        splitter.addWidget(left_widget)
        splitter.addWidget(self.output_panel)
        
        # Set initial splitter sizes (30% left, 70% right)
        splitter.setSizes([400, 800])
        
        layout.addWidget(splitter, 1)  # This takes up remaining space
        
        # Row 5: Student actions bar (spans entire width)
        self._create_student_actions_bar(layout)
    
    def _create_student_actions_bar(self, parent_layout):
        """Create the bottom action bar for student management."""
        from PySide6.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QLabel
        
        students_row = QHBoxLayout()
        
        self.student_input = QLineEdit()
        self.student_input.setPlaceholderText("Add student…")
        
        btn_add_student = QPushButton("Add")
        btn_add_student.clicked.connect(self._add_student)
        
        btn_all = QPushButton("Check all")
        btn_all.clicked.connect(self._check_all)
        
        btn_none = QPushButton("Uncheck all")
        btn_none.clicked.connect(self._uncheck_all)
        
        students_row.addWidget(QLabel("Student actions:"))
        students_row.addWidget(self.student_input, 2)
        students_row.addWidget(btn_add_student)
        students_row.addWidget(btn_all)
        students_row.addWidget(btn_none)
        students_row.addStretch()
        
        parent_layout.addLayout(students_row)
    
    def _add_student(self):
        """Add a student via the bottom bar."""
        self.class_panel.add_student_from_input(self.student_input.text())
        self.student_input.clear()
    
    def _check_all(self):
        """Check all students via the bottom bar."""
        self.class_panel.check_all_students()
    
    def _uncheck_all(self):
        """Uncheck all students via the bottom bar."""
        self.class_panel.uncheck_all_students()
    
    def _on_export_clicked(self):
        """Export the current plan to a text file."""
        schedule = self.get_last_schedule()
        if not schedule:
            QMessageBox.information(self, "Nothing", "Generate groups first.")
            return
        
        class_name = self.get_current_class_name()
        if not class_name:
            class_name = "groups"
        
        # Let user choose where to save
        from ..models import DATA_DIR, export_plan
        from PySide6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Export plan", 
            str(DATA_DIR / "plan.txt"), 
            "Text Files (*.txt)"
        )
        if not filename:
            return
        
        export_plan(filename, class_name, schedule)
        QMessageBox.information(
            self, "Exported",
            f"Saved to:\n{filename}"
        )
    
    def _on_heatmap_clicked(self):
        """Show the co-occurrence matrix."""
        self.show_cooccurrence_matrix()
    
    def _on_generate_clicked(self):
        """Handle generate button click."""
        # Get values from controls panel and generate groups
        students_per_group = self.controls_panel.num_students.value()
        num_groups = self.controls_panel.num_groups.value()
        num_rounds = self.controls_panel.num_rounds.value()
        seed = self.controls_panel.random_seed.value()
        
        self._generate_groups(students_per_group, num_groups, num_rounds, seed)
    
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
        
        #repo_action = help_menu.addAction("View Repository at GitHub")
        #repo_action.triggered.connect(self._open_repository)
        
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
        
        # Update the Layout constant
        Layout.FONT_SIZE = size
        
        # Set application-wide font
        font = QFont()
        font.setPointSize(size)
        QApplication.instance().setFont(font)
        
        # Regenerate and reapply stylesheets with new font size
        app = QApplication.instance()
        if self.current_theme == "dark":
            app.setStyleSheet(get_dark_stylesheet())
        else:
            app.setStyleSheet(get_light_stylesheet())
        
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
        lines.append(f"Quality: {overall_pct:.1f}% unique pairs")
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
        
        # Update current theme state
        self.current_theme = theme
        
        app = QApplication.instance()
        
        if theme == "dark":
            # Dark mode colors using constants
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(DarkTheme.WINDOW))
            palette.setColor(QPalette.WindowText, QColor(DarkTheme.WINDOW_TEXT))
            palette.setColor(QPalette.Base, QColor(DarkTheme.BASE))
            palette.setColor(QPalette.AlternateBase, QColor(DarkTheme.ALTERNATE_BASE))
            palette.setColor(QPalette.ToolTipBase, QColor(DarkTheme.TOOLTIP_BASE))
            palette.setColor(QPalette.ToolTipText, QColor(DarkTheme.TOOLTIP_TEXT))
            palette.setColor(QPalette.Text, QColor(DarkTheme.TEXT))
            palette.setColor(QPalette.Button, QColor(DarkTheme.BUTTON))
            palette.setColor(QPalette.ButtonText, QColor(DarkTheme.BUTTON_TEXT))
            palette.setColor(QPalette.BrightText, QColor(DarkTheme.BRIGHT_TEXT))
            palette.setColor(QPalette.Link, QColor(DarkTheme.LINK))
            palette.setColor(QPalette.Highlight, QColor(DarkTheme.HIGHLIGHT))
            palette.setColor(QPalette.HighlightedText, QColor(DarkTheme.HIGHLIGHTED_TEXT))
            app.setPalette(palette)
            
            # Apply dark theme stylesheet
            app.setStyleSheet(get_dark_stylesheet())
        else:
            # Light mode - reset to default with consistent layout
            app.setPalette(app.style().standardPalette())
            # Apply light theme stylesheet for consistent layout
            app.setStyleSheet(get_light_stylesheet())
    
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
