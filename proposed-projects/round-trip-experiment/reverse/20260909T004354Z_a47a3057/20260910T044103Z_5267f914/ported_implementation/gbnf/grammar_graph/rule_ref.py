from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .graph_node import GraphNode


class RuleRef:
    def __init__(self, value: int):
        self.type = "rule_ref"
        self.value = value
        self._nodes: Optional[List["GraphNode"]] = None

    @property
    def nodes(self) -> List["GraphNode"]:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: List["GraphNode"]) -> None:
        # stored as a list so iteration order matches insertion order
        self._nodes = list(nodes)

    def __repr__(self) -> str:
        return f"RuleRef({self.value!r})"
