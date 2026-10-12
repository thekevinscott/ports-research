import math

import numpy as np

from src.stats import (
    bootstrap_interval,
    compare,
    minimum_detectable_gap,
    null_gaps,
    permutation_p,
    ranks,
    spearman,
)


def describe_compare():
    def it_finds_a_known_gap():
        off = list(range(20))
        on = [value + 50 for value in off]
        result = compare(on, off, shuffles=2_000, resamples=2_000)
        assert result["gap"] == 50
        assert result["p"] < 0.05
        assert result["low"] <= 50 <= result["high"]
        assert result["gap"] > result["minimum_detectable_gap"]

    def it_does_not_call_a_gap_between_two_shuffled_halves():
        values = np.random.default_rng(1).permutation(40)
        result = compare(values[:20], values[20:], shuffles=2_000, resamples=2_000)
        assert result["p"] > 0.05
        assert abs(result["gap"]) < result["minimum_detectable_gap"]

    def it_counts_and_medians_each_group():
        result = compare([1, 2, 30], [4, 5, 6, 7], shuffles=200, resamples=200)
        assert (result["n_on"], result["n_off"]) == (3, 4)
        assert (result["median_on"], result["median_off"]) == (2, 5.5)
        assert result["gap"] == -3.5

    def it_drops_missing_values():
        result = compare([1, None, 3], [float("nan"), 5], shuffles=200, resamples=200)
        assert (result["n_on"], result["n_off"]) == (2, 1)

    def it_gives_the_same_answer_for_the_same_seed():
        on, off = [3, 9, 4, 8, 7], [1, 6, 2, 5, 0]
        assert compare(on, off, shuffles=500, resamples=500) == compare(
            on, off, shuffles=500, resamples=500
        )


def describe_bootstrap_interval():
    def it_covers_the_true_gap_on_synthetic_data():
        rng = np.random.default_rng(7)
        off = rng.normal(50, 10, 48)
        on = rng.normal(60, 10, 48)
        low, high = bootstrap_interval(on, off, resamples=5_000)
        assert low < 10 < high

    def it_is_a_single_point_when_every_value_is_the_same():
        assert bootstrap_interval([4, 4, 4], [1, 1], resamples=100) == (3, 3)


def describe_minimum_detectable_gap():
    def it_is_the_smallest_gap_the_same_shuffles_call():
        nulls = null_gaps(list(range(10)), list(range(5, 15)), shuffles=1_000)
        threshold = minimum_detectable_gap(nulls)
        assert permutation_p(threshold, nulls) >= 0.05
        assert permutation_p(threshold + 1e-9, nulls) < 0.05

    def it_is_unreachable_with_too_few_shuffles():
        assert minimum_detectable_gap(np.zeros(10)) == math.inf


def describe_permutation_p():
    def it_counts_the_observed_split_among_the_shuffles():
        nulls = np.array([-3.0, -1.0, 0.0, 1.0, 2.0])
        assert permutation_p(2.0, nulls) == (2 + 1) / (5 + 1)
        assert permutation_p(-2.5, nulls) == (1 + 1) / (5 + 1)


def describe_ranks():
    def it_shares_the_average_rank_between_ties():
        assert ranks([10, 20, 20, 30]).tolist() == [1, 2.5, 2.5, 4]

    def it_ranks_in_input_order():
        assert ranks([30, 10, 20]).tolist() == [3, 1, 2]


def describe_spearman():
    def it_matches_the_textbook_formula_without_ties():
        # 1 - 6 * sum(d^2) / (n (n^2 - 1)), d = [-1, 1, -1, 1, 0]: 1 - 24 / 120.
        assert math.isclose(spearman([1, 2, 3, 4, 5], [2, 1, 4, 3, 5]), 0.8)

    def it_takes_pearson_over_average_ranks_with_ties():
        # ranks [1, 2.5, 2.5, 4] and [1, 3, 2, 4]: 4.5 / sqrt(4.5 * 5) = sqrt(0.9).
        assert math.isclose(spearman([1, 2, 2, 3], [1, 3, 2, 4]), math.sqrt(0.9))

    def it_is_minus_one_for_a_reversed_order():
        assert math.isclose(spearman([1, 2, 3], [9, 5, 1]), -1.0)

    def it_drops_a_pair_with_a_missing_value():
        assert math.isclose(spearman([1, 2, None, 3], [1, 2, 7, 3]), 1.0)

    def it_is_undefined_for_a_constant_measure():
        assert math.isnan(spearman([1, 2, 3], [4, 4, 4]))


def describe_compare_with_an_empty_group():
    def it_reports_the_counts_and_nothing_else():
        result = compare([1, 2], [], shuffles=100, resamples=100)
        assert (result["n_on"], result["n_off"]) == (2, 0)
        assert result["median_on"] == 1.5
        assert result["gap"] is None
        assert result["p"] is None
        assert result["minimum_detectable_gap"] is None
