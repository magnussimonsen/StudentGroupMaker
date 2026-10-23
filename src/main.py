"""Main entry point for the application."""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFont, QIcon

from .constants import APP_NAME
from .constants.colors_and_styling import Layout
from .ui import MainWindow
from .models import DATA_DIR, create_default_class, seed_sample_student_photos


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

    # Set initial application-wide font size (MainWindow re-applies it once built)
    font = QFont()
    font.setPointSize(Layout.FONT_SIZE)
    app.setFont(font)

    # Ensure default class exists. This is the first write to the data folder,
    # so report it if that folder cannot be used instead of failing silently
    try:
        create_default_class()
        seed_sample_student_photos(Path(resource_path("src/img")))
    except OSError as error:
        QMessageBox.critical(
            None,
            APP_NAME,
            f"{APP_NAME} cannot save its data in:\n{DATA_DIR}\n\n{error}",
        )
        return 1

    # Create and show main window
    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
