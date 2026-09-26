"""Port of ``src/grammar-graph/graph-node.ts``."""

from __future__ import annotations

from typing import Any, Callable, Optional, Union

from .colorize import Color, colorize as default_colorize
from .print import print_graph_node

Colorize = Callable[[Union[str, int], Color], str]


class GraphNodeMeta:
    __slots__ = ("stack_id", "path_id", "step_id")

    def __init__(self, stack_id: int, path_id: int, step_id: int) -> None:
        self.stack_id = stack_id
        self.path_id = path_id
        self.step_id = step_id

    def __repr__(self) -> str:
        return f"GraphNodeMeta({self.stack_id}, {self.path_id}, {self.step_id})"


class GraphNode:
    """Identity-compared, like the JS class."""

    __slots__ = ("rule", "next", "meta", "_id")

    def __init__(
        self,
        rule: Any,
        meta: GraphNodeMeta,
        next: Optional["GraphNode"] = None,
    ) -> None:
        self.rule = rule
        if meta is None:
            raise ValueError("Meta is undefined")
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
        pointers: Optional[Any] = None,
        show_position: bool = False,
        colorize: Colorize = default_colorize,
    ) -> str:
        return print_graph_node(
            self, pointers=pointers, show_position=show_position, colorize=colorize
        )

    def __repr__(self) -> str:
        return self.print(colorize=default_colorize, show_position=False)
