from typing import TYPE_CHECKING, Dict, Optional

if TYPE_CHECKING:  # pragma: no cover
    from .graph_node import GraphNode


class RuleRef:
    def __init__(self, value: int):
        self.value = value
        # Ordered set of nodes, keyed by identity.
        self._nodes: Optional[Dict[int, "GraphNode"]] = None

    @property
    def nodes(self) -> Dict[int, "GraphNode"]:
        if self._nodes is None:
            raise Exception("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: Dict[int, "GraphNode"]) -> None:
        self._nodes = nodes

    def __repr__(self) -> str:
        return f"RuleRef({self.value!r})"
