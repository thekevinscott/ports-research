from typing import List, Sequence, Union

ValidInput = Union[str, int, Sequence[int]]

# A range is a two element list of code points, inclusive on both ends.
Range = List[int]
CharValue = List[Union[int, Range]]


class RuleType:
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"


class _Rule:
    """Base for the rules handed back to callers.

    Instances expose exactly the attributes the reference implementation puts on
    its plain objects, so ``__dict__`` round trips through ``json.dumps``.
    """

    type: str

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash((self.type, repr(getattr(self, "value", None))))


class RuleChar(_Rule):
    def __init__(self, value: CharValue):
        self.type = RuleType.CHAR
        self.value: CharValue = list(value)

    def __repr__(self) -> str:
        return f"RuleChar({self.value!r})"


class RuleCharExclude(_Rule):
    def __init__(self, value: CharValue):
        self.type = RuleType.CHAR_EXCLUDE
        self.value: CharValue = list(value)

    def __repr__(self) -> str:
        return f"RuleCharExclude({self.value!r})"


class RuleEnd(_Rule):
    def __init__(self) -> None:
        self.type = RuleType.END

    def __repr__(self) -> str:
        return "RuleEnd()"
