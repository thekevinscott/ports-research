from typing import NamedTuple, Optional

from .colorize import colorize
from .print import print_graph_node


class GraphNodeMeta(NamedTuple):
    stack_id: int
    path_id: int
    step_id: int


class GraphNode:
    def __init__(self, rule, meta: GraphNodeMeta, next: Optional["GraphNode"] = None):
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

    def print(self, pointers=None, show_position: bool = False, colorize=colorize) -> str:
        return print_graph_node(
            self, pointers=pointers, show_position=show_position, colorize=colorize
        )

    def __repr__(self) -> str:
        return self.print(show_position=False, colorize=lambda s, _c: f"{s}")
