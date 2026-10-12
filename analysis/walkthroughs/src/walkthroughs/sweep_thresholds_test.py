import pytest

from walkthroughs.sweep_thresholds import sweep_thresholds


def graded(reference, port):
    """A fake similarity: the score is written into each port step, so a test sets every pair's score."""
    return [[float(p.split(":")[1]) if p.split(":")[0] == r else 0.0 for p in port] for r in reference]


SIMILARITY = {"name": "fake", "threshold": 0.8, "score": graded, "embeddings": None}


def entry(name, happy=(), errors=(), invariants=()):
    return {"name": name, "happy_path": list(happy), "error_paths": list(errors), "invariants": list(invariants)}


def describe_sweep_thresholds():
    def it_reports_the_section_means_at_the_threshold_and_two_steps_either_side():
        reference = {"entry_points": [entry("f", happy=["a", "b", "c", "d"], errors=["e"])]}
        port = {"entry_points": [entry("f", happy=["a:0.95", "b:0.82", "c:0.76", "d:0.5"], errors=["e:0.88"])]}
        swept = sweep_thresholds(reference, port, SIMILARITY)
        assert [s["threshold"] for s in swept] == pytest.approx([0.7, 0.75, 0.8, 0.85, 0.9])
        assert [s["mean_coverage"] for s in swept] == [0.75, 0.75, 0.5, 0.25, 0.25]
        assert [s["error_paths"]["mean_coverage"] for s in swept] == [1.0, 1.0, 1.0, 1.0, 0.0]
        assert swept[0]["invariants"] == {"mean_coverage": None, "mean_order_agreement": None}
        assert set(swept[0]) == {"threshold", "mean_coverage", "mean_order_agreement", "error_paths", "invariants"}

