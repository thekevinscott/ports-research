class RuleRef:
    def __init__(self, value: int):
        self.value = value
        self.__nodes__ = None

    @property
    def nodes(self):
        if self.__nodes__ is None:
            raise ValueError("Nodes are not set")
        return self.__nodes__

    @nodes.setter
    def nodes(self, nodes) -> None:
        self.__nodes__ = nodes

    def __eq__(self, other: object) -> bool:
        return isinstance(other, RuleRef) and self.value == other.value

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return f"RuleRef(value={self.value})"
