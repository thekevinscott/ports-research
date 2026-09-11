from typing import TYPE_CHECKING, List, Optional

from .rule_type import RuleType

if TYPE_CHECKING:  # pragma: no cover
    from .graph_node import GraphNode


class RuleRef:
    """A reference to another rule in the graph.

    Rule refs are resolved while walking the graph and are never exposed to the
    end user.
    """

    type = RuleType.REF

    def __init__(self, value: int):
        self.value = value
        self.__nodes__: Optional[List["GraphNode"]] = None

    @property
    def nodes(self) -> List["GraphNode"]:
        if self.__nodes__ is None:
            raise ValueError("Nodes are not set")
        return self.__nodes__

    @nodes.setter
    def nodes(self, nodes) -> None:
        self.__nodes__ = list(nodes)

    def equals(self, other: object) -> bool:
        return isinstance(other, RuleRef) and self.value == other.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleRef):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash((RuleRef, self.value))

    def __repr__(self) -> str:
        return f"RuleRef({self.value})"
