from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .graph_node import GraphNode


class RuleRef:
    def __init__(self, value: int):
        self.value = value
        self._nodes: Optional[list["GraphNode"]] = None

    @property
    def nodes(self) -> list["GraphNode"]:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: list["GraphNode"]) -> None:
        self._nodes = nodes

    def __repr__(self) -> str:
        return f"RuleRef({self.value!r})"
