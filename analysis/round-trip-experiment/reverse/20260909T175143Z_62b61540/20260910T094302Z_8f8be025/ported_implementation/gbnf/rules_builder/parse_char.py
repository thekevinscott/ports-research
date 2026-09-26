from ..utils.char_at import char_at
from ..utils.errors import GrammarParseError

ESCAPE_CHARS: dict[str, int] = {
    "t": 9,
    "r": 13,
    "n": 10,
}

LITERAL_ESCAPES = ['"', "[", "]", "\\"]


def parse_char(src: str, pos: int) -> tuple[int, int]:
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        next_ = char_at(src, pos + 1)
        if next_ == "x":
            return int(src[pos + 2 : pos + 4], 16), 4
        if next_ == "u":
            return int(src[pos + 2 : pos + 6], 16), 6
        if next_ == "U":
            return int(src[pos + 2 : pos + 10], 16), 10
        if next_ in ESCAPE_CHARS:
            return ESCAPE_CHARS[next_], 2
        if next_ in LITERAL_ESCAPES:
            return ord(next_), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    return ord(src[pos]), 1
