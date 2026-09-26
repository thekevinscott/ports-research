"""Port of ``src/utils/errors/get-input-as-string.ts``."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ...grammar_graph.types import ValidInput


def get_input_as_string(src: "ValidInput") -> str:
    if isinstance(src, str):
        return src
    code_points = list(src) if isinstance(src, (list, tuple)) else [src]
    return "".join(chr(cp) for cp in code_points)
