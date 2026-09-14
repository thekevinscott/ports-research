from typing import Callable, List, Optional, Sequence, Union

# A Range is a two element [start, end] pair of code points.
Range = List[int]


class RuleType:
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"
    REF = "ref"


class RuleWithListOfIntsOrRanges:
    TYPE = ""

    def __init__(self, value: Sequence[Union[int, Sequence[int]]]):
        self.type = self.TYPE
        self.value: List[Union[int, Range]] = [
            list(v) if isinstance(v, (list, tuple)) else v for v in value
        ]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleWithListOfIntsOrRanges):
            return NotImplemented
        return type(self) is type(other) and self.value == other.value

    def __hash__(self) -> int:
        return hash(
            (self.type, tuple(tuple(v) if isinstance(v, list) else v for v in self.value))
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value!r})"


class RuleChar(RuleWithListOfIntsOrRanges):
    TYPE = RuleType.CHAR


class RuleCharExclude(RuleWithListOfIntsOrRanges):
    TYPE = RuleType.CHAR_EXCLUDE


class RuleEnd:
    def __init__(self) -> None:
        self.type = RuleType.END

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleEnd):
            return NotImplemented
        return True

    def __hash__(self) -> int:
        return hash(RuleType.END)

    def __repr__(self) -> str:
        return "RuleEnd()"


# UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd
# RuleRefs should never be exposed to the end user, so:
# ResolvedRule = RuleChar | RuleCharExclude | RuleEnd

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number intended as input (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]


class PrintOpts:
    def __init__(
        self,
        colorize: Callable[[Union[str, int], str], str],
        pointers: Optional[object] = None,
        show_position: bool = False,
    ):
        self.colorize = colorize
        self.pointers = pointers
        self.show_position = show_position


__all__ = [
    "PrintOpts",
    "Range",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "RuleType",
    "RuleWithListOfIntsOrRanges",
    "ValidInput",
]
