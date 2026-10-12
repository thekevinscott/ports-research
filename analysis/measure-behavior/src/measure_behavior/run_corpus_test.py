import json
from unittest.mock import patch

import pytest

from measure_behavior.run_corpus import run_corpus


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
def run_pair_function():
    with patch("measure_behavior.run_corpus.run_pair", autospec=True) as m:
        m.side_effect = lambda language, implementation, grammar, text: {
            "outcome": "accept" if text in grammar else "reject",
            "error": None,
        }
        yield m


def describe_run_corpus():
    def it_writes_one_record_per_pair_in_id_order(corpus, run_pair_function, tmp_path):
        out = tmp_path / "out.jsonl"
        run_corpus(corpus=corpus, implementation=tmp_path, language="python", out=out)
        assert [json.loads(line) for line in out.read_text().splitlines()] == [
            {"grammar": "g0000", "input": 0, "outcome": "accept", "error": None},
            {"grammar": "g0000", "input": 1, "outcome": "reject", "error": None},
            {"grammar": "g0001", "input": 0, "outcome": "accept", "error": None},
        ]

    def it_runs_each_pair_through_the_implementation_in_the_language(corpus, run_pair_function, tmp_path):
        run_corpus(corpus=corpus, implementation=tmp_path, language="typescript", out=tmp_path / "out.jsonl")
        assert run_pair_function.call_args_list[0].args == ("typescript", tmp_path, 'root ::= "a"\n', "a")
