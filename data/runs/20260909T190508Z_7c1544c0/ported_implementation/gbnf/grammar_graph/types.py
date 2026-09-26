from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Union


class RuleType(str, Enum):
    CHAR = 'char'
    CHAR_EXCLUDE = 'char_exclude'
    END = 'end'


# A range is a two element [start, end] list of code points.
Range = List[int]
RuleValue = List[Union[int, Range]]


@dataclass
class RuleChar:
    value: RuleValue = field(default_factory=list)
    type: RuleType = RuleType.CHAR


@dataclass
class RuleCharExclude:
    value: RuleValue = field(default_factory=list)
    type: RuleType = RuleType.CHAR_EXCLUDE


@dataclass
class RuleEnd:
    type: RuleType = RuleType.END


# UnresolvedRule = RuleChar | RuleCharExclude | RuleRef | RuleEnd
# RuleRefs should never be exposed to the end user.
ResolvedRule = Union[RuleChar, RuleCharExclude, RuleEnd]

# ValidInput can either be a string, or a number indicating a code point.
# It CANNOT be a number representing a number; a number being a "number"
# (like "8") should be passed in as a string.
ValidInput = Union[str, int, List[int]]


def rule_to_dict(rule: Any) -> Dict[str, Any]:
    """The plain-data view of a rule, mirroring the reference implementation's
    JSON shape (``{"type": "char", "value": [102]}``)."""
    if isinstance(rule, RuleEnd):
        return {'type': rule.type.value}
    return {'type': rule.type.value, 'value': rule.value}
