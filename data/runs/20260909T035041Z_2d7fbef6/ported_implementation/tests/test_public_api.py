import pytest

from gbnf import GBNF, InputParseError, ParseState, RuleChar, RuleEnd, RuleType, is_range
from helpers import END, char, rules, rules_after


def test_returns_a_parse_state():
    assert isinstance(GBNF('root ::= "yes" | "no"'), ParseState)


def test_yields_the_rules_that_may_match_next():
    assert rules_after('root ::= "yes" | "no"') == [char(ord("y")), char(ord("n"))]


def test_state_can_be_cast_to_a_list_and_indexed():
    state = GBNF('root ::= "yes" | "no"')
    assert [*state][0].value == [ord("y")]


def test_rules_can_be_iterated_more_than_once():
    state = GBNF('root ::= "yes" | "no"')
    assert rules(state) == rules(state)


def test_rules_method_matches_iteration():
    state = GBNF('root ::= "yes" | "no"')
    assert list(state.rules()) == list(state)


def test_add_advances_the_state():
    assert rules_after('root ::= "yes" | "no"', "y") == [char(ord("e"))]
    assert rules_after('root ::= "yes" | "no"', "y", "e") == [char(ord("s"))]


def test_add_accepts_multiple_characters_at_once():
    grammar = 'root ::= "I like green eggs and ham"'
    assert rules_after(grammar) == [char(ord("I"))]
    assert rules_after(grammar, "I li") == [char(ord("k"))]
    assert rules_after(grammar, "I li", "ke gree") == [char(ord("n"))]


def test_a_completed_grammar_yields_end():
    assert rules_after('root ::= "a"', "a") == [END]


def test_states_are_immutable():
    state = GBNF('root ::= "yes" | "no"')
    state.add("y")
    assert rules(state) == [char(ord("y")), char(ord("n"))]


def test_state_is_callable():
    state = GBNF('root ::= "yes" | "no"')
    assert rules(state("y")) == [char(ord("e"))]


def test_size_counts_the_available_rules():
    state = GBNF('root ::= "yes" | "no"')
    assert state.size == 2
    assert len(state) == 2
    assert state.add("y").size == 1


def test_grammar_is_exposed():
    grammar = 'root ::= "yes" | "no"'
    assert GBNF(grammar).grammar == grammar
    assert GBNF(grammar).add("y").grammar == grammar


def test_accepts_an_initial_string():
    assert rules(GBNF('root ::= "yes" | "no"', "y")) == [char(ord("e"))]
    assert rules(GBNF('root ::= "yes" | "no"', "yes")) == [END]


def test_accepts_a_code_point_as_input():
    assert rules(GBNF('root ::= "abc"', ord("a"))) == [char(ord("b"))]


def test_accepts_a_list_of_code_points_as_input():
    assert rules(GBNF('root ::= "abc"', [ord("a"), ord("b")])) == [char(ord("c"))]
    assert rules(GBNF('root ::= "abc"').add([ord("a")])) == [char(ord("b"))]


def test_accepts_an_object_that_stringifies_to_a_grammar():
    class Grammar:
        def __str__(self):
            return 'root ::= "a"'

    assert rules(GBNF(Grammar())) == [char(ord("a"))]


def test_invalid_input_raises():
    with pytest.raises(InputParseError):
        GBNF('root ::= "yes"').add("n")


def test_rule_types_are_exposed():
    (rule,) = GBNF('root ::= "a"')
    assert isinstance(rule, RuleChar)
    assert rule.type is RuleType.CHAR
    assert rule.type == "char"

    (rule,) = GBNF('root ::= "a"').add("a")
    assert isinstance(rule, RuleEnd)
    assert rule.type is RuleType.END


def test_is_range_identifies_ranges():
    (rule,) = GBNF("root ::= [a-z]")
    assert is_range(rule.value[0])
    assert not is_range(rule.value)

    (rule,) = GBNF('root ::= "a"')
    assert not is_range(rule.value[0])
