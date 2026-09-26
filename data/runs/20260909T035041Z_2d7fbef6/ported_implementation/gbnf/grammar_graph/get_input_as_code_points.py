from __future__ import annotations

from ..utils.js import to_code_units


def get_input_as_code_points(src) -> list[int]:
    if not isinstance(src, str):
        return list(src) if isinstance(src, (list, tuple)) else [src]

    return to_code_units(src)
