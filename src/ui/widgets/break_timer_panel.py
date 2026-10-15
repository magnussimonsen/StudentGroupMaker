"""Break timer panel: a large countdown that keeps counting up once the break is over."""

import time

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer

from ...constants.colors_and_styling import DarkTheme
from .flow_layout import FlowLayout, make_group


class BreakTimerPanel(QWidget):
    """Shows how much of the break is left, then how long ago it ended."""

    PRESET_MINUTES = (5, 10, 15)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Deadline on the monotonic clock while running; remaining seconds while paused
        self._deadline = None
        self._paused_remaining = None

        # Fires once per displayed second, just after the shown value changes,
        # so every second stays on screen for the same length of time
        self._tick_timer = QTimer(self)
        self._tick_timer.setSingleShot(True)
        self._tick_timer.setTimerType(Qt.PreciseTimer)
        self._tick_timer.timeout.connect(self._on_tick)

        self._setup_ui()
        self.reset()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        # Same margins as the toolbar rows on the other pages
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 180)
        self.minutes_spin.setValue(10)
        self.minutes_spin.setSuffix(" min")
        self.seconds_spin = QSpinBox()
        self.seconds_spin.setRange(0, 59)
        self.seconds_spin.setSuffix(" s")

        self.start_btn = QPushButton("Start")
        self.start_btn.setObjectName("generateButton")  # Styled green in the stylesheet
        self.start_btn.clicked.connect(self.toggle_running)

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset)

        controls_row = FlowLayout(spacing=10)
        controls_row.addWidget(make_group(
            QLabel("Break length:"), self.minutes_spin, self.seconds_spin
        ))
        presets = []
        for minutes in self.PRESET_MINUTES:
            button = QPushButton(f"{minutes} min")
            button.clicked.connect(lambda _checked, m=minutes: self.start_preset(m))
            presets.append(button)
        controls_row.addWidget(make_group(QLabel("Quick start:"), *presets))
        controls_row.addWidget(make_group(self.start_btn, self.reset_btn))

        controls_widget = QWidget()
        controls_widget.setLayout(controls_row)
        layout.addWidget(controls_widget)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        # The labels scale with the window, so their size must not hold the window
        # at its current size; otherwise it could grow but never shrink again
        # (an explicit minimum height overrides the one derived from the font size;
        # 0 would mean "unset", hence 1)
        for label in (self.status_label, self.time_label):
            label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
            label.setMinimumHeight(1)

        layout.addStretch(1)
        layout.addWidget(self.status_label)
        layout.addWidget(self.time_label)
        layout.addStretch(2)

    def _selected_seconds(self) -> int:
        return self.minutes_spin.value() * 60 + self.seconds_spin.value()

    def _remaining_seconds(self) -> int:
        """Seconds left of the break; negative once the break is over."""
        if self._deadline is not None:
            # Round up so the display shows 10:00 right after start, not 9:59
            return -int((time.monotonic() - self._deadline) // 1)
        if self._paused_remaining is not None:
            return self._paused_remaining
        return self._selected_seconds()

    def start_preset(self, minutes: int):
        """Set the break length to a whole number of minutes and start right away."""
        self.minutes_spin.setValue(minutes)
        self.seconds_spin.setValue(0)
        self.reset()
        self.toggle_running()

    def toggle_running(self):
        """Start, pause or resume the timer."""
        if self._deadline is None:
            self._deadline = time.monotonic() + self._remaining_seconds()
            self._paused_remaining = None
            self._schedule_next_tick()
        else:
            self._paused_remaining = self._remaining_seconds()
            self._deadline = None
            self._tick_timer.stop()
        self._refresh_display()

    def _on_tick(self):
        self._refresh_display()
        self._schedule_next_tick()

    def _schedule_next_tick(self):
        """Wake up just after the next whole second relative to the deadline."""
        until_next_second = (self._deadline - time.monotonic()) % 1
        # A small margin makes sure the new value is showing when we wake up
        self._tick_timer.start(int(until_next_second * 1000) + 15)

    def reset(self):
        """Stop the timer and show the selected break length again."""
        self._tick_timer.stop()
        self._deadline = None
        self._paused_remaining = None
        self._refresh_display()

    def _refresh_display(self):
        running = self._deadline is not None
        idle = not running and self._paused_remaining is None
        self.start_btn.setText("Pause" if running else ("Start" if idle else "Resume"))
        # The length can only be changed before the timer has been started
        self.minutes_spin.setEnabled(idle)
        self.seconds_spin.setEnabled(idle)

        remaining = self._remaining_seconds()
        if remaining >= 0:
            status, color = "Break time left", DarkTheme.SUCCESS_BG_COLOR
        else:
            status, color = "Break is over", DarkTheme.DANGER_BG_COLOR
        if not running and not idle:
            status += " (paused)"
        minutes, seconds = divmod(abs(remaining), 60)
        self.status_label.setText(status)
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        self._time_color = color
        self._apply_label_sizes()

    def _apply_label_sizes(self):
        """Scale the countdown with the window so it can be read from the back of the room."""
        # The app stylesheet sets a font size on every QLabel, so the size has to
        # go in the label's own stylesheet to take effect
        available_height = max(self.height() - 120, 60)
        time_px = int(min(self.width() / 3.2, available_height * 0.6))
        status_px = max(time_px // 5, 16)
        self.time_label.setStyleSheet(
            f"color: {self._time_color}; font-size: {time_px}px; font-weight: bold;"
        )
        self.status_label.setStyleSheet(f"font-size: {status_px}px;")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_label_sizes()
