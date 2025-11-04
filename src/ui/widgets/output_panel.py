"""Output panel for displaying group results."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPlainTextEdit
from PySide6.QtGui import QFont

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
        
        # Set default font size
        font = QFont()
        font.setPointSize(11)
        self.output_text.setFont(font)
        
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
