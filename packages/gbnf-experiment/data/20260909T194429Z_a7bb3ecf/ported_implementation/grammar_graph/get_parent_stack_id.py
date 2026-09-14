from __future__ import annotations

from typing import TYPE_CHECKING, List

from .colorize import Color, Colorize

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .graph_pointer import GraphPointer


def get_parent_stack_id(pointer: 'GraphPointer', col: Colorize) -> str:
    stack_ids: List[str] = []
    parent = pointer.parent
    while parent:
        meta = parent.node.meta
        stack_ids.append(f'{meta.stack_id},{meta.path_id},{meta.step_id}')
        parent = parent.parent
    return col('<-', Color.GRAY).join(col(id_, Color.RED) for id_ in stack_ids)
