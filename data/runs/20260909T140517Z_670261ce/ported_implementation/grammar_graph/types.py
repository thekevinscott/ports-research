"""Port of ``src/grammar-graph/types.ts``."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterator, List, Mapping, Sequence, Union


class RuleType(str, Enum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"

    def __str__(self) -> str:  # pragma: no cover - convenience only
        return self.value


# A range is a two element ``[start, end]`` pair of code points.
Range = List[int]


class _Rule:
    """Shared behaviour for the rules handed back to callers.

    The reference yields plain objects, so rules are also readable as mappings
    (``rule["type"]``, ``dict(rule)``) and compare equal to the equivalent dict,
    on top of the usual attribute access.
    """

    __slots__ = ()

    # Identity hashing, matching the Javascript `Map`/`Set` keys the graph relies on.
    __hash__ = object.__hash__

    def keys(self) -> Iterator[str]:
        return iter(self._field_names())

    def _field_names(self) -> List[str]:
        return [f for f in ("type", "value") if hasattr(self, f)]

    def __getitem__(self, key: str) -> Any:
        if key in self._field_names():
            return getattr(self, key)
        raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def to_dict(self) -> Dict[str, Any]:
        return {key: getattr(self, key) for key in self._field_names()}

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, _Rule):
            return type(self) is type(other) and self.to_dict() == other.to_dict()
        if isinstance(other, Mapping):
            return self.to_dict() == dict(other)
        return NotImplemented

    def __ne__(self, other: Any) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result


@dataclass(eq=False)
class RuleChar(_Rule):
    value: List[Union[int, Range]] = field(default_factory=list)
    type: RuleType = RuleType.CHAR


@dataclass(eq=False)
class RuleCharExclude(_Rule):
    value: List[Union[int, Range]] = field(default_factory=list)
    type: RuleType = RuleType.CHAR_EXCLUDE


@dataclass(eq=False)
class RuleEnd(_Rule):
    type: RuleType = RuleType.END


# RuleRefs should never be exposed to the end user.
ResolvedRule = Union[RuleCharExclude, RuleChar, RuleEnd]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number" (like "8")
# should be passed in as a string.
ValidInput = Union[str, int, Sequence[int]]
