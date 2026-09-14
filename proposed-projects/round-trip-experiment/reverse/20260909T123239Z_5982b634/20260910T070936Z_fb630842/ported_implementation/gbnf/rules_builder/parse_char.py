from __future__ import annotations

from typing import Tuple

from ..utils.errors import GrammarParseError
from .char_at import char_at

ESCAPED_CONTROL_CHARS = {
    't': '\t',
    'r': '\r',
    'n': '\n',
}

ESCAPED_LITERAL_CHARS = ['"', '[', ']', '\\']

_HEX_DIGITS = '0123456789abcdefABCDEF'


def _parse_int_16(src: str) -> float:
    """Parse a hexadecimal prefix, mirroring JavaScript's `parseInt(src, 16)`."""
    stripped = src.lstrip()
    end = 0
    while end < len(stripped) and stripped[end] in _HEX_DIGITS:
        end += 1
    if end == 0:
        return float('nan')
    return int(stripped[:end], 16)


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if pos >= len(src):
        raise GrammarParseError(
            src,
            pos,
            'Unexpected end of grammar input, failed to complete parse',
        )

    if src[pos] == '\\':
        escaped = char_at(src, pos + 1)
        if escaped == 'x':
            return (_parse_int_16(src[pos + 2 : pos + 4]), 4)
        if escaped == 'u':
            return (_parse_int_16(src[pos + 2 : pos + 6]), 6)
        if escaped == 'U':
            return (_parse_int_16(src[pos + 2 : pos + 10]), 10)
        if escaped in ESCAPED_CONTROL_CHARS:
            return (ord(ESCAPED_CONTROL_CHARS[escaped]), 2)
        if escaped in ESCAPED_LITERAL_CHARS:
            return (ord(escaped), 2)
        raise GrammarParseError(src, pos, f'Unknown escape at {src[pos]}')

    return (ord(src[pos]), 1)
