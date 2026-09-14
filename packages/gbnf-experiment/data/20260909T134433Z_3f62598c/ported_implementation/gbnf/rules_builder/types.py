from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Union


class InternalRuleType(str, Enum):
    CHAR = "CHAR"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    RULE_REF = "RULE_REF"
    ALT = "ALT"
    END = "END"

    CHAR_NOT = "CHAR_NOT"
    CHAR_ALT = "CHAR_ALT"

    def __str__(self) -> str:
        return self.value


@dataclass
class InternalRuleDefChar:
    value: List[int]
    type: InternalRuleType = field(default=InternalRuleType.CHAR, init=False)


@dataclass
class InternalRuleDefCharNot:
    value: List[int]
    type: InternalRuleType = field(default=InternalRuleType.CHAR_NOT, init=False)


@dataclass
class InternalRuleDefCharAlt:
    value: int
    type: InternalRuleType = field(default=InternalRuleType.CHAR_ALT, init=False)


@dataclass
class InternalRuleDefCharRngUpper:
    value: int
    type: InternalRuleType = field(
        default=InternalRuleType.CHAR_RNG_UPPER, init=False
    )


@dataclass
class InternalRuleDefReference:
    value: int
    type: InternalRuleType = field(default=InternalRuleType.RULE_REF, init=False)


@dataclass
class InternalRuleDefAlt:
    type: InternalRuleType = field(default=InternalRuleType.ALT, init=False)


@dataclass
class InternalRuleDefEnd:
    type: InternalRuleType = field(default=InternalRuleType.END, init=False)


InternalRuleDef = Union[
    InternalRuleDefChar,
    InternalRuleDefCharNot,
    InternalRuleDefCharAlt,
    InternalRuleDefCharRngUpper,
    InternalRuleDefReference,
    InternalRuleDefAlt,
    InternalRuleDefEnd,
]
InternalRuleDefCharOrAltChar = Union[InternalRuleDefChar, InternalRuleDefCharAlt]
