"""Output panel for displaying group results."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit
from PySide6.QtGui import QFont, QFontDatabase, QFontMetrics

from ...constants.colors_and_styling import Layout


class OutputPanel(QWidget):
    """Panel for displaying generated group plans."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Use minimal margins
        layout.setSpacing(5)  # Use standard spacing
        
        layout.addWidget(QLabel("Output:"))
        
        self.output_text = QPlainTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Generated groups will appear here…")

        # Use a fixed-width font so tabular/column text aligns nicely
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(Layout.FONT_SIZE if hasattr(Layout, 'FONT_SIZE') else 11)
        self.output_text.setFont(font)

        # Configure a tab stop so "Label:\tValue" aligns values at a consistent column
        # Choose tab width to be wide enough for the longest header label
        fm = QFontMetrics(self.output_text.font())
        # Approximate 24 spaces as the tab column; adjust if labels change
        tab_px = fm.horizontalAdvance(' ') * 24
        try:
            # Qt6 API
            self.output_text.setTabStopDistance(float(tab_px))
        except AttributeError:
            # Fallback for older Qt (not expected in PySide6)
            pass

        layout.addWidget(self.output_text, 1)
    
    def set_text(self, text: str):
        """Set the output text."""
        self.output_text.setPlainText(text)
    
    def get_text(self) -> str:
        """Get the current output text."""
        return self.output_text.toPlainText()
    
    def clear(self):
        """Clear the output."""
        self.output_text.clear()
    
    def set_font(self, font: QFont):
        """Set the font for the output text."""
        self.output_text.setFont(font)
    
    def set_font_size(self, size: int):
        """Set the font size for the output text."""
        font = self.output_text.font()
        font.setPointSize(size)
        self.output_text.setFont(font)
