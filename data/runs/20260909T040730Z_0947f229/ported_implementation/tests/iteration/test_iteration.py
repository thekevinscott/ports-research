"""Port of tests/javascript/iteration/iteration.test.ts."""

import pytest
from cases import table
from gbnf import GBNF

FILE = 'iteration/iteration.test.ts'


@pytest.mark.parametrize('grammar, expected', table(FILE, 0))
def test_it_returns_parse_state_for_a_grammar(grammar, expected):
    state = GBNF(grammar)
    assert [rule.to_dict() for rule in state] == expected
