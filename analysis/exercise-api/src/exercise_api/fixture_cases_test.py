import json

import pytest

from exercise_api.fixture_cases import fixture_cases


@pytest.fixture
def grammars_dir(tmp_path):
    (tmp_path / "b.gbnf").write_text('root ::= "b"\n')
    (tmp_path / "b.json").write_text(json.dumps(["b", ""]))
    (tmp_path / "a.gbnf").write_text('root ::= "a"\n')
    (tmp_path / "a.json").write_text(json.dumps(["a"]))
    return tmp_path


def describe_fixture_cases():
    def it_pairs_each_grammar_with_every_input_in_its_json_list(grammars_dir):
        assert fixture_cases(grammars_dir) == [
            {"grammar": 'root ::= "a"\n', "input": "a"},
            {"grammar": 'root ::= "b"\n', "input": "b"},
            {"grammar": 'root ::= "b"\n', "input": ""},
        ]

    def it_rejects_a_directory_without_grammars(tmp_path):
        with pytest.raises(FileNotFoundError):
            fixture_cases(tmp_path)
