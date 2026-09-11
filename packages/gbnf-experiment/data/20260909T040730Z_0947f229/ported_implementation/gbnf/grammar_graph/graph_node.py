"""Port of ``src/grammar-graph/graph-node.ts``."""

from __future__ import annotations

from typing import Callable, Optional, Union

from .colorize import Color, colorize
from .print import print_graph_node
from .types import UnresolvedRule

Colorize = Callable[[Union[str, int], Color], str]


class GraphNodeMeta:
    __slots__ = ('stack_id', 'path_id', 'step_id')

    def __init__(self, stack_id: int, path_id: int, step_id: int) -> None:
        self.stack_id = stack_id
        self.path_id = path_id
        self.step_id = step_id


class GraphNode:
    __slots__ = ('rule', 'next', 'meta', '_id')

    def __init__(
        self,
        rule: UnresolvedRule,
        meta: GraphNodeMeta,
        next: Optional['GraphNode'] = None,
    ) -> None:
        self.rule = rule
        if meta is None:
            raise ValueError('Meta is undefined')
        self.meta = meta
        self.next = next
        self._id: Optional[str] = None

    @property
    def id(self) -> str:
        if self._id is None:
            self._id = f'{self.meta.stack_id},{self.meta.path_id},{self.meta.step_id}'
        return self._id

    def print(
        self,
        colorize: Colorize = colorize,
        pointers=None,
        show_position: bool = False,
    ) -> str:
        return print_graph_node(
            self, colorize=colorize, pointers=pointers, show_position=show_position
        )

    def __repr__(self) -> str:
        return self.print(colorize=colorize, show_position=False)
