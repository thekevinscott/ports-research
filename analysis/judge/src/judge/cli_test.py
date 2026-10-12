from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from judge.cli import cli


@pytest.fixture
def run_judge_function():
    with patch("judge.cli.run_judge", autospec=True) as m:
        yield m


@pytest.fixture
def report_function():
    with patch("judge.cli.report", autospec=True) as m:
        m.return_value = "the report\n"
        yield m


def invoke(*args):
    return CliRunner().invoke(cli, [str(arg) for arg in args])


def describe_run():
    def it_forwards_every_option(run_judge_function, tmp_path):
        result = invoke("run", "--rubric", "transcript", "--runs", tmp_path, "--runs", tmp_path, "--out", tmp_path / "o", "--limit", 4, "--model", "m", "--effort", "high", "-k", 3, "--replicate-fraction", 0.1)
        assert result.exit_code == 0, result.output
        assert run_judge_function.call_args.kwargs == {
            "rubric": "transcript",
            "runs": [tmp_path.resolve(), tmp_path.resolve()],
            "out": (tmp_path / "o").resolve(),
            "limit": 4,
            "model": "m",
            "effort": "high",
            "concurrency": 3,
            "replicate_fraction": 0.1,
        }

    def it_defaults_to_opus_at_max_effort_two_at_a_time_and_no_limit(run_judge_function, tmp_path):
        invoke("run", "--rubric", "code", "--runs", tmp_path, "--out", tmp_path / "o")
        kwargs = run_judge_function.call_args.kwargs
        assert (kwargs["model"], kwargs["effort"], kwargs["concurrency"], kwargs["limit"], kwargs["replicate_fraction"]) == ("claude-opus-5-5", "max", 2, None, 0)

    def it_rejects_a_replicate_fraction_outside_zero_to_one(run_judge_function, tmp_path):
        result = invoke("run", "--rubric", "code", "--runs", tmp_path, "--out", tmp_path / "o", "--replicate-fraction", 1.5)
        assert result.exit_code != 0
        run_judge_function.assert_not_called()

    def it_rejects_an_unknown_rubric(run_judge_function, tmp_path):
        result = invoke("run", "--rubric", "vibes", "--runs", tmp_path, "--out", tmp_path / "o")
        assert result.exit_code != 0
        run_judge_function.assert_not_called()

    def it_renders_a_failed_item_as_a_click_error(run_judge_function, tmp_path):
        run_judge_function.side_effect = RuntimeError("item-0000000b: overloaded")
        result = invoke("run", "--rubric", "code", "--runs", tmp_path, "--out", tmp_path / "o")
        assert result.exit_code != 0
        assert "item-0000000b: overloaded" in result.output


def describe_report():
    def it_prints_the_report(report_function, tmp_path):
        result = invoke("report", "--out", tmp_path)
        assert result.exit_code == 0, result.output
        assert result.output == "the report\n"
        report_function.assert_called_once_with(Path(tmp_path).resolve())
