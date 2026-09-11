from typing import Callable, Optional

from .colorize import colorize as default_colorize
from .print import print_graph_node


class GraphNodeMeta:
    __slots__ = ("stack_id", "path_id", "step_id")

    def __init__(self, stack_id: int, path_id: int, step_id: int):
        self.stack_id = stack_id
        self.path_id = path_id
        self.step_id = step_id


class GraphNode:
    def __init__(
        self,
        rule,
        meta: GraphNodeMeta,
        next_: Optional["GraphNode"] = None,
    ):
        self.rule = rule
        if meta is None:
            raise Exception("Meta is undefined")
        self.meta = meta
        self.next = next_
        self._id: Optional[str] = None

    @property
    def id(self) -> str:
        if not self._id:
            self._id = f"{self.meta.stack_id},{self.meta.path_id},{self.meta.step_id}"
        return self._id

    def print(
        self,
        pointers=None,
        show_position: bool = False,
        colorize: Callable = default_colorize,
    ) -> str:
        return print_graph_node(
            self, pointers=pointers, show_position=show_position, colorize=colorize
        )

    def __repr__(self) -> str:
        return self.print(show_position=False, colorize=lambda s, c: f"{s}")
