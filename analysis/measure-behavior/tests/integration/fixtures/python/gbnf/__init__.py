# A stand-in implementation whose behavior is keyed on the input, one input per outcome.
import os


class RuleEnd:
    pass


class InputParseError(Exception):
    pass


def GBNF(grammar, initial_string=""):
    print("noise on stdout")
    if initial_string == "accept":
        return [object(), RuleEnd()]
    if initial_string == "prefix":
        return [object()]
    if initial_string == "reject":
        raise InputParseError("rejected at 0")
    if initial_string == "error":
        raise ValueError("bad grammar")
    if initial_string == "hang":
        while True:
            pass
    os._exit(3)
