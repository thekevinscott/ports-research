import pytest

from measure_complexity_curve.generate_grammar import generate_grammar


def describe_generate_grammar():
    def it_starts_with_a_root_rule_pointing_at_the_first_chain_rule():
        grammar = generate_grammar(rule_count=3, nesting_depth=1, alternation_width=1, seed=0)
        assert grammar.startswith("root ::= a\n")

    def it_defines_exactly_rule_count_chain_rules():
        grammar = generate_grammar(rule_count=5, nesting_depth=1, alternation_width=1, seed=0)
        for name in ("a", "b", "c", "d", "e"):
            assert f"{name} ::=" in grammar
        assert "f ::=" not in grammar

    def it_chains_each_rule_to_the_next():
        grammar = generate_grammar(rule_count=3, nesting_depth=0, alternation_width=1, seed=0)
        assert "b" in grammar.splitlines()[1]
        assert "c" in grammar.splitlines()[2]

    def it_terminates_the_chain_with_a_literal_leaf():
        grammar = generate_grammar(rule_count=3, nesting_depth=0, alternation_width=1, seed=0)
        assert '"leaf"' in grammar.splitlines()[-1]

    def it_gives_each_rule_alternation_width_alternatives_plus_the_chain_link():
        grammar = generate_grammar(rule_count=1, nesting_depth=0, alternation_width=4, seed=0)
        rule_line = grammar.splitlines()[1]
        assert rule_line.count("|") == 4

    def it_is_deterministic_for_a_given_seed():
        first = generate_grammar(rule_count=6, nesting_depth=2, alternation_width=3, seed=42)
        second = generate_grammar(rule_count=6, nesting_depth=2, alternation_width=3, seed=42)
        assert first == second

    def it_varies_with_the_seed():
        first = generate_grammar(rule_count=6, nesting_depth=2, alternation_width=3, seed=1)
        second = generate_grammar(rule_count=6, nesting_depth=2, alternation_width=3, seed=2)
        assert first != second

    def it_rejects_a_rule_count_below_one():
        with pytest.raises(ValueError):
            generate_grammar(rule_count=0, nesting_depth=1, alternation_width=1, seed=0)

    def it_rejects_an_alternation_width_below_one():
        with pytest.raises(ValueError):
            generate_grammar(rule_count=1, nesting_depth=1, alternation_width=0, seed=0)
