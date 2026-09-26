import pytest

from . import graph_node as module
from .grammar_graph_types import PrintOpts
from .graph_node import GraphNode, GraphNodeMeta
from .rule_ref import RuleRef

META = GraphNodeMeta(1, 2, 3)
RULE = RuleRef(42)


def test_construct_with_rule_and_meta():
    node = GraphNode(RULE, META)
    assert node.rule is RULE
    assert node.meta is META


def test_raises_if_meta_is_undefined():
    with pytest.raises(ValueError, match="Meta is undefined"):
        GraphNode(RULE, None)


def test_correctly_calculates_and_caches_its_id():
    node = GraphNode(RULE, META)
    assert node.id == "1,2,3"
    node.meta = GraphNodeMeta(4, 5, 6)
    assert node.id == "1,2,3"


def test_delegates_print_to_the_print_graph_node_function(monkeypatch):
    calls = []

    def mock_print_graph_node(node):
        calls.append(node)
        return lambda opts: "mocked_response"

    monkeypatch.setattr(module, "print_graph_node", mock_print_graph_node)
    node = GraphNode(RULE, META)
    opts = PrintOpts(colorize=lambda text, color: str(text), show_position=False)
    assert node.print(opts) == "mocked_response"
    assert calls == [node]


def test_handles_next_node_linkage():
    next_node = GraphNode(RuleRef(43), META)
    node = GraphNode(RULE, META, next_node)
    assert node.next is next_node
