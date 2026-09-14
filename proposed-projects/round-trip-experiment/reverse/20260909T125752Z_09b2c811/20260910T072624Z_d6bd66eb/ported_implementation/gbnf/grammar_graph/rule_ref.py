"""A reference to another rule's nodes."""

from typing import Iterable, List, Optional


class RuleRef:
    def __init__(self, value: int):
        self.type = "ref"
        self.value = value
        self._nodes: Optional[List] = None

    @property
    def nodes(self) -> List:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: Iterable) -> None:
        # Insertion ordered, so alternate paths are yielded in grammar order.
        self._nodes = list(dict.fromkeys(nodes))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, RuleRef) and self.value == other.value

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return f"RuleRef(value={self.value!r})"
