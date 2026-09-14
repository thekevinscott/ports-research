from enum import Enum
from typing import List, Sequence, Union


class RuleType(str, Enum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"

    def __str__(self) -> str:  # pragma: no cover - convenience only
        return self.value


# A `Range` is a two element `[start, end]` pair of code points.
Range = List[int]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]

CharValue = List[Union[int, Range]]


def _normalize(value: Sequence[Union[int, Sequence[int]]]) -> CharValue:
    return [list(v) if isinstance(v, (list, tuple)) else v for v in value]


def _freeze(value: CharValue):
    return tuple(tuple(v) if isinstance(v, list) else v for v in value)


class RuleChar:
    def __init__(self, value: Sequence[Union[int, Range]]):
        self.type = RuleType.CHAR
        self.value = _normalize(value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleChar):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash((self.type, _freeze(self.value)))

    def __repr__(self) -> str:
        return f"RuleChar({self.value!r})"


class RuleCharExclude:
    def __init__(self, value: Sequence[Union[int, Range]]):
        self.type = RuleType.CHAR_EXCLUDE
        self.value = _normalize(value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleCharExclude):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash((self.type, _freeze(self.value)))

    def __repr__(self) -> str:
        return f"RuleCharExclude({self.value!r})"


class RuleEnd:
    def __init__(self) -> None:
        self.type = RuleType.END

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleEnd):
            return NotImplemented
        return True

    def __hash__(self) -> int:
        return hash(self.type)

    def __repr__(self) -> str:
        return "RuleEnd()"
