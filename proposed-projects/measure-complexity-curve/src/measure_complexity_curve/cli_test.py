import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from measure_complexity_curve.cli import cli

REPORT = {
    "language": "python",
    "target": "/data/run/ported_implementation",
    "curve": [{"size": 4, "seconds": 0.001}],
    "log_log_slope": 1.0,
}


@pytest.fixture
def run_complexity_curve_function():
    with patch("measure_complexity_curve.cli.run_complexity_curve", autospec=True) as m:
        m.return_value = REPORT
        yield m


@pytest.fixture
def target(tmp_path):
    directory = tmp_path / "ported_implementation"
    directory.mkdir()
    return directory


def invoke(target, *args):
    return CliRunner().invoke(cli, ["--language", "python", "--target", str(target), *args])


def describe_cli():
    def it_requires_a_language(target):
        result = CliRunner().invoke(cli, ["--target", str(target)])
        assert result.exit_code != 0
        assert "--language" in result.output

    def it_rejects_an_unsupported_language(run_complexity_curve_function, target):
        result = CliRunner().invoke(cli, ["--language", "rust", "--target", str(target)])
        assert result.exit_code != 0
        run_complexity_curve_function.assert_not_called()

    def it_requires_a_target(run_complexity_curve_function):
        result = CliRunner().invoke(cli, ["--language", "python"])
        assert result.exit_code != 0
        assert "--target" in result.output

    def it_rejects_a_target_that_does_not_exist(run_complexity_curve_function, tmp_path):
        missing = tmp_path / "nowhere"
        result = invoke(missing)
        assert result.exit_code != 0
        run_complexity_curve_function.assert_not_called()

    def it_forwards_language_and_target(run_complexity_curve_function, target):
        invoke(target)
        assert run_complexity_curve_function.call_args.kwargs["language"] == "python"
        assert run_complexity_curve_function.call_args.kwargs["target"] == target

    def it_forwards_default_sweep_parameters(run_complexity_curve_function, target):
        invoke(target)
        kwargs = run_complexity_curve_function.call_args.kwargs
        assert kwargs["max_size"] == 128
        assert kwargs["steps"] == 6
        assert kwargs["nesting_depth"] == 1
        assert kwargs["alternation_width"] == 3
        assert kwargs["iterations"] == 25
        assert kwargs["seed"] == 0

    def it_forwards_overridden_sweep_parameters(run_complexity_curve_function, target):
        invoke(
            target,
            "--max-size", "64",
            "--steps", "3",
            "--nesting-depth", "0",
            "--alternation-width", "2",
            "--iterations", "5",
            "--seed", "9",
        )
        kwargs = run_complexity_curve_function.call_args.kwargs
        assert kwargs["max_size"] == 64
        assert kwargs["steps"] == 3
        assert kwargs["nesting_depth"] == 0
        assert kwargs["alternation_width"] == 2
        assert kwargs["iterations"] == 5
        assert kwargs["seed"] == 9

    def it_echoes_the_report_as_json(run_complexity_curve_function, target):
        result = invoke(target)
        assert json.loads(result.output) == REPORT

    def it_exits_zero_on_success(run_complexity_curve_function, target):
        result = invoke(target)
        assert result.exit_code == 0

    def it_renders_errors_as_click_errors(run_complexity_curve_function, target):
        run_complexity_curve_function.side_effect = RecursionError("boom")
        result = invoke(target)
        assert result.exit_code != 0
        assert "boom" in result.output
