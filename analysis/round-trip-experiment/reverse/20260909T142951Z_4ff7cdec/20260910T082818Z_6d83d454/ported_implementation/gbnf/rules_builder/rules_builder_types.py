from typing import Any, List, Optional, Sequence


class InternalRuleType:
    CHAR = "CHAR"
    CHAR_ALT = "CHAR_ALT"
    CHAR_NOT = "CHAR_NOT"
    CHAR_RNG_UPPER = "CHAR_RNG_UPPER"
    REF = "REF"
    ALT = "ALT"
    END = "END"


class InternalRuleDefChar:
    def __init__(self, value: Sequence[int]):
        self.type = InternalRuleType.CHAR
        self.value: List[int] = list(value)

    def __repr__(self) -> str:
        return f"InternalRuleDefChar({self.value!r})"


class InternalRuleDefCharNot:
    def __init__(self, value: Sequence[int]):
        self.type = InternalRuleType.CHAR_NOT
        self.value: List[int] = list(value)

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
        self.type = InternalRuleType.REF
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


def _type_of(rule: Optional[Any]) -> Optional[str]:
    return getattr(rule, "type", None)


def is_rule_def_alt(rule: Optional[Any]) -> bool:
    return _type_of(rule) == InternalRuleType.ALT


def is_rule_def_ref(rule: Optional[Any]) -> bool:
    return _type_of(rule) == InternalRuleType.REF


def is_rule_def_end(rule: Optional[Any]) -> bool:
    return _type_of(rule) == InternalRuleType.END


def is_rule_def_char(rule: Optional[Any]) -> bool:
    return _type_of(rule) == InternalRuleType.CHAR


def is_rule_def_char_not(rule: Optional[Any]) -> bool:
    return _type_of(rule) == InternalRuleType.CHAR_NOT


def is_rule_def_char_alt(rule: Optional[Any]) -> bool:
    return _type_of(rule) == InternalRuleType.CHAR_ALT


def is_rule_def_char_rng_upper(rule: Optional[Any]) -> bool:
    return _type_of(rule) == InternalRuleType.CHAR_RNG_UPPER
