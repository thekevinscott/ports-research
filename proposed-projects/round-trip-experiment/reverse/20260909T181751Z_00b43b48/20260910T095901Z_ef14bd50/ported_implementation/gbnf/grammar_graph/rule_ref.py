from typing import TYPE_CHECKING, List, Optional

from .rule_type import RuleType

if TYPE_CHECKING:
    from .graph_node import GraphNode


class RuleRef:
    def __init__(self, value: int):
        self.type = RuleType.REF
        self.value = value
        # an insertion-ordered collection of the nodes this rule refers to; the
        # graph sets it once every stack has been built.
        self.__nodes: Optional[List["GraphNode"]] = None

    @property
    def nodes(self) -> List["GraphNode"]:
        if self.__nodes is None:
            raise Exception("Nodes are not set")
        return self.__nodes

    @nodes.setter
    def nodes(self, nodes: List["GraphNode"]) -> None:
        self.__nodes = list(nodes)

    def __repr__(self) -> str:
        return f"RuleRef({self.value})"
