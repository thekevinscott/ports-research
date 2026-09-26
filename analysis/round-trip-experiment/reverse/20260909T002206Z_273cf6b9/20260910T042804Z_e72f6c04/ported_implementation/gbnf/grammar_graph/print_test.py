import pytest

from . import print as module
from .grammar_graph_types import PrintOpts, RuleChar
from .print import print_graph_node, print_graph_pointer
from .rule_ref import RuleRef

COLORS = {
    "\x1b[34m": "BLUE",
    "\x1b[36m": "CYAN",
    "\x1b[32m": "GREEN",
    "\x1b[31m": "RED",
    "\x1b[90m": "GRAY",
    "\x1b[33m": "YELLOW",
}


def mock_colorize(text, color):
    if color not in COLORS:
        raise ValueError(f"Invalid color: {color}")
    return f"[{COLORS[color]}]:{text}"


class MockNode:
    def __init__(self, id, rule, next=None):
        self.id = str(id)
        self.rule = rule
        self.next = next

    def print(self, opts):
        return f"Node({self.id})"


class MockGraphPointer:
    def __init__(self, node):
        self.node = node
        self.parent = None

    def print(self, opts):
        return f"Pointer to {self.node.id}"


@pytest.fixture(autouse=True)
def stub_get_parent_stack_id(monkeypatch):
    monkeypatch.setattr(module, "get_parent_stack_id", lambda pointer, col: "")
    yield monkeypatch


def test_print_graph_pointer_prints_graph_pointer_details_correctly(
    stub_get_parent_stack_id,
):
    mock_node = MockNode(1, RuleRef(100))
    mock_pointer = MockGraphPointer(mock_node)
    stub_get_parent_stack_id.setattr(
        module, "get_parent_stack_id", lambda pointer, col: "foo"
    )
    result = print_graph_pointer(mock_pointer)(
        PrintOpts(colorize=mock_colorize, pointers=None, show_position=False)
    )
    assert result == "[RED]:*foo"


def test_print_graph_node_prints_graph_node_with_a_character_rule():
    mock_node = MockNode(1, RuleChar([65]))
    result = print_graph_node(mock_node)(
        PrintOpts(colorize=mock_colorize, show_position=False, pointers=None)
    )
    assert result == "[GRAY]:[[YELLOW]:A[GRAY]:]"


def test_print_graph_node_prints_graph_node_with_a_rule_reference():
    mock_node = MockNode(1, RuleRef(200))
    result = print_graph_node(mock_node)(
        PrintOpts(colorize=mock_colorize, show_position=True, pointers=None)
    )
    assert result == "[BLUE]:{[GRAY]:1[BLUE]:}[GRAY]:Ref([GREEN]:200[GRAY]:)"
