from __future__ import annotations

from typing import Optional

from .print import print_graph_node
from .types import PrintOpts


class GraphNodeMeta:
    __slots__ = ('stack_id', 'path_id', 'step_id')

    def __init__(self, stack_id: int, path_id: int, step_id: int):
        self.stack_id = stack_id
        self.path_id = path_id
        self.step_id = step_id

    def __repr__(self) -> str:
        return f'{{{self.stack_id},{self.path_id},{self.step_id}}}'


class GraphNode:
    def __init__(
        self,
        rule,
        meta: GraphNodeMeta,
        next: Optional['GraphNode'] = None,
    ):
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

    def print(self, opts: PrintOpts) -> str:
        return print_graph_node(self)(opts)

    def __repr__(self) -> str:
        return f'GraphNode({self.id}, {self.rule!r})'
