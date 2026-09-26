from typing import Dict, Optional, Tuple

from ..utils.errors import GrammarParseError

ESCAPE_CHARACTERS: Dict[str, str] = {
    "t": "\t",
    "r": "\r",
    "n": "\n",
}

LITERAL_ESCAPES = ['"', "[", "]", "\\"]


def char_at(src: str, pos: int) -> Optional[str]:
    """Index like JavaScript does: out of bounds yields nothing rather than raising."""
    return src[pos] if 0 <= pos < len(src) else None


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        escaped = char_at(src, pos + 1)
        if escaped == "x":
            return int(src[pos + 2 : pos + 4], 16), 4
        if escaped == "u":
            return int(src[pos + 2 : pos + 6], 16), 6
        if escaped == "U":
            return int(src[pos + 2 : pos + 10], 16), 10
        if escaped is not None and escaped in ESCAPE_CHARACTERS:
            return ord(ESCAPE_CHARACTERS[escaped]), 2
        if escaped in LITERAL_ESCAPES:
            return ord(escaped), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    return ord(src[pos]), 1
