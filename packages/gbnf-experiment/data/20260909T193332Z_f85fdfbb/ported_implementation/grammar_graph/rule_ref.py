from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:  # pragma: no cover
    from .graph_node import GraphNode


class RuleRef:
    """A reference to another rule, resolved to its graph nodes once built."""

    __slots__ = ("value", "_nodes")

    def __init__(self, value: int):
        self.value = value
        self._nodes: list["GraphNode"] | None = None

    @property
    def nodes(self) -> list["GraphNode"]:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: Iterable["GraphNode"]) -> None:
        # An insertion-ordered set: the reference implementation uses a JS `Set`,
        # whose iteration order is insertion order.
        seen: dict[int, "GraphNode"] = {}
        for node in nodes:
            seen.setdefault(id(node), node)
        self._nodes = list(seen.values())

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"RuleRef({self.value})"
