"""Port of tests/javascript/validation/validate-input.test.ts."""

import pytest
from cases import table
from gbnf import GBNF, InputParseError

FILE = 'validation/validate-input.test.ts'


@pytest.mark.parametrize('grammar, input', table(FILE, 0))
def test_it_parses_a_grammar_and_input(grammar, input):
    assert GBNF(grammar, input)


@pytest.mark.parametrize('grammar, input, error_pos', table(FILE, 1))
def test_it_reports_an_error_for_an_invalid_input(grammar, input, error_pos):
    error = InputParseError(input, error_pos, '')
    with pytest.raises(InputParseError) as excinfo:
        graph = GBNF(grammar)
        graph.add(input)
    assert str(excinfo.value) == str(error)
