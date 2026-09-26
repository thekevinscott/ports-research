from __future__ import annotations

from typing import NamedTuple

from .colorize import colorize
from .print import print_graph_node


class GraphNodeMeta(NamedTuple):
    stack_id: int
    path_id: int
    step_id: int


class GraphNode:
    def __init__(self, rule, meta: GraphNodeMeta, next_: "GraphNode | None" = None):
        self.rule = rule
        if meta is None:
            raise ValueError("Meta is undefined")
        self.meta = meta
        self.next = next_
        self._id: str | None = None

    @property
    def id(self) -> str:
        if not self._id:
            self._id = f"{self.meta.stack_id},{self.meta.path_id},{self.meta.step_id}"
        return self._id

    def print(self, col=colorize, pointers=None, show_position: bool = False) -> str:
        return print_graph_node(
            self, col=col, pointers=pointers, show_position=show_position
        )

    def __repr__(self) -> str:
        return self.print(col=colorize, show_position=False)
