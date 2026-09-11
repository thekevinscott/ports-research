from __future__ import annotations

from typing import Optional

from ..utils.errors.gbnf_error import GBNFError
from .colorize import colorize as default_colorize
from .print import print_graph_node


class GraphNodeMeta:
    __slots__ = ("stack_id", "path_id", "step_id")

    def __init__(self, stack_id: int, path_id: int, step_id: int):
        self.stack_id = stack_id
        self.path_id = path_id
        self.step_id = step_id

    def __repr__(self) -> str:
        return f"{{stackId: {self.stack_id}, pathId: {self.path_id}, stepId: {self.step_id}}}"


class GraphNode:
    def __init__(self, rule, meta: GraphNodeMeta, next: Optional["GraphNode"] = None):
        self.rule = rule
        if meta is None:
            raise GBNFError("Meta is undefined")
        self.meta = meta
        self.next = next
        self._id: Optional[str] = None

    @property
    def id(self) -> str:
        if not self._id:
            self._id = f"{self.meta.stack_id},{self.meta.path_id},{self.meta.step_id}"
        return self._id

    def print(
        self, colorize=default_colorize, pointers=None, show_position: bool = False
    ) -> str:
        return print_graph_node(
            self, colorize=colorize, pointers=pointers, show_position=show_position
        )

    def __repr__(self) -> str:
        return self.print(colorize=default_colorize, show_position=False)
