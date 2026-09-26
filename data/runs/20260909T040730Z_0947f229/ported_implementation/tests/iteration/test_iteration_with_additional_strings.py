"""Port of tests/javascript/iteration/iteration-with-additional-strings.test.ts."""

import pytest
from cases import table
from gbnf import GBNF, InputParseError

FILE = 'iteration/iteration-with-additional-strings.test.ts'


@pytest.mark.parametrize('grammar, starting, additional', table(FILE, 0))
def test_it_throws_for_a_grammar_with_starting_and_additional(grammar, starting, additional):
    graph = GBNF(grammar, starting)
    with pytest.raises(Exception):
        graph.add(additional)


@pytest.mark.parametrize('grammar, starting, additional, expected', table(FILE, 1))
def test_it_parses_a_grammar_with_starting_and_additional(
    grammar, starting, additional, expected
):
    state = GBNF(grammar, starting)
    state = state.add(additional)
    assert [rule.to_dict() for rule in state] == expected


@pytest.mark.parametrize('error_for_most_recent_input', table(FILE, 2))
def test_it_throws_a_particular_error(error_for_most_recent_input):
    grammar = 'root ::= "bar"'
    state = GBNF(grammar)
    state = state.add('b')
    state = state.add('a')
    try:
        state.add('z')
        raise AssertionError('Expected an error to be thrown')
    except InputParseError as err:
        expected_err = InputParseError('z', 0, 'ba')
        if error_for_most_recent_input:
            assert err.error_for_most_recent_input == (
                expected_err.error_for_most_recent_input
            )
        else:
            assert err.message == expected_err.message
