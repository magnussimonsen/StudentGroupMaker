"""
Color schemes and styling constants for GroupMaker application.

This module contains all color definitions and styling constants used throughout
the application for both light and dark themes.
"""

# Dark Theme Colors
class DarkTheme:
    """Dark theme color constants."""
     
    # Base color palette
    BASE_COLOR = '#353535'            # Input fields, text areas
    MAIN_WINDOW_COLOR = '#2a2a2a'     # Main window background
    BUTTON_BG_COLOR = '#3d3d3d'       # Buttons
    BORDER_COLOR = '#555555'          # Borders
    
    # Text colors
    TEXT_COLOR = "#ffffff"            # Primary text
    TEXT_PLACEHOLDER_COLOR = "#aaaaaa"  # Placeholder text
    
    # Universal hover color (used for all interactive elements)
    HOVER_BG_COLOR = "#007cda"         # Universal hover background color
    TEXT_COLOR_HOVER = "#ffffff"      # Universal hover text color
    BORDER_COLOR_HOVER = "#005393"    # Hover state borders
    
    # Button pressed/active state
    BUTTON_PRESSED_BG_COLOR = "#1e6bb8"  # Button pressed/active background (darker blue)
    BUTTON_PRESSED_TEXT_COLOR = "#ffffff"  # Button pressed/active text

    # Panel resize handle (QSplitter handle)
    SPLITTER_HANDLE_COLOR = MAIN_WINDOW_COLOR  # Color of the splitter handle
    SPLITTER_HANDLE_COLOR_HOVER = HOVER_BG_COLOR  # Color of the splitter handle on hover

    # Special purpose colors
    HIGHLIGHT_BG_COLOR = "#2a82da"    # Selection/highlight background
    HIGHLIGHT_TEXT_COLOR = "#ffffff"  # Text on highlighted background
    LINK_COLOR = "#2a82da"            # Links
    BRIGHT_TEXT_COLOR = "#ff0000"     # Error/warning text
    SEPARATOR_COLOR = "#555555"       # Menu separators
    
    # Tooltip colors
    TOOLTIP_BG_COLOR = "#191919"      # Tooltip background
    TOOLTIP_TEXT_COLOR = "#ffffff"    # Tooltip text
    
    # Dropdown specific colors
    DROPDOWN_BG_COLOR = "#2a2a2a"     # Dropdown background (same as main window)
    DROPDOWN_BORDER_COLOR = BORDER_COLOR  # Dropdown borders

    

class LightTheme:
    """Light theme color constants."""
    
    # Base color palette
    BASE_COLOR = '#ffffff'            # Input fields, text areas
    MAIN_WINDOW_COLOR = '#f0f0f0'     # Main window background
    BUTTON_BG_COLOR = '#e0e0e0'       # Buttons
    BORDER_COLOR = '#c0c0c0'          # Borders
    
    # Text colors
    TEXT_COLOR = "#000000"            # Primary text
    TEXT_PLACEHOLDER_COLOR = "#888888"  # Placeholder text
    
    # Universal hover color (used for all interactive elements)
    HOVER_BG_COLOR = "#007cda"        # Universal hover background color (Windows blue)
    TEXT_COLOR_HOVER = "#ffffff"      # Universal hover text color
    BORDER_COLOR_HOVER = HOVER_BG_COLOR    # Hover state borders
    
    # Button pressed/active state
    BUTTON_PRESSED_BG_COLOR = "#005393"  # Button pressed/active background (darker blue)
    BUTTON_PRESSED_TEXT_COLOR = "#ffffff"  # Button pressed/active text

    # Panel resize handle (QSplitter handle)
    SPLITTER_HANDLE_COLOR = MAIN_WINDOW_COLOR  # Color of the splitter handle
    SPLITTER_HANDLE_COLOR_HOVER = HOVER_BG_COLOR  # Color of the splitter handle on hover
    
    # Special purpose colors
    HIGHLIGHT_BG_COLOR = HOVER_BG_COLOR    # Selection/highlight background
    HIGHLIGHT_TEXT_COLOR = "#ffffff"  # Text on highlighted background
    LINK_COLOR = "#0078d4"            # Links (Windows blue)
    BRIGHT_TEXT_COLOR = "#d13438"     # Error/warning text (red)
    SEPARATOR_COLOR = "#e1e1e1"       # Menu separators
    
    # Tooltip colors
    TOOLTIP_BG_COLOR = "#ffffe1"      # Tooltip background (light yellow)
    TOOLTIP_TEXT_COLOR = "#000000"    # Tooltip text
    
    # Dropdown specific colors
    DROPDOWN_BG_COLOR = "#ffffff"     # Dropdown background (white)
    DROPDOWN_BORDER_COLOR = BORDER_COLOR  # Dropdown borders


