from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .colorize import Color

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .graph_pointer import GraphPointer


def get_parent_stack_id(pointer: "GraphPointer", col) -> str:
    stack_ids: List[str] = []
    parent: Optional["GraphPointer"] = pointer.parent
    while parent:
        meta = parent.node.meta
        stack_ids.append(f"{meta.stackId},{meta.pathId},{meta.stepId}")
        parent = parent.parent
    return col("<-", Color.GRAY).join(col(id_, Color.RED) for id_ in stack_ids)
