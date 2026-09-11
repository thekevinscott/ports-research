import json
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Union

from .rule_ref import RuleRef
from .rule_type import RuleType

if TYPE_CHECKING:  # pragma: no cover
    from .graph_pointer import GraphPointer
    from .pointers import Pointers

# A range is a two element [start, end] pair of code points.
Range = List[int]


class PrintOpts:
    def __init__(
        self,
        colorize,
        pointers: Optional["Pointers"] = None,
        show_position: bool = False,
    ):
        self.colorize = colorize
        self.pointers = pointers
        self.show_position = show_position


class Rule:
    # the concrete rule type, declared per subclass and copied onto every
    # instance so that it is part of the instance's own attributes, as it is in
    # the reference.
    RULE_TYPE: RuleType

    def __init__(self) -> None:
        self.type = self.RULE_TYPE

    def equals(self, other: object) -> bool:
        return isinstance(other, Rule) and json.dumps(self.to_json()) == json.dumps(
            other.to_json()
        )

    def __eq__(self, other: object) -> bool:
        return self.equals(other)

    def __hash__(self) -> int:
        return hash(json.dumps(self.to_json()))

    def to_json(self) -> Dict[str, object]:
        return {"type": self.type.value}

    def __str__(self) -> str:
        return json.dumps(self.to_json())

    def __repr__(self) -> str:
        return str(self)


class RuleWithListOfIntsOrRanges(Rule):
    def __init__(self, value: Optional[Sequence[Union[int, Range]]] = None):
        super().__init__()
        # the value is copied so that later mutation of the source list cannot
        # leak into the rule.
        self.value: List[Union[int, Range]] = list(value) if value is not None else []

    def to_json(self) -> Dict[str, object]:
        return {"type": self.type.value, "value": self.value}


class RuleChar(RuleWithListOfIntsOrRanges):
    RULE_TYPE = RuleType.CHAR


class RuleCharExclude(RuleWithListOfIntsOrRanges):
    RULE_TYPE = RuleType.CHAR_EXCLUDE


class RuleEnd(Rule):
    RULE_TYPE = RuleType.END


UnresolvedRule = Union[RuleChar, RuleCharExclude, RuleRef, RuleEnd]

# ValidInput can either be a string, or an int indicating a code point.
# It CANNOT be a number representing a number; a number intended as input (like
# "8") should be passed in as a string.
ValidInput = Union[str, int, List[int]]

# RuleRefs should never be exposed to the end user.
ResolvedRule = Union[RuleCharExclude, RuleChar, RuleEnd]

__all__ = [
    "PrintOpts",
    "Range",
    "ResolvedRule",
    "Rule",
    "RuleChar",
    "RuleCharExclude",
    "RuleEnd",
    "RuleRef",
    "RuleType",
    "RuleWithListOfIntsOrRanges",
    "UnresolvedRule",
    "ValidInput",
]
