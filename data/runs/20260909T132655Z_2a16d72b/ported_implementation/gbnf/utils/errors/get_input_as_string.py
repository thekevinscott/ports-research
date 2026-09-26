from typing import Sequence, Union

ValidInput = Union[str, int, Sequence[int]]


def get_input_as_string(src: ValidInput) -> str:
    if isinstance(src, str):
        return src
    code_points = src if isinstance(src, (list, tuple)) else [src]
    return "".join(chr(cp) for cp in code_points)
