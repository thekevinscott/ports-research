from typing import Tuple

from ..utils.char_at import char_at
from ..utils.errors.grammar_parse_error import GrammarParseError


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if char_at(src, pos) == "\\":
        escaped = char_at(src, pos + 1)
        if escaped == "x":
            return (int(src[pos + 2 : pos + 4], 16), 4)
        if escaped == "u":
            return (int(src[pos + 2 : pos + 6], 16), 6)
        if escaped == "U":
            return (int(src[pos + 2 : pos + 10], 16), 10)
        if escaped == "t":
            return (ord("\t"), 2)
        if escaped == "r":
            return (ord("\r"), 2)
        if escaped == "n":
            return (ord("\n"), 2)
        if escaped in ('"', "[", "]"):
            return (ord(src[pos + 1]), 2)
        if escaped == "\\":
            return (ord(src[pos + 1]), 2)
        raise GrammarParseError(src, pos, f"Unknown escape at {char_at(src, pos)}")

    if not char_at(src, pos):
        raise GrammarParseError(
            src, pos, "Unexpected end of grammar input, failed to complete parse"
        )
    return (ord(src[pos]), 1)
