from typing import Any, Optional, Sequence, Union


class InternalBase:
    """Base for the value-less internal rules."""

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return self.__dict__ == other.__dict__

    __hash__ = None  # type: ignore[assignment]


class InternalBaseWithValue:
    def __init__(self, value: Any):
        self.value = value

    def __repr__(self) -> str:
        return f"{type(self).__name__}(value={self.value!r})"

    def __eq__(self, other: object) -> bool:
        if type(self) is not type(other):
            return NotImplemented
        return self.__dict__ == other.__dict__

    __hash__ = None  # type: ignore[assignment]


class InternalBaseWithInt(InternalBaseWithValue):
    def __init__(self, value: int):
        super().__init__(value)


class InternalBaseWithListOfInts(InternalBaseWithValue):
    def __init__(self, value: Optional[Sequence[int]] = None):
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
