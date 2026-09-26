"""Port of ``src/grammar-graph/rule-ref.ts``."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:  # pragma: no cover
    from .graph_node import GraphNode


class RuleRef:
    def __init__(self, value: int):
        self.value = value
        self._nodes: Optional[List["GraphNode"]] = None

    @property
    def nodes(self) -> List["GraphNode"]:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: List["GraphNode"]) -> None:
        # A list, not a set: the reference relies on Javascript `Set` insertion
        # order, which Python sets do not preserve.
        self._nodes = nodes

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"RuleRef({self.value})"
