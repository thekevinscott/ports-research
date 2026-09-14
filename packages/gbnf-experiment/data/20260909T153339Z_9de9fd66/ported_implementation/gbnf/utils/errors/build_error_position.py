from typing import List

MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3


def build_error_position(src: str, pos: int) -> List[str]:
    if src == "":
        return ["No input provided"]

    lines = src.split("\n")

    line_idx = 0
    # an out of bounds line reads as an empty string, mirroring the falsy
    # `undefined` the reference implementation walks off the end of the array with.
    while line_idx < len(lines) and lines[line_idx] and pos > len(lines[line_idx]) - 1:
        pos -= len(lines[line_idx])
        line_idx += 1

    lines_to_show: List[str] = []
    for i in range(max(0, line_idx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1)), line_idx + 1):
        lines_to_show.append(lines[i] if i < len(lines) else "")

    return [
        *lines_to_show,
        " " * max(0, pos) + "^",
    ]
