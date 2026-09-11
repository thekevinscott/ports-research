from ..utils.errors import GrammarParseError

SIMPLE_ESCAPES = {
    "t": "\t",
    "r": "\r",
    "n": "\n",
}

LITERAL_ESCAPES = ['"', "[", "]", "\\"]


def _char_at(src: str, pos: int) -> str:
    return src[pos] if 0 <= pos < len(src) else ""


def parse_char(src: str, pos: int) -> tuple[int, int]:
    """Returns the parsed code point and the number of characters it consumed."""
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        next_ = _char_at(src, pos + 1)
        if next_ == "x":
            return int(src[pos + 2 : pos + 4], 16), 4
        if next_ == "u":
            return int(src[pos + 2 : pos + 6], 16), 6
        if next_ == "U":
            return int(src[pos + 2 : pos + 10], 16), 10
        if next_ in SIMPLE_ESCAPES:
            return ord(SIMPLE_ESCAPES[next_]), 2
        if next_ in LITERAL_ESCAPES:
            return ord(next_), 2
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    return ord(src[pos]), 1
