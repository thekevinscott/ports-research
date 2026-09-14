import pytest

from ported_implementation import GBNF, RuleType, is_range
from ported_implementation.grammar_graph.generic_set import GenericSet
from ported_implementation.grammar_graph.get_input_as_code_points import get_input_as_code_points
from ported_implementation.grammar_graph.get_serialized_rule_key import get_serialized_rule_key
from ported_implementation.grammar_graph.rule_ref import RuleRef
from ported_implementation.grammar_graph.types import RuleChar, RuleCharExclude, RuleEnd
from ported_implementation.grammar_parser.build_rule_stack import build_rule_stack
from ported_implementation.rules_builder import RulesBuilder
from ported_implementation.utils.errors.build_error_position import build_error_position
from ported_implementation.utils.errors.input_parse_error import InputParseError
from ported_implementation.utils.is_point_in_range import is_point_in_range


def test_prints_the_graph():
    state = GBNF('root ::= "ab" | [c-d]')
    assert state._graph.print(colors=False) == (
        '\n{0,0,0}[a]-> {0,0,1}[b]-> {0,0,2}end'
        '\n{0,1,0}[c,d]-> {0,1,1}end'
    )


def test_build_rule_stack_splits_on_alternates():
    stack = build_rule_stack(RulesBuilder('root ::= "a" | [b-c]').rules[0])
    assert [[rule.to_dict() for rule in path] for path in stack] == [
        [{'type': RuleType.CHAR, 'value': [97]}, {'type': RuleType.END}],
        [{'type': RuleType.CHAR, 'value': [[98, 99]]}, {'type': RuleType.END}],
    ]


def test_build_rule_stack_emits_rule_refs():
    stack = build_rule_stack(RulesBuilder('root ::= sub\nsub ::= "a"').rules[0])
    assert isinstance(stack[0][0], RuleRef)
    assert stack[0][0].value == 1


def test_rules_compare_by_value_and_support_item_access():
    rule = RuleChar([97])
    assert rule == RuleChar([97])
    assert rule == {'type': RuleType.CHAR, 'value': [97]}
    assert rule == {'type': 'char', 'value': [97]}
    assert rule != RuleCharExclude([97])
    assert rule['type'] == RuleType.CHAR
    assert rule['value'] == [97]
    assert dict(RuleEnd()) == {'type': RuleType.END}


def test_serialized_rule_keys_are_distinct_per_rule():
    assert get_serialized_rule_key(RuleEnd()) == '0'
    assert get_serialized_rule_key(RuleChar([97, [98, 99]])) == '1-[97,[98,99]]'
    assert get_serialized_rule_key(RuleCharExclude([97])) == '2-[97]'
    assert get_serialized_rule_key(RuleRef(4)) == '3-4'


def test_generic_set_deduplicates_by_key():
    values = GenericSet(lambda item: item['id'])
    first = {'id': 'a'}
    values.add(first)
    values.add({'id': 'a'})
    values.add({'id': 'b'})
    assert values.size == 2
    assert values.get({'id': 'a'}) is first
    assert values.has(first)
    values.delete({'id': 'a'})
    assert values.size == 1


def test_get_input_as_code_points():
    assert get_input_as_code_points('ab') == [97, 98]
    assert get_input_as_code_points(97) == [97]
    assert get_input_as_code_points([97, 98]) == [97, 98]


def test_is_range():
    assert is_range([1, 2])
    assert not is_range([1])
    assert not is_range(1)
    assert not is_range(['a', 'b'])


def test_is_point_in_range():
    assert is_point_in_range(98, [97, 99])
    assert is_point_in_range(97, [97, 99])
    assert not is_point_in_range(100, [97, 99])


def test_build_error_position():
    assert build_error_position('', 0) == ['No input provided']
    assert build_error_position('abc', 1) == ['abc', ' ^']
    assert build_error_position('one\ntwo\nthree\nfour', 4) == ['one', 'two', ' ^']
    # past the last line the reference yields a hole, which joins as a blank line
    assert build_error_position('one\ntwo\nthree\nfour', 15) == ['three', 'four', '', '^']


def test_input_parse_error_reports_the_failing_position():
    state = GBNF('root ::= "abc"').add('ab')
    with pytest.raises(InputParseError) as excinfo:
        state.add('xy')
    error = excinfo.value
    assert error.src == 'abxy'
    assert error.error_for_most_recent_input == 'Failed to parse input string:\n\nxy\n^'
    assert str(error) == 'Failed to parse input string:\n\nabxy\n  ^'
