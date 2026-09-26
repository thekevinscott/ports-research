from typing import List

from .grammar_graph_types import ValidInput


def get_code_point(char: str) -> int:
    if len(char) == 0:
        raise Exception(f"Could not get code point for character: {char}")
    code_point = ord(char)
    if not isinstance(code_point, int):
        raise Exception("code_point must be an integer!")
    return code_point


def get_input_as_code_points(src: ValidInput) -> List[int]:
    if isinstance(src, bool):
        raise Exception(f"Invalid input type: {type(src).__name__}")

    if isinstance(src, int):
        return [src]

    if isinstance(src, list):
        for c in src:
            if not isinstance(c, int) or isinstance(c, bool):
                raise Exception(
                    f"code_point must be an integer for {c} if src is a list"
                )
        return src

    if isinstance(src, str):
        # Python iterates strings by code point, so each character maps to one entry.
        return [get_code_point(char) for char in src]

    raise Exception(f"Invalid input type: {type(src).__name__}")
