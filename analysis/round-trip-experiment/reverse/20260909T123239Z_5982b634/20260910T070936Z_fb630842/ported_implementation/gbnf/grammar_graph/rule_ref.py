from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .types import RuleType

if TYPE_CHECKING:
    from .graph_node import GraphNode


class RuleRef:
    def __init__(self, value: int):
        self.type = RuleType.REF
        self.value = value
        self._nodes: Optional[List['GraphNode']] = None

    @property
    def nodes(self) -> List['GraphNode']:
        if self._nodes is None:
            raise ValueError('Nodes are not set')
        return self._nodes

    @nodes.setter
    def nodes(self, nodes) -> None:
        # Deduplicate by identity, preserving order, mirroring `new Set(nodes)`.
        unique: List['GraphNode'] = []
        seen = set()
        for node in nodes:
            if id(node) not in seen:
                seen.add(id(node))
                unique.append(node)
        self._nodes = unique

    def __repr__(self) -> str:
        return f'RuleRef({self.value!r})'
