"""Port of ``src/rules-builder/parse-char.ts``."""
from __future__ import annotations

from typing import Optional, Tuple

from ..utils.errors.grammar_parse_error import GrammarParseError


def _parse_int_prefix(text: str, base: int) -> Optional[int]:
    """``parseInt`` semantics: consume the valid prefix, ``None`` where JS gives NaN."""
    digits = ''
    for char in text:
        try:
            int(char, base)
        except ValueError:
            break
        digits += char
    return int(digits, base) if digits else None


def parse_char(src: str, pos: int) -> Tuple[int, int]:
    def at(i: int) -> str:
        return src[i] if 0 <= i < len(src) else ''

    if at(pos) == '\\':
        escape = at(pos + 1)
        if escape == 'x':
            return (_parse_int_prefix(src[pos + 2:pos + 4], 16), 4)
        if escape == 'u':
            return (_parse_int_prefix(src[pos + 2:pos + 6], 16), 6)
        if escape == 'U':
            return (_parse_int_prefix(src[pos + 2:pos + 10], 16), 10)
        if escape == 't':
            return (ord('\t'), 2)
        if escape == 'r':
            return (ord('\r'), 2)
        if escape == 'n':
            return (ord('\n'), 2)
        if escape in ('"', '[', ']'):
            return (ord(src[pos + 1]), 2)
        if escape == '\\':
            code_point = at(pos + 1)
            if not code_point:
                raise GrammarParseError(src, pos, 'Could not get code point for character')
            return (ord(code_point), 2)
        raise GrammarParseError(src, pos, f'Unknown escape at {src[pos]}')

    if not at(pos):
        raise GrammarParseError(
            src, pos, 'Unexpected end of grammar input, failed to complete parse')
    return (ord(src[pos]), 1)
