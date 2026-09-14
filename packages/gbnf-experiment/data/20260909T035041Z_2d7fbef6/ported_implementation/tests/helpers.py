"""Small helpers for describing expected parse states compactly."""

from gbnf import GBNF, RuleType

END = (RuleType.END, None)


def char(*values):
    return (RuleType.CHAR, list(values))


def char_exclude(*values):
    return (RuleType.CHAR_EXCLUDE, list(values))


def codes(text):
    """The code points of ``text``, in the order a grammar would match them."""
    return [ord(c) for c in text]


def rules(state):
    """Normalize a parse state into ``(type, value)`` tuples."""
    return [(rule.type, getattr(rule, "value", None)) for rule in state]


def parse(grammar, *inputs):
    """Parse ``grammar``, feed each input in turn, return the final state."""
    state = GBNF(grammar)
    for input_ in inputs:
        state = state.add(input_)
    return state


def rules_after(grammar, *inputs):
    return rules(parse(grammar, *inputs))
