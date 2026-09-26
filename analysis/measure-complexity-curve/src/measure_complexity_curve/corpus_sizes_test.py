import pytest

from measure_complexity_curve.corpus_sizes import corpus_sizes


def describe_corpus_sizes():
    def it_produces_a_clean_power_of_two_progression_for_the_cli_defaults():
        assert corpus_sizes(max_size=128, steps=6) == [4, 8, 16, 32, 64, 128]

    def it_returns_exactly_steps_many_sizes():
        assert len(corpus_sizes(max_size=1000, steps=9)) == 9

    def it_starts_at_the_floor_of_four():
        assert corpus_sizes(max_size=1000, steps=5)[0] == 4

    def it_is_strictly_increasing():
        sizes = corpus_sizes(max_size=1000, steps=9)
        assert sizes == sorted(set(sizes))

    def it_returns_only_max_size_for_a_single_step():
        assert corpus_sizes(max_size=99, steps=1) == [99]

    def it_rejects_a_max_size_below_the_floor():
        with pytest.raises(ValueError):
            corpus_sizes(max_size=3, steps=5)

    def it_rejects_a_step_count_below_one():
        with pytest.raises(ValueError):
            corpus_sizes(max_size=128, steps=0)
