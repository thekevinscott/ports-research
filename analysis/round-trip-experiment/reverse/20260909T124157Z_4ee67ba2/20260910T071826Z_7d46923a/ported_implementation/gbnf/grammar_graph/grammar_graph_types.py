from typing import Any, Dict, List, Union

from ..utils.errors import ValidInput  # noqa: F401  (re-exported)
from .rule_ref import RuleRef

# A range is an inclusive [start, end] pair of code points.
Range = List[int]


class Rule:
    """Base class for every resolved rule the graph can expose.

    `__dict__` is overridden as a property so that a rule serializes to its type and
    (where present) its value, which is what the graph uses for equality and dedupe
    keys.
    """

    @property
    def type(self) -> str:
        return self.__class__.__name__

    @property
    def __dict__(self) -> Dict[str, Any]:
        return {"type": self.type}

    def __str__(self) -> str:
        return f"{self.type}()"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented if not isinstance(other, Rule) else False
        return True

    def __hash__(self) -> int:
        return hash(self.type)


class RuleWithValue(Rule):
    def __init__(self, value: Any):
        self.value = value

    @property
    def __dict__(self) -> Dict[str, Any]:
        return {"type": self.type, "value": self.value}

    def __str__(self) -> str:
        return f"{self.type}(value={self.value})"

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented if not isinstance(other, Rule) else False
        return self.value == other.value

    def __hash__(self) -> int:
        return hash((self.type, str(self.value)))


class RuleWithListOfIntsOrRanges(RuleWithValue):
    def __init__(self, value: Union[List[Union[int, Range]], None] = None):
        super().__init__(list(value) if value is not None else [])


class RuleChar(RuleWithListOfIntsOrRanges):
    pass


class RuleCharExclude(RuleWithListOfIntsOrRanges):
    pass


class RuleEnd(Rule):
    pass


__all__ = [
    "Range",
    "Rule",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "RuleRef",
    "RuleWithListOfIntsOrRanges",
    "RuleWithValue",
    "ValidInput",
]
