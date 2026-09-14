from typing import Any, Dict, List, Sequence, Union


class InternalRuleDefChar:
    def __init__(self, value: Sequence[int]):
        self.value: List[int] = list(value)

    def __repr__(self) -> str:
        return f"InternalRuleDefChar({self.value!r})"


class InternalRuleDefCharNot:
    def __init__(self, value: Sequence[int]):
        self.value: List[int] = list(value)

    def __repr__(self) -> str:
        return f"InternalRuleDefCharNot({self.value!r})"


class InternalRuleDefCharAlt:
    def __init__(self, value: int):
        self.value = value

    def __repr__(self) -> str:
        return f"InternalRuleDefCharAlt({self.value!r})"


class InternalRuleDefCharRngUpper:
    def __init__(self, value: int):
        self.value = value

    def __repr__(self) -> str:
        return f"InternalRuleDefCharRngUpper({self.value!r})"


class InternalRuleDefReference:
    def __init__(self, value: int):
        self.value = value

    def __repr__(self) -> str:
        return f"InternalRuleDefReference({self.value!r})"


class InternalRuleDefAlt:
    def __repr__(self) -> str:
        return "InternalRuleDefAlt()"


class InternalRuleDefEnd:
    def __repr__(self) -> str:
        return "InternalRuleDefEnd()"


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


SymbolIdsMap = Dict[str, int]
