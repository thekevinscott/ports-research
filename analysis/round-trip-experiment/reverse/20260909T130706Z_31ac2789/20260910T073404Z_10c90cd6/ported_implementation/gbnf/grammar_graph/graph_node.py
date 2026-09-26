from typing import Any, Dict, Optional

from .grammar_graph_types import UnresolvedRule
from .print import print_graph_node


# A node's position in the graph: which stack, path and step it came from.
GraphNodeMeta = Dict[str, int]


class GraphNode:
    def __init__(
        self,
        rule: UnresolvedRule,
        meta: Optional[GraphNodeMeta],
        next_node: Optional["GraphNode"] = None,
    ):
        self.rule = rule
        if meta is None:
            raise ValueError("Meta is undefined")
        self.meta = meta
        self.next = next_node
        self.__id__: Optional[str] = None

    @property
    def id(self) -> str:
        if self.__id__ is None:
            self.__id__ = (
                f"{self.meta['stackId']},{self.meta['pathId']},{self.meta['stepId']}"
            )
        return self.__id__

    def print(self, opts: Dict[str, Any]) -> str:
        return print_graph_node(self)(opts)

    def __repr__(self) -> str:
        return f"GraphNode({self.id}, {self.rule!r})"
