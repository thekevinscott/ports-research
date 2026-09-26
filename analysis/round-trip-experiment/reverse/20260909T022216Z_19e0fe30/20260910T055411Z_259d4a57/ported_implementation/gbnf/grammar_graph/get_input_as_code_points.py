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
    if isinstance(src, bool):
        raise ValueError(f"Invalid input type: {type(src)}")

    if isinstance(src, int):
        return [src]

    if isinstance(src, list):
        for c in src:
            if not isinstance(c, int) or isinstance(c, bool):
                raise ValueError(
                    f"code_point must be an integer for {c} if src is a list"
                )
        return src

    if isinstance(src, str):
        # iterating a string yields whole code points
        return [get_code_point(c) for c in src]

    raise ValueError(f"Invalid input type: {type(src)}")
