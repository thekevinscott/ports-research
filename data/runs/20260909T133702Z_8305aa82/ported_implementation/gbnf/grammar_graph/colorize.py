from enum import Enum


class Color(str, Enum):
    BLUE = "\x1b[34m"
    CYAN = "\x1b[36m"
    GREEN = "\x1b[32m"
    RED = "\x1b[31m"
    GRAY = "\x1b[90m"
    YELLOW = "\x1b[33m"

    def __str__(self) -> str:
        return self.value


def colorize(string, color: Color) -> str:
    return f"{color.value}{string}"


def no_colorize(string, color: Color) -> str:
    return f"{string}"
