MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW = 3


def build_error_position(src: str, pos: int) -> list[str]:
    if src == "":
        return ["No input provided"]
    lines = src.split("\n")

    line_idx = 0
    cursor = pos
    while (
        line_idx < len(lines)
        and lines[line_idx]
        and cursor > len(lines[line_idx]) - 1
        and cursor < len(src)
    ):
        cursor -= len(lines[line_idx])
        line_idx += 1

    lines_to_show = lines[
        max(0, line_idx - (MAXIMUM_NUMBER_OF_ERROR_LINES_TO_SHOW - 1)) : line_idx + 1
    ]

    return [*lines_to_show, f"{' ' * max(0, cursor)}^"]
