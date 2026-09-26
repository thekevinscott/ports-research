import pytest

from exercise_api.timing_summary import timing_summary


def _results(*elapsed):
    return [{"ok": True, "error_type": None, "error_pos": None, "rules": [], "elapsed_ns": e} for e in elapsed]


def describe_timing_summary():
    def it_reports_mean_p50_and_p95():
        summary = timing_summary(_results(*range(1, 101)))
        assert summary["mean_elapsed_ns"] == pytest.approx(50.5)
        assert summary["p50_elapsed_ns"] == pytest.approx(50.5)
        assert summary["p95_elapsed_ns"] == pytest.approx(95.05)

    def it_skips_results_without_a_time():
        summary = timing_summary(_results(10, None, 30))
        assert summary["mean_elapsed_ns"] == pytest.approx(20)

    def it_returns_nulls_when_nothing_was_timed():
        assert timing_summary(_results(None)) == {"mean_elapsed_ns": None, "p50_elapsed_ns": None, "p95_elapsed_ns": None}

    def it_handles_a_single_measurement():
        summary = timing_summary(_results(7))
        assert summary == {"mean_elapsed_ns": 7, "p50_elapsed_ns": 7, "p95_elapsed_ns": 7}
