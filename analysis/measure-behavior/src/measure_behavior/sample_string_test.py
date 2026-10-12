import random

from measure_behavior.sample_string import sample_string


def sample(node, rules=None, seed=0):
    return sample_string(node, rules or {}, random.Random(seed))


def describe_sample_string():
    def it_returns_a_literal_verbatim():
        assert sample(("lit", "abc")) == "abc"

    def it_concatenates_a_sequence():
        assert sample(("seq", (("lit", "a"), ("lit", "b")))) == "ab"

    def it_picks_one_branch_of_an_alternation():
        assert {sample(("alt", (("lit", "a"), ("lit", "b"))), seed=s) for s in range(20)} == {"a", "b"}

    def it_draws_a_class_member_or_a_range_member():
        drawn = {sample(("cls", False, ("x", ("0", "2"))), seed=s) for s in range(40)}
        assert drawn == {"x", "0", "1", "2"}

    def it_draws_outside_a_negated_class():
        drawn = {sample(("cls", True, ("a", ("0", "9"))), seed=s) for s in range(40)}
        assert drawn and not drawn & {"a", *"0123456789"}

    def it_repeats_within_the_operator_bounds():
        lengths = {len(sample(("rep", "*", ("lit", "a")), seed=s)) for s in range(40)}
        assert min(lengths) == 0 and max(lengths) <= 3
        assert min(len(sample(("rep", "+", ("lit", "a")), seed=s)) for s in range(40)) == 1
        assert {len(sample(("rep", "?", ("lit", "a")), seed=s)) for s in range(40)} == {0, 1}

    def it_follows_references():
        assert sample(("ref", "x"), {"x": ("lit", "q")}) == "q"

    def it_terminates_on_a_recursive_rule_by_taking_the_last_branch_when_deep():
        rules = {"nest": ("alt", (("seq", (("lit", "("), ("ref", "nest"), ("lit", ")"))), ("lit", "x")))}
        for seed in range(20):
            text = sample(("ref", "nest"), rules, seed)
            assert text.count("(") == text.count(")") and text.strip("()") == "x"
