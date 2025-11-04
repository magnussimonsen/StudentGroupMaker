"""Main entry point for the application."""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QIcon

from .ui import MainWindow
from .models import create_default_class


def resource_path(relative: str) -> str:
    """Resolve a resource path for dev and for PyInstaller (_MEIPASS)."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))  # src -> project root
    return str(base / relative)


def main() -> int:
    """Main entry point."""
    # Reuse an existing QApplication if one was created by a backend import
    app = QApplication.instance() or QApplication(sys.argv)

    # On Windows, use Fusion style to ensure QSS hover states (like splitter handle) apply consistently
    if sys.platform.startswith("win"):
        try:
            from PySide6.QtWidgets import QStyleFactory
            fusion = QStyleFactory.create("Fusion")
            if fusion is not None:
                app.setStyle(fusion)
        except Exception:
            pass

    # Set application/window icon (ICO on Windows, PNG elsewhere)
    icon_rel = "src/icons/icon.ico" if sys.platform.startswith("win") else "src/icons/icon.png"
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
