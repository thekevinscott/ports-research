import re

from ..utils.errors.grammar_parse_error import GrammarParseError

PARSE_NAME_ERROR = "Failed to find a valid name"


def GET_INVALID_CHAR_ERROR(char: str) -> str:
    return (
        f'Invalid character "{char}" when parsing name, '
        "only lowercase letters and hyphens are allowed."
    )


_VALID_CHAR = re.compile(r"[a-zA-Z-]")
_INVALID_NEXT_CHAR = re.compile(r"[_0-9]")


def parse_name(grammar: str, pos: int) -> str:
    name = ""
    while pos < len(grammar) and _VALID_CHAR.search(grammar[pos]):
        name += grammar[pos]
        pos += 1
    if not name:
        raise GrammarParseError(grammar, pos, PARSE_NAME_ERROR)
    if pos < len(grammar) and _INVALID_NEXT_CHAR.search(grammar[pos]):
        raise GrammarParseError(grammar, pos, GET_INVALID_CHAR_ERROR(grammar[pos]))
    return name
