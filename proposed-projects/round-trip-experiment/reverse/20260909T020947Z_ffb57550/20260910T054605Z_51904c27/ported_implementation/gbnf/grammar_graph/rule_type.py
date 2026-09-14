from enum import Enum


class RuleType(str, Enum):
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    REF = "ref"
    END = "end"

    def __str__(self) -> str:
        return self.value
