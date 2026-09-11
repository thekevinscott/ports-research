from __future__ import annotations

from enum import Enum
from typing import Union

from ..utils.validate_non_empty import validate_non_empty

# A Range is a two element list of code points, inclusive on both ends.
Range = list


class RuleType(str, Enum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"
    REF = "ref"

    def __str__(self) -> str:
        return str(self.value)


class RuleChar:
    def __init__(self, value: list | None = None) -> None:
        self.type = RuleType.CHAR
        self.value = list(value) if value is not None else []

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleChar):
            return NotImplemented
        return self.value == other.value

    # Rules are compared by identity when used as keys, matching the reference
    # implementation's use of a Map keyed on the rule object.
    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return f"RuleChar({self.value!r})"


class RuleCharExclude:
    def __init__(self, value: list | None = None) -> None:
        self.type = RuleType.CHAR_EXCLUDE
        self.value = list(value) if value is not None else []

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


UnresolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd, "RuleRef"]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number intended as input (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, list]

# RuleRefs should never be exposed to the end user.
ResolvedRule = Union[RuleCharExclude, RuleChar, RuleEnd]

__all__ = [
    "Range",
    "ResolvedRule",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "RuleType",
    "UnresolvedRule",
    "ValidInput",
    "validate_non_empty",
]
