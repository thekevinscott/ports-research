from typing import Optional, Tuple

from ..utils.errors import GrammarParseError

ESCAPE_SEQUENCES = {
    "t": 9,
    "r": 13,
    "n": 10,
}

LITERAL_ESCAPES = ['"', "[", "]", "\\"]


def char_at(src: str, pos: int) -> Optional[str]:
    """The character at `pos`, or None when out of bounds."""
    return src[pos] if 0 <= pos < len(src) else None


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    """Returns the code point at `pos`, along with the number of characters it consumed."""
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        next_char = char_at(src, pos + 1)
        if next_char == "x":
            return int(src[pos + 2 : pos + 4], 16), 4
        if next_char == "u":
            return int(src[pos + 2 : pos + 6], 16), 6
        if next_char == "U":
            return int(src[pos + 2 : pos + 10], 16), 10
        if next_char in ESCAPE_SEQUENCES:
            return ESCAPE_SEQUENCES[next_char], 2
        if next_char in LITERAL_ESCAPES:
            return ord(next_char), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    return ord(src[pos]), 1
