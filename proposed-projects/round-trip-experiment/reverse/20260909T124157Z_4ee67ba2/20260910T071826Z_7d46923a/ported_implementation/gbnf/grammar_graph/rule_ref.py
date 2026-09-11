from typing import TYPE_CHECKING, Dict, Iterable, Iterator, Optional

if TYPE_CHECKING:  # pragma: no cover
    from .graph_node import GraphNode


class RuleRef:
    """A reference to another rule's stack; resolved into nodes once the graph is built."""

    def __init__(self, value: int):
        self.value = value
        # An insertion-ordered set of nodes, keyed by identity.
        self.__nodes: Optional[Dict["GraphNode", None]] = None

    @property
    def type(self) -> str:
        return self.__class__.__name__

    @property
    def nodes(self) -> Iterable["GraphNode"]:
        if self.__nodes is None:
            raise Exception("Nodes are not set")
        return _NodeSet(self.__nodes)

    @nodes.setter
    def nodes(self, nodes: Iterable["GraphNode"]) -> None:
        self.__nodes = dict.fromkeys(nodes)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, RuleRef) and self.value == other.value

    def __hash__(self) -> int:
        return hash(("RuleRef", self.value))

    def __str__(self) -> str:
        return f"RuleRef(value={self.value})"

    def __repr__(self) -> str:
        return str(self)


class _NodeSet:
    """An insertion-ordered, identity-keyed set of nodes."""

    def __init__(self, nodes: Dict["GraphNode", None]):
        self.__nodes = nodes

    def __iter__(self) -> Iterator["GraphNode"]:
        return iter(self.__nodes)

    def __len__(self) -> int:
        return len(self.__nodes)

    def __contains__(self, node: object) -> bool:
        return node in self.__nodes
