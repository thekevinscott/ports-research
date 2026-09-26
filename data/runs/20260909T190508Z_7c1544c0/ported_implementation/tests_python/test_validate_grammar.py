import pytest
from conftest import cases

from gbnf import GBNF, GrammarParseError


@pytest.mark.parametrize('grammar', cases('valid-grammars'))
def test_it_parses_a_grammar(grammar):
    assert GBNF(grammar)


@pytest.mark.parametrize('grammar,error_pos,error_reason', cases('invalid-grammars'))
def test_it_reports_an_error_for_an_invalid_grammar(grammar, error_pos, error_reason):
    with pytest.raises(GrammarParseError) as raised:
        GBNF(grammar)
    assert raised.value.message == GrammarParseError(
        grammar, error_pos, error_reason
    ).message
