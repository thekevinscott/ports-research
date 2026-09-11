from typing import List

MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3


def build_error_position(src: str, pos: int) -> List[str]:
    if src == "":
        return ["No input provided"]

    lines = src.split("\n")

    line_idx = 0
    # `lines[line_idx]` is falsy in JS both for an empty line and for running off the
    # end of the array, so an empty line halts the walk just like the end of input does.
    while line_idx < len(lines) and lines[line_idx] and pos > len(lines[line_idx]) - 1:
        pos -= len(lines[line_idx])
        line_idx += 1

    lines_to_show: List[str] = []
    for i in range(
        max(0, line_idx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1)), line_idx + 1
    ):
        lines_to_show.append(lines[i] if i < len(lines) else "undefined")
    return [
        *lines_to_show,
        " " * pos + "^",
    ]
