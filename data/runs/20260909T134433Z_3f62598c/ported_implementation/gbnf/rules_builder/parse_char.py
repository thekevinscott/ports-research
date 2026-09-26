from typing import Tuple

from ..utils.char_at import char_at
from ..utils.errors.grammar_parse_error import GrammarParseError


_HEX_DIGITS = "0123456789abcdefABCDEF"


def _parse_hex(src: str, pos: int, start: int, end: int, size: int) -> Tuple[int, int]:
    # `parseInt` skips leading whitespace, accepts a sign, and stops at the first
    # non-hex character rather than failing, so only that prefix is consumed
    slice_ = src[start:end].lstrip(" \t\n\r\f\v ")
    sign = 1
    if slice_[:1] in ("+", "-"):
        sign = -1 if slice_[0] == "-" else 1
        slice_ = slice_[1:]
    digits = 0
    while digits < len(slice_) and slice_[digits] in _HEX_DIGITS:
        digits += 1
    if digits == 0:
        # the reference yields NaN here, which builds a rule that can never match
        raise GrammarParseError(
            src, pos, f'Invalid escape sequence "{src[pos:end]}"'
        )
    return sign * int(slice_[:digits], 16), size


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if char_at(src, pos) == "\\":
        escape = char_at(src, pos + 1)
        if escape == "x":
            return _parse_hex(src, pos, pos + 2, pos + 4, 4)
        if escape == "u":
            return _parse_hex(src, pos, pos + 2, pos + 6, 6)
        if escape == "U":
            return _parse_hex(src, pos, pos + 2, pos + 10, 10)
        if escape == "t":
            return ord("\t"), 2
        if escape == "r":
            return ord("\r"), 2
        if escape == "n":
            return ord("\n"), 2
        if escape in ('"', "[", "]"):
            return ord(src[pos + 1]), 2
        if escape == "\\":
            return ord(src[pos + 1]), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {char_at(src, pos)}")

    if not char_at(src, pos):
        raise GrammarParseError(
            src, pos, "Unexpected end of grammar input, failed to complete parse"
        )
    return ord(src[pos]), 1