# Layout and Spacing Constants
class Layout:
    """Layout and spacing constants."""
    # Menu bar spacing
    MENU_ITEM_PADDING = "4px 8px"
    MENU_ITEM_MARGIN = "0px"
    
    # Widget spacing
    WIDGET_SPACING_TIGHT = ""
    WIDGET_SPACING_NORMAL =""
    WIDGET_SPACING_LOOSE = ""
    WIDGET_SPACING = ""          # Standard spacing between widgets
    SECTION_SPACING = ""         # Spacing between sections
    
    # Margins and padding
    PANEL_MARGIN = ""             # Tight layout for panels
    CONTENT_MARGIN = ""
    CONTAINER_PADDING = ""       # Padding around main containers
    SECTION_PADDING = ""         # Padding around sections
    DROPDOWN_PADDING = "4px"     # Dropdown menu padding
    
    # Widget Heights (for consistent alignment)
    WIDGET_HEIGHT = ""  # Standard height for buttons, text fields, combo boxes ("" = OS default)
    BUTTON_HEIGHT = ""  # Button height
    INPUT_HEIGHT = ""   # Text fields, combo boxes, spin boxes
    LABEL_HEIGHT = ""   # Labels
    
    # Font Size (dynamic - will be updated by application)
    FONT_SIZE = 11      # Default font size in points


