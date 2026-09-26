"""
Internal (linear) rule definitions produced by the RulesBuilder, before they
are folded into a stack of paths by `build_rule_stack`.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union


class InternalBase:
    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self))

    def __hash__(self) -> int:
        return id(self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class InternalBaseWithValue(InternalBase):
    def __init__(self, value: Any) -> None:
        self.value = value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and other.value == self.value

    def __hash__(self) -> int:
        return id(self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(value={self.value})"


class InternalBaseWithInt(InternalBaseWithValue):
    def __init__(self, value: int) -> None:
        super().__init__(value)


class InternalBaseWithListOfInts(InternalBaseWithValue):
    def __init__(self, value: Optional[List[int]] = None) -> None:
        # copy the incoming list
        super().__init__(list(value) if value is not None else [])


class InternalRuleDefWithNumericValue(InternalBaseWithInt):
    pass


class InternalRuleDefChar(InternalBaseWithListOfInts):
    pass


class InternalRuleDefCharAlt(InternalBaseWithInt):
    pass


class InternalRuleDefAlt(InternalBase):
    pass


class InternalRuleDefCharNot(InternalBaseWithListOfInts):
    pass


class InternalRuleDefCharRngUpper(InternalBaseWithInt):
    pass


class InternalRuleDefReference(InternalBaseWithInt):
    pass


class InternalRuleDefEnd(InternalBase):
    pass


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

SymbolIds = Dict[str, int]


def is_rule_def_alt(rule: object) -> bool:
    return isinstance(rule, InternalRuleDefAlt)


def is_rule_def_ref(rule: object) -> bool:
    return isinstance(rule, InternalRuleDefReference)


def is_rule_def_end(rule: object) -> bool:
    return isinstance(rule, InternalRuleDefEnd)


def is_rule_def_char(rule: object) -> bool:
    return isinstance(rule, InternalRuleDefChar)


def is_rule_def_char_not(rule: object) -> bool:
    return isinstance(rule, InternalRuleDefCharNot)


def is_rule_def_char_alt(rule: object) -> bool:
    return isinstance(rule, InternalRuleDefCharAlt)


def is_rule_def_char_rng_upper(rule: object) -> bool:
    return isinstance(rule, InternalRuleDefCharRngUpper)
