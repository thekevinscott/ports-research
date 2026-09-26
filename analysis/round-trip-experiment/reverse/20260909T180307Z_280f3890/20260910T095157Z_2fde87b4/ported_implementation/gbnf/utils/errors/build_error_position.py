from typing import List, Optional

MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3


def build_error_position(src: str, pos: int) -> List[str]:
    if src == "":
        return ["No input provided"]
    lines = src.split("\n")

    line_idx = 0
    line: Optional[str] = lines[line_idx] if line_idx < len(lines) else None
    while line and pos > len(line) - 1 and pos < len(src):
        pos -= len(line)
        line_idx += 1
        line = lines[line_idx] if line_idx < len(lines) else None

    lines_to_show = lines[
        max(0, line_idx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1)) : line_idx + 1
    ]

    return [*lines_to_show, f"{' ' * max(0, pos)}^"]
