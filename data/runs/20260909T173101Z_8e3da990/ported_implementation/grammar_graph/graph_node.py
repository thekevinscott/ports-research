from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .colorize import colorize as default_colorize
from .print import print_graph_node


@dataclass
class GraphNodeMeta:
    stack_id: int
    path_id: int
    step_id: int


class GraphNode:
    def __init__(self, rule: Any, meta: GraphNodeMeta, next: "GraphNode | None" = None):
        self.rule = rule
        if meta is None:
            raise RuntimeError('Meta is undefined')
        self.meta = meta
        self.next = next
        self._id: str | None = None

    @property
    def id(self) -> str:
        if not self._id:
            self._id = f'{self.meta.stack_id},{self.meta.path_id},{self.meta.step_id}'
        return self._id

    def print(
        self,
        pointers: Any = None,
        show_position: bool = False,
        colorize: Callable[..., str] = default_colorize,
    ) -> str:
        return print_graph_node(self, pointers=pointers, show_position=show_position, colorize=colorize)

    def __repr__(self) -> str:
        return self.print(show_position=False)
