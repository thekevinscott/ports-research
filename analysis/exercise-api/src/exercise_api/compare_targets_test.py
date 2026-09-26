from unittest.mock import patch

import pytest

from exercise_api.compare_targets import compare_targets

CASES = [{"grammar": f'root ::= "{c}"', "input": c} for c in "abc"]


def _result(ok, elapsed_ns, error_type=None, phases=False):
    result = {"ok": ok, "error_type": error_type, "error_pos": None if ok else 0, "rules": [] if ok else None, "elapsed_ns": elapsed_ns}
    return {**result, "construct_ns": [elapsed_ns], "add_ns": [elapsed_ns]} if phases else result


REFERENCE = [_result(True, 10), _result(True, 20), _result(False, 30, "InputParseError")]
SAME = [_result(True, 1), _result(True, 2), _result(False, 3, "InputParseError")]
OTHER = [_result(True, 1), _result(False, 2, "InputParseError"), _result(False, 3, "InputParseError")]
THIRD = [_result(True, 1), _result(False, 2, "InputParseError"), _result(True, 3)]


@pytest.fixture
def outcome_key_function():
    with patch("exercise_api.compare_targets.outcome_key", autospec=True) as m:
        m.side_effect = lambda result: (result["ok"], result["error_type"])
        yield m


@pytest.fixture
def timing_summary_function():
    with patch("exercise_api.compare_targets.timing_summary", autospec=True) as m:
        m.side_effect = lambda results: {"mean_elapsed_ns": results[0]["elapsed_ns"], "p50_elapsed_ns": 0, "p95_elapsed_ns": 0}
        yield m


@pytest.fixture
def ladder_summary_function():
    with patch("exercise_api.compare_targets.ladder_summary", autospec=True) as m:
        m.side_effect = lambda cases, results: [{"rung": r["elapsed_ns"]} for r in results]
        yield m


def describe_compare_targets():
    def it_counts_agreement_per_target(outcome_key_function, timing_summary_function):
        report = compare_targets(cases=CASES, reference=REFERENCE, targets={"same": SAME, "other": OTHER})
        assert report["targets"]["same"]["agree_with_reference"] == 3
        assert report["targets"]["same"]["disagree_with_reference"] == 0
        assert report["targets"]["other"]["agree_with_reference"] == 2
        assert report["targets"]["other"]["disagree_with_reference"] == 1

    def it_lists_each_disagreement_with_case_and_both_outputs_minus_timing(outcome_key_function, timing_summary_function):
        report = compare_targets(cases=CASES, reference=REFERENCE, targets={"other": OTHER})
        [disagreement] = report["targets"]["other"]["disagreements"]
        assert disagreement["case"] == CASES[1]
        assert disagreement["reference"] == {"ok": True, "error_type": None, "error_pos": None, "rules": []}
        assert disagreement["target"] == {"ok": False, "error_type": "InputParseError", "error_pos": 0, "rules": None}

    def it_caps_disagreements_at_twenty(outcome_key_function, timing_summary_function):
        cases = [{"grammar": "g", "input": str(i)} for i in range(30)]
        reference = [_result(True, 1)] * 30
        target = [_result(False, 1, "E")] * 30
        report = compare_targets(cases=cases, reference=reference, targets={"t": target})
        assert report["targets"]["t"]["disagree_with_reference"] == 30
        assert len(report["targets"]["t"]["disagreements"]) == 20

    def it_counts_error_cases_on_both_sides(outcome_key_function, timing_summary_function):
        report = compare_targets(cases=CASES, reference=REFERENCE, targets={"other": OTHER})
        assert report["targets"]["other"]["reference_error_cases"] == 1
        assert report["targets"]["other"]["target_error_cases"] == 2

    def it_reports_timing_for_reference_and_target(outcome_key_function, timing_summary_function):
        report = compare_targets(cases=CASES, reference=REFERENCE, targets={"other": OTHER})
        assert report["targets"]["other"]["reference_mean_elapsed_ns"] == 10
        assert report["targets"]["other"]["target_mean_elapsed_ns"] == 1
        assert report["targets"]["other"]["reference_p95_elapsed_ns"] == 0
        assert report["targets"]["other"]["target_p50_elapsed_ns"] == 0

    def it_reports_the_case_count(outcome_key_function, timing_summary_function):
        report = compare_targets(cases=CASES, reference=REFERENCE, targets={"same": SAME})
        assert report["cases"] == 3
        assert report["targets"]["same"]["cases"] == 3

    def it_omits_cross_target_agreement_with_a_single_target(outcome_key_function, timing_summary_function):
        report = compare_targets(cases=CASES, reference=REFERENCE, targets={"same": SAME})
        assert "agree_all_targets" not in report
        assert "agree_all_targets_not_reference" not in report

    def it_counts_cases_where_every_target_agrees(outcome_key_function, timing_summary_function):
        report = compare_targets(cases=CASES, reference=REFERENCE, targets={"other": OTHER, "third": THIRD})
        assert report["agree_all_targets"] == 2

    def it_counts_cases_where_every_target_agrees_against_the_reference(outcome_key_function, timing_summary_function):
        report = compare_targets(cases=CASES, reference=REFERENCE, targets={"other": OTHER, "third": THIRD})
        assert report["agree_all_targets_not_reference"] == 1

    def it_omits_timings_when_the_driver_measured_each_case_once(outcome_key_function, timing_summary_function, ladder_summary_function):
        report = compare_targets(cases=CASES, reference=REFERENCE, targets={"same": SAME})
        assert "timings" not in report["targets"]["same"]
        assert "reference_timings" not in report["targets"]["same"]
        ladder_summary_function.assert_not_called()

    def it_summarises_both_sides_when_the_driver_repeated_each_case(outcome_key_function, timing_summary_function, ladder_summary_function):
        reference = [_result(True, 10, phases=True)]
        target = [_result(True, 1, phases=True)]
        report = compare_targets(cases=CASES[:1], reference=reference, targets={"same": target})
        assert report["targets"]["same"]["timings"] == [{"rung": 1}]
        assert report["targets"]["same"]["reference_timings"] == [{"rung": 10}]

    def it_keeps_the_per_repetition_lists_out_of_the_disagreements(outcome_key_function, timing_summary_function, ladder_summary_function):
        reference = [_result(True, 10, phases=True)]
        target = [_result(False, 1, "InputParseError", phases=True)]
        report = compare_targets(cases=CASES[:1], reference=reference, targets={"other": target})
        [disagreement] = report["targets"]["other"]["disagreements"]
        assert set(disagreement["target"]) == {"ok", "error_type", "error_pos", "rules"}
        assert set(disagreement["reference"]) == {"ok", "error_type", "error_pos", "rules"}
