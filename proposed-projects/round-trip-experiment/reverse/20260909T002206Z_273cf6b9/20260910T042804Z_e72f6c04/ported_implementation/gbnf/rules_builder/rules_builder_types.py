from dataclasses import dataclass, field
from typing import Any, Dict, List, Union


@dataclass
class InternalRuleDefWithNumericValue:
    value: int


@dataclass
class InternalBase:
    pass


@dataclass
class InternalBaseWithValue:
    value: Any


@dataclass
class InternalBaseWithInt(InternalBaseWithValue):
    value: int


@dataclass
class InternalBaseWithListOfInts(InternalBaseWithValue):
    value: List[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        # copied, so that a rule built from this def can mutate its own value
        self.value = list(self.value)


@dataclass
class InternalRuleDefChar(InternalBaseWithListOfInts):
    pass


@dataclass
class InternalRuleDefCharAlt(InternalBaseWithInt):
    pass


@dataclass
class InternalRuleDefAlt(InternalBase):
    pass


@dataclass
class InternalRuleDefCharNot(InternalBaseWithListOfInts):
    pass


@dataclass
class InternalRuleDefCharRngUpper(InternalBaseWithInt):
    pass


@dataclass
class InternalRuleDefReference(InternalBaseWithInt):
    pass


@dataclass
class InternalRuleDefEnd(InternalBase):
    pass


@dataclass
class InternalRuleDefWithoutValue(InternalBase):
    pass


InternalRuleDef = Union[
    InternalRuleDefChar,
    InternalRuleDefEnd,
    InternalRuleDefReference,
    InternalRuleDefCharNot,
    InternalRuleDefWithNumericValue,
    InternalRuleDefWithoutValue,
    InternalRuleDefAlt,
    InternalRuleDefCharRngUpper,
    InternalRuleDefCharAlt,
]

InternalRuleDefCharOrAltChar = Union[InternalRuleDefChar, InternalRuleDefCharAlt]

SymbolIdsRecord = Dict[str, int]


def is_rule_def_alt(rule: Any) -> bool:
    return isinstance(rule, InternalRuleDefAlt)


def is_rule_def_ref(rule: Any) -> bool:
    return isinstance(rule, InternalRuleDefReference)


def is_rule_def_end(rule: Any) -> bool:
    return isinstance(rule, InternalRuleDefEnd)


def is_rule_def_char(rule: Any) -> bool:
    return isinstance(rule, InternalRuleDefChar)


def is_rule_def_char_not(rule: Any) -> bool:
    return isinstance(rule, InternalRuleDefCharNot)


def is_rule_def_char_alt(rule: Any) -> bool:
    return isinstance(rule, InternalRuleDefCharAlt)


def is_rule_def_char_rng_upper(rule: Any) -> bool:
    return isinstance(rule, InternalRuleDefCharRngUpper)
