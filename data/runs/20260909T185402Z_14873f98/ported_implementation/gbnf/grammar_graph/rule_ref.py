class RuleRef:
    def __init__(self, value: int):
        self.value = value
        self._nodes = None

    @property
    def nodes(self):
        if self._nodes is None:
            raise RuntimeError("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes) -> None:
        self._nodes = nodes

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return f"RuleRef({self.value})"
