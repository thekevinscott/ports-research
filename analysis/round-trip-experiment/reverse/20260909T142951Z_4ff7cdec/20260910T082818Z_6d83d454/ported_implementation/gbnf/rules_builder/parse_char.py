from typing import Optional, Tuple

from ..utils.errors import GrammarParseError

ESCAPE_CHARS = {
    "t": 9,
    "r": 13,
    "n": 10,
}

LITERAL_ESCAPE_CHARS = ['"', "[", "]", "\\"]


def _char_at(src: str, pos: int) -> Optional[str]:
    return src[pos] if 0 <= pos < len(src) else None


def _parse_hex(src: str, pos: int, length: int) -> int:
    return int(src[pos : pos + length], 16)


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        escaped = _char_at(src, pos + 1)
        if escaped == "x":
            return _parse_hex(src, pos + 2, 2), 4
        if escaped == "u":
            return _parse_hex(src, pos + 2, 4), 6
        if escaped == "U":
            return _parse_hex(src, pos + 2, 8), 10
        escape_char = ESCAPE_CHARS.get(escaped) if escaped is not None else None
        if escape_char is not None:
            return escape_char, 2
        if escaped in LITERAL_ESCAPE_CHARS:
            return ord(escaped), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    return ord(src[pos]), 1
