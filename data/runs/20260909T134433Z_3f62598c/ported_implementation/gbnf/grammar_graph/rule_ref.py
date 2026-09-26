from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, Optional

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .graph_node import GraphNode


class RuleRef:
    def __init__(self, value: int):
        self.value = value
        self._nodes: Optional[Iterable["GraphNode"]] = None

    @property
    def nodes(self) -> Iterable["GraphNode"]:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: Iterable["GraphNode"]) -> None:
        self._nodes = nodes

    def __repr__(self) -> str:
        return f"RuleRef({self.value})"
