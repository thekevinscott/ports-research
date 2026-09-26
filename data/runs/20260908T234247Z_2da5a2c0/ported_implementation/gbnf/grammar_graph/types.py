"""Port of ``src/grammar-graph/types.ts``.

The TypeScript original describes rules with interfaces over plain objects. Here
they are small classes so that ``rule.type`` / ``rule.value`` read identically,
with value-based equality (the original compares rules by their serialized form).

A ``Range`` is a two-element ``list[int]``, matching the JS ``[number, number]``.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Sequence, Union


class RuleType(str, Enum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"

    def __str__(self) -> str:  # mirrors JS string-enum stringification
        return self.value


Range = List[int]
RangeOrCodePoint = Union[int, Range]


class _ValueRule:
    """Common base for the two rules that carry a list of code points/ranges."""

    type: RuleType

    __slots__ = ("value",)

    def __init__(self, value: Sequence[RangeOrCodePoint] = ()) -> None:
        self.value: List[RangeOrCodePoint] = [
            list(v) if isinstance(v, (list, tuple)) else v for v in value
        ]

    def _key(self) -> tuple:
        return (
            self.type,
            tuple(tuple(v) if isinstance(v, list) else v for v in self.value),
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, dict):
            # the reference's rules are plain objects; compare equal to that shape too
            return self.to_dict() == other
        if not isinstance(other, _ValueRule):
            return NotImplemented
        return self._key() == other._key()

    def __hash__(self) -> int:
        return hash(self._key())

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type.value, "value": self.value}

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value!r})"


class RuleChar(_ValueRule):
    type = RuleType.CHAR


class RuleCharExclude(_ValueRule):
    type = RuleType.CHAR_EXCLUDE


class RuleEnd:
    type = RuleType.END

    __slots__ = ()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, dict):
            return self.to_dict() == other
        if not isinstance(other, RuleEnd):
            return NotImplemented
        return True

    def __hash__(self) -> int:
        return hash(RuleType.END)

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type.value}

    def __repr__(self) -> str:
        return "RuleEnd()"


# UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd
# RuleRefs should never be exposed to the end user.
# ResolvedRule = RuleCharExclude | RuleChar | RuleEnd
ResolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, List[int]]
