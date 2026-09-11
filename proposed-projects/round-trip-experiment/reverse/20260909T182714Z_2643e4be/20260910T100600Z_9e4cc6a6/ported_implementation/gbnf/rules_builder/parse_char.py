from __future__ import annotations

from typing import Dict, Tuple

from ..utils.errors.grammar_parse_error import GrammarParseError

ESCAPED_CHARS: Dict[str, str] = {
    "t": "\t",
    "r": "\r",
    "n": "\n",
}


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        next_char = src[pos + 1]
        if next_char == "x":
            return int(src[pos + 2 : pos + 4], 16), 4
        if next_char == "u":
            return int(src[pos + 2 : pos + 6], 16), 6
        if next_char == "U":
            return int(src[pos + 2 : pos + 10], 16), 10
        if next_char in ESCAPED_CHARS:
            return ord(ESCAPED_CHARS[next_char]), 2
        if next_char in ['"', "[", "]", "\\"]:
            return ord(next_char), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    return ord(src[pos]), 1
