from __future__ import annotations

from ..utils.errors import GrammarParseError
from .char_at import char_at

ESCAPE_CHARS = {
    "t": 9,
    "r": 13,
    "n": 10,
}

HEX_DIGITS = "0123456789abcdefABCDEF"
JS_WHITESPACE = " \t\n\r\v\f      　﻿"


def parse_hex(raw: str) -> float:
    """Mirror `parseInt(raw, 16)`.

    Leading whitespace and an optional sign are skipped, hex digits are consumed until
    the first character that isn't one, and a missing digit yields NaN rather than an
    error. Callers propagate the NaN as a code point, exactly as the reference does.
    """
    idx = 0
    while idx < len(raw) and raw[idx] in JS_WHITESPACE:
        idx += 1
    sign = 1
    if idx < len(raw) and raw[idx] in "+-":
        if raw[idx] == "-":
            sign = -1
        idx += 1
    if raw[idx : idx + 2].lower() == "0x":
        idx += 2
    digits = ""
    while idx < len(raw) and raw[idx] in HEX_DIGITS:
        digits += raw[idx]
        idx += 1
    if not digits:
        return float("nan")
    return sign * int(digits, 16)


def parse_char(src: str, pos: int) -> tuple[float, int]:
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        next_char = char_at(src, pos + 1)
        if next_char == "x":
            return (parse_hex(src[pos + 2 : pos + 4]), 4)
        if next_char == "u":
            return (parse_hex(src[pos + 2 : pos + 6]), 6)
        if next_char == "U":
            return (parse_hex(src[pos + 2 : pos + 10]), 10)
        if next_char in ESCAPE_CHARS:
            return (ESCAPE_CHARS[next_char], 2)
        if next_char in ('"', "[", "]", "\\"):
            return (ord(next_char), 2)
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    return (ord(src[pos]), 1)
