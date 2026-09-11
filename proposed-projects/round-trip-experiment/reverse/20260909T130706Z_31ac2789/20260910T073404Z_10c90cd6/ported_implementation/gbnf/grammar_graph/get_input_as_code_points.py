from typing import List

from .grammar_graph_types import ValidInput


def get_code_point(char: str) -> int:
    if len(char) == 0:
        raise ValueError(f"Could not get code point for character: {char}")
    code_point = ord(char[0])
    if not isinstance(code_point, int):  # pragma: no cover - defensive
        raise ValueError("code_point must be an integer!")
    return code_point


def get_input_as_code_points(src: ValidInput) -> List[int]:
    if isinstance(src, bool):
        raise ValueError(f"Invalid input type: {type(src)}")

    if isinstance(src, int):
        return [src]

    if isinstance(src, (list, tuple)):
        for c in src:
            if not isinstance(c, int) or isinstance(c, bool):
                raise ValueError(
                    f"code_point must be an integer for {c} if src is a list"
                )
        return list(src)

    if isinstance(src, str):
        return [get_code_point(s) for s in src]

    raise ValueError(f"Invalid input type: {type(src)}")


getCodePoint = get_code_point
getInputAsCodePoints = get_input_as_code_points
