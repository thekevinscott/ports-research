from typing import TYPE_CHECKING, Optional

from .print import print_graph_node

if TYPE_CHECKING:
    from .grammar_graph_types import PrintOpts, UnresolvedRule


class GraphNodeMeta:
    def __init__(self, stack_id: int, path_id: int, step_id: int):
        self.stack_id = stack_id
        self.path_id = path_id
        self.step_id = step_id


class GraphNode:
    def __init__(
        self,
        rule: "UnresolvedRule",
        meta: Optional[GraphNodeMeta],
        next: Optional["GraphNode"] = None,
    ):
        self.rule = rule
        if meta is None:
            raise Exception("Meta is undefined")
        self.meta = meta
        self.next = next
        self.__id: Optional[str] = None

    @property
    def id(self) -> str:
        if self.__id is None:
            self.__id = f"{self.meta.stack_id},{self.meta.path_id},{self.meta.step_id}"
        return self.__id

    def print(self, opts: "PrintOpts") -> str:
        return print_graph_node(self)(opts)
