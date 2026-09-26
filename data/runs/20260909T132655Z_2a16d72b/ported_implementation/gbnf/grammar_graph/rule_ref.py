from typing import List, Optional


class RuleRef:
    def __init__(self, value: int):
        self.value = value
        self._nodes: Optional[List["object"]] = None

    @property
    def nodes(self):
        if self._nodes is None:
            raise Exception("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes) -> None:
        self._nodes = nodes

    def __repr__(self) -> str:
        return f"RuleRef({self.value})"
