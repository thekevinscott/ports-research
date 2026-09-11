from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .colorize import no_color
from .print import print_graph_node
from .types import UnresolvedRule


@dataclass(frozen=True)
class GraphNodeMeta:
    stackId: int
    pathId: int
    stepId: int


class GraphNode:
    def __init__(
        self,
        rule: UnresolvedRule,
        meta: GraphNodeMeta,
        next: Optional["GraphNode"] = None,
    ):
        self.rule = rule
        if meta is None:
            raise ValueError("Meta is undefined")
        self.meta = meta
        self.next = next
        self._id: Optional[str] = None

    @property
    def id(self) -> str:
        if not self._id:
            self._id = f"{self.meta.stackId},{self.meta.pathId},{self.meta.stepId}"
        return self._id

    def print(self, pointers=None, show_position: bool = False, colorize=no_color) -> str:
        return print_graph_node(
            self, pointers=pointers, show_position=show_position, colorize=colorize
        )

    def __repr__(self) -> str:
        return self.print(show_position=False, colorize=no_color)
