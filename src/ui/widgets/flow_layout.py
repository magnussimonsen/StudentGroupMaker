"""Flow layout that wraps its widgets onto new lines when space runs out."""

from PySide6.QtWidgets import QLayout, QSizePolicy, QWidget, QHBoxLayout
from PySide6.QtCore import Qt, QRect, QSize, QPoint


class FlowLayout(QLayout):
    """Lay out items left to right, wrapping to a new line like text.

    Based on the Qt "Flow Layout" example.
    """

    def __init__(self, parent=None, spacing=10):
        super().__init__(parent)
        self._items = []
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(spacing)

    def __del__(self):
        while self.count():
            self.takeAt(0)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), test_only=True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, test_only=False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        # Wide enough for the widest single item, so the window can shrink to that
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect, test_only):
        margins = self.contentsMargins()
        effective = rect.adjusted(margins.left(), margins.top(), -margins.right(), -margins.bottom())
        spacing = self.spacing()

        # Split items into lines that fit the available width
        lines = [[]]
        x = effective.x()
        for item in self._items:
            hint = item.sizeHint()
            if lines[-1] and x + hint.width() > effective.right() + 1:
                lines.append([])
                x = effective.x()
            lines[-1].append(item)
            x += hint.width() + spacing

        # Place each line, centering items vertically within it
        y = effective.y()
        for line in lines:
            line_height = max((item.sizeHint().height() for item in line), default=0)
            x = effective.x()
            for item in line:
                hint = item.sizeHint()
                if not test_only:
                    offset = (line_height - hint.height()) // 2
                    item.setGeometry(QRect(QPoint(x, y + offset), hint))
                x += hint.width() + spacing
            y += line_height + spacing

        return y - spacing - rect.y() + margins.bottom()


def make_group(*widgets, spacing=6):
    """Bundle widgets (e.g. a label and its field) so they wrap together."""
    group = QWidget()
    row = QHBoxLayout(group)
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(spacing)
    for widget in widgets:
        row.addWidget(widget)
    group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    return group
