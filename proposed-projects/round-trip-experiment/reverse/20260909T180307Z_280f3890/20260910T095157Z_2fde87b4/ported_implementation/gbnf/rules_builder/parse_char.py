from typing import Optional, Tuple

from ..utils.errors import GrammarParseError

ESCAPE_SEQUENCES = {
    "t": 0x09,
    "r": 0x0D,
    "n": 0x0A,
    '"': 0x22,
    "[": 0x5B,
    "]": 0x5D,
    "\\": 0x5C,
}

_HEX_DIGITS = "0123456789abcdefABCDEF"


def _parse_int_hex(hex: str) -> Optional[int]:
    """Parse a hex string the way `Number.parseInt(s, 16)` does.

    Leading whitespace and an optional sign are skipped, then the longest run of
    hex digits is used; anything after it is ignored. `None` stands in for `NaN`.
    """
    idx = 0
    while idx < len(hex) and hex[idx].isspace():
        idx += 1
    sign = 1
    if idx < len(hex) and hex[idx] in "+-":
        if hex[idx] == "-":
            sign = -1
        idx += 1
    start = idx
    while idx < len(hex) and hex[idx] in _HEX_DIGITS:
        idx += 1
    if idx == start:
        return None
    return sign * int(hex[start:idx], 16)


def _parse_hex(src: str, start: int, end: int, pos: int) -> int:
    hex = src[start:end]
    value = _parse_int_hex(hex)
    if len(hex) != end - start or value is None:
        raise GrammarParseError(src, pos, f"Invalid escape sequence at {pos}")
    return value


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    """Parse a single (possibly escaped) character out of `src` at `pos`.

    Returns the code point along with the number of characters consumed.
    """
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        next_char = src[pos + 1] if pos + 1 < len(src) else None
        if next_char == "x":
            return _parse_hex(src, pos + 2, pos + 4, pos), 4
        if next_char == "u":
            return _parse_hex(src, pos + 2, pos + 6, pos), 6
        if next_char == "U":
            return _parse_hex(src, pos + 2, pos + 10, pos), 10
        if next_char is not None and next_char in ESCAPE_SEQUENCES:
            return ESCAPE_SEQUENCES[next_char], 2
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    # Python indexes strings by code point, so every character advances by one.
    return ord(src[pos]), 1
