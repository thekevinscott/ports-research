from __future__ import annotations

import re
from typing import Optional, Tuple

from ..utils.errors.grammar_parse_error import GrammarParseError

ESCAPED_CHARS = {
    "t": 9,
    "r": 13,
    "n": 10,
}

HEX_ESCAPES = {
    "x": 4,
    "u": 6,
    "U": 10,
}

LITERAL_ESCAPES = ['"', "[", "]", "\\"]

HEX_DIGITS = re.compile(r"^[0-9a-fA-F]+$")


def _char_at(src: str, pos: int) -> Optional[str]:
    """The character at `pos`, or None when `pos` is out of bounds."""
    return src[pos] if 0 <= pos < len(src) else None


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    """Parse a single (possibly escaped) character out of `src` at `pos`.

    Returns a tuple of the character's code point and the number of characters consumed.
    """
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        escaped = _char_at(src, pos + 1)

        hex_length = HEX_ESCAPES.get(escaped) if escaped is not None else None
        if hex_length is not None:
            hex_value = src[pos + 2 : pos + hex_length]
            if HEX_DIGITS.match(hex_value) is None:
                raise GrammarParseError(
                    src,
                    pos,
                    f"Invalid hex escape at {src[pos]}",
                )
            return (int(hex_value, 16), hex_length)

        if escaped in ESCAPED_CHARS:
            return (ESCAPED_CHARS[escaped], 2)

        if escaped in LITERAL_ESCAPES:
            return (ord(escaped), 2)

        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    return (ord(src[pos]), 1)
