from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, List, Sequence, Union

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .rule_ref import RuleRef


class RuleType(str, Enum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"

    def __str__(self) -> str:
        return self.value


# A range is a two element sequence of code points, inclusive on both ends.
Range = List[int]
RuleValue = List[Union[int, Range]]


@dataclass
class RuleChar:
    value: RuleValue = field(default_factory=list)

    type: RuleType = field(default=RuleType.CHAR, init=False, repr=True)


@dataclass
class RuleCharExclude:
    value: RuleValue = field(default_factory=list)

    type: RuleType = field(default=RuleType.CHAR_EXCLUDE, init=False, repr=True)


@dataclass
class RuleEnd:
    type: RuleType = field(default=RuleType.END, init=False, repr=True)


# RuleRefs should never be exposed to the end user.
ResolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd]
UnresolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd, "RuleRef"]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, Sequence[int]]
