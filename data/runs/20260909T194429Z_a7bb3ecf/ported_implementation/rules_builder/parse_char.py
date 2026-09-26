from __future__ import annotations

from typing import Tuple

from ..utils.errors.grammar_parse_error import GrammarParseError
from ..utils.js import char_at, js_parse_int_hex


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    if char_at(src, pos) == '\\':
        escaped = char_at(src, pos + 1)
        if escaped == 'x':
            return js_parse_int_hex(src[pos + 2:pos + 4]), 4
        if escaped == 'u':
            return js_parse_int_hex(src[pos + 2:pos + 6]), 6
        if escaped == 'U':
            return js_parse_int_hex(src[pos + 2:pos + 10]), 10
        if escaped == 't':
            return ord('\t'), 2
        if escaped == 'r':
            return ord('\r'), 2
        if escaped == 'n':
            return ord('\n'), 2
        if escaped in ('"', '[', ']'):
            return ord(src[pos + 1]), 2
        if escaped == '\\':
            code_point = char_at(src, pos + 1)
            if not code_point:
                raise GrammarParseError(src, pos, 'Could not get code point for character')
            return ord(code_point), 2
        raise GrammarParseError(src, pos, f'Unknown escape at {char_at(src, pos)}')

    if not char_at(src, pos):
        raise GrammarParseError(src, pos, 'Unexpected end of grammar input, failed to complete parse')
    return ord(src[pos]), 1
