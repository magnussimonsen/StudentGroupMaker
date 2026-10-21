"""UI widgets package."""

from .break_timer_panel import BreakTimerPanel
from .class_panel import ClassPanel
from .class_seating_panel import ClassSeatingPanel
from .controls_panel import ControlsPanel
from .output_panel import OutputPanel
from .red_cross_panel import RedCrossPanel
from .red_cross_store import RedCrossStore

__all__ = [
    'BreakTimerPanel', 'ClassPanel', 'ClassSeatingPanel', 'ControlsPanel', 'OutputPanel',
    'RedCrossPanel', 'RedCrossStore',
]
