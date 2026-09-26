from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Iterable, Optional

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .graph_node import GraphNode


class RuleRef:
    __slots__ = ('value', '_nodes')

    def __init__(self, value: int):
        self.value = value
        self._nodes: Optional[Dict[int, 'GraphNode']] = None

    @property
    def nodes(self) -> Iterable['GraphNode']:
        if self._nodes is None:
            raise Exception('Nodes are not set')
        return list(self._nodes.values())

    @nodes.setter
    def nodes(self, nodes: Iterable['GraphNode']) -> None:
        # an insertion-ordered, identity-based set of nodes
        self._nodes = {id(node): node for node in nodes}

    def __repr__(self) -> str:
        return f'RuleRef({self.value})'
