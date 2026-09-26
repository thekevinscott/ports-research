import pytest
from conftest import cases

from gbnf import GBNF, InputParseError


@pytest.mark.parametrize('grammar,input_', cases('valid-inputs'))
def test_it_parses_a_grammar_and_input(grammar, input_):
    assert GBNF(grammar, input_)


@pytest.mark.parametrize('grammar,input_,error_pos', cases('invalid-inputs'))
def test_it_reports_an_error_for_an_invalid_input(grammar, input_, error_pos):
    with pytest.raises(InputParseError) as raised:
        graph = GBNF(grammar)
        graph.add(input_)
    assert raised.value.message == InputParseError(input_, error_pos, '').message
