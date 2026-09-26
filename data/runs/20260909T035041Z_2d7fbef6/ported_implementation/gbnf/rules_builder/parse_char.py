from __future__ import annotations

from ..utils.errors.grammar_parse_error import GrammarParseError
from ..utils.js import char_at, char_code_at, code_point_at, parse_int


def parse_char(src: str, pos: int) -> tuple[int, int]:
    """Parse the character at ``pos``, returning ``(code point, chars consumed)``."""
    if char_at(src, pos) == "\\":
        escape = char_at(src, pos + 1)
        if escape == "x":
            return (parse_int(src[pos + 2 : pos + 4], 16), 4)
        if escape == "u":
            return (parse_int(src[pos + 2 : pos + 6], 16), 6)
        if escape == "U":
            return (parse_int(src[pos + 2 : pos + 10], 16), 10)
        if escape == "t":
            return (ord("\t"), 2)
        if escape == "r":
            return (ord("\r"), 2)
        if escape == "n":
            return (ord("\n"), 2)
        if escape in ('"', "[", "]"):
            return (char_code_at(src, pos + 1), 2)
        if escape == "\\":
            code_point = code_point_at(src, pos + 1)
            if code_point is None:
                raise GrammarParseError(src, pos, "Could not get code point for character")
            return (code_point, 2)
        raise GrammarParseError(src, pos, f"Unknown escape at {char_at(src, pos)}")

    if not char_at(src, pos):
        raise GrammarParseError(
            src, pos, "Unexpected end of grammar input, failed to complete parse"
        )
    return (char_code_at(src, pos), 1)
