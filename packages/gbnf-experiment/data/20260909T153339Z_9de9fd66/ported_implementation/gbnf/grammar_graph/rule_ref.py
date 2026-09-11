from typing import Dict, Optional


class RuleRef:
    """A reference to another rule in the graph.

    RuleRefs should never be exposed to the end user; they are resolved away
    while walking the graph.
    """

    def __init__(self, value: int):
        self.value = value
        # an insertion ordered set of GraphNodes, keyed by object id.
        self._nodes: Optional[Dict[int, "object"]] = None

    @property
    def nodes(self):
        if self._nodes is None:
            raise Exception("Nodes are not set")
        return list(self._nodes.values())

    @nodes.setter
    def nodes(self, nodes) -> None:
        self._nodes = {id(node): node for node in nodes}

    def __repr__(self) -> str:
        return f"RuleRef({self.value})"
