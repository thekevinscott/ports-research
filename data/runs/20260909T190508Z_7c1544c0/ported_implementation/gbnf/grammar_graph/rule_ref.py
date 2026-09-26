from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:  # pragma: no cover
    from .graph_node import GraphNode


class RuleRef:
    """A reference to another rule, resolved to its nodes once the graph is built.

    The reference implementation stores the nodes in a JS ``Set``; the nodes are
    already distinct, so a list preserves both uniqueness and iteration order.
    """

    def __init__(self, value: int):
        self.value = value
        self._nodes: Optional[List['GraphNode']] = None

    @property
    def nodes(self) -> List['GraphNode']:
        if self._nodes is None:
            raise Exception('Nodes are not set')
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: List['GraphNode']) -> None:
        self._nodes = list(nodes)
