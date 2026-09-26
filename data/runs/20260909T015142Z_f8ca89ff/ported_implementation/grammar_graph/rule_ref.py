from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List, Optional

if TYPE_CHECKING:  # pragma: no cover
    from .graph_node import GraphNode

__all__ = ["RuleRef"]


class RuleRef:
    __slots__ = ("value", "_nodes")

    def __init__(self, value: int):
        self.value = value
        self._nodes: Optional[List["GraphNode"]] = None

    @property
    def nodes(self) -> List["GraphNode"]:
        if self._nodes is None:
            raise Exception("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: Iterable["GraphNode"]) -> None:
        # A list rather than a set: the reference relies on insertion order when
        # walking referenced nodes, which JS `Set` preserves and Python's does not.
        unique: List["GraphNode"] = []
        seen = set()
        for node in nodes:
            if id(node) not in seen:
                seen.add(id(node))
                unique.append(node)
        self._nodes = unique

    def __repr__(self) -> str:
        return f"RuleRef({self.value})"
