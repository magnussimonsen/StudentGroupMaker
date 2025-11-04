"""
Color schemes and styling constants for GroupMaker application.

This module contains all color definitions and styling constants used throughout
the application for both light and dark themes.
"""

# Dark Theme Colors
class DarkTheme:
    """Dark theme color constants."""
    # Main background colors
    WINDOW = "#353535"          # Main window background
    BASE = "#232323"            # Input fields, text areas
    ALTERNATE_BASE = "#353535"  # Alternate background
    
    # Text colors
    TEXT = "#ffffff"            # Primary text
    WINDOW_TEXT = "#ffffff"     # Window text
    BUTTON_TEXT = "#ffffff"     # Button text
    
    # Interactive elements
    BUTTON = "#353535"          # Button background
    BUTTON_HOVER = "#2a82da"     # Button hover state
    HIGHLIGHT = "#2a82da"       # Selection/highlight color
    HIGHLIGHTED_TEXT = "#ffffff" # Text on highlighted background
    
    # Universal hover color (used for all interactive elements)
    HOVER_BG = "#2a82da"        # Universal hover background color
    HOVER_TEXT = "#ffffff"      # Universal hover text color
    
    # Borders and lines
    BORDER = "#555555"          # Standard borders
    BORDER_HOVER = "#2a82da"    # Hover state borders
    SEPARATOR = "#555555"       # Menu separators
    
    # Dropdown specific colors (deprecated - use HOVER_BG/HOVER_TEXT instead)
    DROPDOWN_BG = "#2a2a2a"     # Dropdown background (darker than window)
    DROPDOWN_ITEM_HOVER = "#2a82da"  # Dropdown item hover (use HOVER_BG instead)
    DROPDOWN_HOVER_TEXT = "#ffffff"  # Text color when hovering over dropdown items (use HOVER_TEXT instead)
    DROPDOWN_BORDER = "#666666"      # Dropdown borders
    
    # Menu specific colors (deprecated - use HOVER_TEXT instead)
    MENU_HOVER_TEXT = "#ffffff"      # Text color when hovering over menu items (use HOVER_TEXT instead)
    
    # Special colors
    BRIGHT_TEXT = "#ff0000"     # Error/warning text
    LINK = "#2a82da"           # Links
    TOOLTIP_BASE = "#191919"    # Tooltip background
    TOOLTIP_TEXT = "#ffffff"    # Tooltip text


class LightTheme:
    """Light theme color constants."""
    # Main background colors
    WINDOW = "#f0f0f0"          # Main window background
    BASE = "#ffffff"            # Input fields, text areas
    ALTERNATE_BASE = "#f5f5f5"  # Alternate background
    
    # Text colors
    TEXT = "#000000"            # Primary text
    WINDOW_TEXT = "#000000"     # Window text
    BUTTON_TEXT = "#000000"     # Button text
    
    # Interactive elements
    BUTTON = "#e1e1e1"          # Button background
    BUTTON_HOVER = "#0078d4"    # Button hover state (Windows blue)
    HIGHLIGHT = "#0078d4"       # Selection/highlight color
    HIGHLIGHTED_TEXT = "#ffffff" # Text on highlighted background
    
    # Universal hover color (used for all interactive elements)
    HOVER_BG = "#0078d4"        # Universal hover background color
    HOVER_TEXT = "#ffffff"      # Universal hover text color
    
    # Borders and lines
    BORDER = "#3D3D3D"          # Standard borders
    BORDER_HOVER = "#0078d4"    # Hover state borders
    SEPARATOR = "#e1e1e1"       # Menu separators
    
    # Dropdown specific colors (deprecated - use HOVER_BG/HOVER_TEXT instead)
    DROPDOWN_BG = "#f0f0f0"     # Dropdown background (slightly darker than white)
    DROPDOWN_HOVER = "#0078d4"  # Dropdown item hover (use HOVER_BG instead)
    DROPDOWN_ITEM_HOVER = "#e5f3ff"  # Dropdown item hover (use HOVER_BG instead)
    DROPDOWN_HOVER_TEXT = "#ffffff"  # Text color when hovering over dropdown items (use HOVER_TEXT instead)
    DROPDOWN_BORDER = "#cccccc"      # Dropdown borders
    
    # Menu specific colors (deprecated - use HOVER_TEXT instead)
    MENU_HOVER_TEXT = "#ffffff"      # Text color when hovering over menu items (use HOVER_TEXT instead)
    
    # Special colors
    BRIGHT_TEXT = "#d13438"     # Error/warning text (red)
    LINK = "#0078d4"           # Links (Windows blue)
    TOOLTIP_BASE = "#ffffe1"    # Tooltip background (light yellow)
    TOOLTIP_TEXT = "#000000"    # Tooltip text


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
    background-color: {DarkTheme.BUTTON};
    color: {DarkTheme.BUTTON_TEXT};
    border: 1px solid {DarkTheme.BORDER};
    padding: 6px 12px;
    border-radius: 3px;
    font-size: {Layout.FONT_SIZE}pt;
    {f"min-height: {Layout.BUTTON_HEIGHT}px; max-height: {Layout.BUTTON_HEIGHT}px;" if Layout.BUTTON_HEIGHT else ""}
}}
QPushButton:hover {{
    background-color: {DarkTheme.HOVER_BG};
    border: 1px solid {DarkTheme.BORDER_HOVER};
    color: {DarkTheme.HOVER_TEXT};
}}
QPushButton:pressed {{
    background-color: {DarkTheme.HIGHLIGHT};
    border: 1px solid {DarkTheme.BORDER_HOVER};
    color: {DarkTheme.HOVER_TEXT};
}}

