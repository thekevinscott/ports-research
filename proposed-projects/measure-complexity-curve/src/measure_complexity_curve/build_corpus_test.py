from measure_complexity_curve.build_corpus import build_corpus


def describe_build_corpus():
    def it_returns_one_entry_per_size():
        corpus = build_corpus(sizes=[4, 8, 16], nesting_depth=0, alternation_width=1, seed=0)
        assert len(corpus) == 3

    def it_preserves_size_order_and_records_each_size():
        corpus = build_corpus(sizes=[4, 8, 16], nesting_depth=0, alternation_width=1, seed=0)
        assert [entry["size"] for entry in corpus] == [4, 8, 16]

    def it_generates_a_bigger_grammar_string_for_a_bigger_size():
        corpus = build_corpus(sizes=[4, 64], nesting_depth=0, alternation_width=1, seed=0)
        assert len(corpus[0]["grammar"]) < len(corpus[1]["grammar"])

    def it_is_deterministic_for_a_given_seed():
        first = build_corpus(sizes=[4, 8], nesting_depth=1, alternation_width=2, seed=7)
        second = build_corpus(sizes=[4, 8], nesting_depth=1, alternation_width=2, seed=7)
        assert first == second
