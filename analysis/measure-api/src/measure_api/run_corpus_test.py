import json
from unittest.mock import patch

import pytest

from measure_api.run_corpus import run_corpus


@pytest.fixture
def corpus(tmp_path):
    root = tmp_path / "corpus"
    (root / "grammars").mkdir(parents=True)
    (root / "inputs").mkdir()
    (root / "grammars" / "g0001.gbnf").write_text('root ::= "b"\n')
    (root / "inputs" / "g0001.json").write_text(json.dumps(["b"]))
    (root / "grammars" / "g0000.gbnf").write_text('root ::= "a"\n')
    (root / "inputs" / "g0000.json").write_text(json.dumps(["a", "x"]))
    return root


@pytest.fixture
def run_case_function():
    with patch("measure_api.run_corpus.run_case", autospec=True) as m:
        m.side_effect = lambda language, implementation, grammar, text: {"steps": [{"step": "whole", "input": text}], "crash": None}
        yield m


def describe_run_corpus():
    def it_writes_one_record_per_case_in_id_order(corpus, run_case_function, tmp_path):
        out = tmp_path / "out.jsonl"
        run_corpus(corpus=corpus, implementation=tmp_path, language="python", out=out)
        assert [json.loads(line) for line in out.read_text().splitlines()] == [
            {"grammar": "g0000", "input": 0, "steps": [{"step": "whole", "input": "a"}], "crash": None},
            {"grammar": "g0000", "input": 1, "steps": [{"step": "whole", "input": "x"}], "crash": None},
            {"grammar": "g0001", "input": 0, "steps": [{"step": "whole", "input": "b"}], "crash": None},
        ]

    def it_runs_each_case_through_the_implementation_in_the_language(corpus, run_case_function, tmp_path):
        run_corpus(corpus=corpus, implementation=tmp_path, language="typescript", out=tmp_path / "out.jsonl")
        assert run_case_function.call_args_list[0].args == ("typescript", tmp_path, 'root ::= "a"\n', "a")