QComboBox {{
    background-color: {DarkTheme.DROPDOWN_BG};
    color: {DarkTheme.TEXT};
    border: 1px solid {DarkTheme.DROPDOWN_BORDER};
    font-size: {Layout.FONT_SIZE}pt;
}}
QComboBox::drop-down {{
    background-color: {DarkTheme.BUTTON};
    border: 1px solid {DarkTheme.BORDER};
    width: 20px;
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid {DarkTheme.TEXT};
}}

QLineEdit {{
    background-color: {DarkTheme.BASE};
    color: {DarkTheme.TEXT};
    border: 1px solid {DarkTheme.BORDER};
    padding: 4px;
    border-radius: 3px;
    font-size: {Layout.FONT_SIZE}pt;
    {f"min-height: {Layout.INPUT_HEIGHT}px; max-height: {Layout.INPUT_HEIGHT}px;" if Layout.INPUT_HEIGHT else ""}
}}

QSpinBox {{
    background-color: {DarkTheme.BASE};
    color: {DarkTheme.TEXT};
    border: 1px solid {DarkTheme.BORDER};
    font-size: {Layout.FONT_SIZE}pt;
}}
QSpinBox::up-button {{
    background-color: {DarkTheme.BUTTON};
    border: 1px solid {DarkTheme.BORDER};
}}
QSpinBox::down-button {{
    background-color: {DarkTheme.BUTTON};
    border: 1px solid {DarkTheme.BORDER};
}}
QSpinBox::up-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 4px solid {DarkTheme.TEXT};
}}
QSpinBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 4px solid {DarkTheme.TEXT};
}}

QLabel {{
    color: {DarkTheme.TEXT};
    font-size: {Layout.FONT_SIZE}pt;
    {f"min-height: {Layout.LABEL_HEIGHT}px;" if Layout.LABEL_HEIGHT else ""}
}}

QComboBox:hover {{
    border: 1px solid {DarkTheme.BORDER_HOVER};
}}
QComboBox QAbstractItemView {{
    background-color: {DarkTheme.DROPDOWN_BG};
    color: {DarkTheme.TEXT};
    selection-background-color: {DarkTheme.HIGHLIGHT};
    selection-color: {DarkTheme.HIGHLIGHTED_TEXT};
    border: 1px solid {DarkTheme.DROPDOWN_BORDER};
}}
QComboBox QAbstractItemView::item {{
    padding: 4px;
    background-color: {DarkTheme.DROPDOWN_BG};
    color: {DarkTheme.TEXT};
}}
QComboBox QAbstractItemView::item:selected {{
    background-color: {DarkTheme.HIGHLIGHT};
    color: {DarkTheme.HIGHLIGHTED_TEXT};
}}
QComboBox QAbstractItemView::item:hover {{
    background-color: {DarkTheme.HOVER_BG};
    color: {DarkTheme.HOVER_TEXT};
}}

