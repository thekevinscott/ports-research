"""The internal rule definitions produced by the ``RulesBuilder``.

These are a flat, linear representation of the grammar; ``build_rule_stack``
turns them into the stacked rules the graph is built from.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

T = TypeVar("T")


class InternalRuleType:
    CHAR = "char"
    CHAR_ALT = "char_alt"
    CHAR_NOT = "char_not"
    CHAR_RNG_UPPER = "char_rng_upper"
    ALT = "alt"
    END = "end"
    RULE_REF = "rule_ref"


class InternalBase:
    type: str

    def equals(self, other: object) -> bool:
        return type(other) is type(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InternalBase):
            return NotImplemented
        return type(other) is type(self)

    def __hash__(self) -> int:
        return hash(type(self))

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class InternalBaseWithValue(InternalBase, Generic[T]):
    def __init__(self, value: T):
        self.value = value

    def equals(self, other: object) -> bool:
        return type(other) is type(self) and other.value == self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InternalBase):
            return NotImplemented
        return type(other) is type(self) and other.value == self.value

    def __hash__(self) -> int:
        return hash((type(self), repr(self.value)))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.value!r})"


class InternalBaseWithInt(InternalBaseWithValue[int]):
    pass


class InternalBaseWithListOfInts(InternalBaseWithValue[List[int]]):
    def __init__(self, value: Optional[List[int]] = None):
        super().__init__(list(value) if value is not None else [])


class InternalRuleDefChar(InternalBaseWithListOfInts):
    type = InternalRuleType.CHAR


class InternalRuleDefCharNot(InternalBaseWithListOfInts):
    type = InternalRuleType.CHAR_NOT


class InternalRuleDefCharAlt(InternalBaseWithInt):
    type = InternalRuleType.CHAR_ALT


class InternalRuleDefCharRngUpper(InternalBaseWithInt):
    type = InternalRuleType.CHAR_RNG_UPPER


class InternalRuleDefReference(InternalBaseWithInt):
    type = InternalRuleType.RULE_REF


class InternalRuleDefAlt(InternalBase):
    type = InternalRuleType.ALT


class InternalRuleDefEnd(InternalBase):
    type = InternalRuleType.END


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


isRuleDefAlt = is_rule_def_alt
isRuleDefRef = is_rule_def_ref
isRuleDefEnd = is_rule_def_end
isRuleDefChar = is_rule_def_char
isRuleDefCharNot = is_rule_def_char_not
isRuleDefCharAlt = is_rule_def_char_alt
isRuleDefCharRngUpper = is_rule_def_char_rng_upper
