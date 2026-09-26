"""Port of ``src/utils/errors/get-input-as-string.ts``."""

from __future__ import annotations

from typing import List, Sequence, Union

ValidInput = Union[str, int, Sequence[int]]


def get_input_as_string(src: ValidInput) -> str:
    if isinstance(src, str):
        return src

    code_points: List[int] = list(src) if isinstance(src, (list, tuple)) else [src]
    return "".join(chr(cp) for cp in code_points)


getInputAsString = get_input_as_string
