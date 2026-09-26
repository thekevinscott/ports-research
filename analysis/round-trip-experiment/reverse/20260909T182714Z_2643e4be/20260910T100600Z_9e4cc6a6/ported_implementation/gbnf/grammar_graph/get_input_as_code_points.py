from __future__ import annotations

from typing import List

from .grammar_graph_types import ValidInput


def get_code_point(char: str) -> int:
    code_point = ord(char)
    if not isinstance(code_point, int):
        raise ValueError("code_point must be an integer!")
    return code_point


def get_input_as_code_points(src: ValidInput) -> List[int]:
    if isinstance(src, int):
        return [src]

    if isinstance(src, list):
        for c in src:
            if not isinstance(c, int):
                raise ValueError(
                    f"code_point must be an integer for {c} if src is a list",
                )
        return src

    if isinstance(src, str):
        return [get_code_point(char) for char in src]

    raise ValueError(f"Invalid input type: {type(src)}")
