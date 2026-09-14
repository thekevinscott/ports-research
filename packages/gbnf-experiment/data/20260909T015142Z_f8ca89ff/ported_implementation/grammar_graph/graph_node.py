from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from .colorize import Colorize, colorize
from .print import print_graph_node
from .types import UnresolvedRule

if TYPE_CHECKING:  # pragma: no cover
    from .types import Pointers

__all__ = ["GraphNode", "GraphNodeMeta"]


@dataclass
class GraphNodeMeta:
    stack_id: int
    path_id: int
    step_id: int

    # camelCase aliases, matching the reference API
    @property
    def stackId(self) -> int:
        return self.stack_id

    @property
    def pathId(self) -> int:
        return self.path_id

    @property
    def stepId(self) -> int:
        return self.step_id


class GraphNode:
    def __init__(
        self,
        rule: UnresolvedRule,
        meta: GraphNodeMeta,
        next: Optional["GraphNode"] = None,
    ):
        self.rule = rule
        if meta is None:
            raise Exception("Meta is undefined")
        self.meta = meta
        self.next = next
        self._id: Optional[str] = None

    @property
    def id(self) -> str:
        if not self._id:
            self._id = f"{self.meta.stack_id},{self.meta.path_id},{self.meta.step_id}"
        return self._id

    def print(
        self,
        pointers: Optional["Pointers"] = None,
        show_position: bool = False,
        colorize: Colorize = colorize,
    ) -> str:
        return print_graph_node(self)(
            pointers=pointers,
            show_position=show_position,
            colorize=colorize,
        )

    def __repr__(self) -> str:
        return self.print(colorize=colorize, show_position=False)
