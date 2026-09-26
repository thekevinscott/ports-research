from dataclasses import dataclass
from typing import Optional

from .grammar_graph_types import PrintOpts, UnresolvedRule
from .print import print_graph_node


@dataclass
class GraphNodeMeta:
    stack_id: int
    path_id: int
    step_id: int


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
        return f"GraphNode({self.rule!r}, {self.meta!r})"
