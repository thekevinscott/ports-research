"""Port of tests/javascript/iteration/grammars.test.ts."""

import pytest
from cases import table
from gbnf import GBNF

FILE = 'iteration/grammars.test.ts'


def unescape(string):
    return string.replace('\\n', '\n').replace('\\t', '\t')


@pytest.mark.parametrize('name, test_case, grammar', table(FILE, 0))
def test_it_parses_a_known_valid_grammar(name, test_case, grammar):
    test_case = unescape(test_case)

    state = GBNF(unescape(grammar))

    for char in test_case:
        state = state.add(char)
