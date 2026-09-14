from __future__ import annotations

from .colorize import Color


def get_parent_stack_id(pointer, col) -> str:
    stack_ids: list[str] = []
    parent = pointer.parent
    while parent is not None:
        stack_ids.append(
            f"{parent.node.meta.stack_id},"
            f"{parent.node.meta.path_id},"
            f"{parent.node.meta.step_id}",
        )
        parent = parent.parent
    arrow = col("<-", Color.GRAY)
    return arrow.join(col(stack_id, Color.RED) for stack_id in stack_ids)
