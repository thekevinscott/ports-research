import pytest

from ..utils.errors import GrammarParseError
from .parse_name import PARSE_NAME_ERROR, parse_name


def test_should_return_correct_name_when_encountering_a_valid_name():
    src = "validName"
    assert parse_name(src, 0) == src


def test_should_return_correct_name_when_starting_at_a_non_zero_position():
    src = "123validName"
    assert parse_name(src, 3) == "validName"


def test_should_raise_error_when_encountering_an_invalid_name():
    src = "123"
    with pytest.raises(GrammarParseError) as e:
        parse_name(src, 0)
    assert str(e.value) == str(GrammarParseError(src, 0, PARSE_NAME_ERROR))
