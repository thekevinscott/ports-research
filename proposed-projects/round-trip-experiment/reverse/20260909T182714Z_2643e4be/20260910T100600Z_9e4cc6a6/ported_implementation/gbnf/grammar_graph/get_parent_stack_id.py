from __future__ import annotations

from typing import Callable, List, Union

from .colorize import Color


def get_parent_stack_id(
    pointer,
    col: Callable[[Union[str, int], str], str],
) -> str:
    stack_ids: List[str] = []
    parent = pointer.parent
    while parent:
        stack_ids.append(
            f"{parent.node.meta.stack_id},"
            f"{parent.node.meta.path_id},"
            f"{parent.node.meta.step_id}",
        )
        parent = parent.parent
    arrow = col("<-", Color.GRAY)
    return arrow.join(col(stack_id, Color.RED) for stack_id in stack_ids)
