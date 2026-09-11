from typing import List

MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3


def build_error_position(src: str, pos: int) -> List[str]:
    if src == "":
        return ["No input provided"]

    lines = src.split("\n")

    line_idx = 0
    # an empty line terminates the walk, matching the falsiness check of the reference
    while line_idx < len(lines) and lines[line_idx] and pos > len(lines[line_idx]) - 1:
        pos -= len(lines[line_idx])
        line_idx += 1

    lines_to_show: List[str] = []
    start = max(0, line_idx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1))
    for i in range(start, line_idx + 1):
        # when the position runs past the end of the input, the walk above stops on
        # a line that does not exist; the reference renders it as a blank line
        lines_to_show.append(lines[i] if i < len(lines) else "")

    return [
        *lines_to_show,
        " " * pos + "^",
    ]
