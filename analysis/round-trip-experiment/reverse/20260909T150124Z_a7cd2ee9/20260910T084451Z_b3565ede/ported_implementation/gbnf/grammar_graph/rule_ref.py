from .grammar_graph_types import RuleType


class RuleRef:
    def __init__(self, value: int) -> None:
        self.type = RuleType.REF
        self.value = value
        self._nodes: list | None = None

    @property
    def nodes(self) -> list:
        if self._nodes is None:
            raise ValueError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: list) -> None:
        self._nodes = nodes

    def __repr__(self) -> str:
        return f"RuleRef(value={self.value!r})"
