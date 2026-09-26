"""Normalize the various accepted input shapes into code points."""

from typing import List, Union

ValidInput = Union[str, int, List[int]]


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

    if isinstance(src, (list, tuple)):
        for c in src:
            if not isinstance(c, int) or isinstance(c, bool):
                raise ValueError(
                    f"code_point must be an integer for {c} if src is a list"
                )
        return list(src)

    if isinstance(src, str):
        return [get_code_point(char) for char in src]

    raise ValueError(f"Invalid input type: {type(src)}")
