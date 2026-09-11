from typing import List

from ..char_at import item_at

MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3


def build_error_position(src: str, pos: int) -> List[str]:
    if src == "":
        return ["No input provided"]

    lines = src.split("\n")

    line_idx = 0
    while item_at(lines, line_idx) and pos > len(lines[line_idx]) - 1:
        pos -= len(lines[line_idx])
        line_idx += 1

    lines_to_show: List[str] = []
    start = max(0, line_idx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1))
    for i in range(start, line_idx + 1):
        line = item_at(lines, i)
        lines_to_show.append("" if line is None else line)
    return [
        *lines_to_show,
        " " * max(0, pos) + "^",
    ]
