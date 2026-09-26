from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .colorize import Color, Colorize

if TYPE_CHECKING:  # pragma: no cover
    from .graph_pointer import GraphPointer

__all__ = ["get_parent_stack_id", "getParentStackId"]


def get_parent_stack_id(pointer: "GraphPointer", col: Colorize) -> str:
    stack_ids: List[str] = []
    parent: Optional["GraphPointer"] = pointer.parent
    while parent is not None:
        meta = parent.node.meta
        stack_ids.append(f"{meta.stack_id},{meta.path_id},{meta.step_id}")
        parent = parent.parent
    return col("<-", Color.GRAY).join(col(stack_id, Color.RED) for stack_id in stack_ids)


getParentStackId = get_parent_stack_id
