"""Main entry point for the application."""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from .ui import MainWindow
from .models import create_default_class


def main() -> int:
    """Main entry point."""
    app = QApplication(sys.argv)
    
    # Set initial application-wide font size
    font = QFont()
    font.setPointSize(11)  # Default size matching controls panel
    app.setFont(font)
    
    # Ensure default class exists
    create_default_class()
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
