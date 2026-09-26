import re

from ..utils.errors.grammar_parse_error import GrammarParseError

PARSE_NAME_ERROR = 'Failed to find a valid name'


def GET_INVALID_CHAR_ERROR(char: str) -> str:
    return f'Invalid character "{char}" when parsing name, only lowercase letters and hyphens are allowed.'


_VALID_CHAR = re.compile(r'[a-zA-Z-]')
_INVALID_NEXT_CHAR = re.compile(r'[_0-9]')


def _is_valid_char(char: str) -> bool:
    return _VALID_CHAR.search(char) is not None


def _is_invalid_next_char(char: str) -> bool:
    return _INVALID_NEXT_CHAR.search(char) is not None


def parse_name(grammar: str, pos: int) -> str:
    name = ''
    while pos < len(grammar) and _is_valid_char(grammar[pos]):
        name += grammar[pos]
        pos += 1
    if not name:
        raise GrammarParseError(grammar, pos, PARSE_NAME_ERROR)
    if pos < len(grammar) and _is_invalid_next_char(grammar[pos]):
        raise GrammarParseError(grammar, pos, GET_INVALID_CHAR_ERROR(grammar[pos]))
    return name


parseName = parse_name
