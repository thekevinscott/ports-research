from typing import Union, Sequence

ValidInput = Union[str, int, Sequence[int]]


def get_input_as_string(src: ValidInput) -> str:
    if isinstance(src, str):
        return src
    code_points = src if isinstance(src, (list, tuple)) else [src]
    return "".join(chr(code_point) for code_point in code_points)
