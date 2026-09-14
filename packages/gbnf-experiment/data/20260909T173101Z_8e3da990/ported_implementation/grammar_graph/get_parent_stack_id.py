from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .colorize import Color


def get_parent_stack_id(pointer: Any, col: Callable[..., str]) -> str:
    stack_ids: list[str] = []
    parent = pointer.parent
    while parent:
        meta = parent.node.meta
        stack_ids.append(f'{meta.stack_id},{meta.path_id},{meta.step_id}')
        parent = parent.parent
    return col('<-', Color.GRAY).join(col(stack_id, Color.RED) for stack_id in stack_ids)


getParentStackId = get_parent_stack_id
