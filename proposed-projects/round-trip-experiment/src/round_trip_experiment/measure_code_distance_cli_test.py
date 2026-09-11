import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from round_trip_experiment.measure_code_distance_cli import cli

REPORT = {
    "language": "python",
    "a": "/data/reference/python",
    "b": "/data/run/ported_implementation",
    "file_count_a": 2,
    "file_count_b": 3,
    "token_count_a": 10,
    "token_count_b": 12,
    "char_count_a": 40,
    "char_count_b": 50,
    "token_levenshtein": 0.25,
    "token_levenshtein_raw": 0.5,
    "char_levenshtein": 0.4,
    "path_count_a": 4,
    "path_count_b": 5,
    "path_levenshtein": 0.2,
}
GIT_DIFF_REPORT = {
    "language": "python",
    "a": "/data/reference/python",
    "b": "/data/run/ported_implementation",
    "insertions": 120,
    "deletions": 80,
    "reference_lines": 400,
    "diff_ratio": 0.5,
    "similarity_pct": 66.7,
    "identical": 3,
    "modified": 5,
    "renamed": 1,
    "added": 2,
    "deleted": 4,
    "formatter_failures": [],
}


@pytest.fixture
def measure_function():
    with patch("round_trip_experiment.measure_code_distance_cli.measure_code_distance", autospec=True) as m:
        m.return_value = REPORT
        yield m


@pytest.fixture
def git_diff_function():
    with patch("round_trip_experiment.measure_code_distance_cli.measure_git_diff", autospec=True) as m:
        m.return_value = GIT_DIFF_REPORT
        yield m


@pytest.fixture
def a(tmp_path):
    directory = tmp_path / "a"
    directory.mkdir()
    return directory


@pytest.fixture
def b(tmp_path):
    directory = tmp_path / "b"
    directory.mkdir()
    return directory


def invoke(command, a, b, *args):
    return CliRunner().invoke(cli, [command, "--language", "python", "--a", str(a), "--b", str(b), *args])


def describe_levenshtein():
    def it_requires_a_language(a, b):
        result = CliRunner().invoke(cli, ["levenshtein", "--a", str(a), "--b", str(b)])
        assert result.exit_code != 0
        assert "--language" in result.output

    def it_rejects_an_unsupported_language(measure_function, a, b):
        result = CliRunner().invoke(cli, ["levenshtein", "--language", "rust", "--a", str(a), "--b", str(b)])
        assert result.exit_code != 0
        measure_function.assert_not_called()

    def it_requires_both_directories(measure_function, a):
        result = CliRunner().invoke(cli, ["levenshtein", "--language", "python", "--a", str(a)])
        assert result.exit_code != 0
        assert "--b" in result.output

    def it_rejects_a_directory_that_does_not_exist(measure_function, a, tmp_path):
        result = invoke("levenshtein", a, tmp_path / "nowhere")
        assert result.exit_code != 0
        measure_function.assert_not_called()

    def it_forwards_language_and_both_directories(measure_function, a, b):
        invoke("levenshtein", a, b)
        kwargs = measure_function.call_args.kwargs
        assert (kwargs["language"], kwargs["a"], kwargs["b"]) == ("python", a, b)

    def it_forwards_no_excludes_by_default(measure_function, a, b):
        invoke("levenshtein", a, b)
        assert measure_function.call_args.kwargs["exclude"] == []

    def it_forwards_every_exclude_in_order(measure_function, a, b):
        invoke("levenshtein", a, b, "--exclude", "*_test.py", "--exclude", "build")
        assert measure_function.call_args.kwargs["exclude"] == ["*_test.py", "build"]

    def it_echoes_the_report_as_json(measure_function, a, b):
        assert json.loads(invoke("levenshtein", a, b).output) == REPORT

    def it_exits_zero_on_success(measure_function, a, b):
        assert invoke("levenshtein", a, b).exit_code == 0

    def it_renders_errors_as_click_errors(measure_function, a, b):
        measure_function.side_effect = FileNotFoundError("no python source")
        result = invoke("levenshtein", a, b)
        assert result.exit_code != 0
        assert "no python source" in result.output


def describe_git_diff():
    def it_requires_a_language(a, b):
        result = CliRunner().invoke(cli, ["git-diff", "--a", str(a), "--b", str(b)])
        assert result.exit_code != 0
        assert "--language" in result.output

    def it_rejects_an_unsupported_language(git_diff_function, a, b):
        result = CliRunner().invoke(cli, ["git-diff", "--language", "rust", "--a", str(a), "--b", str(b)])
        assert result.exit_code != 0
        git_diff_function.assert_not_called()

    def it_rejects_a_directory_that_does_not_exist(git_diff_function, a, tmp_path):
        result = invoke("git-diff", a, tmp_path / "nowhere")
        assert result.exit_code != 0
        git_diff_function.assert_not_called()

    def it_forwards_language_and_both_directories(git_diff_function, a, b):
        invoke("git-diff", a, b)
        kwargs = git_diff_function.call_args.kwargs
        assert (kwargs["language"], kwargs["a"], kwargs["b"]) == ("python", a, b)

    def it_forwards_every_exclude_in_order(git_diff_function, a, b):
        invoke("git-diff", a, b, "--exclude", "*_test.py", "--exclude", "build")
        assert git_diff_function.call_args.kwargs["exclude"] == ["*_test.py", "build"]

    def it_echoes_the_report_as_json(git_diff_function, a, b):
        assert json.loads(invoke("git-diff", a, b).output) == GIT_DIFF_REPORT

    def it_exits_zero_on_success(git_diff_function, a, b):
        assert invoke("git-diff", a, b).exit_code == 0

    def it_renders_errors_as_click_errors(git_diff_function, a, b):
        git_diff_function.side_effect = FileNotFoundError("no python source")
        result = invoke("git-diff", a, b)
        assert result.exit_code != 0
        assert "no python source" in result.output

    def it_does_not_run_the_levenshtein_measure(measure_function, git_diff_function, a, b):
        invoke("git-diff", a, b)
        measure_function.assert_not_called()
