from __future__ import annotations

from typing import List

from .colorize import Color
from .types import Colorize


def get_parent_stack_id(pointer, col: Colorize) -> str:
    stack_ids: List[str] = []
    parent = pointer.parent
    while parent:
        meta = parent.node.meta
        stack_ids.append(f'{meta.stack_id},{meta.path_id},{meta.step_id}')
        parent = parent.parent
    return col('<-', Color.GRAY).join(
        col(stack_id, Color.RED) for stack_id in stack_ids
    )
