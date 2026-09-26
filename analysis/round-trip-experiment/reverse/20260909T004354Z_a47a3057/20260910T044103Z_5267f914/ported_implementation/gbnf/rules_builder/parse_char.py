from typing import Dict, Tuple

from ..utils.errors import GrammarParseError

ESCAPE_CODES: Dict[str, int] = {
    "t": 9,
    "r": 13,
    "n": 10,
}


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        next_char = src[pos + 1] if pos + 1 < len(src) else None
        if next_char == "x":
            return int(src[pos + 2 : pos + 4], 16), 4
        if next_char == "u":
            return int(src[pos + 2 : pos + 6], 16), 6
        if next_char == "U":
            return int(src[pos + 2 : pos + 10], 16), 10
        if next_char in ESCAPE_CODES:
            return ESCAPE_CODES[next_char], 2
        if next_char in ['"', "[", "]", "\\"]:
            return ord(next_char), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    return ord(src[pos]), 1
