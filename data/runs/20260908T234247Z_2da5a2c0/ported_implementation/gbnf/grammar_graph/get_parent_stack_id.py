"""Port of ``src/grammar-graph/get-parent-stack-id.ts``."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, List, Union

from .colorize import Color

if TYPE_CHECKING:  # pragma: no cover
    from .graph_pointer import GraphPointer

Colorize = Callable[[Union[str, int], Color], str]


def get_parent_stack_id(pointer: "GraphPointer", col: Colorize) -> str:
    stack_ids: List[str] = []
    parent = pointer.parent
    while parent is not None:
        meta = parent.node.meta
        stack_ids.append(f"{meta.stack_id},{meta.path_id},{meta.step_id}")
        parent = parent.parent
    return col("<-", Color.GRAY).join(col(id, Color.RED) for id in stack_ids)
