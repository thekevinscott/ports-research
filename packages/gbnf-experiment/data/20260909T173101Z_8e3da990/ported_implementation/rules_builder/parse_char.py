from ..utils.errors.grammar_parse_error import GrammarParseError
from ..utils.strings import char_at

_HEX_DIGITS = '0123456789abcdefABCDEF'


def _parse_hex(src: str) -> int | float:
    """`parseInt(str, 16)`: consume the leading hex digits, NaN if there are none."""
    s = src.lstrip()
    sign = 1
    if s[:1] in ('+', '-'):
        sign = -1 if s[0] == '-' else 1
        s = s[1:]
    if s[:2].lower() == '0x':
        s = s[2:]
    digits = ''
    for char in s:
        if char not in _HEX_DIGITS:
            break
        digits += char
    if not digits:
        return float('nan')
    return sign * int(digits, 16)


def parse_char(src: str, pos: int) -> tuple[int | float, int]:
    if char_at(src, pos) == '\\':
        escaped = char_at(src, pos + 1)
        if escaped == 'x':
            return (_parse_hex(src[pos + 2:pos + 4]), 4)
        if escaped == 'u':
            return (_parse_hex(src[pos + 2:pos + 6]), 6)
        if escaped == 'U':
            return (_parse_hex(src[pos + 2:pos + 10]), 10)
        if escaped == 't':
            return (ord('\t'), 2)
        if escaped == 'r':
            return (ord('\r'), 2)
        if escaped == 'n':
            return (ord('\n'), 2)
        if escaped in ('"', '[', ']'):
            return (ord(src[pos + 1]), 2)
        if escaped == '\\':
            code_point = char_at(src, pos + 1)
            if not code_point:
                raise GrammarParseError(src, pos, "Could not get code point for character")
            return (ord(code_point), 2)
        raise GrammarParseError(src, pos, f'Unknown escape at {char_at(src, pos)}')

    if not char_at(src, pos):
        raise GrammarParseError(src, pos, "Unexpected end of grammar input, failed to complete parse")
    return (ord(src[pos]), 1)


parseChar = parse_char
