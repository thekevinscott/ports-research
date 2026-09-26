"""Small helpers that reproduce JavaScript semantics relied upon by the reference
implementation.

The reference is written in TypeScript, where indexing a string out of bounds
yields ``undefined`` (falsy) rather than raising, and where ``JSON.stringify``
emits no whitespace. These helpers keep the ported code a close, readable
transcription of the original.
"""

from __future__ import annotations

import json
from typing import Any

__all__ = [
    "char_at",
    "json_stringify",
    "js_parse_int",
    "NAN",
]

NAN = float("nan")


def char_at(src: str, pos: int) -> str:
    """``src[pos]`` in JS: out-of-range (or negative) yields a falsy value."""
    if src is None:
        return ""
    if pos < 0 or pos >= len(src):
        return ""
    return src[pos]


def json_stringify(value: Any) -> str:
    """``JSON.stringify`` equivalent: no separator whitespace, no ASCII escaping."""
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


def js_parse_int(src: str, radix: int = 10) -> Any:
    """``parseInt``: parse the longest valid prefix, or NaN if there is none."""
    text = src.strip()
    sign = 1
    if text[:1] in ("+", "-"):
        if text[0] == "-":
            sign = -1
        text = text[1:]

    digits = ""
    for char in text:
        try:
            if int(char, radix) >= 0:
                digits += char
                continue
        except ValueError:
            pass
        break

    if not digits:
        return NAN
    return sign * int(digits, radix)

