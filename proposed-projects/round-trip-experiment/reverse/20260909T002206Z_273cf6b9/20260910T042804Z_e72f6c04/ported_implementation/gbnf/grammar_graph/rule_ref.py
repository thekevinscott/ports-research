from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:  # pragma: no cover - import cycle only matters for type checkers
    from .graph_node import GraphNode


class RuleRef:
    def __init__(self, value: int) -> None:
        self.value = value
        self._nodes: Optional[List["GraphNode"]] = None

    @property
    def nodes(self) -> List["GraphNode"]:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes) -> None:
        # An ordered, de-duplicated collection, mirroring the reference's `Set`.
        self._nodes = list(dict.fromkeys(nodes))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, RuleRef) and self.value == other.value

    def __hash__(self) -> int:
        return hash((RuleRef, self.value))

    def __repr__(self) -> str:
        return f"RuleRef(value={self.value})"
