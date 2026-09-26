from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .graph_node import GraphNode


class RuleRef:
    def __init__(self, value: int):
        self.value = value
        # the referenced nodes, in insertion order (the reference implementation uses a
        # JS Set, which is ordered; Python's set is not).
        self._nodes: Optional[List["GraphNode"]] = None

    @property
    def nodes(self) -> List["GraphNode"]:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: List["GraphNode"]) -> None:
        self._nodes = nodes

    def __repr__(self) -> str:
        return f"RuleRef({self.value})"
