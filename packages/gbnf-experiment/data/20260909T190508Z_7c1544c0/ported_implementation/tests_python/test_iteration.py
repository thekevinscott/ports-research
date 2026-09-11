import pytest
from conftest import cases

from gbnf import GBNF, InputParseError, rule_to_dict


def rules(state):
    return [rule_to_dict(rule) for rule in state]


@pytest.mark.parametrize('grammar,expected', cases('iteration'))
def test_it_returns_parse_state_for_a_grammar(grammar, expected):
    assert rules(GBNF(grammar)) == expected


@pytest.mark.parametrize(
    'grammar,input_,expected', cases('iteration-with-an-initial-string')
)
def test_it_returns_parse_state_for_a_grammar_and_initial_string(
    grammar, input_, expected
):
    state = GBNF(grammar)
    state = state.add(input_)
    assert rules(state) == expected


@pytest.mark.parametrize(
    'grammar,starting,additional,expected', cases('iteration-with-additional-strings')
)
def test_it_parses_a_grammar_with_starting_and_additional_strings(
    grammar, starting, additional, expected
):
    state = GBNF(grammar, starting)
    state = state.add(additional)
    assert rules(state) == expected


@pytest.mark.parametrize(
    'grammar,starting,additional', cases('throwing-additional-strings')
)
def test_it_throws_for_invalid_additional_strings(grammar, starting, additional):
    graph = GBNF(grammar, starting)
    with pytest.raises(Exception):
        graph.add(additional)


@pytest.mark.parametrize('error_for_most_recent_input', [False, True])
def test_it_throws_a_particular_error(error_for_most_recent_input):
    state = GBNF('root ::= "bar"')
    state = state.add('b')
    state = state.add('a')
    with pytest.raises(InputParseError) as raised:
        state.add('z')
    expected = InputParseError('z', 0, 'ba')
    if error_for_most_recent_input:
        assert (
            raised.value.error_for_most_recent_input
            == expected.error_for_most_recent_input
        )
    else:
        assert raised.value.message == expected.message
