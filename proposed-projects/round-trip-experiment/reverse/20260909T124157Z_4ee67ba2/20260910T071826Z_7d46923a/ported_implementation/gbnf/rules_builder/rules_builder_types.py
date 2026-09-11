"""The intermediate ("internal") rule representation produced by the RulesBuilder,
before it is folded into the graph's rule stacks.

Each class is a distinct nominal type: the type guards below rely on `isinstance`.
"""

from typing import Any, Dict, List, Optional


class InternalRuleDefWithNumericValue:
    def __init__(self, value: int):
        self.value = value

    def __eq__(self, other: object) -> bool:
        return type(self) is type(other) and self.value == other.value

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.value))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(value={self.value})"


class InternalBase:
    """Base for rules that carry no value; equality is "same class"."""

    def __eq__(self, other: object) -> bool:
        return type(self) is type(other)

    def __hash__(self) -> int:
        return hash(type(self).__name__)

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class InternalBaseWithInt:
    """Base for rules that carry a single integer value."""

    def __init__(self, value: int):
        self.value = value

    def __eq__(self, other: object) -> bool:
        return type(self) is type(other) and self.value == other.value

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.value))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(value={self.value})"


class InternalBaseWithListOfInts:
    """Base for rules that carry a list of integer values; copied on construction."""

    def __init__(self, value: Optional[List[int]] = None):
        self.value: List[int] = list(value) if value is not None else []

    def __eq__(self, other: object) -> bool:
        return type(self) is type(other) and self.value == other.value

    def __hash__(self) -> int:
        return hash((type(self).__name__, str(self.value)))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(value={self.value})"


class InternalRuleDefChar(InternalBaseWithListOfInts):
    pass


class InternalRuleDefCharNot(InternalBaseWithListOfInts):
    pass


class InternalRuleDefCharAlt(InternalBaseWithInt):
    pass


class InternalRuleDefCharRngUpper(InternalBaseWithInt):
    pass


class InternalRuleDefReference(InternalBaseWithInt):
    pass


class InternalRuleDefAlt(InternalBase):
    pass


class InternalRuleDefEnd(InternalBase):
    pass


class InternalRuleDefWithoutValue(InternalBase):
    pass


SymbolIdsMap = Dict[str, int]


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
