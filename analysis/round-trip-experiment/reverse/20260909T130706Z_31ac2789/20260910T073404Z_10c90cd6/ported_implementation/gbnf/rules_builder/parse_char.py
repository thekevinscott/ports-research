from typing import Tuple

from ..utils.errors import GrammarParseError

ESCAPE_CHARS = {
    "t": 9,
    "r": 13,
    "n": 10,
}

ESCAPED_LITERALS = ['"', "[", "]", "\\"]


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    """Parse a single character (or escape sequence) at ``pos``.

    Returns the character's code point, along with the number of characters
    that were consumed.
    """
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        next_char = src[pos + 1] if pos + 1 < len(src) else ""
        if next_char == "x":
            return int(src[pos + 2 : pos + 4], 16), 4
        if next_char == "u":
            return int(src[pos + 2 : pos + 6], 16), 6
        if next_char == "U":
            return int(src[pos + 2 : pos + 10], 16), 10
        if next_char in ESCAPE_CHARS:
            return ESCAPE_CHARS[next_char], 2
        if next_char in ESCAPED_LITERALS:
            return ord(next_char), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    # Python strings are indexed by code point, so every character - astral or
    # not - is a single position wide.
    return ord(src[pos]), 1


parseChar = parse_char
