from typing import TYPE_CHECKING, List

from .colorize import Color

if TYPE_CHECKING:
    from .grammar_graph_types import Colorize
    from .graph_pointer import GraphPointer


def get_parent_stack_id(pointer: "GraphPointer", col: "Colorize") -> str:
    stack_ids: List[str] = []
    parent = pointer.parent
    while parent:
        meta = parent.node.meta
        stack_ids.append(f"{meta.stack_id},{meta.path_id},{meta.step_id}")
        parent = parent.parent
    arrow = col("<-", Color.GRAY)
    return arrow.join(col(stack_id, Color.RED) for stack_id in stack_ids)
