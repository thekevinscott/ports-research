from .colorize import Color


def get_parent_stack_id(pointer, col) -> str:
    stack_ids: list[str] = []
    parent = pointer.parent
    while parent is not None:
        meta = parent.node.meta
        stack_ids.append(f"{meta.stack_id},{meta.path_id},{meta.step_id}")
        parent = parent.parent
    return col("<-", Color.GRAY).join(col(i, Color.RED) for i in stack_ids)
