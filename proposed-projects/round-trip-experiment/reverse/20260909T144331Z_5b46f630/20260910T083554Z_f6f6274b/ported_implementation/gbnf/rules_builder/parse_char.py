import re
from typing import Tuple

from ..utils.errors import GrammarParseError
from .char_at import char_at

ESCAPE_CHARACTERS = {
    "t": 9,
    "r": 13,
    "n": 10,
}

LITERAL_ESCAPES = ['"', "[", "]", "\\"]

HEX = re.compile(r"^[0-9a-fA-F]+$")


def _parse_hex(src: str, start: int, end: int, pos: int) -> int:
    hex_digits = src[start:end]
    if len(hex_digits) != end - start or not HEX.match(hex_digits):
        raise GrammarParseError(src, pos, f"Invalid hex escape at {pos}")
    return int(hex_digits, 16)


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    """Parse a single character from the grammar, returning its code point along with the
    number of characters consumed."""
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        escaped = char_at(src, pos + 1)
        if escaped == "x":
            return _parse_hex(src, pos + 2, pos + 4, pos), 4
        if escaped == "u":
            return _parse_hex(src, pos + 2, pos + 6, pos), 6
        if escaped == "U":
            return _parse_hex(src, pos + 2, pos + 10, pos), 10
        if escaped is not None and escaped in ESCAPE_CHARACTERS:
            return ESCAPE_CHARACTERS[escaped], 2
        if escaped is not None and escaped in LITERAL_ESCAPES:
            return ord(escaped), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    # Python strings are indexed by code point, so every character - astral or not -
    # occupies exactly one position.
    return ord(src[pos]), 1
