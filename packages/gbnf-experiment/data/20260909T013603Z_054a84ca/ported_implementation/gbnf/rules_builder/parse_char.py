from __future__ import annotations

from typing import Tuple

from ..utils.errors.grammar_parse_error import GrammarParseError
from ..utils.js import char_at, parse_int_hex


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if char_at(src, pos) == '\\':
        escape = char_at(src, pos + 1)
        if escape in ('x', 'u', 'U'):
            width = {'x': 4, 'u': 6, 'U': 10}[escape]
            code_point = parse_int_hex(src[pos + 2:pos + width])
            if code_point is None:
                raise GrammarParseError(src, pos, f'Invalid escape at {char_at(src, pos)}')
            return (code_point, width)
        if escape == 't':
            return (ord('\t'), 2)
        if escape == 'r':
            return (ord('\r'), 2)
        if escape == 'n':
            return (ord('\n'), 2)
        if escape in ('"', '[', ']'):
            return (ord(src[pos + 1]), 2)
        if escape == '\\':
            code_point = char_at(src, pos + 1)
            if code_point == '':
                raise GrammarParseError(src, pos, 'Could not get code point for character')
            return (ord(code_point), 2)
        raise GrammarParseError(src, pos, f'Unknown escape at {char_at(src, pos)}')

    if not char_at(src, pos):
        raise GrammarParseError(src, pos, 'Unexpected end of grammar input, failed to complete parse')
    return (ord(src[pos]), 1)
