class RuleType:
    CHAR = "char"
    CHAR_EXCLUDE = "char_exclude"
    END = "end"

    @classmethod
    def values(cls):
        return (cls.CHAR, cls.CHAR_EXCLUDE, cls.END)


class _Rule:
    """Base for the rules handed back to callers.

    Instances are compared structurally but hashed by identity: the graph relies on
    reference equality the way the reference implementation's `Map`/`Set` do.
    """

    __hash__ = object.__hash__

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return f"{type(self).__name__}({getattr(self, 'value', '')!r})"


class RuleChar(_Rule):
    def __init__(self, value=None):
        self.type = RuleType.CHAR
        self.value = list(value) if value is not None else []


class RuleCharExclude(_Rule):
    def __init__(self, value=None):
        self.type = RuleType.CHAR_EXCLUDE
        self.value = list(value) if value is not None else []


class RuleEnd(_Rule):
    def __init__(self):
        self.type = RuleType.END
