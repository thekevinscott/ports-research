from .colorize import Color


def get_parent_stack_id(pointer, col) -> str:
    stack_ids = []
    parent = pointer.parent
    while parent is not None:
        meta = parent.node.meta
        stack_ids.append(f"{meta['stackId']},{meta['pathId']},{meta['stepId']}")
        parent = parent.parent
    return col("<-", Color.GRAY).join(col(id_, Color.RED) for id_ in stack_ids)
