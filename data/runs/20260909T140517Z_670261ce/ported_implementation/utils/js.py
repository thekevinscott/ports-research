"""Small helpers that reproduce Javascript semantics the port relies on."""

from __future__ import annotations

from typing import Optional, Sequence, TypeVar

T = TypeVar("T")

_HEX_DIGITS = "0123456789abcdefABCDEF"


def char_at(src: str, pos: int) -> str:
    """``src[pos]`` with Javascript's out-of-bounds semantics.

    Javascript yields ``undefined`` (falsy) for an out-of-range index; the empty
    string is the closest falsy Python equivalent, and every comparison the
    reference makes against a real character still behaves identically.
    """
    if 0 <= pos < len(src):
        return src[pos]
    return ""


def last(items: Sequence[T]) -> Optional[T]:
    """``items[items.length - 1]``, ``None`` when empty (Javascript ``undefined``)."""
    return items[-1] if items else None


def parse_hex(src: str) -> Optional[int]:
    """``parseInt(src, 16)``: consume the leading run of hex digits.

    Returns ``None`` where Javascript would return ``NaN``.
    """
    end = 0
    while end < len(src) and src[end] in _HEX_DIGITS:
        end += 1
    if end == 0:
        return None
    return int(src[:end], 16)
