from __future__ import annotations

MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3


def build_error_position(src: str, pos: int) -> list[str]:
    """Render the line(s) surrounding `pos`, with a caret pointing at it."""
    if src == "":
        return ["No input provided"]

    lines = src.split("\n")
    src_length = len(src)

    line_idx = 0
    while (
        line_idx < len(lines)
        and len(lines[line_idx]) > 0
        and pos > len(lines[line_idx]) - 1
        and pos < src_length
    ):
        pos -= len(lines[line_idx])
        line_idx += 1

    start = max(0, line_idx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1))
    lines_to_show = lines[start : line_idx + 1]

    return [*lines_to_show, " " * max(0, pos) + "^"]
