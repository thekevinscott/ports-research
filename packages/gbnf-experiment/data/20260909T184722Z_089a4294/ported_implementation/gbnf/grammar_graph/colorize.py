from __future__ import annotations

from enum import StrEnum


class Color(StrEnum):
    BLUE = "\x1b[34m"
    CYAN = "\x1b[36m"
    GREEN = "\x1b[32m"
    RED = "\x1b[31m"
    GRAY = "\x1b[90m"
    YELLOW = "\x1b[33m"


def colorize(string: str | int, color: Color) -> str:
    return f"{color}{string}"


def no_color(string: str | int, color: Color) -> str:
    return f"{string}"
