import pytest

from .grammar_graph_types import RuleChar, RuleCharExclude, RuleEnd
from .graph_node import GraphNode, GraphNodeMeta
from .graph_pointer import GraphPointer
from .rule_ref import RuleRef
from .type_guards import (
    is_graph_pointer_rule_char,
    is_graph_pointer_rule_char_exclude,
    is_graph_pointer_rule_end,
    is_graph_pointer_rule_ref,
    is_range,
    is_rule,
    is_rule_char,
    is_rule_char_exclude,
    is_rule_end,
    is_rule_ref,
)

META = GraphNodeMeta(1, 2, 3)


def pointer_for(rule):
    return GraphPointer(GraphNode(rule, META))


def test_is_graph_pointer_rule_ref_returns_true():
    assert is_graph_pointer_rule_ref(pointer_for(RuleRef(1))) is True


def test_is_graph_pointer_rule_ref_returns_false():
    assert is_graph_pointer_rule_ref(pointer_for(RuleEnd())) is False


def test_is_graph_pointer_rule_end_returns_false():
    assert is_graph_pointer_rule_end(pointer_for(RuleRef(1))) is False


def test_is_graph_pointer_rule_end_returns_true():
    assert is_graph_pointer_rule_end(pointer_for(RuleEnd())) is True


def test_is_graph_pointer_rule_char_returns_true():
    assert is_graph_pointer_rule_char(pointer_for(RuleChar([97]))) is True


def test_is_graph_pointer_rule_char_returns_false():
    assert is_graph_pointer_rule_char(pointer_for(RuleEnd())) is False


def test_is_graph_pointer_rule_char_exclude_returns_true():
    assert is_graph_pointer_rule_char_exclude(pointer_for(RuleCharExclude([97]))) is True


def test_is_graph_pointer_rule_char_exclude_returns_false():
    assert is_graph_pointer_rule_char_exclude(pointer_for(RuleChar([97]))) is False


def test_is_rule_returns_false_for_none():
    assert is_rule(None) is False


def test_is_rule_returns_false_for_a_non_rule():
    assert is_rule({"type": "invalid", "value": []}) is False


def test_is_rule_returns_true_for_valid_rule_objects():
    assert is_rule(RuleChar([65, [66, 67]])) is True


def test_is_rule_ref_returns_true_for_valid_rule_refs():
    assert is_rule_ref(RuleRef(1)) is True


def test_is_rule_ref_returns_false_for_invalid_rule_refs():
    assert is_rule_ref(RuleChar([65])) is False


def test_is_rule_end_returns_true_for_valid_rule_ends():
    assert is_rule_end(RuleEnd()) is True


def test_is_rule_end_returns_false_for_invalid_rule_ends():
    assert is_rule_end(RuleChar([65])) is False


def test_is_rule_char_returns_true_for_valid_rule_chars():
    assert is_rule_char(RuleChar([65])) is True


def test_is_rule_char_returns_false_for_invalid_rule_chars():
    assert is_rule_char(RuleCharExclude([65])) is False


def test_is_rule_char_exclude_returns_true_for_valid_rule_chars():
    assert is_rule_char_exclude(RuleCharExclude([65])) is True


def test_is_rule_char_exclude_returns_false_for_invalid_rule_chars():
    assert is_rule_char_exclude(RuleChar([65])) is False


def test_is_range_returns_true_for_valid_ranges():
    assert is_range([1, 10]) is True


@pytest.mark.parametrize("value", [[1, "10"], [1], 5])
def test_is_range_returns_false_for_invalid_range(value):
    assert is_range(value) is False
