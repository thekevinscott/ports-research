from typing import Union

ValidInput = Union[str, int, list]

# A range is a two-element list of code points, inclusive on both ends.
Range = list


class RuleType:
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"


ALL_RULE_TYPES = frozenset({RuleType.CHAR, RuleType.CHAR_EXCLUDE, RuleType.END})


class RuleChar:
    def __init__(self, value):
        self.type = RuleType.CHAR
        self.value = list(value)

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return self.value == other.value

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return f"RuleChar({self.value})"


class RuleCharExclude:
    def __init__(self, value):
        self.type = RuleType.CHAR_EXCLUDE
        self.value = list(value)

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return self.value == other.value

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return f"RuleCharExclude({self.value})"


class RuleEnd:
    def __init__(self):
        self.type = RuleType.END

    def __eq__(self, other):
        if type(other) is not type(self):
            return NotImplemented
        return True

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return "RuleEnd()"
