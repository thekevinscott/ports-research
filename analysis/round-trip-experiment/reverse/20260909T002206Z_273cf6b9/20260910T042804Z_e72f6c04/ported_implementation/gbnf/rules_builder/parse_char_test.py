import pytest

from ..utils.errors import GrammarParseError
from .parse_char import parse_char

PREFIX_LENGTH = len('root ::= "')


@pytest.mark.parametrize(
    ("description", "char", "code_point"),
    [
        ("escaped 8-bit unicode char", "a", ord("a")),
        ("escaped 8-bit unicode char", "9", ord("9")),
    ],
)
def test_simple(description, char, code_point):
    grammar = f'root ::= "{char}" "foo"'
    assert parse_char(grammar, PREFIX_LENGTH) == (code_point, 1)


@pytest.mark.parametrize(
    ("description", "escaped_char", "code_point", "inc_pos"),
    [
        ("escaped 8-bit unicode char", "\\x2A", 0x2A, 4),
        ("escaped 16-bit unicode char", "\\u006F", 0x6F, 6),
        ("escaped 32-bit unicode char", "\\U0001F4A9", 128169, 10),
        ("escaped tab char", "\\t", 9, 2),
        ("escaped new line char", "\\n", 10, 2),
        ("escaped \r char", "\\r", 13, 2),
        ("escaped quote char", '\\"', 34, 2),
        ("escaped [ char", "\\[", 91, 2),
        ("escaped ] char", "\\]", 93, 2),
        ("escaped \\ char", "\\\\", 92, 2),
    ],
)
def test_complex(description, escaped_char, code_point, inc_pos):
    grammar = f'root ::= "{escaped_char}" "foo"'
    assert parse_char(grammar, PREFIX_LENGTH) == (code_point, inc_pos)


@pytest.mark.parametrize(
    ("input", "pos"),
    [
        ("", 0),
        ("a", 1),
        ("a", 2),
    ],
)
def test_it_raises(input, pos):
    with pytest.raises(GrammarParseError):
        parse_char(input, pos)
