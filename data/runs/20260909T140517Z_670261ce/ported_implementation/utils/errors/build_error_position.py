"""Port of ``src/utils/errors/build-error-position.ts``."""

from __future__ import annotations

from typing import List

MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3

# The reference implementation can index past the end of the `lines` array; the
# resulting `undefined` is rendered as an empty string by Javascript's
# `Array.join`, so error messages keep an empty line there.
MISSING_LINE = ""


def _line_at(lines: List[str], idx: int) -> str:
    """`lines[idx]` with Javascript's out-of-bounds semantics (falsy result)."""
    if 0 <= idx < len(lines):
        return lines[idx]
    return ""


def build_error_position(src: str, pos: int) -> List[str]:
    if src == "":
        return ["No input provided"]

    lines = src.split("\n")

    line_idx = 0
    while _line_at(lines, line_idx) and pos > len(lines[line_idx]) - 1:
        pos -= len(lines[line_idx])
        line_idx += 1

    lines_to_show: List[str] = []
    for i in range(max(0, line_idx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1)), line_idx + 1):
        lines_to_show.append(lines[i] if 0 <= i < len(lines) else MISSING_LINE)

    return [
        *lines_to_show,
        " " * pos + "^",
    ]


# Camel-cased alias mirroring the reference export name.
buildErrorPosition = build_error_position
