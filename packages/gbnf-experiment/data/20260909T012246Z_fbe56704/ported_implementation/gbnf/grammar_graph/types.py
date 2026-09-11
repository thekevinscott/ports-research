from enum import Enum
from typing import Iterable, List, Sequence, Tuple, Union


class RuleType(str, Enum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"

    def __str__(self) -> str:
        return self.value


# A range of code points, inclusive on both ends.
Range = Tuple[int, int]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]


def _normalize_values(
    value: Iterable[Union[int, Sequence[int]]]
) -> List[Union[int, Range]]:
    """Ranges are normalized to tuples so that rules stay hashable and comparable."""
    return [tuple(v) if isinstance(v, (list, tuple)) else v for v in value]


class _RuleWithValue:
    # overridden by each subclass; copied onto the instance so that `__dict__`
    # carries the same shape the reference implementation serializes.
    type: RuleType = RuleType.CHAR

    def __init__(self, value: Iterable[Union[int, Sequence[int]]]):
        self.type = type(self).type
        self.value = _normalize_values(value)

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash((self.type, tuple(self.value)))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value!r})"


class RuleChar(_RuleWithValue):
    type = RuleType.CHAR


class RuleCharExclude(_RuleWithValue):
    type = RuleType.CHAR_EXCLUDE


class RuleEnd:
    def __init__(self) -> None:
        self.type = RuleType.END

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return True

    def __hash__(self) -> int:
        return hash(RuleType.END)

    def __repr__(self) -> str:
        return "RuleEnd()"


# RuleRefs should never be exposed to the end user.
ResolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd]
UnresolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd, "RuleRef"]
