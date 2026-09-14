"""The intermediate rule definitions produced while parsing a grammar."""

from typing import Any, List, Optional, Sequence


class InternalRuleType:
    CHAR = "char"
    CHAR_ALT = "char_alt"
    ALT = "alt"
    CHAR_NOT = "char_not"
    CHAR_RNG_UPPER = "char_rng_upper"
    REFERENCE = "reference"
    END = "end"


class InternalRuleDefChar:
    def __init__(self, value: Optional[Sequence[int]] = None):
        self.type = InternalRuleType.CHAR
        self.value: List[int] = list(value) if value is not None else []

    def __repr__(self) -> str:
        return f"InternalRuleDefChar(value={self.value!r})"


class InternalRuleDefCharNot:
    def __init__(self, value: Optional[Sequence[int]] = None):
        self.type = InternalRuleType.CHAR_NOT
        self.value: List[int] = list(value) if value is not None else []

    def __repr__(self) -> str:
        return f"InternalRuleDefCharNot(value={self.value!r})"


class InternalRuleDefCharAlt:
    def __init__(self, value: int):
        self.type = InternalRuleType.CHAR_ALT
        self.value = value

    def __repr__(self) -> str:
        return f"InternalRuleDefCharAlt(value={self.value!r})"


class InternalRuleDefCharRngUpper:
    def __init__(self, value: int):
        self.type = InternalRuleType.CHAR_RNG_UPPER
        self.value = value

    def __repr__(self) -> str:
        return f"InternalRuleDefCharRngUpper(value={self.value!r})"


class InternalRuleDefReference:
    def __init__(self, value: int):
        self.type = InternalRuleType.REFERENCE
        self.value = value

    def __repr__(self) -> str:
        return f"InternalRuleDefReference(value={self.value!r})"


class InternalRuleDefAlt:
    def __init__(self) -> None:
        self.type = InternalRuleType.ALT

    def __repr__(self) -> str:
        return "InternalRuleDefAlt()"


class InternalRuleDefEnd:
    def __init__(self) -> None:
        self.type = InternalRuleType.END

    def __repr__(self) -> str:
        return "InternalRuleDefEnd()"


def is_rule_def_alt(rule: Any = None) -> bool:
    return isinstance(rule, InternalRuleDefAlt)


def is_rule_def_ref(rule: Any = None) -> bool:
    return isinstance(rule, InternalRuleDefReference)


def is_rule_def_end(rule: Any = None) -> bool:
    return isinstance(rule, InternalRuleDefEnd)


def is_rule_def_char(rule: Any = None) -> bool:
    return isinstance(rule, InternalRuleDefChar)


def is_rule_def_char_not(rule: Any = None) -> bool:
    return isinstance(rule, InternalRuleDefCharNot)


def is_rule_def_char_alt(rule: Any = None) -> bool:
    return isinstance(rule, InternalRuleDefCharAlt)


def is_rule_def_char_rng_upper(rule: Any = None) -> bool:
    return isinstance(rule, InternalRuleDefCharRngUpper)
