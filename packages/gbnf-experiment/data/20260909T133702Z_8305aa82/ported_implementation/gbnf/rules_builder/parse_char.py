from typing import Tuple

from ..utils.errors.grammar_parse_error import GrammarParseError


def _at(src: str, pos: int) -> str:
    return src[pos] if 0 <= pos < len(src) else ""


def _parse_hex(src: str, pos: int, start: int, end: int) -> int:
    try:
        return int(src[start:end], 16)
    except ValueError:
        raise GrammarParseError(
            src, pos, f"Invalid hex escape at {pos}"
        ) from None


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if _at(src, pos) == "\\":
        escape = _at(src, pos + 1)
        if escape == "x":
            return (_parse_hex(src, pos, pos + 2, pos + 4), 4)
        if escape == "u":
            return (_parse_hex(src, pos, pos + 2, pos + 6), 6)
        if escape == "U":
            return (_parse_hex(src, pos, pos + 2, pos + 10), 10)
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
