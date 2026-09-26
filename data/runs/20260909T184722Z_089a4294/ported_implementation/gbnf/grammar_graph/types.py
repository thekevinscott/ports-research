from __future__ import annotations

from enum import StrEnum
from typing import Union


class RuleType(StrEnum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"


# A range is a two element list of code points, `[start, end]`.
Range = list


class _RuleWithValue:
    """Base for the char-matching rules, which hold code points and/or ranges."""

    type: RuleType

    def __init__(self, value):
        self.value = [list(v) if isinstance(v, (list, tuple)) else v for v in value]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _RuleWithValue):
            return NotImplemented
        return self.type == other.type and self.value == other.value

    def __hash__(self) -> int:
        return hash((self.type, repr(self.value)))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value!r})"


class RuleChar(_RuleWithValue):
    def __init__(self, value):
        self.type = RuleType.CHAR
        super().__init__(value)


class RuleCharExclude(_RuleWithValue):
    def __init__(self, value):
        self.type = RuleType.CHAR_EXCLUDE
        super().__init__(value)


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


ResolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, list]
