from __future__ import annotations

from typing import Any, Callable, List, Union

from .colorize import Color


def get_parent_stack_id(
    pointer: Any,
    col: Callable[[Union[str, int], str], str],
) -> str:
    stack_ids: List[str] = []
    parent = pointer.parent
    while parent:
        meta = parent.node.meta
        stack_ids.append(f"{meta.stack_id},{meta.path_id},{meta.step_id}")
        parent = parent.parent
    arrow = col("<-", Color.GRAY)
    return arrow.join(col(stack_id, Color.RED) for stack_id in stack_ids)
