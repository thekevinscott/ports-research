from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union

Range = List[int]

ValidInput = Union[str, int, List[int]]


class Rule:
    @property
    def type(self) -> str:
        """
        The class name, as reported by this rule's `__dict__`.
        """
        return type(self).__name__

    @property  # type: ignore[misc]
    def __dict__(self) -> Dict[str, Any]:  # type: ignore[override]
        return {"type": type(self).__name__}

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self))

    def __hash__(self) -> int:
        return id(self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    def __str__(self) -> str:
        return f"{type(self).__name__}()"


class RuleWithValue(Rule):
    def __init__(self, value: Any) -> None:
        self.value = value

    @property  # type: ignore[misc]
    def __dict__(self) -> Dict[str, Any]:  # type: ignore[override]
        return {"type": type(self).__name__, "value": self.value}

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and other.value == self.value

    def __hash__(self) -> int:
        return id(self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(value={self.value})"

    def __str__(self) -> str:
        return f"{type(self).__name__}(value={self.value})"


class RuleWithListOfIntsOrRanges(RuleWithValue):
    def __init__(
        self,
        value: Optional[List[Union[int, Range]]] = None,
    ) -> None:
        # copy the incoming list
        super().__init__(list(value) if value is not None else [])


class RuleChar(RuleWithListOfIntsOrRanges):
    pass


class RuleCharExclude(RuleWithListOfIntsOrRanges):
    pass


class RuleEnd(Rule):
    pass


UnresolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd, "Any"]

# RuleRefs should never be exposed to the end user.
ResolvedRule = Union[RuleCharExclude, RuleChar, RuleEnd]

@dataclass
class PrintOpts:
    pointers: Any
    colorize: Callable[[Union[str, int], str], str]
    show_position: bool = False

__all__ = [
    "PrintOpts",
    "Range",
    "ResolvedRule",
    "Rule",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "RuleWithListOfIntsOrRanges",
    "RuleWithValue",
    "UnresolvedRule",
    "ValidInput",
]
