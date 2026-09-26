from typing import Union

from ..utils.validate_non_empty import validate_non_empty

# A range of code points, inclusive on both ends: [start, end].
Range = list

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number intended as input (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, list]


class RuleType:
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"
    REF = "ref"


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


class RuleChar:
    def __init__(self, value: list) -> None:
        self.type = RuleType.CHAR
        self.value = list(validate_non_empty(value))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleChar):
            return NotImplemented
        return self.value == other.value

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return f"RuleChar(value={self.value!r})"


class RuleCharExclude:
    def __init__(self, value: list) -> None:
        self.type = RuleType.CHAR_EXCLUDE
        self.value = list(validate_non_empty(value))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RuleCharExclude):
            return NotImplemented
        return self.value == other.value

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return f"RuleCharExclude(value={self.value!r})"
