"""Port of ``src/grammar-graph/colorize.ts``."""

from __future__ import annotations

from enum import Enum
from typing import Union


class Color(str, Enum):
    BLUE = '\x1b[34m'
    CYAN = '\x1b[36m'
    GREEN = '\x1b[32m'
    RED = '\x1b[31m'
    GRAY = '\x1b[90m'
    YELLOW = '\x1b[33m'


def colorize(value: Union[str, int], color: Color) -> str:
    return f'{color.value}{value}'


def no_color(value: Union[str, int], color: Color) -> str:
    return f'{value}'
