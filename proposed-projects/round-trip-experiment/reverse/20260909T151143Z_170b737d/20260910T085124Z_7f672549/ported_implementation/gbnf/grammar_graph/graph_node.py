from typing import Optional

from .grammar_graph_types import UnresolvedRule
from .print import print_graph_node


class GraphNode:
    def __init__(self, rule: UnresolvedRule, meta, next_node: Optional["GraphNode"] = None):
        self.rule = rule
        if meta is None:
            raise ValueError("Meta is undefined")
        self.meta = meta
        self.next = next_node
        self.__id__ = None

    @property
    def id(self) -> str:
        if self.__id__ is None:
            self.__id__ = (
                f"{self.meta['stackId']},{self.meta['pathId']},{self.meta['stepId']}"
            )
        return self.__id__

    def print(self, **opts) -> str:
        return print_graph_node(self, **opts)

    def __repr__(self) -> str:
        return f"<GraphNode {self.id} {self.rule}>"
