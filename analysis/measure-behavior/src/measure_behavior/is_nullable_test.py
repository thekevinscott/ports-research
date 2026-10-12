from measure_behavior.is_nullable import is_nullable

LIT = ("lit", "a")
CLS = ("cls", False, ("a",))


def describe_is_nullable():
    def it_is_false_for_a_literal_and_a_class():
        assert not is_nullable(LIT, {})
        assert not is_nullable(CLS, {})

    def it_is_true_for_star_and_optional_and_false_for_plus():
        assert is_nullable(("rep", "*", LIT), {})
        assert is_nullable(("rep", "?", LIT), {})
        assert not is_nullable(("rep", "+", LIT), {})

    def it_is_true_for_a_sequence_only_when_every_child_is():
        assert is_nullable(("seq", (("rep", "?", LIT), ("rep", "*", CLS))), {})
        assert not is_nullable(("seq", (("rep", "?", LIT), LIT)), {})

    def it_is_true_for_an_alternation_when_any_child_is():
        assert is_nullable(("alt", (LIT, ("rep", "?", LIT))), {})
        assert not is_nullable(("alt", (LIT, CLS)), {})

    def it_follows_references():
        rules = {"x": ("rep", "?", LIT), "y": LIT}
        assert is_nullable(("ref", "x"), rules)
        assert not is_nullable(("ref", "y"), rules)