# Style sheet templates
def get_dark_stylesheet():
    """Generate dark theme stylesheet with current font size."""
    return f"""
QPushButton {{
    background-color: {DarkTheme.BUTTON_BG_COLOR};
    color: {DarkTheme.TEXT_COLOR};
    border: 1px solid {DarkTheme.BORDER_COLOR};
    padding: 6px 12px;
    border-radius: 3px;
    font-size: {Layout.FONT_SIZE}pt;
    {f"min-height: {Layout.BUTTON_HEIGHT}px; max-height: {Layout.BUTTON_HEIGHT}px;" if Layout.BUTTON_HEIGHT else ""}
}}
QPushButton:hover {{
    background-color: {DarkTheme.HOVER_BG_COLOR};
    border: 1px solid {DarkTheme.BORDER_COLOR_HOVER};
    color: {DarkTheme.TEXT_COLOR_HOVER};
}}

QPushButton:pressed {{
    background-color: {DarkTheme.BUTTON_PRESSED_BG_COLOR};
    border: 1px solid {DarkTheme.BORDER_COLOR_HOVER};
    color: {DarkTheme.BUTTON_PRESSED_TEXT_COLOR};
}}

QComboBox {{
    background-color: {DarkTheme.DROPDOWN_BG_COLOR};
    color: {DarkTheme.TEXT_COLOR};
    border: 1px solid {DarkTheme.DROPDOWN_BORDER_COLOR};
    font-size: {Layout.FONT_SIZE}pt;
    padding: 4px;
}}

QLineEdit {{
    background-color: {DarkTheme.BASE_COLOR};
    color: {DarkTheme.TEXT_COLOR};
    border: 1px solid {DarkTheme.BORDER_COLOR};
    padding: 4px;
    border-radius: 3px;
    font-size: {Layout.FONT_SIZE}pt;
    {f"min-height: {Layout.INPUT_HEIGHT}px; max-height: {Layout.INPUT_HEIGHT}px;" if Layout.INPUT_HEIGHT else ""}
}}

QSpinBox {{
    font-size: {Layout.FONT_SIZE}pt;
}}

QLabel {{
    color: {DarkTheme.TEXT_COLOR};
    font-size: {Layout.FONT_SIZE}pt;
    {f"min-height: {Layout.LABEL_HEIGHT}px;" if Layout.LABEL_HEIGHT else ""}
}}

QComboBox:hover {{
    border: 1px solid {DarkTheme.BORDER_COLOR_HOVER};
}}
QComboBox QAbstractItemView {{
    background-color: {DarkTheme.DROPDOWN_BG_COLOR};
    color: {DarkTheme.TEXT_COLOR};
    selection-background-color: {DarkTheme.HIGHLIGHT_BG_COLOR};
    selection-color: {DarkTheme.HIGHLIGHT_TEXT_COLOR};
    border: 1px solid {DarkTheme.DROPDOWN_BORDER_COLOR};
}}
QComboBox QAbstractItemView::item {{
    padding: 4px;
    background-color: {DarkTheme.DROPDOWN_BG_COLOR};
    color: {DarkTheme.TEXT_COLOR};
}}
QComboBox QAbstractItemView::item:selected {{
    background-color: {DarkTheme.HIGHLIGHT_BG_COLOR};
    color: {DarkTheme.HIGHLIGHT_TEXT_COLOR};
}}
QComboBox QAbstractItemView::item:hover {{
    background-color: {DarkTheme.HOVER_BG_COLOR};
    color: {DarkTheme.TEXT_COLOR_HOVER};
}}

/* Ensure consistent selection highlight across list/tree/table views */
QAbstractItemView {{
    selection-background-color: {DarkTheme.HIGHLIGHT_BG_COLOR};
    selection-color: {DarkTheme.HIGHLIGHT_TEXT_COLOR};
}}
QAbstractItemView::item:selected:active {{
    background-color: {DarkTheme.HIGHLIGHT_BG_COLOR};
    color: {DarkTheme.HIGHLIGHT_TEXT_COLOR};
}}
QAbstractItemView::item:selected:!active {{
    background-color: {DarkTheme.HIGHLIGHT_BG_COLOR};
    color: {DarkTheme.HIGHLIGHT_TEXT_COLOR};
}}
QListWidget::item:hover, QListView::item:hover, QTreeView::item:hover {{
    background-color: {DarkTheme.HOVER_BG_COLOR};
    color: {DarkTheme.TEXT_COLOR_HOVER};
}}

QMenuBar {{
    background-color: {DarkTheme.MAIN_WINDOW_COLOR};
    color: {DarkTheme.TEXT_COLOR};
    border-bottom: 1px solid {DarkTheme.BORDER_COLOR};
    spacing: {Layout.WIDGET_SPACING_TIGHT}px;
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenuBar::item {{
    background-color: transparent;
    padding: {Layout.MENU_ITEM_PADDING};
    margin: {Layout.MENU_ITEM_MARGIN};
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenuBar::item:selected {{
    background-color: {DarkTheme.HOVER_BG_COLOR};
    color: {DarkTheme.TEXT_COLOR_HOVER};
}}
QMenuBar::item:pressed {{
    background-color: {DarkTheme.HIGHLIGHT_BG_COLOR};
    color: {DarkTheme.TEXT_COLOR_HOVER};
}}

QMenu {{
    background-color: {DarkTheme.DROPDOWN_BG_COLOR};
    color: {DarkTheme.TEXT_COLOR};
    border: 1px solid {DarkTheme.DROPDOWN_BORDER_COLOR};
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenu::item {{
    padding: 6px 20px;
    background-color: transparent;
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenu::item:selected {{
    background-color: {DarkTheme.HIGHLIGHT_BG_COLOR};
    color: {DarkTheme.TEXT_COLOR_HOVER};
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenuBar::item:hover {{
    background-color: {DarkTheme.HOVER_BG_COLOR};
    color: {DarkTheme.TEXT_COLOR_HOVER};
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenu::separator {{
    height: 1px;
    background-color: {DarkTheme.SEPARATOR_COLOR};
    margin: 2px 0px;
}}

QSplitter::handle {{
    background-color: {DarkTheme.SPLITTER_HANDLE_COLOR};
    image: none;  /* Ensure Windows style doesn't paint over background */
}}
QSplitter::handle:horizontal {{
    width: 8px;
}}
QSplitter::handle:vertical {{
    height: 8px;
}}
QSplitter::handle:hover,
QSplitter::handle:horizontal:hover,
QSplitter::handle:vertical:hover {{
    background-color: {DarkTheme.SPLITTER_HANDLE_COLOR_HOVER};
}}
QSplitter::handle:pressed {{
    background-color: {DarkTheme.HOVER_BG_COLOR};
}}
"""


