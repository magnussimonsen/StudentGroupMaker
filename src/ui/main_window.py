"""Main application window."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QMessageBox, QDialog, QPushButton, QLabel, QStackedWidget,
    QButtonGroup, QListWidget, QListWidgetItem, QDialogButtonBox,
    QFileDialog, QCheckBox, QAbstractItemView
)
from PySide6.QtCore import Qt, QStandardPaths
from pathlib import Path

from ..constants import APP_NAME, VERSION, REPOSITORY
from ..constants.colors_and_styling import (
    DARK_STYLESHEET, LIGHT_STYLESHEET, DarkTheme, LightTheme, Layout,
    get_dark_stylesheet, get_light_stylesheet
)
from ..core import schedule_groups, schedule_quality
from ..models import export_classes, import_classes, list_classes
from .widgets import (
    BreakTimerPanel, ClassPanel, ClassSeatingPanel, ControlsPanel, OutputPanel,
    RedCrossPanel, RedCrossStore,
)
from .widgets.red_cross_store import confirm_show_red_crosses
from .widgets.flow_layout import FlowLayout, make_group
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
        
        # Apply the font through the same path as the Font Size menu
        self._on_font_size_changed(Layout.FONT_SIZE)
    
    def _setup_ui(self):
        """Set up the main UI layout."""
        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        self.secondary_menubar = QWidget(central)
        self.secondary_menubar.setObjectName("secondaryMenuBar")
        # Wraps onto extra lines when the window is narrow
        self.secondary_menubar_layout = FlowLayout(self.secondary_menubar, spacing=10)
        # Same margins and spacing as the toolbar rows on the other pages, so the
        # first row of controls sits in the same place on every page
        self.secondary_menubar_layout.setContentsMargins(10, 10, 10, 6)
        central_layout.addWidget(self.secondary_menubar)

        self.mode_stack = QStackedWidget()
        central_layout.addWidget(self.mode_stack, 1)
        self.setCentralWidget(central)

        self.edit_classes_page = QWidget()
        self.mode_stack.addWidget(self.edit_classes_page)
        self.student_groups_page = QWidget()
        self.mode_stack.addWidget(self.student_groups_page)
        self.class_seating_page = QWidget()
        self.mode_stack.addWidget(self.class_seating_page)
        # Shared by the Red Crosses tab and the desks on the Class Seating page
        self.red_crosses = RedCrossStore(self)
        self.red_cross_panel = RedCrossPanel(self.red_crosses)
        self.mode_stack.addWidget(self.red_cross_panel)
        self.break_timer_panel = BreakTimerPanel()
        self.mode_stack.addWidget(self.break_timer_panel)
        
        layout = QVBoxLayout(self.student_groups_page)
        layout.setContentsMargins(10, 10, 10, 10)  # Use standard margins
        layout.setSpacing(6)  # Compact spacing between toolbar rows
        
        # Create separate panels to extract controls from
        self.class_panel = ClassPanel()
        self.class_panel.class_changed.connect(self._on_class_changed)
        self.class_panel.class_combo.setMinimumWidth(150)
        self.class_seating_panel = ClassSeatingPanel(self.red_crosses, self.class_seating_page)
        class_seating_layout = QVBoxLayout(self.class_seating_page)
        class_seating_layout.setContentsMargins(0, 0, 0, 0)
        class_seating_layout.addWidget(self.class_seating_panel)
        self.class_panel.students_changed.connect(self.class_seating_panel.set_class)
        self.class_panel.students_changed.connect(self.red_crosses.set_class)

        self.seating_controls = {}
        for label in ("Add row", "Remove row", "Add column", "Remove column",
                      "Export seating as PNG", "Show red crosses", "Flip classroom"):
            button = QPushButton(label)
            button.hide()
            self.secondary_menubar_layout.addWidget(button)
            self.seating_controls[label] = button

        self.seating_controls["Add row"].clicked.connect(
            self.class_seating_panel.add_row
        )
        self.seating_controls["Remove row"].clicked.connect(
            self.class_seating_panel.remove_row
        )
        self.seating_controls["Add column"].clicked.connect(
            self.class_seating_panel.add_column
        )
        self.seating_controls["Remove column"].clicked.connect(
            self.class_seating_panel.remove_column
        )
        self.seating_controls["Flip classroom"].setObjectName("flipClassroomButton")
        self.seating_controls["Flip classroom"].clicked.connect(
            self.class_seating_panel.flip_classroom
        )
        show_crosses_button = self.seating_controls["Show red crosses"]
        show_crosses_button.setObjectName("showRedCrossesButton")
        show_crosses_button.setCheckable(True)
        show_crosses_button.toggled.connect(self._on_show_crosses_toggled)
        self.seating_controls["Export seating as PNG"].clicked.connect(
            self.class_seating_panel.export_png
        )
        self.class_seating_panel.grid_dimensions_changed.connect(
            self._update_seating_controls
        )
        for set_class in (self.class_seating_panel.set_class, self.red_crosses.set_class):
            set_class(
                self.class_panel.get_current_class_name(),
                self.class_panel.get_student_records(),
            )

        self.controls_panel = ControlsPanel()
        self.controls_panel.generate_requested.connect(self._generate_groups)
        
        # Row 2: Main controls row (wraps onto extra lines when the window is narrow)
        controls_row = FlowLayout(spacing=10)
        
        # Class selector (the combo box is moved in here by _set_mode)
        self.groups_class_group = make_group(QLabel("Class:"))
        controls_row.addWidget(self.groups_class_group)

        # Students per group selector
        controls_row.addWidget(make_group(QLabel("Students per group:"), self.controls_panel.num_students))
        
        # Groups selector
        controls_row.addWidget(make_group(QLabel("Groups:"), self.controls_panel.num_groups))
        
        # Rounds selector  
        controls_row.addWidget(make_group(QLabel("Rounds:"), self.controls_panel.num_rounds))
        
        # Seed selector
        controls_row.addWidget(make_group(QLabel("Seed:"), self.controls_panel.random_seed))
        
        layout.addWidget(self._wrap_row(controls_row))
        
        # Row 3: Student actions and group action buttons (spans entire width)
        self.generate_btn = QPushButton("Generate groups")
        self.generate_btn.setObjectName("generateButton")  # Styled green in the stylesheet
        self.generate_btn.clicked.connect(self._on_generate_clicked)

        self.export_btn = QPushButton("Export plan as file")
        self.export_btn.clicked.connect(self._on_export_clicked)

        self.heatmap_btn = QPushButton("Show Co-occurrence Heatmap")
        self.heatmap_btn.clicked.connect(self._on_heatmap_clicked)

        self._create_student_actions_bar(
            layout, self.generate_btn, self.export_btn, self.heatmap_btn
        )

        # Row 4: Main panels (horizontal splitter)
        splitter = QSplitter(Qt.Horizontal)

        # Left side: Student list from class panel
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(QLabel("Students:"))
        left_layout.addWidget(self.class_panel.student_list)
        self.groups_students_layout = left_layout
        # Enforce a sensible minimum width so the list and names remain readable
        left_widget.setMinimumWidth(120)

        # Right side: Output panel
        self.output_panel = OutputPanel()
        # Enforce a sensible minimum width so the output doesn't collapse
        self.output_panel.setMinimumWidth(160)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(self.output_panel)

        # Prevent panels from being collapsed to zero size with the splitter
        splitter.setChildrenCollapsible(False)
        try:
            splitter.setCollapsible(0, False)
            splitter.setCollapsible(1, False)
        except AttributeError:
            # Older Qt: setChildrenCollapsible covers the behavior
            pass
        
        # Set initial splitter sizes (30% left, 70% right)
        splitter.setSizes([400, 800])
        
        layout.addWidget(splitter, 1)  # This takes up remaining space

        self._create_edit_classes_page()

    def _create_edit_classes_page(self):
        """Create the page for adding/deleting classes and students."""
        from PySide6.QtWidgets import QLineEdit

        layout = QVBoxLayout(self.edit_classes_page)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # Row 1: Class actions
        class_row = FlowLayout(spacing=10)

        # Class selector (the combo box is moved in here by _set_mode)
        self.edit_class_group = make_group(QLabel("Class:"))
        class_row.addWidget(self.edit_class_group)

        self.add_class_btn = QPushButton("Add class")
        self.add_class_btn.clicked.connect(self.class_panel._add_class)
        class_row.addWidget(make_group(self.class_panel.new_class_name, self.add_class_btn))

        self.delete_class_btn = QPushButton("Delete class")
        self.delete_class_btn.setObjectName("deleteClassButton")  # Styled red in the stylesheet
        self.delete_class_btn.clicked.connect(self.class_panel._delete_class)
        class_row.addWidget(self.delete_class_btn)

        layout.addWidget(self._wrap_row(class_row))

        # Row 2: Student actions
        students_row = FlowLayout(spacing=10)

        self.student_input = QLineEdit()
        self.student_input.setPlaceholderText("Add student…")
        self.student_input.setMinimumWidth(150)

        btn_add_student = QPushButton("Add student")
        btn_add_student.clicked.connect(self._add_student)

        btn_remove_student = QPushButton("Remove checked student(s)")
        btn_remove_student.clicked.connect(self._remove_checked_students)

        btn_all = QPushButton("Check all")
        btn_all.clicked.connect(self._check_all)

        btn_none = QPushButton("Uncheck all")
        btn_none.clicked.connect(self._uncheck_all)

        students_row.addWidget(make_group(self.student_input, btn_add_student))
        students_row.addWidget(btn_remove_student)
        students_row.addWidget(btn_all)
        students_row.addWidget(btn_none)

        layout.addWidget(self._wrap_row(students_row))

        # Row 3: Student list (the list widget is moved in here by _set_mode)
        layout.addWidget(QLabel("Students:"))
        self.edit_students_layout = QVBoxLayout()
        self.edit_students_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.edit_students_layout, 1)

    def _create_student_actions_bar(self, parent_layout, *extra_widgets):
        """Create the check/uncheck bar for student attendance, followed by extra_widgets."""
        students_row = FlowLayout(spacing=10)

        btn_all = QPushButton("Check all")
        btn_all.clicked.connect(self._check_all)

        btn_none = QPushButton("Uncheck all")
        btn_none.clicked.connect(self._uncheck_all)

        students_row.addWidget(QLabel("Student actions:"))
        students_row.addWidget(btn_all)
        students_row.addWidget(btn_none)
        for widget in extra_widgets:
            students_row.addWidget(widget)

        parent_layout.addWidget(self._wrap_row(students_row))
    
    @staticmethod
    def _wrap_row(flow_layout):
        """Put a flow layout in its own widget so the row grows taller as it wraps."""
        row = QWidget()
        row.setLayout(flow_layout)
        return row
    
    def _add_student(self):
        """Add a student via the student actions bar."""
        self.class_panel.add_student_from_input(self.student_input.text())
        self.student_input.clear()
    
    def _remove_checked_students(self):
        """Remove checked students via the student actions bar."""
        self.class_panel.remove_checked_students()
    
    def _check_all(self):
        """Check all students via the student actions bar."""
        self.class_panel.check_all_students()
    
    def _uncheck_all(self):
        """Uncheck all students via the student actions bar."""
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
        seed_value = self.controls_panel.random_seed.value()
        # Treat 0 as "totally random" by passing None to the scheduler
        seed = None if seed_value == 0 else seed_value
        
        self._generate_groups(students_per_group, num_groups, num_rounds, seed)
    
    def _setup_menu(self):
        """Set up the menu bar."""
        menubar = self.menuBar()

        self.mode_button_group = QButtonGroup(self)
        self.mode_button_group.setExclusive(True)

        self.mode_selector = QWidget(menubar)
        mode_selector_layout = QHBoxLayout(self.mode_selector)
        mode_selector_layout.setContentsMargins(4, 0, 4, 0)
        mode_selector_layout.setSpacing(4)

        self.export_classes_button = QPushButton("Export classes")
        self.export_classes_button.clicked.connect(self._show_export_classes_dialog)
        mode_selector_layout.addWidget(self.export_classes_button)

        self.import_classes_button = QPushButton("Import classes")
        self.import_classes_button.clicked.connect(self._on_import_classes_clicked)
        mode_selector_layout.addWidget(self.import_classes_button)

        self.edit_classes_button = QPushButton("Edit classes")
        self.edit_classes_button.setObjectName("workspaceModeButton")
        self.edit_classes_button.setCheckable(True)
        self.mode_button_group.addButton(self.edit_classes_button)
        self.edit_classes_button.clicked.connect(
            lambda: self._set_mode("edit_classes")
        )
        mode_selector_layout.addWidget(self.edit_classes_button)

        self.student_groups_button = QPushButton("Student Groups")
        self.student_groups_button.setObjectName("workspaceModeButton")
        self.student_groups_button.setCheckable(True)
        self.student_groups_button.setChecked(True)
        self.mode_button_group.addButton(self.student_groups_button)
        self.student_groups_button.clicked.connect(
            lambda: self._set_mode("student_groups")
        )
        mode_selector_layout.addWidget(self.student_groups_button)

        self.class_seating_button = QPushButton("Class Seating")
        self.class_seating_button.setObjectName("workspaceModeButton")
        self.class_seating_button.setCheckable(True)
        self.mode_button_group.addButton(self.class_seating_button)
        self.class_seating_button.clicked.connect(
            lambda: self._set_mode("class_seating")
        )
        mode_selector_layout.addWidget(self.class_seating_button)

        self.red_crosses_button = QPushButton("Red Crosses")
        self.red_crosses_button.setObjectName("workspaceModeButton")
        self.red_crosses_button.setCheckable(True)
        self.mode_button_group.addButton(self.red_crosses_button)
        self.red_crosses_button.clicked.connect(self._on_red_crosses_clicked)
        mode_selector_layout.addWidget(self.red_crosses_button)

        self.break_timer_button = QPushButton("Break Timer")
        self.break_timer_button.setObjectName("workspaceModeButton")
        self.break_timer_button.setCheckable(True)
        self.mode_button_group.addButton(self.break_timer_button)
        self.break_timer_button.clicked.connect(
            lambda: self._set_mode("break_timer")
        )
        mode_selector_layout.addWidget(self.break_timer_button)
        
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

        menubar.setCornerWidget(self.mode_selector, Qt.TopRightCorner)

        self.mode_buttons = {
            "edit_classes": self.edit_classes_button,
            "student_groups": self.student_groups_button,
            "class_seating": self.class_seating_button,
            "red_crosses": self.red_crosses_button,
            "break_timer": self.break_timer_button,
        }
        self._set_mode("student_groups")

    def _show_export_classes_dialog(self):
        """Let the user choose classes for a single Desktop export bundle."""
        classes = list_classes()
        if not classes:
            QMessageBox.information(self, "Export classes", "There are no classes to export.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Export classes")
        dialog.setMinimumWidth(320)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Select the classes to include:"))

        class_list = QListWidget(dialog)
        class_list.setSelectionMode(QAbstractItemView.NoSelection)
        for class_name in classes:
            item = QListWidgetItem(class_name, class_list)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
        layout.addWidget(class_list)

        select_all = QCheckBox("Select all", dialog)
        select_all.setChecked(True)
        select_all.setTristate(True)

        def set_class_checks(state: int):
            if state == Qt.PartiallyChecked:
                return
            class_list.blockSignals(True)
            check_state = Qt.Checked if state == Qt.Checked else Qt.Unchecked
            for index in range(class_list.count()):
                class_list.item(index).setCheckState(check_state)
            class_list.blockSignals(False)

        def update_select_all(_item: QListWidgetItem):
            checked_count = sum(
                class_list.item(index).checkState() == Qt.Checked
                for index in range(class_list.count())
            )
            if checked_count == 0:
                state = Qt.Unchecked
            elif checked_count == class_list.count():
                state = Qt.Checked
            else:
                state = Qt.PartiallyChecked
            select_all.blockSignals(True)
            select_all.setCheckState(state)
            select_all.blockSignals(False)

        select_all.stateChanged.connect(set_class_checks)
        class_list.itemChanged.connect(update_select_all)
        layout.addWidget(select_all)

        button_box = QDialogButtonBox(dialog)
        button_box.addButton("Export to Desktop", QDialogButtonBox.AcceptRole)
        button_box.addButton(QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() != QDialog.Accepted:
            return
        selected_classes = [
            class_list.item(index).text()
            for index in range(class_list.count())
            if class_list.item(index).checkState() == Qt.Checked
        ]
        if not selected_classes:
            QMessageBox.information(
                self, "Export classes", "Select at least one class to export."
            )
            return

        desktop = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        if not desktop or not Path(desktop).is_dir():
            QMessageBox.warning(
                self, "Export classes", "The Desktop folder could not be found."
            )
            return
        destination = Path(desktop) / "GroupMaker_classes.json"
        if destination.exists():
            reply = QMessageBox.question(
                self,
                "Replace export file",
                f"'{destination.name}' already exists on the Desktop. Replace it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        try:
            export_classes(selected_classes, destination)
        except (OSError, ValueError) as error:
            QMessageBox.critical(self, "Export failed", str(error))
            return
        QMessageBox.information(
            self, "Classes exported", f"Saved {len(selected_classes)} class(es) to:\n{destination}"
        )

    def _on_import_classes_clicked(self):
        """Import classes and their saved seating charts from a JSON bundle."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import classes",
            "",
            "GroupMaker class exports (*.json);;JSON files (*.json)",
        )
        if not filename:
            return
        try:
            imported = import_classes(Path(filename))
        except (OSError, ValueError) as error:
            QMessageBox.critical(self, "Import failed", str(error))
            return

        first_imported_name = imported[0][1]
        self.class_panel.refresh_classes(first_imported_name)
        details = "\n".join(
            f"{source} imported as {destination}"
            if source != destination
            else f"{source} imported"
            for source, destination in imported
        )
        QMessageBox.information(
            self, "Classes imported", f"Imported {len(imported)} class(es):\n{details}"
        )

    def _on_red_crosses_clicked(self):
        """Open the Red Crosses tab after confirming, since the class may see the screen."""
        if self.current_mode != "red_crosses" and not confirm_show_red_crosses(self):
            self.mode_buttons[self.current_mode].setChecked(True)
            return
        self._set_mode("red_crosses")

    def _set_mode(self, mode: str):
        """Switch the main view and show controls belonging to the selected mode."""
        self.current_mode = mode
        is_class_seating = mode == "class_seating"
        pages = {
            "edit_classes": self.edit_classes_page,
            "student_groups": self.student_groups_page,
            "class_seating": self.class_seating_page,
            "red_crosses": self.red_cross_panel,
            "break_timer": self.break_timer_panel,
        }
        self.mode_stack.setCurrentWidget(pages[mode])
        if mode == "break_timer":
            # The timer page has no class selector or student list
            self.secondary_menubar.setVisible(False)
            return

        # The class combo and student list are shared, so move them onto the active page
        combo = self.class_panel.class_combo
        combo_slots = {
            "edit_classes": (self.edit_class_group.layout(), 1),
            "student_groups": (self.groups_class_group.layout(), 1),
            "class_seating": (self.secondary_menubar_layout, 0),
            "red_crosses": (self.red_cross_panel.class_group.layout(), 1),
        }
        for slot_layout, _ in combo_slots.values():
            slot_layout.removeWidget(combo)
        slot_layout, index = combo_slots[mode]
        slot_layout.insertWidget(index, combo)

        student_list = self.class_panel.student_list
        self.groups_students_layout.removeWidget(student_list)
        self.edit_students_layout.removeWidget(student_list)
        if mode == "edit_classes":
            self.edit_students_layout.addWidget(student_list)
        else:
            self.groups_students_layout.addWidget(student_list)

        self.secondary_menubar.setVisible(is_class_seating)
        for button in self.seating_controls.values():
            button.setVisible(is_class_seating)

    def _update_seating_controls(self, rows: int, columns: int):
        """Enable dimension controls only when the grid can change that way."""
        self.seating_controls["Add row"].setEnabled(rows < 15)
        self.seating_controls["Remove row"].setEnabled(rows > 1)
        self.seating_controls["Add column"].setEnabled(columns < 12)
        self.seating_controls["Remove column"].setEnabled(columns > 1)

    def _on_show_crosses_toggled(self, checked: bool):
        """Show or hide red crosses, unchecking the button if the teacher cancels."""
        shown = self.class_seating_panel.set_show_crosses(checked)
        if shown != checked:
            button = self.seating_controls["Show red crosses"]
            button.blockSignals(True)
            button.setChecked(shown)
            button.blockSignals(False)

    def _on_class_changed(self, name: str):
        """Handle class selection change."""
        # Clear output when switching classes
        self.output_panel.clear()
    
    def _on_font_size_changed(self, size: int):
        """Handle font size change - applies globally to entire application."""
        # Update the Layout constant
        Layout.FONT_SIZE = size

        # Reapply the theme; it regenerates the stylesheet and sets the app font
        self._set_theme(self.current_theme)

        # Also explicitly update output panel
        self.output_panel.set_font_size(size)

        # Spin boxes are naturally a little taller than buttons and combo boxes,
        # which made toolbar rows differ in height between pages
        row_height = self.generate_btn.sizeHint().height()
        for spinbox in (self.controls_panel.num_students, self.controls_panel.num_groups,
                        self.controls_panel.num_rounds, self.controls_panel.random_seed):
            spinbox.setFixedHeight(row_height)
    
    def _generate_groups(self, students_per_group: int, num_groups: int, 
                        num_rounds: int, seed: int | None):
        """Generate groups based on current settings."""
        present = self.class_panel.get_present_students()
        
        if not present:
            QMessageBox.warning(self, "No students", "No students are checked as present.")
            return

        # Validate: cannot create more groups than students (would create empty groups)
        if num_groups > len(present):
            QMessageBox.warning(
                self,
                "Too many groups",
                f"You selected {num_groups} groups but only {len(present)} student(s) are present.\n"
                "Reduce the number of groups or add more students."
            )
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
        
        # Format output as a simple one-column header
        lines = []
        lines.append(f"Class:\t{self.class_panel.get_current_class_name()}")
        lines.append(f"Students:\t{len(present)}")
        lines.append(f"Groups per round:\t{num_groups}")
        lines.append(f"Students per group:\t{students_per_group}")
        lines.append(f"Rounds:\t{num_rounds}")
        lines.append(f"Quality:\t{overall_pct:.1f}% unique pairs")
        lines.append(f"Random seed:\t{seed if seed is not None else 'Random (0)'}")
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
        from PySide6.QtGui import QPalette, QColor, QFont
        from PySide6.QtCore import Qt

        # Update current theme state
        self.current_theme = theme
        
        app = QApplication.instance()
        
        if theme == "dark":
            # Dark mode colors using constants
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(DarkTheme.MAIN_WINDOW_COLOR))
            palette.setColor(QPalette.WindowText, QColor(DarkTheme.TEXT_COLOR))
            palette.setColor(QPalette.Base, QColor(DarkTheme.BASE_COLOR))
            palette.setColor(QPalette.AlternateBase, QColor(DarkTheme.MAIN_WINDOW_COLOR))
            palette.setColor(QPalette.ToolTipBase, QColor(DarkTheme.TOOLTIP_BG_COLOR))
            palette.setColor(QPalette.ToolTipText, QColor(DarkTheme.TOOLTIP_TEXT_COLOR))
            palette.setColor(QPalette.Text, QColor(DarkTheme.TEXT_COLOR))
            palette.setColor(QPalette.Button, QColor(DarkTheme.BUTTON_BG_COLOR))
            palette.setColor(QPalette.ButtonText, QColor(DarkTheme.TEXT_COLOR))
            palette.setColor(QPalette.BrightText, QColor(DarkTheme.BRIGHT_TEXT_COLOR))
            palette.setColor(QPalette.Link, QColor(DarkTheme.LINK_COLOR))
            palette.setColor(QPalette.Highlight, QColor(DarkTheme.HIGHLIGHT_BG_COLOR))
            palette.setColor(QPalette.HighlightedText, QColor(DarkTheme.HIGHLIGHT_TEXT_COLOR))
            app.setPalette(palette)
            
            # Apply dark theme stylesheet
            app.setStyleSheet(get_dark_stylesheet())
        else:
            # Light mode - build a palette from LightTheme constants to avoid OS/Qt dark auto palette
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(LightTheme.MAIN_WINDOW_COLOR))
            palette.setColor(QPalette.WindowText, QColor(LightTheme.TEXT_COLOR))
            palette.setColor(QPalette.Base, QColor(LightTheme.BASE_COLOR))
            palette.setColor(QPalette.AlternateBase, QColor(LightTheme.MAIN_WINDOW_COLOR))
            palette.setColor(QPalette.ToolTipBase, QColor(LightTheme.TOOLTIP_BG_COLOR))
            palette.setColor(QPalette.ToolTipText, QColor(LightTheme.TOOLTIP_TEXT_COLOR))
            palette.setColor(QPalette.Text, QColor(LightTheme.TEXT_COLOR))
            palette.setColor(QPalette.Button, QColor(LightTheme.BUTTON_BG_COLOR))
            palette.setColor(QPalette.ButtonText, QColor(LightTheme.TEXT_COLOR))
            palette.setColor(QPalette.BrightText, QColor(LightTheme.BRIGHT_TEXT_COLOR))
            palette.setColor(QPalette.Link, QColor(LightTheme.LINK_COLOR))
            palette.setColor(QPalette.Highlight, QColor(LightTheme.HIGHLIGHT_BG_COLOR))
            palette.setColor(QPalette.HighlightedText, QColor(LightTheme.HIGHLIGHT_TEXT_COLOR))
            app.setPalette(palette)

            # Apply light theme stylesheet for consistent layout and selection visuals
            app.setStyleSheet(get_light_stylesheet())

        # Set the app font after the stylesheet: setStyleSheet restores Qt's
        # per-class platform fonts (e.g. 9pt for item views such as the class
        # dropdown list on Windows), and setFont clears them again.
        font = QFont()
        font.setPointSize(Layout.FONT_SIZE)
        app.setFont(font)

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
        from PySide6.QtWidgets import QSizePolicy

        names, matrix = build_pair_matrix(self.last_schedule)

        # Create dialog to display matrix as a free-floating, resizable window
        dialog = QDialog(self)
        dialog.setWindowTitle("Student Co-occurrence Matrix")
        dialog.resize(900, 800)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        dialog.setWindowModality(Qt.NonModal)

        layout = QVBoxLayout()

        # Create and add matplotlib figure
        fig = create_heatmap_figure(names, matrix)
        canvas = FigureCanvas(fig)
        # Let the canvas expand/shrink with the dialog size
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(canvas)

        # Add close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        # Show as non-modal so it can be moved/resized freely without blocking the main window
        dialog.show()
