"""Group generation settings (the spin boxes are placed in the toolbar by MainWindow)."""

from PySide6.QtWidgets import QWidget, QSpinBox

from ...constants.start_values import (
    DEFAULT_NUM_GROUPS,
    DEFAULT_NUM_ROUNDS
)


class ControlsPanel(QWidget):
    """Spin boxes for the group generation settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Create the spin boxes."""
        self.num_groups = QSpinBox()
        self.num_groups.setRange(1, 99)
        self.num_groups.setValue(DEFAULT_NUM_GROUPS)

        self.num_rounds = QSpinBox()
        # Generation time grows with the rounds; 20 keeps even a large class to a few seconds
        self.num_rounds.setRange(1, 20)
        self.num_rounds.setValue(DEFAULT_NUM_ROUNDS)

        self.random_seed = QSpinBox()
        self.random_seed.setRange(0, 999999)
        self.random_seed.setValue(0)
        # Help users understand that 0 means totally random
        self.random_seed.setToolTip("0 = totally random; any other number reproduces the same grouping")
        # Show a friendly label when at the minimum value
        self.random_seed.setSpecialValueText("Random")
