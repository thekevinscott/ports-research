"""Port of ``src/rules-builder/parse-char.ts``."""

from __future__ import annotations

from typing import Tuple

from ..utils.errors.grammar_parse_error import GrammarParseError
from .char_at import char_at

_HEX_DIGITS = '0123456789abcdefABCDEF'


def _parse_hex(src: str, start: int, end: int, pos: int) -> int:
    """``parseInt(slice, 16)``: consume the leading hex digits, ignore the rest."""
    digits = ''
    for char in src[start:end]:
        if char not in _HEX_DIGITS:
            break
        digits += char
    if not digits:
        raise GrammarParseError(src, pos, 'Could not parse hex escape')
    return int(digits, 16)


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if char_at(src, pos) == '\\':
        next_char = char_at(src, pos + 1)
        if next_char == 'x':
            return _parse_hex(src, pos + 2, pos + 4, pos), 4
        if next_char == 'u':
            return _parse_hex(src, pos + 2, pos + 6, pos), 6
        if next_char == 'U':
            return _parse_hex(src, pos + 2, pos + 10, pos), 10
        if next_char == 't':
            return ord('\t'), 2
        if next_char == 'r':
            return ord('\r'), 2
        if next_char == 'n':
            return ord('\n'), 2
        if next_char in ('"', '[', ']'):
            return ord(next_char), 2
        if next_char == '\\':
            if not next_char:
                raise GrammarParseError(src, pos, 'Could not get code point for character')
            return ord(next_char), 2
        raise GrammarParseError(src, pos, f'Unknown escape at {char_at(src, pos)}')

    if not char_at(src, pos):
        raise GrammarParseError(
            src, pos, 'Unexpected end of grammar input, failed to complete parse'
        )
    return ord(src[pos]), 1
