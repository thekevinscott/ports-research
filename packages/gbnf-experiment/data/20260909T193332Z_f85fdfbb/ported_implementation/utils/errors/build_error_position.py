from __future__ import annotations

MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3


def build_error_position(src: str, pos: int) -> list[str]:
    if src == "":
        return ["No input provided"]

    lines = src.split("\n")

    line_idx = 0
    # `lines[lineIdx] &&` in the reference: an out of range index or an empty
    # line is falsy and stops the walk.
    while line_idx < len(lines) and lines[line_idx] and pos > len(lines[line_idx]) - 1:
        pos -= len(lines[line_idx])
        line_idx += 1

    lines_to_show: list[str] = []
    start = max(0, line_idx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1))
    for i in range(start, line_idx + 1):
        # Out of range reads yield `undefined` in JS, which joins as an empty line.
        lines_to_show.append(lines[i] if i < len(lines) else "")

    return [
        *lines_to_show,
        " " * max(0, pos) + "^",
    ]
