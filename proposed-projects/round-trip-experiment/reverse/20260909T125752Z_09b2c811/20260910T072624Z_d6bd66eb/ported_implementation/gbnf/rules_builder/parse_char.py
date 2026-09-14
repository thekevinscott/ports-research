"""Parse a single (possibly escaped) character out of a grammar."""

from typing import Optional, Tuple

from ..utils.errors import GrammarParseError

ESCAPED_CONTROL_CHARS = {
    "t": 9,
    "r": 13,
    "n": 10,
}

ESCAPED_LITERAL_CHARS = ['"', "[", "]", "\\"]


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        next_char: Optional[str] = src[pos + 1] if pos + 1 < len(src) else None
        if next_char == "x":
            return int(src[pos + 2 : pos + 4], 16), 4
        if next_char == "u":
            return int(src[pos + 2 : pos + 6], 16), 6
        if next_char == "U":
            return int(src[pos + 2 : pos + 10], 16), 10
        if next_char in ESCAPED_CONTROL_CHARS:
            return ESCAPED_CONTROL_CHARS[next_char], 2
        if next_char in ESCAPED_LITERAL_CHARS:
            return ord(next_char), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    return ord(src[pos]), 1
