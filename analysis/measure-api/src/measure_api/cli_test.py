import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from measure_api.cli import cli

REPORT = {"cases": 1, "agreements": 1, "agreement_rate": 1.0, "confusion": {}}


@pytest.fixture
def generate_corpus_function():
    with patch("measure_api.cli.generate_corpus", autospec=True) as m:
        yield m


@pytest.fixture
def run_corpus_function():
    with patch("measure_api.cli.run_corpus", autospec=True) as m:
        yield m


@pytest.fixture
def compare_cases_function():
    with patch("measure_api.cli.compare_cases", autospec=True) as m:
        m.return_value = REPORT
        yield m


def invoke(*args):
    return CliRunner().invoke(cli, [str(arg) for arg in args])


def describe_generate():
    def it_forwards_out_seed_and_count(generate_corpus_function, tmp_path):
        result = invoke("generate", "--out", tmp_path / "c", "--seed", 4, "--count", 9)
        assert result.exit_code == 0, result.output
        assert generate_corpus_function.call_args.kwargs == {"out": (tmp_path / "c").resolve(), "seed": 4, "count": 9}

    @pytest.mark.parametrize("missing", ["--out", "--seed", "--count"])
    def it_requires_every_option(generate_corpus_function, tmp_path, missing):
        options = {"--out": tmp_path / "c", "--seed": 4, "--count": 9}
        result = invoke("generate", *[x for k, v in options.items() if k != missing for x in (k, v)])
        assert result.exit_code != 0
        assert missing in result.output


def describe_run():
    def it_forwards_corpus_implementation_language_and_out(run_corpus_function, tmp_path):
        result = invoke("run", "--corpus", tmp_path, "--implementation", tmp_path, "--language", "typescript", "--out", tmp_path / "o.jsonl")
        assert result.exit_code == 0, result.output
        assert run_corpus_function.call_args.kwargs == {
            "corpus": tmp_path.resolve(),
            "implementation": tmp_path.resolve(),
            "language": "typescript",
            "out": (tmp_path / "o.jsonl").resolve(),
        }

    def it_rejects_an_unsupported_language(run_corpus_function, tmp_path):
        result = invoke("run", "--corpus", tmp_path, "--implementation", tmp_path, "--language", "rust", "--out", tmp_path / "o")
        assert result.exit_code != 0
        run_corpus_function.assert_not_called()

    def it_rejects_a_corpus_that_does_not_exist(run_corpus_function, tmp_path):
        result = invoke("run", "--corpus", tmp_path / "nowhere", "--implementation", tmp_path, "--language", "python", "--out", tmp_path / "o")
        assert result.exit_code != 0
        run_corpus_function.assert_not_called()


def describe_compare():
    def it_writes_the_report_to_out(compare_cases_function, tmp_path):
        (tmp_path / "r.jsonl").write_text("")
        result = invoke("compare", "--reference", tmp_path / "r.jsonl", "--port", tmp_path / "r.jsonl", "--out", tmp_path / "c.json")
        assert result.exit_code == 0, result.output
        assert json.loads((tmp_path / "c.json").read_text()) == REPORT

    def it_renders_errors_as_click_errors(compare_cases_function, tmp_path):
        (tmp_path / "r.jsonl").write_text("")
        compare_cases_function.side_effect = ValueError("different cases")
        result = invoke("compare", "--reference", tmp_path / "r.jsonl", "--port", tmp_path / "r.jsonl", "--out", tmp_path / "c.json")
        assert result.exit_code != 0
        assert "different cases" in result.output
