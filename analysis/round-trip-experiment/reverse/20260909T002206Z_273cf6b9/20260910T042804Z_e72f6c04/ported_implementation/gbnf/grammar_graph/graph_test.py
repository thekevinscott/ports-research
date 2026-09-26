import pytest

from .grammar_graph_types import RuleChar, RuleCharExclude, RuleEnd
from .graph import Graph
from .graph_node import GraphNode, GraphNodeMeta
from .graph_pointer import GraphPointer
from .pointers import Pointers
from .rule_ref import RuleRef
from .type_guards import is_rule

GRAMMAR = "example-grammar"
ROOT_ID = 0


def stacked_rules():
    return [
        [
            [RuleChar([65, 66, 67])],
            [RuleChar([68, 69, 70])],
        ],
        [
            [RuleChar([71, 72, 73])],
            [RuleChar([74, 75, 76])],
        ],
    ]


def test_should_create_a_graph_instance():
    graph = Graph(GRAMMAR, stacked_rules(), ROOT_ID)
    assert isinstance(graph, Graph)
    assert graph.grammar == GRAMMAR


def test_should_get_the_root_node():
    graph = Graph(GRAMMAR, stacked_rules(), ROOT_ID)
    root_node = graph.get_root_node(ROOT_ID)
    assert isinstance(root_node, dict)
    assert len(root_node) == 2


def test_should_get_the_initial_pointers():
    graph = Graph(GRAMMAR, stacked_rules(), ROOT_ID)
    pointers = graph.get_initial_pointers()
    assert isinstance(pointers, Pointers)
    assert pointers.size == 2


def test_should_print_the_graph():
    graph = Graph(GRAMMAR, stacked_rules(), ROOT_ID)
    printed_graph = graph.print(None, True)
    assert isinstance(printed_graph, str)
    assert len(printed_graph) > 0


def test_should_iterate_over_pointers():
    graph = Graph(GRAMMAR, stacked_rules(), ROOT_ID)
    rules = [
        RuleChar([65, 66, 67]),
        RuleChar([68, 69, 70]),
        RuleChar([71, 72, 73]),
        RuleChar([74, 75, 76]),
        RuleCharExclude([1]),
        RuleEnd(),
    ]
    mock_pointers = Pointers(
        *[
            GraphPointer(GraphNode(rule, GraphNodeMeta(idx, idx, idx)))
            for idx, rule in enumerate(rules)
        ]
    )

    result = list(graph.iterate_over_pointers(mock_pointers))
    assert len(result) == 6
    all_pointers = list(mock_pointers)
    for rule, pointers in result:
        assert is_rule(rule) is True
        assert len(pointers) >= 1
        for pointer in pointers:
            assert any(pointer is candidate for candidate in all_pointers)


def test_should_raise_error_on_reference_rule():
    graph = Graph(GRAMMAR, stacked_rules(), ROOT_ID)
    mock_pointers = [
        GraphPointer(GraphNode(RuleRef(0), GraphNodeMeta(0, 0, 0))),
    ]

    with pytest.raises(ValueError, match="Encountered a reference rule in the graph"):
        list(graph.iterate_over_pointers(mock_pointers))
