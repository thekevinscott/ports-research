from typing import List, Optional, Sequence


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
        return f"InternalRuleDefChar({self.value!r})"


class InternalRuleDefCharNot:
    def __init__(self, value: Optional[Sequence[int]] = None):
        self.type = InternalRuleType.CHAR_NOT
        self.value: List[int] = list(value) if value is not None else []

    def __repr__(self) -> str:
        return f"InternalRuleDefCharNot({self.value!r})"


class InternalRuleDefCharAlt:
    def __init__(self, value: int):
        self.type = InternalRuleType.CHAR_ALT
        self.value = value

    def __repr__(self) -> str:
        return f"InternalRuleDefCharAlt({self.value!r})"


class InternalRuleDefCharRngUpper:
    def __init__(self, value: int):
        self.type = InternalRuleType.CHAR_RNG_UPPER
        self.value = value

    def __repr__(self) -> str:
        return f"InternalRuleDefCharRngUpper({self.value!r})"


class InternalRuleDefReference:
    def __init__(self, value: int):
        self.type = InternalRuleType.REFERENCE
        self.value = value

    def __repr__(self) -> str:
        return f"InternalRuleDefReference({self.value!r})"


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


def _type_of(rule):
    return getattr(rule, "type", None)


def is_rule_def_alt(rule) -> bool:
    return _type_of(rule) == InternalRuleType.ALT


def is_rule_def_ref(rule) -> bool:
    return _type_of(rule) == InternalRuleType.REFERENCE


def is_rule_def_end(rule) -> bool:
    return _type_of(rule) == InternalRuleType.END


def is_rule_def_char(rule) -> bool:
    return _type_of(rule) == InternalRuleType.CHAR


def is_rule_def_char_not(rule) -> bool:
    return _type_of(rule) == InternalRuleType.CHAR_NOT


def is_rule_def_char_alt(rule) -> bool:
    return _type_of(rule) == InternalRuleType.CHAR_ALT


def is_rule_def_char_rng_upper(rule) -> bool:
    return _type_of(rule) == InternalRuleType.CHAR_RNG_UPPER
