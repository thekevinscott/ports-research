from dataclasses import dataclass
from typing import Any, Optional

from .colorize import colorize
from .print import print_graph_node


@dataclass
class GraphNodeMeta:
    stack_id: int
    path_id: int
    step_id: int


class GraphNode:
    def __init__(
        self,
        rule: Any,
        meta: GraphNodeMeta,
        next_: Optional['GraphNode'] = None,
    ):
        self.rule = rule
        if meta is None:
            raise Exception('Meta is undefined')
        self.meta = meta
        self.next = next_
        self._id: Optional[str] = None
        self.print = print_graph_node(self)

    @property
    def id(self) -> str:
        if not self._id:
            self._id = f'{self.meta.stack_id},{self.meta.path_id},{self.meta.step_id}'
        return self._id

    def __repr__(self) -> str:
        return self.print(colorize=colorize, show_position=False)
