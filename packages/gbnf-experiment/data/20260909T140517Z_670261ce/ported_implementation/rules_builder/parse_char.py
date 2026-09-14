"""Port of ``src/rules-builder/parse-char.ts``."""

from __future__ import annotations

from typing import Tuple

from ..utils.errors.grammar_parse_error import GrammarParseError
from ..utils.js import char_at, parse_hex


def _hex(src: str, pos: int, start: int, end: int, width: int) -> Tuple[int, int]:
    value = parse_hex(src[start:end])
    if value is None:
        raise GrammarParseError(src, pos, f"Unknown escape at {char_at(src, pos)}")
    return (value, width)


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if char_at(src, pos) == "\\":
        escape = char_at(src, pos + 1)
        if escape == "x":
            return _hex(src, pos, pos + 2, pos + 4, 4)
        if escape == "u":
            return _hex(src, pos, pos + 2, pos + 6, 6)
        if escape == "U":
            return _hex(src, pos, pos + 2, pos + 10, 10)
        if escape == "t":
            return (ord("\t"), 2)
        if escape == "r":
            return (ord("\r"), 2)
        if escape == "n":
            return (ord("\n"), 2)
        if escape in ('"', "[", "]"):
            return (ord(src[pos + 1]), 2)
        if escape == "\\":
            code_point = char_at(src, pos + 1)
            if not code_point:
                raise GrammarParseError(src, pos, "Could not get code point for character")
            return (ord(code_point), 2)
        raise GrammarParseError(src, pos, f"Unknown escape at {char_at(src, pos)}")

    if not char_at(src, pos):
        raise GrammarParseError(
            src, pos, "Unexpected end of grammar input, failed to complete parse"
        )
    return (ord(src[pos]), 1)


parseChar = parse_char
