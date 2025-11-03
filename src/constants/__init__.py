"""Constants package - application metadata and configuration."""

from .app_info import (
    APP_NAME,
    VERSION,
    AUTHOR,
    AUTHOR_COPYRIGHT,
    DESCRIPTION,
    REPOSITORY,
    FEATURES,
    DEFAULT_STUDENTS,
)
from .license import MIT_LICENSE_TEXT, MIT_LICENSE_HTML
from .start_values import (
    DEFAULT_STUDENTS_PER_GROUP,
    DEFAULT_NUM_GROUPS,
    DEFAULT_NUM_ROUNDS,
)

__all__ = [
    "APP_NAME",
    "VERSION",
    "AUTHOR",
    "AUTHOR_COPYRIGHT",
    "DESCRIPTION",
    "REPOSITORY",
    "FEATURES",
    "DEFAULT_STUDENTS",
    "MIT_LICENSE_TEXT",
    "MIT_LICENSE_HTML",
    "DEFAULT_STUDENTS_PER_GROUP",
    "DEFAULT_NUM_GROUPS",
    "DEFAULT_NUM_ROUNDS",
]
