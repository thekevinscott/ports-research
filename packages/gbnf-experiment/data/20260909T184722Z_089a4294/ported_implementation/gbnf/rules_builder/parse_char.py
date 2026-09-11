from __future__ import annotations

from ..utils.errors.grammar_parse_error import GrammarParseError
from .parse_space import char_at


def parse_char(src: str, pos: int) -> tuple[int, int]:
    if char_at(src, pos) == "\\":
        escape = char_at(src, pos + 1)
        if escape == "x":
            return (int(src[pos + 2 : pos + 4], 16), 4)
        if escape == "u":
            return (int(src[pos + 2 : pos + 6], 16), 6)
        if escape == "U":
            return (int(src[pos + 2 : pos + 10], 16), 10)
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

    if not char_at(src, pos):
        raise GrammarParseError(
            src, pos, "Unexpected end of grammar input, failed to complete parse"
        )
    return (ord(src[pos]), 1)
