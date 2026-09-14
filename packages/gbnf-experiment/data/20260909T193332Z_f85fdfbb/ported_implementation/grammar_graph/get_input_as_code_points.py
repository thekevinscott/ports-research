from __future__ import annotations

from typing import TYPE_CHECKING

from ..utils.utf16 import code_units

if TYPE_CHECKING:  # pragma: no cover
    from .types import ValidInput


def get_input_as_code_points(src: "ValidInput") -> list[int]:
    if not isinstance(src, str):
        return list(src) if isinstance(src, (list, tuple)) else [src]

    return code_units(src)
