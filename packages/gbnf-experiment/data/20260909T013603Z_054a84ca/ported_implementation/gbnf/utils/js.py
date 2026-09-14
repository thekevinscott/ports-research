"""Small helpers that reproduce JavaScript semantics the port relies on.

The reference implementation indexes strings freely (``src[pos]`` yields
``undefined`` past the end rather than throwing) and uses ``parseInt``, which
parses a leading prefix of digits. These helpers keep the ported code a
line-for-line match for the original instead of scattering bounds checks
through every parser loop.
"""

from __future__ import annotations

from typing import Optional

HEX_DIGITS = '0123456789abcdefABCDEF'


def char_at(src: str, pos: int) -> str:
    """``src[pos]`` with JavaScript's out-of-range behaviour ('' for undefined)."""
    if pos < 0 or pos >= len(src):
        return ''
    return src[pos]


def at(seq, idx):
    """``seq[idx]`` returning ``None`` when the index is out of range."""
    if idx < 0 or idx >= len(seq):
        return None
    return seq[idx]


def parse_int_hex(src: str) -> Optional[int]:
    """``parseInt(src, 16)``: parse the leading hex digits, ``None`` for NaN."""
    end = 0
    while end < len(src) and src[end] in HEX_DIGITS:
        end += 1
    if end == 0:
        return None
    return int(src[:end], 16)
