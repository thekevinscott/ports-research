import pytest

from exercise_api.read_cases import read_cases


@pytest.fixture
def cases_file(tmp_path):
    path = tmp_path / "cases.jsonl"
    path.write_text('{"grammar": "root ::= \\"a\\"", "input": "a"}\n\n{"grammar": "", "input": ""}\n')
    return path


def describe_read_cases():
    def it_reads_one_case_per_non_blank_line(cases_file):
        assert read_cases(cases_file) == [
            {"grammar": 'root ::= "a"', "input": "a"},
            {"grammar": "", "input": ""},
        ]

    def it_rejects_a_case_without_grammar_and_input(tmp_path):
        path = tmp_path / "cases.jsonl"
        path.write_text('{"grammar": "root ::= \\"a\\""}\n')
        with pytest.raises(ValueError):
            read_cases(path)

    def it_keeps_an_optional_rung(tmp_path):
        path = tmp_path / "cases.jsonl"
        path.write_text('{"grammar": "g", "input": "a", "rung": "1-literal"}\n')
        assert read_cases(path) == [{"grammar": "g", "input": "a", "rung": "1-literal"}]

    def it_keeps_an_optional_repeat_and_warmup_budget(tmp_path):
        path = tmp_path / "cases.jsonl"
        path.write_text('{"grammar": "g", "input": "a", "repeat": 5, "warmup": 1}\n')
        assert read_cases(path) == [{"grammar": "g", "input": "a", "repeat": 5, "warmup": 1}]

    def it_rejects_a_case_with_any_other_key(tmp_path):
        path = tmp_path / "cases.jsonl"
        path.write_text('{"grammar": "g", "input": "a", "note": "x"}\n')
        with pytest.raises(ValueError):
            read_cases(path)
