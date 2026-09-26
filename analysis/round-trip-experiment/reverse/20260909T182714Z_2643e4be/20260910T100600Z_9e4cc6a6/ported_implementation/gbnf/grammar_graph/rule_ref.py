from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Set

if TYPE_CHECKING:  # pragma: no cover
    from .graph_node import GraphNode


class RuleRef:
    def __init__(self, value: int) -> None:
        self._nodes: Optional[Set["GraphNode"]] = None
        self.value = value

    @property
    def nodes(self) -> Set["GraphNode"]:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: Set["GraphNode"]) -> None:
        self._nodes = nodes

    def __eq__(self, other: object) -> bool:
        return isinstance(other, RuleRef) and other.value == self.value

    def __hash__(self) -> int:
        return id(self)

    def __repr__(self) -> str:
        return f"RuleRef(value={self.value})"
