from __future__ import annotations

from .colorize import Color


def get_parent_stack_id(pointer, col) -> str:
    stack_ids: list[str] = []
    parent = pointer.parent
    while parent:
        meta = parent.node.meta
        stack_ids.append(f"{meta.stack_id},{meta.path_id},{meta.step_id}")
        parent = parent.parent
    return col("<-", Color.GRAY).join(col(id_, Color.RED) for id_ in stack_ids)
