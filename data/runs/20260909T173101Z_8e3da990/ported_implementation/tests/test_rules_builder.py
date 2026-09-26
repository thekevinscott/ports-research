import pytest

from ported_implementation.rules_builder import RulesBuilder
from ported_implementation.rules_builder.parse_char import parse_char
from ported_implementation.rules_builder.parse_name import parse_name
from ported_implementation.rules_builder.parse_space import parse_space
from ported_implementation.rules_builder.types import InternalRuleType as T
from ported_implementation.utils.errors.grammar_parse_error import GrammarParseError


def defs(grammar):
    return [
        [(entry.type, entry.value) for entry in rule]
        for rule in RulesBuilder(grammar).rules
    ]


def test_builds_a_literal():
    assert defs('root ::= "ab"') == [[(T.CHAR, [97]), (T.CHAR, [98]), (T.END, None)]]


def test_builds_a_char_class_with_ranges_and_alts():
    assert defs('root ::= [a-z0-9]') == [[
        (T.CHAR, [97]),
        (T.CHAR_RNG_UPPER, 122),
        (T.CHAR_ALT, 48),
        (T.CHAR_RNG_UPPER, 57),
        (T.END, None),
    ]]


def test_builds_a_negated_char_class():
    assert defs('root ::= sub\nsub ::= [^x]') == [
        [(T.RULE_REF, 1), (T.END, None)],
        [(T.CHAR_NOT, [120]), (T.END, None)],
    ]


def test_expands_repetition_into_generated_rules():
    assert defs('root ::= "a"? "b"+') == [
        [(T.RULE_REF, 1), (T.RULE_REF, 2), (T.END, None)],
        [(T.CHAR, [97]), (T.ALT, None), (T.END, None)],
        [(T.CHAR, [98]), (T.RULE_REF, 2), (T.ALT, None), (T.CHAR, [98]), (T.END, None)],
    ]


def test_records_symbol_ids_in_order():
    builder = RulesBuilder('root ::= "a"? "b"+')
    assert list(builder.symbol_ids) == [('root', 0), ('root_1', 1), ('root_2', 2)]
    assert builder.symbol_ids.size == 3
    assert builder.symbol_ids.get('root_2') == 2
    assert builder.symbol_ids.reverse_get(2) == 'root_2'


def test_alternates_are_separated_by_alt():
    assert defs('root ::= "a" | "b"') == [[
        (T.CHAR, [97]), (T.ALT, None), (T.CHAR, [98]), (T.END, None),
    ]]


def test_raises_on_an_unterminated_rule():
    with pytest.raises(GrammarParseError):
        RulesBuilder('root ::= "a" "b" ) ')


def test_enforces_a_time_limit():
    with pytest.raises(GrammarParseError, match='duration of 0 exceeded'):
        RulesBuilder('root ::= "a bit of text to parse" | "another alternate"', 0)


@pytest.mark.parametrize(('src', 'expected'), [
    ('a', (97, 1)),
    (r'\n', (10, 2)),
    (r'\t', (9, 2)),
    (r'\r', (13, 2)),
    (r'\x41', (65, 4)),
    (r'\u00e9', (233, 6)),
    ('é', (233, 1)),
    (r'\U0001F600', (128512, 10)),
    (r'\"', (34, 2)),
    (r'\[', (91, 2)),
    (r'\]', (93, 2)),
    ('\\\\', (92, 2)),
])
def test_parse_char(src, expected):
    assert parse_char(src, 0) == expected


def test_parse_char_rejects_an_unknown_escape():
    with pytest.raises(GrammarParseError):
        parse_char(r'\q', 0)


def test_parse_char_rejects_the_end_of_input():
    with pytest.raises(GrammarParseError):
        parse_char('', 0)


def test_parse_name():
    assert parse_name('my-rule ::= "a"', 0) == 'my-rule'
    with pytest.raises(GrammarParseError, match='Failed to find a valid name'):
        parse_name('1234', 0)


def test_parse_space():
    assert parse_space('   a', 0, False) == 3
    assert parse_space('  \n a', 0, False) == 2
    assert parse_space('  \n a', 0, True) == 4
    assert parse_space('# comment\na', 0, True) == 10
