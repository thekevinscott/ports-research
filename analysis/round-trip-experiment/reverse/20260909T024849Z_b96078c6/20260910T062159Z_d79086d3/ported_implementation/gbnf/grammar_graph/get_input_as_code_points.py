from __future__ import annotations

from typing import List

from .grammar_graph_types import ValidInput


def get_code_point(char: str) -> int:
    if not char:
        raise ValueError(f"Could not get code point for character: {char}")
    code_point = ord(char[0])
    if not isinstance(code_point, int):
        raise ValueError("code_point must be an integer!")
    return code_point


def get_input_as_code_points(src: ValidInput) -> List[int]:
    if isinstance(src, str):
        return [get_code_point(char) for char in src]

    if isinstance(src, int) and not isinstance(src, bool):
        return [src]

    if isinstance(src, (list, tuple)):
        for code_point in src:
            if not isinstance(code_point, int) or isinstance(code_point, bool):
                raise ValueError(
                    f"code_point must be an integer for {code_point} if src is a list",
                )
        return list(src)

    raise ValueError(f"Invalid input type: {type(src).__name__}")
