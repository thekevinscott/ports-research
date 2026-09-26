from __future__ import annotations

from ..js import from_code_point


def get_input_as_string(src) -> str:
    if isinstance(src, str):
        return src
    code_points = src if isinstance(src, (list, tuple)) else [src]
    return "".join(from_code_point(cp) for cp in code_points)
