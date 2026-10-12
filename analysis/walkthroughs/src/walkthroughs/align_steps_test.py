import pytest

from walkthroughs.align_steps import align_steps


def table(scores):
    """A fake similarity from (reference step, port step) to score; anything unlisted scores 0."""

    def similarity(reference, port):
        return [[scores.get((r, p), 0.0) for p in port] for r in reference]

    return similarity


def describe_align_steps():
    def it_matches_each_step_above_the_threshold_and_reports_coverage():
        aligned = align_steps(["a", "b", "c", "d"], ["A", "B", "X"], similarity=table({("a", "A"): 0.9, ("b", "B"): 0.85}), threshold=0.8)
        assert aligned["coverage"] == 0.5
        assert aligned["missing_steps"] == ["c", "d"]
        assert aligned["extra_steps"] == ["X"]
        assert aligned["matches"] == [{"reference": 0, "port": 0, "similarity": 0.9}, {"reference": 1, "port": 1, "similarity": 0.85}]

    def it_leaves_a_pair_below_the_threshold_unmatched():
        aligned = align_steps(["a"], ["A"], similarity=table({("a", "A"): 0.79}), threshold=0.8)
        assert (aligned["coverage"], aligned["missing_steps"], aligned["extra_steps"]) == (0.0, ["a"], ["A"])

    def it_matches_one_to_one_taking_the_most_similar_pair_first():
        aligned = align_steps(["a", "b"], ["A"], similarity=table({("a", "A"): 0.85, ("b", "A"): 0.95}), threshold=0.8)
        assert aligned["matches"] == [{"reference": 1, "port": 0, "similarity": 0.95}]
        assert aligned["missing_steps"] == ["a"]

    def it_breaks_a_tie_by_relative_position_so_order_is_kept_where_possible():
        aligned = align_steps(["a", "b"], ["A", "B"], similarity=table({(r, p): 0.9 for r in "ab" for p in "AB"}), threshold=0.8)
        assert [(m["reference"], m["port"]) for m in aligned["matches"]] == [(0, 0), (1, 1)]
        assert aligned["order_agreement"] == 1.0

    def it_scores_order_by_the_longest_increasing_run_of_port_positions():
        scores = {("a", "C"): 0.9, ("b", "A"): 0.9, ("c", "B"): 0.9}
        aligned = align_steps(["a", "b", "c"], ["A", "B", "C"], similarity=table(scores), threshold=0.8)
        assert aligned["order_agreement"] == pytest.approx(2 / 3)

    def it_has_no_coverage_without_reference_steps_and_no_order_without_matches():
        aligned = align_steps([], ["A"], similarity=table({}), threshold=0.8)
        assert (aligned["coverage"], aligned["order_agreement"], aligned["extra_steps"]) == (None, None, ["A"])
