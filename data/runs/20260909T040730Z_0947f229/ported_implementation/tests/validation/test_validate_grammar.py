"""Port of tests/javascript/validation/validate-grammar.test.ts."""

import pytest
from cases import table
from gbnf import GBNF, GrammarParseError

FILE = 'validation/validate-grammar.test.ts'


@pytest.mark.parametrize('grammar', table(FILE, 0))
def test_it_parses_a_grammar(grammar):
    assert GBNF(grammar)


@pytest.mark.parametrize('grammar, error_pos, error_reason', table(FILE, 1))
def test_it_reports_an_error_for_an_invalid_grammar(grammar, error_pos, error_reason):
    with pytest.raises(GrammarParseError) as excinfo:
        GBNF(grammar)
    assert str(excinfo.value) == str(GrammarParseError(grammar, error_pos, error_reason))
