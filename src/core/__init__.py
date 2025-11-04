"""Core business logic package.

Avoid importing visualization at package import time to prevent Qt/Matplotlib
side effects (like creating a QApplication) before the app starts.
"""

from .grouping import partition_sizes, build_round, schedule_groups
from .quality import schedule_quality

__all__ = [
    'partition_sizes',
    'build_round',
    'schedule_groups',
    'schedule_quality',
]