def get_light_stylesheet():
    """Generate light theme stylesheet with current font size."""
    return f"""
QPushButton {{
    background-color: {LightTheme.BUTTON_BG_COLOR};
    color: {LightTheme.TEXT_COLOR};
    border: 1px solid {LightTheme.BORDER_COLOR};
    {f"min-height: {Layout.BUTTON_HEIGHT}px; max-height: {Layout.BUTTON_HEIGHT}px;" if Layout.BUTTON_HEIGHT else ""}
    padding: 6px 12px;
    border-radius: 3px;
    font-size: {Layout.FONT_SIZE}pt;
}}
QPushButton:hover {{
    background-color: {LightTheme.HOVER_BG_COLOR};
    border: 1px solid {LightTheme.BORDER_COLOR_HOVER};
    color: {LightTheme.TEXT_COLOR_HOVER};
}}
QPushButton:pressed {{
    background-color: {LightTheme.BUTTON_PRESSED_BG_COLOR};
    border: 1px solid {LightTheme.BORDER_COLOR_HOVER};
    color: {LightTheme.BUTTON_PRESSED_TEXT_COLOR};
}}

QComboBox {{
    background-color: {LightTheme.DROPDOWN_BG_COLOR};
    color: {LightTheme.TEXT_COLOR};
    border: 1px solid {LightTheme.DROPDOWN_BORDER_COLOR};
    font-size: {Layout.FONT_SIZE}pt;
    padding: 4px;
}}

QLineEdit {{
    background-color: {LightTheme.BASE_COLOR};
    color: {LightTheme.TEXT_COLOR};
    border: 1px solid {LightTheme.BORDER_COLOR};
    {f"min-height: {Layout.INPUT_HEIGHT}px; max-height: {Layout.INPUT_HEIGHT}px;" if Layout.INPUT_HEIGHT else ""}
    padding: 4px;
    border-radius: 3px;
    font-size: {Layout.FONT_SIZE}pt;
}}

QSpinBox {{
    font-size: {Layout.FONT_SIZE}pt;
}}

QLabel {{
    color: {LightTheme.TEXT_COLOR};
    font-size: {Layout.FONT_SIZE}pt;
    {f"min-height: {Layout.LABEL_HEIGHT}px;" if Layout.LABEL_HEIGHT else ""}
}}

QComboBox:hover {{
    border: 1px solid {LightTheme.BORDER_COLOR_HOVER};
}}
QComboBox QAbstractItemView {{
    background-color: {LightTheme.DROPDOWN_BG_COLOR};
    color: {LightTheme.TEXT_COLOR};
    selection-background-color: {LightTheme.HIGHLIGHT_BG_COLOR};
    selection-color: {LightTheme.HIGHLIGHT_TEXT_COLOR};
    border: 1px solid {LightTheme.DROPDOWN_BORDER_COLOR};
}}
QComboBox QAbstractItemView::item {{
    padding: 4px;
    background-color: {LightTheme.DROPDOWN_BG_COLOR};
    color: {LightTheme.TEXT_COLOR};
}}
QComboBox QAbstractItemView::item:selected {{
    background-color: {LightTheme.HIGHLIGHT_BG_COLOR};
    color: {LightTheme.HIGHLIGHT_TEXT_COLOR};
}}
QComboBox QAbstractItemView::item:hover {{
    background-color: {LightTheme.HOVER_BG_COLOR};
    color: {LightTheme.TEXT_COLOR_HOVER};
}}

/* Ensure consistent selection highlight across list/tree/table views */
QAbstractItemView {{
    selection-background-color: {LightTheme.HIGHLIGHT_BG_COLOR};
    selection-color: {LightTheme.HIGHLIGHT_TEXT_COLOR};
}}
QAbstractItemView::item:selected:active {{
    background-color: {LightTheme.HIGHLIGHT_BG_COLOR};
    color: {LightTheme.HIGHLIGHT_TEXT_COLOR};
}}
QAbstractItemView::item:selected:!active {{
    background-color: {LightTheme.HIGHLIGHT_BG_COLOR};
    color: {LightTheme.HIGHLIGHT_TEXT_COLOR};
}}
QListWidget::item:hover, QListView::item:hover, QTreeView::item:hover {{
    background-color: {LightTheme.HOVER_BG_COLOR};
    color: {LightTheme.TEXT_COLOR_HOVER};
}}

QMenuBar {{
    background-color: {LightTheme.MAIN_WINDOW_COLOR};
    color: {LightTheme.TEXT_COLOR};
    border-bottom: 1px solid {LightTheme.BORDER_COLOR};
    spacing: {Layout.WIDGET_SPACING_TIGHT}px;
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenuBar::item {{
    background-color: transparent;
    color: {LightTheme.TEXT_COLOR};
    padding: {Layout.MENU_ITEM_PADDING};
    margin: {Layout.MENU_ITEM_MARGIN};
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenuBar::item:selected {{
    background-color: {LightTheme.HOVER_BG_COLOR};
    color: {LightTheme.TEXT_COLOR_HOVER};
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenuBar::item:pressed {{
    background-color: {LightTheme.BUTTON_PRESSED_BG_COLOR};
    color: {LightTheme.BUTTON_PRESSED_TEXT_COLOR};
    font-size: {Layout.FONT_SIZE}pt;
}}

QMenu {{
    background-color: {LightTheme.DROPDOWN_BG_COLOR};
    color: {LightTheme.TEXT_COLOR};
    border: 1px solid {LightTheme.DROPDOWN_BORDER_COLOR};
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenu::item {{
    padding: 6px 20px;
    background-color: transparent;
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenu::item:selected {{
    background-color: {LightTheme.HIGHLIGHT_BG_COLOR};
    color: {LightTheme.TEXT_COLOR_HOVER};
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenuBar::item:hover {{
    background-color: {LightTheme.HOVER_BG_COLOR};
    color: {LightTheme.TEXT_COLOR_HOVER};
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenu::separator {{
    height: 1px;
    background-color: {LightTheme.SEPARATOR_COLOR};
    margin: 2px 0px;
}}

QSplitter::handle {{
    background-color: {LightTheme.SPLITTER_HANDLE_COLOR};
    image: none;  /* Ensure Windows style doesn't paint over background */
}}
QSplitter::handle:horizontal {{
    width: 8px;
}}
QSplitter::handle:vertical {{
    height: 8px;
}}
QSplitter::handle:hover,
QSplitter::handle:horizontal:hover,
QSplitter::handle:vertical:hover {{
    background-color: {LightTheme.SPLITTER_HANDLE_COLOR_HOVER};
}}
QSplitter::handle:pressed {{
    background-color: {LightTheme.HOVER_BG_COLOR};
}}
"""


# Backwards compatibility - use the functions to generate default stylesheets
DARK_STYLESHEET = get_dark_stylesheet()
LIGHT_STYLESHEET = get_light_stylesheet()