import json

from .colorize import Color
from .get_parent_stack_id import get_parent_stack_id
from .grammar_graph_types import RuleEnd
from .graph_node import GraphNode, GraphNodeMeta
from .graph_pointer import GraphPointer


def s(value):
    return json.dumps(value)


def mock_colorize(text, color):
    return f"[{s(color)}]:{text}"


RED = s(Color.RED)
GRAY = s(Color.GRAY)


def create_mock_pointer(stack_id, path_id, step_id, parent=None):
    return GraphPointer(
        GraphNode(RuleEnd(), GraphNodeMeta(stack_id, path_id, step_id)),
        parent,
    )


def test_returns_an_empty_string_if_no_parents():
    pointer = create_mock_pointer(1, 1, 1)
    assert get_parent_stack_id(pointer, mock_colorize) == ""


def test_returns_a_single_parent_id_colored_correctly():
    parent_pointer = create_mock_pointer(1, 1, 1)
    pointer = create_mock_pointer(2, 2, 2, parent_pointer)
    assert get_parent_stack_id(pointer, mock_colorize) == f"[{RED}]:1,1,1"


def test_returns_multiple_parent_ids_separated_by_colored_arrows():
    grandparent_pointer = create_mock_pointer(0, 0, 0)
    parent_pointer = create_mock_pointer(1, 1, 1, grandparent_pointer)
    pointer = create_mock_pointer(2, 2, 2, parent_pointer)
    assert (
        get_parent_stack_id(pointer, mock_colorize)
        == f"[{RED}]:1,1,1[{GRAY}]:<-[{RED}]:0,0,0"
    )


def test_handles_deep_nesting_of_pointers():
    great_grandparent_pointer = create_mock_pointer(0, 0, 0)
    grandparent_pointer = create_mock_pointer(1, 1, 1, great_grandparent_pointer)
    parent_pointer = create_mock_pointer(2, 2, 2, grandparent_pointer)
    pointer = create_mock_pointer(3, 3, 3, parent_pointer)
    assert (
        get_parent_stack_id(pointer, mock_colorize)
        == f"[{RED}]:2,2,2[{GRAY}]:<-[{RED}]:1,1,1[{GRAY}]:<-[{RED}]:0,0,0"
    )
