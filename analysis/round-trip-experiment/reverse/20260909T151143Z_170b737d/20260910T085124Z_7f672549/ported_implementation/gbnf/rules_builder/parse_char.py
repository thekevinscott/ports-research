from typing import Tuple

from ..utils.errors import GrammarParseError

ESCAPED_CONTROL_CHARS = {
    "t": "\t",
    "r": "\r",
    "n": "\n",
}

ESCAPED_LITERAL_CHARS = ['"', "[", "]", "\\"]


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    """Return a `(code point, characters consumed)` pair."""
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        escaped = src[pos + 1]
        if escaped == "x":
            return int(src[pos + 2 : pos + 4], 16), 4
        if escaped == "u":
            return int(src[pos + 2 : pos + 6], 16), 6
        if escaped == "U":
            return int(src[pos + 2 : pos + 10], 16), 10
        if escaped in ESCAPED_CONTROL_CHARS:
            return ord(ESCAPED_CONTROL_CHARS[escaped]), 2
        if escaped in ESCAPED_LITERAL_CHARS:
            return ord(escaped), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    return ord(src[pos]), 1
