"""Port of ``src/grammar-graph/rule-ref.ts``."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, List, Optional

if TYPE_CHECKING:  # pragma: no cover
    from .graph_node import GraphNode


class RuleRef:
    """A reference to another rule. Identity-compared, like the JS class.

    The original stores referenced nodes in a ``Set``, which iterates in insertion
    order; a de-duplicated list is used here to keep that ordering deterministic.
    """

    __slots__ = ("value", "_nodes")

    def __init__(self, value: int) -> None:
        self.value = value
        self._nodes: Optional[List["GraphNode"]] = None

    @property
    def nodes(self) -> List["GraphNode"]:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: Iterable["GraphNode"]) -> None:
        seen: List["GraphNode"] = []
        for node in nodes:
            if not any(node is existing for existing in seen):
                seen.append(node)
        self._nodes = seen

    def __repr__(self) -> str:
        return f"RuleRef({self.value})"
