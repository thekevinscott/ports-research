from measure_api.classify_case import classify_case


def record(*steps, crash=None):
    return {"grammar": "g0000", "input": 0, "steps": None if crash else list(steps), "crash": crash}


CONSTRUCT = {"step": "construct", "rules": [{"type": "char", "value": [97]}]}
WHOLE = {"step": "whole", "rules": [{"type": "end", "value": None}]}
OTHER = {"step": "whole", "rules": [{"type": "char", "value": [98]}]}
RAISED = {"step": "whole", "error": {"class": "InputParseError", "pos": 0}}
RAISED_ELSEWHERE = {"step": "whole", "error": {"class": "InputParseError", "pos": 1}}


def describe_classify_case():
    def it_calls_every_step_equal_a_match():
        assert classify_case(record(CONSTRUCT, WHOLE), record(CONSTRUCT, WHOLE)) == ("match", None)

    def it_calls_equal_steps_with_an_error_an_error_match():
        assert classify_case(record(CONSTRUCT, RAISED), record(CONSTRUCT, RAISED)) == ("error_match", None)

    def it_calls_differing_rules_a_mismatch_at_the_first_differing_step():
        assert classify_case(record(CONSTRUCT, WHOLE), record(CONSTRUCT, OTHER)) == ("mismatch", 1)

    def it_calls_an_error_on_one_side_an_error_mismatch():
        assert classify_case(record(CONSTRUCT, WHOLE), record(CONSTRUCT, RAISED)) == ("error_mismatch", 1)
        assert classify_case(record(CONSTRUCT, RAISED), record(CONSTRUCT, WHOLE)) == ("error_mismatch", 1)

    def it_calls_errors_that_differ_an_error_mismatch():
        assert classify_case(record(CONSTRUCT, RAISED), record(CONSTRUCT, RAISED_ELSEWHERE)) == ("error_mismatch", 1)

    def it_calls_a_missing_step_an_error_mismatch():
        assert classify_case(record(CONSTRUCT, WHOLE), record(CONSTRUCT)) == ("error_mismatch", 1)

    def it_calls_a_crash_on_either_side_a_crash():
        assert classify_case(record(CONSTRUCT), record(crash="timed out after 10s")) == ("crash", None)
        assert classify_case(record(crash="exit 1"), record(CONSTRUCT)) == ("crash", None)
