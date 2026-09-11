from typing import Any, Optional

from .print import print_graph_node


class GraphNodeMeta:
    def __init__(self, stack_id: int, path_id: int, step_id: int):
        self.stack_id = stack_id
        self.path_id = path_id
        self.step_id = step_id


class GraphNode:
    def __init__(
        self,
        rule: Any,
        meta: Optional[GraphNodeMeta],
        next_node: Optional["GraphNode"] = None,
    ):
        self.rule = rule
        if meta is None:
            raise Exception("Meta is undefined")
        self.meta = meta
        self.next = next_node
        self.__id: Optional[str] = None

    @property
    def id(self) -> str:
        if self.__id is None:
            self.__id = f"{self.meta.stack_id},{self.meta.path_id},{self.meta.step_id}"
        return self.__id

    def print(self, **opts: Any) -> str:
        return print_graph_node(self)(**opts)

    def __str__(self) -> str:
        return f"<GraphNode {self.rule}>"

    def __repr__(self) -> str:
        return str(self)
