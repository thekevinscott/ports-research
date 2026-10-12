# A stand-in implementation whose construction is keyed on the grammar; "!" in an added input raises at its position.
import os


class RuleChar:
    def __init__(self, value):
        self.value = value


class RuleEnd:
    pass


class InputParseError(Exception):
    def __init__(self, pos):
        super().__init__(f"rejected at {pos}")
        self.pos = pos


class State:
    def __init__(self, seen):
        self.seen = seen

    def __iter__(self):
        return iter([RuleChar([ord(c) for c in self.seen]), RuleEnd()])

    def add(self, text):
        if "!" in text:
            raise InputParseError(text.index("!"))
        return State(self.seen + text)


def GBNF(grammar):
    print("noise on stdout")
    if grammar == "error":
        raise ValueError("bad grammar")
    if grammar == "hang":
        while True:
            pass
    if grammar == "exit":
        os._exit(3)
    return State("")
