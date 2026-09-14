from typing import Tuple

from ..utils.errors.grammar_parse_error import GrammarParseError
from ..utils.js import char_at, slice_


def _parse_hex(src: str, pos: int, start: int, end: int) -> int:
    """``parseInt(src.slice(start, end), 16)``.

    JS yields NaN for a non-hex slice; we raise instead, since a NaN code point
    would silently produce an unmatchable rule.
    """
    raw = slice_(src, start, end)
    digits = ''
    for char in raw:
        if char in '0123456789abcdefABCDEF':
            digits += char
        else:
            break
    if not digits:
        raise GrammarParseError(src, pos, f'Invalid hex escape "{raw}"')
    return int(digits, 16)


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if char_at(src, pos) == '\\':
        escape = char_at(src, pos + 1)
        if escape == 'x':
            return (_parse_hex(src, pos, pos + 2, pos + 4), 4)
        if escape == 'u':
            return (_parse_hex(src, pos, pos + 2, pos + 6), 6)
        if escape == 'U':
            return (_parse_hex(src, pos, pos + 2, pos + 10), 10)
        if escape == 't':
            return (ord('\t'), 2)
        if escape == 'r':
            return (ord('\r'), 2)
        if escape == 'n':
            return (ord('\n'), 2)
        if escape in ('"', '[', ']'):
            return (ord(src[pos + 1]), 2)
        if escape == '\\':
            return (ord(src[pos + 1]), 2)
        raise GrammarParseError(src, pos, f'Unknown escape at {char_at(src, pos)}')

    if not char_at(src, pos):
        raise GrammarParseError(
            src, pos, 'Unexpected end of grammar input, failed to complete parse'
        )
    return (ord(src[pos]), 1)
