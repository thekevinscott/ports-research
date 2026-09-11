from __future__ import annotations

from typing import Iterable, Union

ValidInput = Union[str, int, Iterable[int]]


def get_input_as_string(src: ValidInput) -> str:
    if isinstance(src, str):
        return src
    code_points = src if isinstance(src, (list, tuple)) else [src]
    return ''.join(chr(cp) for cp in code_points)
