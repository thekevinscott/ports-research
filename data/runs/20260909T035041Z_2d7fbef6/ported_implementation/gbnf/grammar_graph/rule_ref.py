from __future__ import annotations

from ..utils.errors.gbnf_error import GBNFError


class RuleRef:
    """A reference to another rule stack; resolved into graph nodes by :class:`Graph`."""

    def __init__(self, value: int):
        self.value = value
        self._nodes = None

    @property
    def nodes(self):
        if self._nodes is None:
            raise GBNFError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes) -> None:
        self._nodes = nodes

    def __repr__(self) -> str:
        return f"Ref({self.value})"
