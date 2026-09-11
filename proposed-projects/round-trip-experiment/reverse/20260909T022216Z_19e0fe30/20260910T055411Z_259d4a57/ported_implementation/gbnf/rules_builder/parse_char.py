import re
from typing import Tuple

from ..utils.errors import GrammarParseError

ESCAPED_CONTROL_CHARS = {
    "t": ord("\t"),
    "r": ord("\r"),
    "n": ord("\n"),
}

ESCAPED_LITERAL_CHARS = ['"', "[", "]", "\\"]

_HEX = re.compile(r"^[0-9a-fA-F]+$")


def _parse_hex(raw: str) -> int:
    if not _HEX.match(raw):
        raise ValueError(f'Invalid hexadecimal escape sequence: "{raw}"')
    return int(raw, 16)


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    """Parse a single character at ``pos``.

    Returns its code point along with the number of characters consumed.
    """
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            "Unexpected end of grammar input, failed to complete parse",
        )

    if src[pos] == "\\":
        escaped = src[pos + 1] if pos + 1 < len(src) else ""
        if escaped == "x":
            return (_parse_hex(src[pos + 2 : pos + 4]), 4)
        if escaped == "u":
            return (_parse_hex(src[pos + 2 : pos + 6]), 6)
        if escaped == "U":
            return (_parse_hex(src[pos + 2 : pos + 10]), 10)
        if escaped in ESCAPED_CONTROL_CHARS:
            return (ESCAPED_CONTROL_CHARS[escaped], 2)
        if escaped in ESCAPED_LITERAL_CHARS:
            return (ord(escaped), 2)
        raise GrammarParseError(src, pos, f"Unknown escape at {src[pos]}")

    return (ord(src[pos]), 1)
