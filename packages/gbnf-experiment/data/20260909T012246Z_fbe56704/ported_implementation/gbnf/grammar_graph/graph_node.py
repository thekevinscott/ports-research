from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from .colorize import Color, colorize as default_colorize
from .print import print_graph_node
from .types import UnresolvedRule

if TYPE_CHECKING:
    from .generic_set import GenericSet


@dataclass(frozen=True)
class GraphNodeMeta:
    stack_id: int
    path_id: int
    step_id: int


class GraphNode:
    def __init__(
        self,
        rule: UnresolvedRule,
        meta: GraphNodeMeta,
        next: Optional["GraphNode"] = None,
    ):
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
        colorize=default_colorize,
        pointers: Optional["GenericSet"] = None,
        show_position: bool = False,
    ) -> str:
        return print_graph_node(
            self, colorize=colorize, pointers=pointers, show_position=show_position
        )

    def __repr__(self) -> str:
        return self.print(colorize=default_colorize, show_position=False)
