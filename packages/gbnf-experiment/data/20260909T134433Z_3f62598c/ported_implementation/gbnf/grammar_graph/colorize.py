from enum import Enum
from typing import Callable, Union


class Color(str, Enum):
    BLUE = "\x1b[34m"
    CYAN = "\x1b[36m"
    GREEN = "\x1b[32m"
    RED = "\x1b[31m"
    GRAY = "\x1b[90m"
    YELLOW = "\x1b[33m"

    def __str__(self) -> str:
        return self.value


Colorize = Callable[[Union[str, int], Color], str]


def colorize(value: Union[str, int], color: Color) -> str:
    return f"{color.value}{value}"


def no_color(value: Union[str, int], color: Color) -> str:
    return f"{value}"
