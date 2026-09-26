from enum import Enum
from typing import Iterable, List, Sequence, Union


class RuleType(str, Enum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"

    def __str__(self) -> str:  # pragma: no cover - convenience only
        return self.value


# A Range is a two element list of code points, [start, end], inclusive.
Range = List[int]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, Sequence[int]]


class _RuleWithValue:
    """Base for the rules that carry a list of code points and/or ranges."""

    type: RuleType

    def __init__(self, value: Iterable[Union[int, Range]]):
        self.type = self.__class__.type
        self.value = [list(v) if isinstance(v, (list, tuple)) else v for v in value]

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return self.__dict__ == other.__dict__

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value!r})"


class RuleChar(_RuleWithValue):
    type = RuleType.CHAR


class RuleCharExclude(_RuleWithValue):
    type = RuleType.CHAR_EXCLUDE


class RuleEnd:
    def __init__(self) -> None:
        self.type = RuleType.END

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            return NotImplemented
        return self.__dict__ == other.__dict__

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return "RuleEnd()"
