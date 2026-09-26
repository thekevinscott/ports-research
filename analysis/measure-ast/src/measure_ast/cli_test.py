import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from measure_ast.cli import cli

REPORT = {
    "language": "python",
    "target": "/data/run/ported_implementation",
    "parsed_file_count": 2,
    "node_count": 18,
    "max_depth": 6,
    "function_count": 1,
    "mean_function_lines": 4.0,
    "max_function_lines": 4,
    "mean_cyclomatic": 2.0,
    "max_cyclomatic": 2,
}


@pytest.fixture
def measure_ast_function():
    with patch("measure_ast.cli.measure_ast", autospec=True) as m:
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

    def it_rejects_an_unsupported_language(measure_ast_function, target):
        result = CliRunner().invoke(cli, ["--language", "rust", "--target", str(target)])
        assert result.exit_code != 0
        measure_ast_function.assert_not_called()

    def it_requires_a_target(measure_ast_function):
        result = CliRunner().invoke(cli, ["--language", "python"])
        assert result.exit_code != 0
        assert "--target" in result.output

    def it_rejects_a_target_that_does_not_exist(measure_ast_function, tmp_path):
        result = invoke(tmp_path / "nowhere")
        assert result.exit_code != 0
        measure_ast_function.assert_not_called()

    def it_forwards_language_and_target(measure_ast_function, target):
        invoke(target)
        assert measure_ast_function.call_args.kwargs["language"] == "python"
        assert measure_ast_function.call_args.kwargs["target"] == target

    def it_forwards_no_excludes_by_default(measure_ast_function, target):
        invoke(target)
        assert measure_ast_function.call_args.kwargs["exclude"] == []

    def it_forwards_every_exclude_in_order(measure_ast_function, target):
        invoke(target, "--exclude", "*_test.py", "--exclude", "build")
        assert measure_ast_function.call_args.kwargs["exclude"] == ["*_test.py", "build"]

    def it_echoes_the_report_as_json(measure_ast_function, target):
        result = invoke(target)
        assert json.loads(result.output) == REPORT

    def it_exits_zero_on_success(measure_ast_function, target):
        result = invoke(target)
        assert result.exit_code == 0

    def it_renders_errors_as_click_errors(measure_ast_function, target):
        measure_ast_function.side_effect = FileNotFoundError("no python source")
        result = invoke(target)
        assert result.exit_code != 0
        assert "no python source" in result.output
