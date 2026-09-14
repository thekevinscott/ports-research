from enum import Enum


class RuleType(str, Enum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"
    REF = "ref"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value
