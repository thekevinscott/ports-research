from ..utils.errors import GrammarParseError
from .char_at import char_at

ESCAPE_CHARS = {
    "t": "\t",
    "r": "\r",
    "n": "\n",
}

LITERAL_ESCAPES = ['"', "[", "]", "\\"]


def _parse_hex(src: str, start: int, end: int, pos: int) -> int:
    try:
        return int(src[start:end], 16)
    except ValueError:
        raise GrammarParseError(
            src, pos, f"Failed to parse hex escape at {pos}"
        ) from None


def parse_char(src: str, pos: int) -> tuple[int, int]:
    if pos >= len(src):
        raise GrammarParseError(
            src, pos, "Unexpected end of grammar input, failed to complete parse"
        )

    if src[pos] == "\\":
        next_char = char_at(src, pos + 1)
        if next_char == "x":
            return _parse_hex(src, pos + 2, pos + 4, pos), 4
        if next_char == "u":
            return _parse_hex(src, pos + 2, pos + 6, pos), 6
        if next_char == "U":
            return _parse_hex(src, pos + 2, pos + 10, pos), 10
        if next_char in ESCAPE_CHARS:
            return ord(ESCAPE_CHARS[next_char]), 2
        if next_char in LITERAL_ESCAPES:
            return ord(next_char), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    return ord(src[pos]), 1
