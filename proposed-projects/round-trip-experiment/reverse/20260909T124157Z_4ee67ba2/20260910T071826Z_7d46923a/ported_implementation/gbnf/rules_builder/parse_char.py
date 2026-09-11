from typing import Optional, Tuple

from ..utils.errors import GrammarParseError


def _parse_hex(src: str, pos: int, value: str) -> int:
    """Mirrors Python's `int(value, 16)`: the whole slice must be a hex literal."""
    try:
        return int(value, 16)
    except ValueError:
        raise GrammarParseError(src, pos, f"Invalid hex escape: {value}") from None


ESCAPE_CHARS = {
    "t": 0x09,
    "r": 0x0D,
    "n": 0x0A,
}

LITERAL_ESCAPE_CHARS = ['"', "[", "]", "\\"]


def _char_at(src: str, pos: int) -> Optional[str]:
    return src[pos] if 0 <= pos < len(src) else None


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        next_char = _char_at(src, pos + 1)
        if next_char == "x":
            return _parse_hex(src, pos, src[pos + 2 : pos + 4]), 4
        if next_char == "u":
            return _parse_hex(src, pos, src[pos + 2 : pos + 6]), 6
        if next_char == "U":
            return _parse_hex(src, pos, src[pos + 2 : pos + 10]), 10
        if next_char in ESCAPE_CHARS:
            return ESCAPE_CHARS[next_char], 2
        if next_char in LITERAL_ESCAPE_CHARS:
            return ord(next_char), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    return ord(src[pos]), 1
