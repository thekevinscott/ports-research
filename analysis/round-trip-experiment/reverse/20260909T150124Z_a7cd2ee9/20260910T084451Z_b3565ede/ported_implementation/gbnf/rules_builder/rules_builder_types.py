from ..utils.validate_non_empty import validate_non_empty


class InternalRuleType:
    CHAR = "char"
    CHAR_RNG_UPPER = "char_rng_upper"
    CHAR_ALT = "char_alt"
    CHAR_NOT = "char_not"
    ALT = "alt"
    END = "end"
    REF = "ref"


class InternalRuleDef:
    type: str

    def __repr__(self) -> str:
        value = getattr(self, "value", None)
        if value is None:
            return f"{type(self).__name__}(type={self.type!r})"
        return f"{type(self).__name__}(type={self.type!r}, value={value!r})"


class InternalRuleDefChar(InternalRuleDef):
    type = InternalRuleType.CHAR

    def __init__(self, value: list[int]):
        self.value = list(validate_non_empty(value))


class InternalRuleDefCharNot(InternalRuleDef):
    type = InternalRuleType.CHAR_NOT

    def __init__(self, value: list[int]):
        self.value = list(validate_non_empty(value))


class InternalRuleDefCharAlt(InternalRuleDef):
    type = InternalRuleType.CHAR_ALT

    def __init__(self, value: int):
        self.value = value


class InternalRuleDefCharRngUpper(InternalRuleDef):
    type = InternalRuleType.CHAR_RNG_UPPER

    def __init__(self, value: int):
        self.value = value


class InternalRuleDefReference(InternalRuleDef):
    type = InternalRuleType.REF

    def __init__(self, value: int):
        self.value = value


class InternalRuleDefAlt(InternalRuleDef):
    type = InternalRuleType.ALT


class InternalRuleDefEnd(InternalRuleDef):
    type = InternalRuleType.END


def internal_rule_def_char(value: list[int]) -> InternalRuleDefChar:
    return InternalRuleDefChar(value)


def internal_rule_def_char_not(value: list[int]) -> InternalRuleDefCharNot:
    return InternalRuleDefCharNot(value)


def internal_rule_def_char_alt(value: int) -> InternalRuleDefCharAlt:
    return InternalRuleDefCharAlt(value)


def internal_rule_def_char_rng_upper(value: int) -> InternalRuleDefCharRngUpper:
    return InternalRuleDefCharRngUpper(value)


def internal_rule_def_reference(value: int) -> InternalRuleDefReference:
    return InternalRuleDefReference(value)


def internal_rule_def_alt() -> InternalRuleDefAlt:
    return InternalRuleDefAlt()


def internal_rule_def_end() -> InternalRuleDefEnd:
    return InternalRuleDefEnd()


def is_rule_def_alt(rule: InternalRuleDef | None) -> bool:
    return isinstance(rule, InternalRuleDefAlt)


def is_rule_def_ref(rule: InternalRuleDef | None) -> bool:
    return isinstance(rule, InternalRuleDefReference)


def is_rule_def_end(rule: InternalRuleDef | None) -> bool:
    return isinstance(rule, InternalRuleDefEnd)


def is_rule_def_char(rule: InternalRuleDef | None) -> bool:
    return isinstance(rule, InternalRuleDefChar)


def is_rule_def_char_not(rule: InternalRuleDef | None) -> bool:
    return isinstance(rule, InternalRuleDefCharNot)


def is_rule_def_char_alt(rule: InternalRuleDef | None) -> bool:
    return isinstance(rule, InternalRuleDefCharAlt)


def is_rule_def_char_rng_upper(rule: InternalRuleDef | None) -> bool:
    return isinstance(rule, InternalRuleDefCharRngUpper)
