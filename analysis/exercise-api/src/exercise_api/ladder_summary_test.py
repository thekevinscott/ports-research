import pytest

from exercise_api.ladder_summary import ladder_summary

CASES = [
    {"grammar": "g", "input": "a", "rung": "1-literal"},
    {"grammar": "g", "input": "aaaa", "rung": "3-repetition"},
]


def _result(construct, add, ok=True):
    return {
        "ok": ok,
        "error_type": None if ok else "InputParseError",
        "error_pos": None,
        "rules": [] if ok else None,
        "elapsed_ns": 1,
        "construct_ns": construct,
        "add_ns": add,
    }


def describe_ladder_summary():
    def it_reports_median_p90_min_and_spread_per_phase():
        results = [_result(list(range(1, 101)), list(range(2, 202, 2))), _result([1], [2])]
        [first, _] = ladder_summary(cases=CASES, results=results)
        assert first["construct_ns"]["median"] == pytest.approx(50.5)
        assert first["construct_ns"]["p90"] == pytest.approx(90.1)
        assert first["construct_ns"]["min"] == 1
        assert first["construct_ns"]["spread"] == pytest.approx((90.1 - 10.9) / 50.5)
        assert first["add_ns"]["median"] == pytest.approx(101.0)

    def it_labels_each_entry_with_its_rung_and_input_length():
        results = [_result([1], [2]), _result([3], [4])]
        assert [(e["rung"], e["input_len"]) for e in ladder_summary(cases=CASES, results=results)] == [
            ("1-literal", 1),
            ("3-repetition", 4),
        ]

    def it_reports_a_single_repetition_without_spread():
        [entry] = ladder_summary(cases=CASES[:1], results=[_result([7], [9])])
        assert entry["construct_ns"] == {"median": 7, "p90": 7, "min": 7, "spread": 0.0}

    def it_drops_a_case_that_raised():
        results = [_result(None, None, ok=False), _result([3], [4])]
        assert [e["rung"] for e in ladder_summary(cases=CASES, results=results)] == ["3-repetition"]

    def it_drops_a_case_the_driver_never_timed():
        results = [{"ok": False, "error_type": "driver_failed", "error_pos": None, "rules": None, "elapsed_ns": None}]
        assert ladder_summary(cases=CASES[:1], results=results) == []

    def it_returns_nothing_for_no_cases():
        assert ladder_summary(cases=[], results=[]) == []
