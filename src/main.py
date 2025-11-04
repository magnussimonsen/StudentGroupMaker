"""Main entry point for the application."""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QIcon
from pathlib import Path

from .ui import MainWindow
from .models import create_default_class

from pathlib import Path

def resource_path(relative: str) -> str:
    # Works both in dev and in PyInstaller bundles
    base = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)  # src -> project root
    return str(Path(base) / relative)

app = QApplication(sys.argv)
app.setWindowIcon(QIcon(resource_path("icons/groupmaker.png")))

def main() -> int:
    """Main entry point."""
    # Reuse an existing QApplication if one was created by a backend import
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Helper to resolve resources in dev and in PyInstaller bundles
    def resource_path(relative: str) -> str:
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
        return str(base / relative)
    
    # Set application/window icon (ICO on Windows, PNG elsewhere)
    if sys.platform.startswith("win"):
        icon_rel = "src/icons/icon.ico"
    else:
        icon_rel = "src/icons/icon.png"
    app.setWindowIcon(QIcon(resource_path(icon_rel)))
    
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
