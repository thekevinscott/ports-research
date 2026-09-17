import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from gbnf_experiment.config import prepare_cache_key, settings

from execute_test_suite.cli import cli

REPORT = {
    "language": "python",
    "target": "/data/run/ported_implementation",
    "test_suite_directory": "/cache/.../tests/python",
    "total": 3,
    "passed": 3,
    "failed": 0,
    "errors": 0,
    "skipped": 0,
    "success": True,
}


@pytest.fixture
def execute_test_suite_function():
    with patch("execute_test_suite.cli.execute_test_suite", autospec=True) as m:
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

    def it_rejects_an_unsupported_language(execute_test_suite_function, target):
        result = CliRunner().invoke(
            cli, ["--language", "rust", "--target", str(target)]
        )
        assert result.exit_code != 0
        execute_test_suite_function.assert_not_called()

    def it_requires_a_target(execute_test_suite_function):
        result = CliRunner().invoke(cli, ["--language", "python"])
        assert result.exit_code != 0
        assert "--target" in result.output

    def it_rejects_a_target_that_does_not_exist(execute_test_suite_function, tmp_path):
        missing = tmp_path / "nowhere"
        result = invoke(missing)
        assert result.exit_code != 0
        execute_test_suite_function.assert_not_called()

    def it_resolves_a_relative_target_to_an_absolute_path(
        execute_test_suite_function, target, monkeypatch
    ):
        monkeypatch.chdir(target.parent)

        result = CliRunner().invoke(
            cli, ["--language", "python", "--target", f"./{target.name}"]
        )

        assert result.exit_code == 0
        assert execute_test_suite_function.call_args.kwargs["target"] == target

    def it_forwards_language_and_target(execute_test_suite_function, target):
        invoke(target)
        assert execute_test_suite_function.call_args.kwargs["language"] == "python"
        assert execute_test_suite_function.call_args.kwargs["target"] == target

    def it_forwards_the_real_prepare_cache_key_and_directory(
        execute_test_suite_function, target
    ):
        invoke(target)

        assert (
            execute_test_suite_function.call_args.kwargs["derivation_cache_key"]
            == prepare_cache_key
        )
        assert (
            execute_test_suite_function.call_args.kwargs["derivations_directory"]
            == settings.prepared_directory
        )

    def it_forwards_no_suite_by_default(execute_test_suite_function, target):
        invoke(target)
        assert execute_test_suite_function.call_args.kwargs["suite"] is None

    def it_forwards_the_suite(execute_test_suite_function, target):
        invoke(target, "--suite", "integration")
        assert execute_test_suite_function.call_args.kwargs["suite"] == "integration"

    def it_forwards_no_adapt_by_default(execute_test_suite_function, target):
        invoke(target)
        assert execute_test_suite_function.call_args.kwargs["adapt"] is False

    def it_forwards_adapt(execute_test_suite_function, target):
        invoke(target, "--adapt")
        assert execute_test_suite_function.call_args.kwargs["adapt"] is True

    def it_forwards_no_coverage_by_default(execute_test_suite_function, target):
        invoke(target)
        assert execute_test_suite_function.call_args.kwargs["coverage"] is False

    def it_forwards_coverage(execute_test_suite_function, target):
        invoke(target, "--coverage")
        assert execute_test_suite_function.call_args.kwargs["coverage"] is True

    def it_rejects_an_unknown_suite(execute_test_suite_function, target):
        result = invoke(target, "--suite", "smoke")
        assert result.exit_code != 0
        execute_test_suite_function.assert_not_called()

    def it_echoes_the_report_as_json(execute_test_suite_function, target):
        result = invoke(target)
        assert json.loads(result.output) == REPORT

    def it_exits_zero_on_success(execute_test_suite_function, target):
        result = invoke(target)
        assert result.exit_code == 0

    def it_exits_nonzero_on_failure(execute_test_suite_function, target):
        execute_test_suite_function.return_value = {**REPORT, "success": False}
        result = invoke(target)
        assert result.exit_code == 1

    def it_renders_errors_as_click_errors(execute_test_suite_function, target):
        execute_test_suite_function.side_effect = FileNotFoundError("no derivation")
        result = invoke(target)
        assert result.exit_code != 0
        assert "no derivation" in result.output
