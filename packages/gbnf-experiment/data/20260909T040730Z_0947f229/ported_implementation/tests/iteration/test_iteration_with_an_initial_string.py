"""Port of tests/javascript/iteration/iteration-with-an-initial-string.test.ts."""

import pytest
from cases import table
from gbnf import GBNF

FILE = 'iteration/iteration-with-an-initial-string.test.ts'


@pytest.mark.parametrize('grammar, input, expected', table(FILE, 0))
def test_it_returns_parse_state_for_a_grammar_and_initial_string(grammar, input, expected):
    state = GBNF(grammar)
    state = state.add(input)
    assert [rule.to_dict() for rule in state] == expected
