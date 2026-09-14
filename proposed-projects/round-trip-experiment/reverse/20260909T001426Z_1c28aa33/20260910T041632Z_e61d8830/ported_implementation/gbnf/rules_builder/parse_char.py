from typing import Dict, Tuple, Union

from ..utils.errors import GrammarParseError

ESCAPE_CHARS: Dict[str, int] = {
    "t": 9,
    "r": 13,
    "n": 10,
}

LITERAL_ESCAPES = ['"', "[", "]", "\\"]

HEX_DIGITS = "0123456789abcdefABCDEF"
JS_WHITESPACE = " \t\n\r\v\f ﻿"


def parse_hex(src: str) -> Union[int, float]:
    """Mirrors JavaScript's parseInt(src, 16).

    Only the longest leading run of hex digits is read; a string with no digits at
    all yields NaN, which then flows on through the rules as an unmatchable value.
    """
    pos = 0
    while pos < len(src) and src[pos] in JS_WHITESPACE:
        pos += 1
    sign = 1
    if pos < len(src) and src[pos] in "+-":
        sign = -1 if src[pos] == "-" else 1
        pos += 1
    if src[pos : pos + 2].lower() == "0x":
        pos += 2
    end = pos
    while end < len(src) and src[end] in HEX_DIGITS:
        end += 1
    if end == pos:
        return float("nan")
    return sign * int(src[pos:end], 16)


def parse_char(src: str, pos: int) -> Tuple[Union[int, float], int]:
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        next_char = src[pos + 1] if pos + 1 < len(src) else ""
        if next_char == "x":
            return (parse_hex(src[pos + 2 : pos + 4]), 4)
        if next_char == "u":
            return (parse_hex(src[pos + 2 : pos + 6]), 6)
        if next_char == "U":
            return (parse_hex(src[pos + 2 : pos + 10]), 10)
        if next_char in ESCAPE_CHARS:
            return (ESCAPE_CHARS[next_char], 2)
        if next_char in LITERAL_ESCAPES:
            return (ord(next_char), 2)
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    return (ord(src[pos]), 1)
