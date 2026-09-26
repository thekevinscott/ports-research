"""Error-path tests. Messages were verified against the TypeScript reference."""
import pytest

from ported_implementation import GBNF, GrammarParseError, InputParseError
from ported_implementation.utils.errors.build_error_position import build_error_position
from ported_implementation.utils.errors.get_input_as_string import get_input_as_string
from ported_implementation.utils.errors.grammar_parse_error import (
    GRAMMAR_PARSER_ERROR_HEADER_MESSAGE,
)
from ported_implementation.utils.errors.input_parse_error import (
    INPUT_PARSER_ERROR_HEADER_MESSAGE,
)


@pytest.mark.parametrize(
    "grammar,message",
    [
        (
            "root ::= missing",
            'Failed to parse grammar: Undefined rule identifier "missing"\n\nroot ::= missing\n         ^',
        ),
        (
            'root ::= "a"\nfoo1 ::= "b"',
            'Failed to parse grammar: Invalid character "1" when parsing name, only lowercase '
            'letters and hyphens are allowed.\n\nroot ::= "a"\nfoo1 ::= "b"\n    ^',
        ),
        (
            'root "a"',
            'Failed to parse grammar: Expecting ::= at 5\n\nroot "a"\n     ^',
        ),
        (
            "root ::= *",
            "Failed to parse grammar: Expecting preceding item to */+/? at 9\n\nroot ::= *\n         ^",
        ),
        (
            'root ::= ("a"',
            "Failed to parse grammar: Expecting ')' at 13\n\nroot ::= (\"a\"\n\n^",
        ),
        (
            r'root ::= "\q"',
            'Failed to parse grammar: Unknown escape at \\\n\nroot ::= "\\q"\n          ^',
        ),
        (
            "",
            "Failed to parse grammar: No rules were found\n\nNo input provided",
        ),
        (
            "# just a comment",
            "Failed to parse grammar: No rules were found\n\n# just a comment\n^",
        ),
    ],
)
def test_grammar_parse_errors(grammar, message):
    with pytest.raises(GrammarParseError) as excinfo:
        GBNF(grammar)
    assert str(excinfo.value) == message


def test_grammar_parse_error_attributes():
    with pytest.raises(GrammarParseError) as excinfo:
        GBNF("root ::= missing")
    error = excinfo.value
    assert error.grammar == "root ::= missing"
    assert error.reason == 'Undefined rule identifier "missing"'
    assert error.pos == 9
    assert error.name == "GrammarParseError"


def test_missing_root_symbol():
    with pytest.raises(GrammarParseError) as excinfo:
        GBNF('a ::= "b"')
    assert "Grammar does not contain a root symbol" in str(excinfo.value)


def test_input_parse_error_on_initial_string():
    with pytest.raises(InputParseError) as excinfo:
        GBNF('root ::= "yes"', "yq")
    error = excinfo.value
    assert str(error) == "Failed to parse input string:\n\nyq\n ^"
    assert error.src == "yq"
    assert error.pos == 1
    assert error.error_for_most_recent_input == "Failed to parse input string:\n\nyq\n ^"


def test_input_parse_error_carries_previous_input():
    state = GBNF('root ::= "yes"', "y")
    with pytest.raises(InputParseError) as excinfo:
        state.add("q")
    error = excinfo.value
    # the full message spans everything parsed so far ...
    assert str(error) == "Failed to parse input string:\n\nyq\n ^"
    assert error.src == "yq"
    # ... while `error_for_most_recent_input` is scoped to the failing chunk
    assert error.error_for_most_recent_input == "Failed to parse input string:\n\nq\n^"
    assert error.errorForMostRecentInput == error.error_for_most_recent_input


def test_input_parse_error_name():
    with pytest.raises(InputParseError) as excinfo:
        GBNF('root ::= "a"', "b")
    assert excinfo.value.name == "InputParseError"


@pytest.mark.parametrize(
    "src,pos,expected",
    [
        ("", 0, ["No input provided"]),
        ("abc", 0, ["abc", "^"]),
        ("abc", 2, ["abc", "  ^"]),
        ("abc\ndef\nghi", 5, ["abc", "def", "  ^"]),
    ],
)
def test_build_error_position(src, pos, expected):
    assert build_error_position(src, pos) == expected


def test_build_error_position_shows_at_most_three_lines():
    lines = build_error_position("a\nb\nc\nd\ne", 8)
    assert len(lines) == 4  # three source lines plus the caret


def test_error_header_messages():
    assert GRAMMAR_PARSER_ERROR_HEADER_MESSAGE("nope") == "Failed to parse grammar: nope"
    assert INPUT_PARSER_ERROR_HEADER_MESSAGE == "Failed to parse input string:"


@pytest.mark.parametrize(
    "src,expected",
    [("abc", "abc"), (97, "a"), ([97, 98], "ab"), ("", "")],
)
def test_get_input_as_string(src, expected):
    assert get_input_as_string(src) == expected
