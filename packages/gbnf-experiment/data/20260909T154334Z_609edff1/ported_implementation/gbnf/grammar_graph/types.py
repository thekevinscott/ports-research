import json
from enum import Enum
from typing import List, Sequence, Union


class RuleType(str, Enum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"


# A range is a two element list of code points, inclusive on both ends.
Range = List[int]
RuleCharValue = List[Union[int, Range]]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]


class _RuleWithValue:
    type: str

    def __init__(self, value: Sequence[Union[int, Range]]):
        self.value: RuleCharValue = list(value)

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash((self.type, json.dumps(self.value, separators=(",", ":"))))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"


class RuleChar(_RuleWithValue):
    def __init__(self, value: Sequence[Union[int, Range]]):
        self.type = RuleType.CHAR.value
        super().__init__(value)


class RuleCharExclude(_RuleWithValue):
    def __init__(self, value: Sequence[Union[int, Range]]):
        self.type = RuleType.CHAR_EXCLUDE.value
        super().__init__(value)


class RuleEnd:
    def __init__(self) -> None:
        self.type = RuleType.END.value

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return True

    def __hash__(self) -> int:
        return hash(self.type)

    def __repr__(self) -> str:
        return "RuleEnd()"
