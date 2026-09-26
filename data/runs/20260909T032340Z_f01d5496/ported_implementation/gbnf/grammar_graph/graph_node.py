from typing import NamedTuple, Optional

from .colorize import colorize
from .print import print_graph_node


class GraphNodeMeta(NamedTuple):
    stack_id: int
    path_id: int
    step_id: int


class GraphNode:
    def __init__(self, rule, meta: GraphNodeMeta, next_: Optional["GraphNode"] = None):
        self.rule = rule
        if meta is None:
            raise Exception("Meta is undefined")
        self.meta = meta
        self.next = next_
        self._id: Optional[str] = None

    @property
    def id(self) -> str:
        if self._id is None:
            self._id = f"{self.meta.stack_id},{self.meta.path_id},{self.meta.step_id}"
        return self._id

    def print(self, colorize=colorize, pointers=None, show_position: bool = False):
        return print_graph_node(
            self, colorize, pointers=pointers, show_position=show_position
        )

    def __repr__(self) -> str:
        return self.print(colorize=lambda v, c: f"{v}", show_position=True)
