import pytest
from conftest import cases

from gbnf import GBNF


@pytest.mark.parametrize('name,test_case,grammar', cases('grammars'))
def test_it_parses_a_known_valid_grammar(name, test_case, grammar):
    state = GBNF(grammar)

    for char in test_case:
        state = state.add(char)