QMenuBar {{
    background-color: {DarkTheme.WINDOW};
    color: {DarkTheme.TEXT};
    border-bottom: 1px solid {DarkTheme.BORDER};
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
    background-color: {DarkTheme.HOVER_BG};
    color: {DarkTheme.HOVER_TEXT};
}}
QMenuBar::item:pressed {{
    background-color: {DarkTheme.HIGHLIGHT};
    color: {DarkTheme.HOVER_TEXT};
}}

QMenu {{
    background-color: {DarkTheme.DROPDOWN_BG};
    color: {DarkTheme.TEXT};
    border: 1px solid {DarkTheme.DROPDOWN_BORDER};
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenu::item {{
    padding: 6px 20px;
    background-color: transparent;
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenu::item:selected {{
    background-color: {DarkTheme.HIGHLIGHT};
    color: {DarkTheme.HOVER_TEXT};
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenuBar::item:hover {{
    background-color: {DarkTheme.HOVER_BG};
    color: {DarkTheme.HOVER_TEXT};
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenu::separator {{
    height: 1px;
    background-color: {DarkTheme.SEPARATOR};
    margin: 2px 0px;
}}
"""


def get_light_stylesheet():
    """Generate light theme stylesheet with current font size."""
    return f"""
QPushButton {{
    background-color: {LightTheme.BUTTON};
    color: {LightTheme.BUTTON_TEXT};
    border: 1px solid {LightTheme.BORDER};
    {f"min-height: {Layout.BUTTON_HEIGHT}px; max-height: {Layout.BUTTON_HEIGHT}px;" if Layout.BUTTON_HEIGHT else ""}
    padding: 6px 12px;
    border-radius: 3px;
}}
QPushButton:hover {{
    background-color: {LightTheme.HOVER_BG};
    border: 1px solid {LightTheme.BORDER_HOVER};
    color: {LightTheme.HOVER_TEXT};
}}
QPushButton:pressed {{
    background-color: {LightTheme.HIGHLIGHT};
    border: 1px solid {LightTheme.BORDER_HOVER};
    color: {LightTheme.HOVER_TEXT};
}}

QComboBox {{
    background-color: {LightTheme.DROPDOWN_BG};
    font-size: {Layout.FONT_SIZE}pt;
}}

QLineEdit {{
    {f"min-height: {Layout.INPUT_HEIGHT}px; max-height: {Layout.INPUT_HEIGHT}px;" if Layout.INPUT_HEIGHT else ""}
    padding: 4px;
    border-radius: 3px;
}}

QSpinBox {{
    font-size: {Layout.FONT_SIZE}pt;
}}

QLabel {{
    {f"min-height: {Layout.LABEL_HEIGHT}px;" if Layout.LABEL_HEIGHT else ""}
}}

QMenuBar {{
    background-color: {LightTheme.WINDOW};
    color: {LightTheme.TEXT};
    border-bottom: 1px solid {LightTheme.BORDER};
    spacing: {Layout.WIDGET_SPACING_TIGHT}px;
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenuBar::item {{
    background-color: transparent;
    color: {LightTheme.TEXT};
    padding: {Layout.MENU_ITEM_PADDING};
    margin: {Layout.MENU_ITEM_MARGIN};
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenuBar::item:selected {{
    background-color: {LightTheme.HOVER_BG};
    color: {LightTheme.HOVER_TEXT};
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenuBar::item:pressed {{
    background-color: {LightTheme.HIGHLIGHT};
    color: {LightTheme.HOVER_TEXT};
    font-size: {Layout.FONT_SIZE}pt;
}}

QMenu {{
    background-color: {LightTheme.DROPDOWN_BG};
    color: {LightTheme.TEXT};
    border: 1px solid {LightTheme.BORDER};
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenu::item {{
    padding: 6px 20px;
    background-color: transparent;
    font-size: {Layout.FONT_SIZE}pt;
}}
QMenu::item:selected {{
    background-color: {LightTheme.HIGHLIGHT};
    color: {LightTheme.HOVER_TEXT};
    font-size: {Layout.FONT_SIZE}pt;
}}

QComboBox QAbstractItemView {{
    background-color: {LightTheme.DROPDOWN_BG};
}}
QComboBox QAbstractItemView::item:hover {{
    background-color: {LightTheme.HOVER_BG};
    color: {LightTheme.HOVER_TEXT};
}}
"""


# Backwards compatibility - use the functions to generate default stylesheets
DARK_STYLESHEET = get_dark_stylesheet()
LIGHT_STYLESHEET = get_light_stylesheet()