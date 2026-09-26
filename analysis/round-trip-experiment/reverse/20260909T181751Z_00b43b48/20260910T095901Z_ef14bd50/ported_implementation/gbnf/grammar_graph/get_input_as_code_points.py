from typing import List

from .grammar_graph_types import ValidInput


def get_code_point(char: str) -> int:
    if len(char) == 0:
        raise Exception(f"Could not get code point for character: {char}")
    code_point = ord(char[0])
    if not isinstance(code_point, int):
        raise Exception("codePoint must be an integer!")
    return code_point


def get_input_as_code_points(src: ValidInput) -> List[int]:
    if isinstance(src, bool):
        raise Exception(f"Invalid input type: {type(src)}")

    if isinstance(src, int):
        return [src]

    if isinstance(src, list):
        for c in src:
            if not isinstance(c, int) or isinstance(c, bool):
                raise Exception(
                    f"codePoint must be an integer for {c} if src is a list"
                )
        return src

    if isinstance(src, str):
        # iterate by code point, matching the reference implementation's per-character walk
        return [get_code_point(char) for char in src]

    raise Exception(f"Invalid input type: {type(src)}")
