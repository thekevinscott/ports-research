from typing import List, Union


class InternalBase:
    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self))

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class InternalBaseWithValue(InternalBase):
    def __init__(self, value):
        self.value = value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, type(self)) and self.value == other.value

    __hash__ = object.__hash__

    def __repr__(self) -> str:
        return f"{type(self).__name__}(value={self.value})"


class InternalBaseWithInt(InternalBaseWithValue):
    def __init__(self, value: int):
        super().__init__(value)


class InternalBaseWithListOfInts(InternalBaseWithValue):
    def __init__(self, value: Union[List[int], None] = None):
        # Copy the incoming list so later mutation can't reach the caller's list.
        super().__init__(list(value) if value is not None else [])


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
    InternalRuleDefWithoutValue,
    InternalRuleDefAlt,
    InternalRuleDefCharRngUpper,
    InternalRuleDefCharAlt,
]

InternalRuleDefCharOrAltChar = Union[InternalRuleDefChar, InternalRuleDefCharAlt]


def is_rule_def_alt(rule) -> bool:
    return isinstance(rule, InternalRuleDefAlt)


def is_rule_def_ref(rule) -> bool:
    return isinstance(rule, InternalRuleDefReference)


def is_rule_def_end(rule) -> bool:
    return isinstance(rule, InternalRuleDefEnd)


def is_rule_def_char(rule) -> bool:
    return isinstance(rule, InternalRuleDefChar)


def is_rule_def_char_not(rule) -> bool:
    return isinstance(rule, InternalRuleDefCharNot)


def is_rule_def_char_alt(rule) -> bool:
    return isinstance(rule, InternalRuleDefCharAlt)


def is_rule_def_char_rng_upper(rule) -> bool:
    return isinstance(rule, InternalRuleDefCharRngUpper)
