from __future__ import annotations

MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3


def build_error_position(src: str, pos: int) -> list[str | None]:
    """Render the offending line(s) of ``src`` with a caret under ``pos``.

    Mirrors the reference implementation, including the fact that a position
    past the end of the input yields a trailing ``None`` (JS ``undefined``)
    entry, which renders as an empty line.
    """
    if src == "":
        return ["No input provided"]

    lines = src.split("\n")

    line_idx = 0
    while line_idx < len(lines) and lines[line_idx] and pos > len(lines[line_idx]) - 1:
        pos -= len(lines[line_idx])
        line_idx += 1

    lines_to_show: list[str | None] = []
    first = max(0, line_idx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1))
    for i in range(first, line_idx + 1):
        lines_to_show.append(lines[i] if i < len(lines) else None)

    return [
        *lines_to_show,
        " " * max(pos, 0) + "^",
    ]
