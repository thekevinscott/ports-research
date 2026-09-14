import pytest

from . import graph_pointer as module
from . import type_guards as actual_guards
from .grammar_graph_types import RuleChar, RuleCharExclude, RuleEnd
from .graph_node import GraphNode, GraphNodeMeta
from .graph_pointer import GraphPointer

GUARDS = [
    "is_graph_pointer_rule_ref",
    "is_graph_pointer_rule_end",
    "is_graph_pointer_rule_char",
    "is_graph_pointer_rule_char_exclude",
]


@pytest.fixture(autouse=True)
def stub_guards(monkeypatch):
    for guard in GUARDS:
        monkeypatch.setattr(module, guard, lambda pointer: False)
    yield monkeypatch


def enable(monkeypatch, guard):
    monkeypatch.setattr(module, guard, lambda pointer: True)


def test_constructor():
    node = GraphNode(RuleEnd(), GraphNodeMeta(1, 2, 3))
    pointer = GraphPointer(node)
    assert pointer.node is node
    assert pointer.id == "1,2,3"
    assert pointer.parent is None


def test_it_raises_error_if_node_is_undefined():
    with pytest.raises(ValueError, match="Node is undefined"):
        GraphPointer(None)


def test_it_initializes_correctly_with_node_and_parent():
    parent_node = GraphNode(RuleChar([97]), GraphNodeMeta(1, 2, 3))
    child_node = GraphNode(RuleChar([98]), GraphNodeMeta(4, 5, 6))
    parent_pointer = GraphPointer(parent_node)
    child_pointer = GraphPointer(child_node, parent_pointer)
    assert child_pointer.parent is parent_pointer
    assert child_pointer.id == "1,2,3-4,5,6"


def test_resolve_raises_error_on_unknown_rule_types():
    node = GraphNode(object(), GraphNodeMeta(1, 2, 3))
    pointer = GraphPointer(node)
    with pytest.raises(ValueError, match="Unknown rule"):
        list(pointer.resolve())


def test_resolve_yields_a_char_rule(stub_guards):
    enable(stub_guards, "is_graph_pointer_rule_char")
    node = GraphNode(RuleChar([97]), GraphNodeMeta(1, 2, 3))
    pointer = GraphPointer(node)
    assert list(pointer.resolve()) == [pointer]


def test_resolve_yields_a_char_excluded_rule(stub_guards):
    enable(stub_guards, "is_graph_pointer_rule_char_exclude")
    node = GraphNode(RuleCharExclude([97]), GraphNodeMeta(1, 2, 3))
    pointer = GraphPointer(node)
    assert list(pointer.resolve()) == [pointer]


def test_resolve_yields_an_end_rule_without_a_parent(stub_guards):
    enable(stub_guards, "is_graph_pointer_rule_end")
    node = GraphNode(RuleEnd(), GraphNodeMeta(1, 2, 3))
    pointer = GraphPointer(node)
    assert list(pointer.resolve()) == [pointer]


def test_resolve_yields_an_end_rule_with_a_parent(stub_guards):
    enable(stub_guards, "is_graph_pointer_rule_end")
    rule = RuleEnd()
    parent_node = GraphNode(rule, GraphNodeMeta(2, 1, 1))
    parent_pointer = GraphPointer(parent_node)
    child_node = GraphNode(rule, GraphNodeMeta(1, 1, 1))
    child_pointer = GraphPointer(child_node, parent_pointer)
    assert list(child_pointer.resolve()) == [parent_pointer]


def test_resolve_yields_an_end_rule_with_a_grandparent(stub_guards):
    enable(stub_guards, "is_graph_pointer_rule_end")
    rule = RuleEnd()
    grandparent_node = GraphNode(rule, GraphNodeMeta(2, 1, 1))
    grandparent_pointer = GraphPointer(grandparent_node)
    parent_node = GraphNode(rule, GraphNodeMeta(2, 1, 1))
    parent_pointer = GraphPointer(parent_node, grandparent_pointer)
    child_node = GraphNode(rule, GraphNodeMeta(1, 1, 1))
    child_pointer = GraphPointer(child_node, parent_pointer)
    assert list(child_pointer.resolve()) == [grandparent_pointer]


def test_resolve_yields_an_end_rule_with_a_parent_that_is_not_an_end(stub_guards):
    stub_guards.setattr(
        module, "is_graph_pointer_rule_end", actual_guards.is_graph_pointer_rule_end
    )
    stub_guards.setattr(
        module, "is_graph_pointer_rule_char", actual_guards.is_graph_pointer_rule_char
    )
    rule = RuleEnd()
    grandparent_node = GraphNode(rule, GraphNodeMeta(2, 1, 1))
    grandparent_pointer = GraphPointer(grandparent_node)
    parent_node = GraphNode(RuleChar([97]), GraphNodeMeta(2, 1, 1))
    parent_pointer = GraphPointer(parent_node, grandparent_pointer)
    child_node = GraphNode(rule, GraphNodeMeta(1, 1, 1))
    child_pointer = GraphPointer(child_node, parent_pointer)
    assert list(child_pointer.resolve()) == [parent_pointer]
