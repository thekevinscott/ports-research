import sys

import pytest

from measure_complexity_curve.generate_grammar import generate_grammar

PARAMETER_GRID = [
    (rule_count, nesting_depth, alternation_width)
    for rule_count in (1, 4, 16)
    for nesting_depth in (0, 1)
    for alternation_width in (1, 2, 3)
]


def parse_with_reference(python_reference, grammar: str) -> None:
    """Imports the real reference fresh, so a stale `gbnf` module from an
    earlier test (or another fixture) can never mask a real parse failure."""
    for name in list(sys.modules):
        if name == "gbnf" or name.startswith("gbnf."):
            del sys.modules[name]
    sys.path.insert(0, str(python_reference))
    try:
        import gbnf

        gbnf.GBNF(grammar)
    finally:
        sys.path.remove(str(python_reference))


def describe_generate_grammar():
    @pytest.mark.parametrize(("rule_count", "nesting_depth", "alternation_width"), PARAMETER_GRID)
    def it_produces_grammar_kevins_python_reference_accepts(
        python_reference, rule_count, nesting_depth, alternation_width
    ):
        grammar = generate_grammar(
            rule_count=rule_count,
            nesting_depth=nesting_depth,
            alternation_width=alternation_width,
            seed=0,
        )
        parse_with_reference(python_reference, grammar)

    def it_hits_a_recursion_limit_in_the_reference_above_nesting_depth_one(python_reference):
        """Documents a reference limitation, not a generator defect: two or more
        stacked repetition operators recurse until Python's stack limit trips,
        regardless of grammar size. `generate_grammar` stays capable of emitting
        this GBNF; callers just should not set `nesting_depth` above 1 when
        comparing against this reference."""
        grammar = generate_grammar(rule_count=1, nesting_depth=2, alternation_width=1, seed=0)
        with pytest.raises(RecursionError):
            parse_with_reference(python_reference, grammar)
