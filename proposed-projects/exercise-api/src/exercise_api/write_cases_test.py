import json

from exercise_api.write_cases import write_cases

CASES = [{"grammar": 'root ::= "a"', "input": "a"}, {"grammar": 'root ::= "b"', "input": "\n"}]


def describe_write_cases():
    def it_writes_one_json_line_per_case(tmp_path):
        path = tmp_path / "cases.jsonl"
        write_cases(CASES, path)
        assert [json.loads(line) for line in path.read_text().splitlines()] == CASES

    def it_creates_missing_parent_directories(tmp_path):
        path = tmp_path / "nested" / "cases.jsonl"
        write_cases(CASES, path)
        assert path.is_file()
