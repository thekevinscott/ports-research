import re
from typing import Tuple

from ..utils.errors.grammar_parse_error import GrammarParseError

_HEX_PREFIX = re.compile(r"^[+-]?[0-9a-fA-F]+")


def _parse_int_16(value: str) -> float:
    """Mimic JS `parseInt(value, 16)`: parse the longest valid prefix, else NaN."""
    match = _HEX_PREFIX.match(value.lstrip())
    if match is None:
        return float("nan")
    return int(match.group(0), 16)


def _at(src: str, pos: int):
    return src[pos] if 0 <= pos < len(src) else None


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if _at(src, pos) == "\\":
        nxt = _at(src, pos + 1)
        if nxt == "x":
            return _parse_int_16(src[pos + 2 : pos + 4]), 4
        if nxt == "u":
            return _parse_int_16(src[pos + 2 : pos + 6]), 6
        if nxt == "U":
            return _parse_int_16(src[pos + 2 : pos + 10]), 10
        if nxt == "t":
            return ord("\t"), 2
        if nxt == "r":
            return ord("\r"), 2
        if nxt == "n":
            return ord("\n"), 2
        if nxt in ('"', "[", "]"):
            return ord(src[pos + 1]), 2
        if nxt == "\\":
            code_point = _at(src, pos + 1)
            if code_point is None:
                raise GrammarParseError(
                    src, pos, "Could not get code point for character"
                )
            return ord(code_point), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    if not _at(src, pos):
        raise GrammarParseError(
            src, pos, "Unexpected end of grammar input, failed to complete parse"
        )
    return ord(src[pos]), 1
