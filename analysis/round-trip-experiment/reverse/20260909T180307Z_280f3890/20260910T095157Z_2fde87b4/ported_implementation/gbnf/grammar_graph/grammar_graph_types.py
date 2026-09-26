from typing import List, Optional, Sequence, Union

# A Range is a two element list of code points, [start, end].
Range = List[int]


class RuleType:
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"
    REF = "ref"


class RuleChar:
    def __init__(self, value: Optional[Sequence[Union[int, Range]]] = None):
        self.type = RuleType.CHAR
        self.value: List[Union[int, Range]] = list(value) if value is not None else []

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleChar):
            return NotImplemented
        return self.value == other.value

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return f"RuleChar({self.value!r})"


class RuleCharExclude:
    def __init__(self, value: Optional[Sequence[Union[int, Range]]] = None):
        self.type = RuleType.CHAR_EXCLUDE
        self.value: List[Union[int, Range]] = list(value) if value is not None else []

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleCharExclude):
            return NotImplemented
        return self.value == other.value

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return f"RuleCharExclude({self.value!r})"


class RuleEnd:
    def __init__(self) -> None:
        self.type = RuleType.END

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleEnd):
            return NotImplemented
        return True

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return "RuleEnd()"


# UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd
UnresolvedRule = object

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number intended as input (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]

# RuleRefs should never be exposed to the end user.
ResolvedRule = Union[RuleCharExclude, RuleChar, RuleEnd]
