from typing import TYPE_CHECKING, Callable, List, Union

from .colorize import Color

if TYPE_CHECKING:
    from .graph_pointer import GraphPointer


def get_parent_stack_id(
    pointer: "GraphPointer", col: Callable[[Union[str, int], Color], str]
) -> str:
    stack_ids: List[str] = []
    parent = pointer.parent
    while parent:
        meta = parent.node.meta
        stack_ids.append(f"{meta.stack_id},{meta.path_id},{meta.step_id}")
        parent = parent.parent
    return col("<-", Color.GRAY).join(col(id, Color.RED) for id in stack_ids)
