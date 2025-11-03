"""About dialog for the application."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from ...constants import APP_NAME, VERSION, AUTHOR, AUTHOR_COPYRIGHT, DESCRIPTION, FEATURES, REPOSITORY
from ...constants import MIT_LICENSE_HTML


def show_about_dialog(parent) -> None:
    """
    Show the About dialog.
    
    Args:
        parent: Parent widget
    """
    features_html = "<ul>\n" + "\n".join(f"<li>{f}</li>" for f in FEATURES) + "\n</ul>"
    
    about_text = f"""
<h2>{APP_NAME}</h2>
<p><b>Version:</b> {VERSION}</p>
<p><b>Author:</b> {AUTHOR}</p>
<p><b>Description:</b> {DESCRIPTION}</p>

<h3>Features:</h3>
{features_html}

<h3>License:</h3>
<p><b>MIT License</b></p>
<p>Copyright (c) 2025 {AUTHOR_COPYRIGHT}</p>

{MIT_LICENSE_HTML}

<p><b>Built with:</b> Python and PySide6</p>
<p><b>Repository:</b> <a href="{REPOSITORY}">{REPOSITORY}</a></p>
    """
    
    msg = QMessageBox(parent)
    msg.setWindowTitle(f"About {APP_NAME}")
    msg.setTextFormat(Qt.RichText)
    msg.setText(about_text)
    msg.setIcon(QMessageBox.Information)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec()
