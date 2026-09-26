import json
from typing import Any, List, Optional, Sequence


class InternalBase:
    @property
    def type(self) -> str:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        return isinstance(other, InternalBase) and type(other) is type(self)

    def __hash__(self) -> int:
        return hash(self.type)

    def __repr__(self) -> str:
        return f"{self.type}()"


class InternalBaseWithValue(InternalBase):
    def __init__(self, value: Any):
        self.value = value

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, InternalBaseWithValue)
            and type(other) is type(self)
            and self.value == other.value
        )

    def __hash__(self) -> int:
        return hash((self.type, json.dumps(self.value)))

    def __repr__(self) -> str:
        return f"{self.type}(value={json.dumps(self.value)})"


class InternalBaseWithInt(InternalBaseWithValue):
    pass


class InternalBaseWithListOfInts(InternalBaseWithValue):
    def __init__(self, value: Optional[Sequence[int]] = None):
        super().__init__(list(value) if value is not None else [])


class InternalRuleDefWithNumericValue(InternalBaseWithInt):
    @property
    def type(self) -> str:
        return "InternalRuleDefWithNumericValue"


class InternalRuleDefChar(InternalBaseWithListOfInts):
    @property
    def type(self) -> str:
        return "InternalRuleDefChar"


class InternalRuleDefCharAlt(InternalBaseWithInt):
    @property
    def type(self) -> str:
        return "InternalRuleDefCharAlt"


class InternalRuleDefAlt(InternalBase):
    @property
    def type(self) -> str:
        return "InternalRuleDefAlt"


class InternalRuleDefCharNot(InternalBaseWithListOfInts):
    @property
    def type(self) -> str:
        return "InternalRuleDefCharNot"


class InternalRuleDefCharRngUpper(InternalBaseWithInt):
    @property
    def type(self) -> str:
        return "InternalRuleDefCharRngUpper"


class InternalRuleDefReference(InternalBaseWithInt):
    @property
    def type(self) -> str:
        return "InternalRuleDefReference"


class InternalRuleDefEnd(InternalBase):
    @property
    def type(self) -> str:
        return "InternalRuleDefEnd"


class InternalRuleDefWithoutValue(InternalBase):
    @property
    def type(self) -> str:
        return "InternalRuleDefWithoutValue"


InternalRuleDef = InternalBase


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


__all__: List[str] = [
    "InternalBase",
    "InternalBaseWithInt",
    "InternalBaseWithListOfInts",
    "InternalBaseWithValue",
    "InternalRuleDef",
    "InternalRuleDefAlt",
    "InternalRuleDefChar",
    "InternalRuleDefCharAlt",
    "InternalRuleDefCharNot",
    "InternalRuleDefCharRngUpper",
    "InternalRuleDefEnd",
    "InternalRuleDefReference",
    "InternalRuleDefWithNumericValue",
    "InternalRuleDefWithoutValue",
    "is_rule_def_alt",
    "is_rule_def_char",
    "is_rule_def_char_alt",
    "is_rule_def_char_not",
    "is_rule_def_char_rng_upper",
    "is_rule_def_end",
    "is_rule_def_ref",
]
