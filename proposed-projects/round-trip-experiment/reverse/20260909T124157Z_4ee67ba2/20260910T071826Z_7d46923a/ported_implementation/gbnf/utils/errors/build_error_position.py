from typing import List

MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3


def build_error_position(src: str, pos: int) -> List[str]:
    if src == "":
        return ["No input provided"]

    lines = src.split("\n")

    line_idx = 0
    while (
        line_idx < len(lines)
        and lines[line_idx]
        and pos > len(lines[line_idx]) - 1
        and pos < len(src)
    ):
        pos -= len(lines[line_idx])
        line_idx += 1

    lines_to_show: List[str] = []
    for i in range(
        max(0, line_idx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1)),
        line_idx + 1,
    ):
        # The walk above can leave line_idx one past the final line; indexing out of
        # range yields nothing here rather than the reference's `undefined` entry.
        if i < len(lines):
            lines_to_show.append(lines[i])

    return [*lines_to_show, " " * max(0, pos) + "^"]
