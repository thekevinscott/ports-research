import re
from typing import Tuple

from ..utils.errors.grammar_parse_error import GrammarParseError

_HEX_PREFIX = re.compile(r"^[0-9a-fA-F]+")


def _parse_hex(src: str) -> int:
    """Parse a leading run of hex digits, the way JS's parseInt(str, 16) does."""
    match = _HEX_PREFIX.search(src)
    if match is None:
        raise GrammarParseError(src, 0, f"Could not parse hex value from {src}")
    return int(match.group(0), 16)


def _at(src: str, pos: int) -> str:
    return src[pos] if 0 <= pos < len(src) else ""


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if _at(src, pos) == "\\":
        escaped = _at(src, pos + 1)
        if escaped == "x":
            return _parse_hex(src[pos + 2 : pos + 4]), 4
        if escaped == "u":
            return _parse_hex(src[pos + 2 : pos + 6]), 6
        if escaped == "U":
            return _parse_hex(src[pos + 2 : pos + 10]), 10
        if escaped == "t":
            return ord("\t"), 2
        if escaped == "r":
            return ord("\r"), 2
        if escaped == "n":
            return ord("\n"), 2
        if escaped in ('"', "[", "]"):
            return ord(src[pos + 1]), 2
        if escaped == "\\":
            code_point = _at(src, pos + 1)
            if not code_point:
                raise GrammarParseError(src, pos, "Could not get code point for character")
            return ord(code_point), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    if not _at(src, pos):
        raise GrammarParseError(
            src, pos, "Unexpected end of grammar input, failed to complete parse"
        )
    return ord(src[pos]), 1
