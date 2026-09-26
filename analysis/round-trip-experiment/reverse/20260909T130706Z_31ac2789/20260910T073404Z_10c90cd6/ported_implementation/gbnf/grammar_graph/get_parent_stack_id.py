from typing import Callable, List

from .colorize import Color


def get_parent_stack_id(pointer, col: Callable[..., str]) -> str:
    stack_ids: List[str] = []
    parent = pointer.parent
    while parent:
        stack_ids.append(
            f"{parent.node.meta['stackId']},"
            f"{parent.node.meta['pathId']},"
            f"{parent.node.meta['stepId']}"
        )
        parent = parent.parent
    arrow = col("<-", Color.GRAY)
    return arrow.join(col(stack_id, Color.RED) for stack_id in stack_ids)


getParentStackId = get_parent_stack_id
