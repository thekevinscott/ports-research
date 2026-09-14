import re

from ..utils.errors.grammar_parse_error import GrammarParseError

_LEADING_HEX = re.compile(r"^[0-9a-fA-F]+")


def _parse_hex(src: str, start: int, end: int) -> int:
    """Mirror JS `parseInt(str, 16)`: consume the leading hex digits only."""
    match = _LEADING_HEX.match(src[start:end])
    if match is None:
        raise GrammarParseError(
            src, start, f"Failed to parse hex escape at {start}"
        )
    return int(match.group(0), 16)


def _at(src: str, pos: int) -> str:
    return src[pos] if 0 <= pos < len(src) else ""


def parse_char(src: str, pos: int) -> tuple[int, int]:
    """Returns the code point at `pos` and how far to advance past it."""
    if _at(src, pos) == "\\":
        escape = _at(src, pos + 1)
        if escape == "x":
            return (_parse_hex(src, pos + 2, pos + 4), 4)
        if escape == "u":
            return (_parse_hex(src, pos + 2, pos + 6), 6)
        if escape == "U":
            return (_parse_hex(src, pos + 2, pos + 10), 10)
        if escape == "t":
            return (ord("\t"), 2)
        if escape == "r":
            return (ord("\r"), 2)
        if escape == "n":
            return (ord("\n"), 2)
        if escape in ('"', "[", "]"):
            return (ord(src[pos + 1]), 2)
        if escape == "\\":
            return (ord(src[pos + 1]), 2)
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    if not _at(src, pos):
        raise GrammarParseError(
            src, pos, "Unexpected end of grammar input, failed to complete parse"
        )
    return (ord(src[pos]), 1)
