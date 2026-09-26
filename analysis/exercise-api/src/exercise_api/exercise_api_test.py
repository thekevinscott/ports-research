from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest

from exercise_api.exercise_api import exercise_api

REFERENCE = Path("/reference")
TARGETS = [Path("/ports/a"), Path("/ports/b")]
CASES = [{"grammar": 'root ::= "a"', "input": "a"}]
RESULTS = [{"ok": True, "error_type": None, "error_pos": None, "rules": [], "elapsed_ns": 1}]
REPORT = {"cases": 1, "targets": {}}
LIMIT = 4 * 1024**3


@pytest.fixture
def run_driver_function():
    with patch("exercise_api.exercise_api.run_driver", autospec=True) as m:
        m.return_value = RESULTS
        yield m


@pytest.fixture
def compare_targets_function():
    with patch("exercise_api.exercise_api.compare_targets", autospec=True) as m:
        m.return_value = REPORT
        yield m


def describe_exercise_api():
    def it_runs_the_reference_unadapted_then_each_target_with_the_adapt_flag(run_driver_function, compare_targets_function):
        exercise_api(language="python", reference=REFERENCE, targets=TARGETS, cases=CASES, adapt=True, timeout=60, memory_limit_bytes=LIMIT)
        assert run_driver_function.call_args_list == [
            call(language="python", target=REFERENCE, cases=CASES, adapt=False, timeout=60, memory_limit_bytes=LIMIT, repeat=1, warmup=0),
            call(language="python", target=TARGETS[0], cases=CASES, adapt=True, timeout=60, memory_limit_bytes=LIMIT, repeat=1, warmup=0),
            call(language="python", target=TARGETS[1], cases=CASES, adapt=True, timeout=60, memory_limit_bytes=LIMIT, repeat=1, warmup=0),
        ]

    def it_gives_every_driver_the_same_repeat_and_warmup(run_driver_function, compare_targets_function):
        exercise_api(language="python", reference=REFERENCE, targets=TARGETS, cases=CASES, adapt=True, timeout=60, memory_limit_bytes=LIMIT, repeat=30, warmup=3)
        assert [(c.kwargs["repeat"], c.kwargs["warmup"]) for c in run_driver_function.call_args_list] == [(30, 3)] * 3

    def it_compares_targets_keyed_by_path(run_driver_function, compare_targets_function):
        exercise_api(language="python", reference=REFERENCE, targets=TARGETS, cases=CASES, adapt=False, timeout=60, memory_limit_bytes=LIMIT)
        assert compare_targets_function.call_args.kwargs == {
            "cases": CASES,
            "reference": RESULTS,
            "targets": {"/ports/a": RESULTS, "/ports/b": RESULTS},
        }

    def it_checkpoints_the_report_so_far_after_each_target(run_driver_function, compare_targets_function):
        compare_targets_function.side_effect = lambda **kwargs: {**REPORT, "targets": dict(kwargs["targets"])}
        checkpoint = Mock()
        exercise_api(language="python", reference=REFERENCE, targets=TARGETS, cases=CASES, adapt=False, timeout=60, memory_limit_bytes=LIMIT, checkpoint=checkpoint)
        assert [c.args[0]["targets"] for c in checkpoint.call_args_list] == [
            {"/ports/a": RESULTS},
            {"/ports/a": RESULTS, "/ports/b": RESULTS},
        ]
        assert checkpoint.call_args.args[0] == {"language": "python", "reference": "/reference", "cases": 1, "targets": {"/ports/a": RESULTS, "/ports/b": RESULTS}}

    def it_returns_the_comparison_with_language_and_reference(run_driver_function, compare_targets_function):
        report = exercise_api(language="typescript", reference=REFERENCE, targets=TARGETS, cases=CASES, adapt=False, timeout=60, memory_limit_bytes=LIMIT)
        assert report == {"language": "typescript", "reference": "/reference", **REPORT}
