"""Helpers that reproduce JavaScript semantics the reference implementation relies on.

The reference implementation is written in TypeScript, where strings are
sequences of UTF-16 code units and out-of-range indexing yields ``undefined``
rather than raising. These helpers let the port index and measure strings the
same way so that grammars/inputs containing astral-plane characters behave
identically.
"""

from __future__ import annotations

import math
from typing import Any

NAN = float("nan")


def to_code_units(value: str) -> list[int]:
    """Return the UTF-16 code units of ``value`` (what JS iterates over)."""
    units: list[int] = []
    for char in value:
        code_point = ord(char)
        if code_point > 0xFFFF:
            offset = code_point - 0x10000
            units.append(0xD800 + (offset >> 10))
            units.append(0xDC00 + (offset & 0x3FF))
        else:
            units.append(code_point)
    return units


def to_utf16(value: str) -> str:
    """Expand astral characters into surrogate pairs.

    The result indexes, slices and measures exactly like the equivalent
    JavaScript string.
    """
    for char in value:
        if ord(char) > 0xFFFF:
            return "".join(chr(unit) for unit in to_code_units(value))
    return value


def char_at(src: str, pos: int) -> str:
    """``src[pos]`` with JS semantics: out of range yields an empty string."""
    if 0 <= pos < len(src):
        return src[pos]
    return ""


def char_code_at(src: str, pos: int) -> int:
    """``src.charCodeAt(pos)``."""
    if 0 <= pos < len(src):
        return ord(src[pos])
    return NAN


def code_point_at(src: str, pos: int) -> int | None:
    """``src.codePointAt(pos)`` -- combines surrogate pairs."""
    if not 0 <= pos < len(src):
        return None
    first = ord(src[pos])
    if 0xD800 <= first <= 0xDBFF and pos + 1 < len(src):
        second = ord(src[pos + 1])
        if 0xDC00 <= second <= 0xDFFF:
            return (first - 0xD800) * 0x400 + second - 0xDC00 + 0x10000
    return first


def from_char_code(code: int) -> str:
    """``String.fromCharCode(code)`` -- truncates to 16 bits."""
    if isinstance(code, float) and math.isnan(code):
        return "\x00"
    return chr(int(code) & 0xFFFF)


def from_code_point(code: int) -> str:
    """``String.fromCodePoint(code)``."""
    return chr(int(code))


def parse_int(value: str, radix: int) -> Any:
    """``parseInt(value, radix)`` -- parses the longest valid prefix, else NaN."""
    text = value.lstrip(" \t\n\r\f\v")
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


def join(parts: list[Any], separator: str) -> str:
    """``Array.prototype.join`` -- ``None`` entries become empty strings."""
    return separator.join("" if part is None else str(part) for part in parts)
