import re
from typing import Tuple

from ..utils.errors.grammar_parse_error import GrammarParseError
from .char_at import char_at

# mirrors parseInt(str, 16): leading whitespace and sign are allowed, an optional 0x
# prefix is consumed, and parsing stops at the first character that is not a hex digit.
JS_PARSE_INT_HEX = re.compile(r"^\s*([+-]?)(?:0[xX])?([0-9a-fA-F]*)")


def _parse_hex(src: str, pos: int, start: int, end: int) -> int:
    digits = src[start:end]
    sign, hex_digits = JS_PARSE_INT_HEX.match(digits).groups()
    if not hex_digits:
        # parseInt would return NaN here, which the reference implementation goes on to
        # store as an unmatchable code point; failing loudly is more useful.
        raise GrammarParseError(src, pos, f'Invalid hex escape "{digits}"')
    return int(hex_digits, 16) * (-1 if sign == "-" else 1)


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    """Returns the code point at pos, and how far to advance past it."""
    if char_at(src, pos) == "\\":
        escape = char_at(src, pos + 1)
        if escape == "x":
            return _parse_hex(src, pos, pos + 2, pos + 4), 4
        if escape == "u":
            return _parse_hex(src, pos, pos + 2, pos + 6), 6
        if escape == "U":
            return _parse_hex(src, pos, pos + 2, pos + 10), 10
        if escape == "t":
            return ord("\t"), 2
        if escape == "r":
            return ord("\r"), 2
        if escape == "n":
            return ord("\n"), 2
        if escape in ('"', "[", "]", "\\"):
            return ord(escape), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {char_at(src, pos)}")

    if not char_at(src, pos):
        raise GrammarParseError(
            src, pos, "Unexpected end of grammar input, failed to complete parse"
        )
    return ord(src[pos]), 1
