"""A single step in a rule path."""

from typing import Any, Optional


class GraphNodeMeta:
    def __init__(self, stack_id: int, path_id: int, step_id: int):
        self.stack_id = stack_id
        self.path_id = path_id
        self.step_id = step_id


class GraphNode:
    def __init__(
        self,
        rule: Any,
        meta: Optional[GraphNodeMeta],
        next_node: Optional["GraphNode"] = None,
    ):
        self.rule = rule
        if not meta:
            raise ValueError("Meta is undefined")
        self.meta = meta
        self.next = next_node
        self._id: Optional[str] = None

    @property
    def id(self) -> str:
        if self._id is None:
            self._id = f"{self.meta.stack_id},{self.meta.path_id},{self.meta.step_id}"
        return self._id

    def print(self, opts: Any) -> str:
        from .print import print_graph_node

        return print_graph_node(self)(opts)

    def __repr__(self) -> str:
        return f"GraphNode(id={self.id}, rule={self.rule!r})"
