from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Optional

__all__ = ["Color", "colorize", "no_color", "Colorize"]


class Color(str, Enum):
    BLUE = "\x1b[34m"
    CYAN = "\x1b[36m"
    GREEN = "\x1b[32m"
    RED = "\x1b[31m"
    GRAY = "\x1b[90m"
    YELLOW = "\x1b[33m"

    def __str__(self) -> str:
        return self.value


def colorize(value: Any, color: Optional[Color] = None) -> str:
    return f"{color}{value}"


def no_color(value: Any, color: Optional[Color] = None) -> str:
    """Drop-in for `colorize` that ignores the requested color."""
    return f"{value}"


Colorize = Callable[..., str]
