from typing import List

from .get_input_as_string import get_length_in_code_points

MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3


def build_error_position(src: str, pos: int) -> List[str]:
    if src == "":
        return ["No input provided"]
    lines = src.split("\n")
    src_length = get_length_in_code_points(src)

    line_idx = 0
    while (
        line_idx < len(lines)
        and lines[line_idx]
        and pos > get_length_in_code_points(lines[line_idx]) - 1
        and pos < src_length
    ):
        pos -= get_length_in_code_points(lines[line_idx])
        line_idx += 1

    lines_to_show = lines[
        max(0, line_idx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1)) : line_idx + 1
    ]

    return [*lines_to_show, f"{' ' * max(0, pos)}^"]
