from typing import Optional

from .grammar_graph_types import PrintOpts, UnresolvedRule
from .print import print_graph_node


class GraphNodeMeta:
    __slots__ = ("stack_id", "path_id", "step_id")

    def __init__(self, stack_id: int, path_id: int, step_id: int):
        self.stack_id = stack_id
        self.path_id = path_id
        self.step_id = step_id


class GraphNode:
    def __init__(
        self,
        rule: UnresolvedRule,
        meta: Optional[GraphNodeMeta],
        next_node: Optional["GraphNode"] = None,
    ):
        self.rule = rule
        if meta is None:
            raise ValueError("Meta is undefined")
        self.meta = meta
        self.next = next_node
        self._id: Optional[str] = None

    @property
    def id(self) -> str:
        if self._id is None:
            meta = self.meta
            self._id = f"{meta.stack_id},{meta.path_id},{meta.step_id}"
        return self._id

    def print(self, opts: PrintOpts) -> str:
        return print_graph_node(self)(opts)

    def __repr__(self) -> str:
        return f"GraphNode({self.id}, {self.rule!r})"
