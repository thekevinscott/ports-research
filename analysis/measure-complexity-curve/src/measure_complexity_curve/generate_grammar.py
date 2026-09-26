import random

from .nested_literal import nested_literal
from .rule_name import rule_name


def generate_grammar(*, rule_count: int, nesting_depth: int, alternation_width: int, seed: int) -> str:
    """A deterministic GBNF grammar chained across `rule_count` rules.

    Each rule alternates `alternation_width` nested literals with a link to the
    next rule in the chain, so a parser genuinely walks the whole chain rather
    than resolving the first rule and stopping — that walk is the thing whose
    scaling this package fingerprints. The last rule closes the chain with a
    plain literal instead of a link, so `root` always resolves to a finite
    grammar.

    `nesting_depth` above 1 is syntactically valid GBNF but not usable against
    Kevin's python reference: two or more stacked repetition operators make its
    grammar-graph resolver recurse until Python's stack limit trips
    (`RecursionError`), independent of grammar size — a reference construction
    limit, not a scaling difference, so out of scope for what this package
    measures. See `tests/integration/generate_grammar_test.py`.
    """
    if rule_count < 1:
        raise ValueError("rule_count must be at least 1")
    if alternation_width < 1:
        raise ValueError("alternation_width must be at least 1")

    rng = random.Random(seed)
    lines = [f"root ::= {rule_name(0)}"]
    for i in range(rule_count):
        alternatives = [nested_literal(rng, nesting_depth) for _ in range(alternation_width)]
        alternatives.append(rule_name(i + 1) if i + 1 < rule_count else '"leaf"')
        lines.append(f"{rule_name(i)} ::= {' | '.join(alternatives)}")
    return "\n".join(lines) + "\n"
