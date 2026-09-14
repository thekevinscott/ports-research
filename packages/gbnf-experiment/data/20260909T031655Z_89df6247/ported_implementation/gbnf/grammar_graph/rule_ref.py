class RuleRef:
    """A reference to another rule; never exposed to the end user."""

    def __init__(self, value: int):
        self.value = value
        self._nodes = None

    @property
    def nodes(self):
        if self._nodes is None:
            raise Exception("Nodes are not set")
        return self._nodes

    @nodes.setter
    def nodes(self, nodes):
        self._nodes = nodes

    def __repr__(self):
        return f"RuleRef({self.value})"
