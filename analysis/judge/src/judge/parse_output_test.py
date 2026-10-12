import json

import pytest

from judge.parse_output import parse_output

USAGE = {"input_tokens": 10, "output_tokens": 20}


def output(**fields):
    return json.dumps({"type": "result", "is_error": False, **fields})


def describe_parse_output():
    def it_takes_the_structured_output_when_the_cli_returns_one():
        parsed = parse_output(output(result='{"a": 1}', structured_output={"a": 1}, usage=USAGE))
        assert parsed == {"verdicts": {"a": 1}, "raw": '{"a": 1}', "usage": USAGE}

    def it_falls_back_to_the_first_json_object_in_the_result_text():
        text = 'Here it is:\n```json\n{"a": {"b": [1, 2]}}\n```\nand {"c": 3}'
        assert parse_output(output(result=text, usage=USAGE))["verdicts"] == {"a": {"b": [1, 2]}}

    def it_skips_braces_that_do_not_open_an_object():
        assert parse_output(output(result='a {not json} then {"a": 1}'))["verdicts"] == {"a": 1}

    def it_records_no_usage_when_the_cli_gives_none():
        assert parse_output(output(result='{"a": 1}'))["usage"] is None

    def it_rejects_a_result_with_no_json_object():
        with pytest.raises(ValueError, match="no JSON object"):
            parse_output(output(result="I cannot judge this."))

    def it_rejects_an_error_result():
        with pytest.raises(ValueError, match="overloaded"):
            parse_output(json.dumps({"type": "result", "is_error": True, "result": "overloaded"}))
