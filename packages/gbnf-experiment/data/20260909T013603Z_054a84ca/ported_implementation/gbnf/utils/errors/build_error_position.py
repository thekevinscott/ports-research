from __future__ import annotations

from typing import List

from ..js import at

MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3


def build_error_position(src: str, pos: int) -> List[str]:
    if src == '':
        return ['No input provided']

    lines = src.split('\n')

    line_idx = 0
    while at(lines, line_idx) and pos > len(lines[line_idx]) - 1:
        pos -= len(lines[line_idx])
        line_idx += 1

    lines_to_show: List[str] = []
    for i in range(max(0, line_idx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1)), line_idx + 1):
        line = at(lines, i)
        # Out-of-range lines are `undefined` in the reference; joining renders
        # them as an empty line.
        lines_to_show.append('' if line is None else line)

    return [*lines_to_show, ' ' * pos + '^']
