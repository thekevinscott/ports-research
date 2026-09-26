from __future__ import annotations

from typing import List

MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3


def build_error_position(src: str, pos: int) -> List[str]:
    if src == "":
        return ["No input provided"]

    lines = src.split("\n")
    src_length = len(src)

    line_idx = 0
    # `lines[line_idx]` is evaluated first, so walking past the last line raises
    # an IndexError rather than ending the loop.
    while (
        lines[line_idx]
        and pos > len(lines[line_idx]) - 1
        and pos < src_length
    ):
        pos -= len(lines[line_idx])
        line_idx += 1

    lines_to_show = lines[
        max(0, line_idx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1)) : line_idx + 1
    ]

    return [*lines_to_show, f"{' ' * max(0, pos)}^"]
