import json
from unittest.mock import call, patch

import pytest
from click.testing import CliRunner

from exercise_api.cli import cli

CASES = [{"grammar": 'root ::= "a"', "input": "a"}]
REPORT = {"language": "python", "reference": "/reference", "cases": 1, "targets": {}}


@pytest.fixture
def exercise_api_function():
    with patch("exercise_api.cli.exercise_api", autospec=True) as m:
        m.return_value = REPORT
        yield m


@pytest.fixture
def read_cases_function():
    with patch("exercise_api.cli.read_cases", autospec=True) as m:
        m.return_value = CASES
        yield m


@pytest.fixture
def generate_cases_function():
    with patch("exercise_api.cli.generate_cases", autospec=True) as m:
        m.return_value = CASES
        yield m


@pytest.fixture
def fixture_cases_function():
    with patch("exercise_api.cli.fixture_cases", autospec=True) as m:
        m.return_value = CASES
        yield m


@pytest.fixture
def ladder_cases_function():
    with patch("exercise_api.cli.ladder_cases", autospec=True) as m:
        m.return_value = CASES
        yield m


@pytest.fixture
def write_cases_function():
    with patch("exercise_api.cli.write_cases", autospec=True) as m:
        yield m


@pytest.fixture
def write_report_function():
    with patch("exercise_api.cli.write_report", autospec=True) as m:
        yield m


@pytest.fixture
def reference(tmp_path):
    directory = tmp_path / "reference"
    directory.mkdir()
    return directory


@pytest.fixture
def target(tmp_path):
    directory = tmp_path / "target"
    directory.mkdir()
    return directory


@pytest.fixture
def cases_file(tmp_path):
    path = tmp_path / "cases.jsonl"
    path.write_text("")
    return path


def invoke(reference, target, cases_file, *args):
    return CliRunner().invoke(
        cli,
        ["--language", "python", "--reference", str(reference), "--target", str(target), "--cases", str(cases_file), *args],
    )


def describe_cli():
    def it_requires_a_language(exercise_api_function, read_cases_function, reference, target, cases_file):
        result = CliRunner().invoke(cli, ["--reference", str(reference), "--target", str(target), "--cases", str(cases_file)])
        assert result.exit_code != 0
        exercise_api_function.assert_not_called()

    def it_rejects_an_unsupported_language(exercise_api_function, read_cases_function, reference, target, cases_file):
        result = CliRunner().invoke(cli, ["--language", "rust", "--reference", str(reference), "--target", str(target), "--cases", str(cases_file)])
        assert result.exit_code != 0
        exercise_api_function.assert_not_called()

    def it_requires_at_least_one_target(exercise_api_function, read_cases_function, reference, cases_file):
        result = CliRunner().invoke(cli, ["--language", "python", "--reference", str(reference), "--cases", str(cases_file)])
        assert result.exit_code != 0
        exercise_api_function.assert_not_called()

    def it_rejects_a_reference_that_does_not_exist(exercise_api_function, read_cases_function, tmp_path, target, cases_file):
        result = invoke(tmp_path / "nowhere", target, cases_file)
        assert result.exit_code != 0
        exercise_api_function.assert_not_called()

    def it_reads_the_cases_file(exercise_api_function, read_cases_function, reference, target, cases_file):
        invoke(reference, target, cases_file)
        assert read_cases_function.call_args.args[0] == cases_file

    def it_forwards_language_reference_targets_and_cases(exercise_api_function, read_cases_function, reference, target, cases_file):
        invoke(reference, target, cases_file)
        kwargs = exercise_api_function.call_args.kwargs
        assert kwargs["language"] == "python"
        assert kwargs["reference"] == reference
        assert kwargs["targets"] == [target]
        assert kwargs["cases"] == CASES

    def it_forwards_every_target_in_order(exercise_api_function, read_cases_function, reference, target, cases_file, tmp_path):
        other = tmp_path / "other"
        other.mkdir()
        invoke(reference, target, cases_file, "--target", str(other))
        assert exercise_api_function.call_args.kwargs["targets"] == [target, other]

    def it_does_not_adapt_by_default(exercise_api_function, read_cases_function, reference, target, cases_file):
        invoke(reference, target, cases_file)
        assert exercise_api_function.call_args.kwargs["adapt"] is False

    def it_forwards_adapt(exercise_api_function, read_cases_function, reference, target, cases_file):
        invoke(reference, target, cases_file, "--adapt")
        assert exercise_api_function.call_args.kwargs["adapt"] is True

    def it_forwards_the_timeout(exercise_api_function, read_cases_function, reference, target, cases_file):
        invoke(reference, target, cases_file, "--timeout", "12")
        assert exercise_api_function.call_args.kwargs["timeout"] == 12

    def it_caps_a_python_driver_at_4_gib_by_default(exercise_api_function, read_cases_function, reference, target, cases_file):
        invoke(reference, target, cases_file)
        assert exercise_api_function.call_args.kwargs["memory_limit_bytes"] == 4 * 1024**3

    def it_caps_a_typescript_driver_at_28_gib_by_default(exercise_api_function, read_cases_function, reference, target, cases_file):
        CliRunner().invoke(cli, ["--language", "typescript", "--reference", str(reference), "--target", str(target), "--cases", str(cases_file)])
        assert exercise_api_function.call_args.kwargs["memory_limit_bytes"] == 28 * 1024**3

    def it_forwards_the_memory_limit(exercise_api_function, read_cases_function, reference, target, cases_file):
        invoke(reference, target, cases_file, "--memory-limit-bytes", "2147483648")
        assert exercise_api_function.call_args.kwargs["memory_limit_bytes"] == 2147483648

    def it_measures_each_case_once_without_warm_ups_by_default(exercise_api_function, read_cases_function, reference, target, cases_file):
        invoke(reference, target, cases_file)
        assert exercise_api_function.call_args.kwargs["repeat"] == 1
        assert exercise_api_function.call_args.kwargs["warmup"] == 0

    def it_forwards_repeat_and_warmup(exercise_api_function, read_cases_function, reference, target, cases_file):
        invoke(reference, target, cases_file, "--repeat", "30", "--warmup", "3")
        assert exercise_api_function.call_args.kwargs["repeat"] == 30
        assert exercise_api_function.call_args.kwargs["warmup"] == 3

    def it_echoes_the_report_as_json(exercise_api_function, read_cases_function, reference, target, cases_file):
        result = invoke(reference, target, cases_file)
        assert result.exit_code == 0, result.output
        assert json.loads(result.output) == REPORT

    def it_writes_nothing_without_out(exercise_api_function, read_cases_function, write_report_function, reference, target, cases_file):
        exercise_api_function.side_effect = lambda **kwargs: kwargs["checkpoint"](REPORT) or REPORT
        result = invoke(reference, target, cases_file)
        assert result.exit_code == 0, result.output
        write_report_function.assert_not_called()

    def it_writes_each_checkpoint_to_the_partial_path_then_the_report_to_out(exercise_api_function, read_cases_function, write_report_function, reference, target, cases_file, tmp_path):
        out = tmp_path / "report.json"
        exercise_api_function.side_effect = lambda **kwargs: kwargs["checkpoint"](REPORT) or REPORT
        result = invoke(reference, target, cases_file, "--out", str(out))
        assert result.exit_code == 0, result.output
        assert write_report_function.call_args_list == [call(tmp_path / "report.partial.json", REPORT), call(out, REPORT)]

    def it_removes_the_partial_once_the_report_is_written(exercise_api_function, read_cases_function, write_report_function, reference, target, cases_file, tmp_path):
        out, partial = tmp_path / "report.json", tmp_path / "report.partial.json"
        partial.write_text("{}")
        invoke(reference, target, cases_file, "--out", str(out))
        assert not partial.exists()

    def it_keeps_the_partial_when_the_run_dies_after_a_checkpoint(exercise_api_function, read_cases_function, write_report_function, reference, target, cases_file, tmp_path):
        out = tmp_path / "report.json"

        def checkpoint_then_die(**kwargs):
            kwargs["checkpoint"](REPORT)
            raise RuntimeError("killed")

        exercise_api_function.side_effect = checkpoint_then_die
        result = invoke(reference, target, cases_file, "--out", str(out))
        assert result.exit_code != 0
        assert write_report_function.call_args_list == [call(tmp_path / "report.partial.json", REPORT)]

    def it_renders_errors_as_click_errors(exercise_api_function, read_cases_function, reference, target, cases_file):
        exercise_api_function.side_effect = RuntimeError("driver produced no output")
        result = invoke(reference, target, cases_file)
        assert result.exit_code != 0
        assert "driver produced no output" in result.output


def describe_generate():
    def it_forwards_seed_and_count_and_writes_the_cases(generate_cases_function, write_cases_function, tmp_path):
        out = tmp_path / "cases.jsonl"
        result = CliRunner().invoke(cli, ["generate", "--seed", "4", "--count", "9", "--out", str(out)])
        assert result.exit_code == 0, result.output
        assert generate_cases_function.call_args.kwargs == {"seed": 4, "count": 9}
        assert write_cases_function.call_args.args == (CASES, out)

    def it_requires_an_out_path(generate_cases_function, write_cases_function):
        result = CliRunner().invoke(cli, ["generate", "--seed", "4", "--count", "9"])
        assert result.exit_code != 0
        write_cases_function.assert_not_called()


def describe_fixtures():
    def it_reads_the_grammars_directory_and_writes_the_cases(fixture_cases_function, write_cases_function, tmp_path):
        grammars = tmp_path / "grammars"
        grammars.mkdir()
        out = tmp_path / "cases.jsonl"
        result = CliRunner().invoke(cli, ["fixtures", "--grammars", str(grammars), "--out", str(out)])
        assert result.exit_code == 0, result.output
        assert fixture_cases_function.call_args.args[0] == grammars
        assert write_cases_function.call_args.args == (CASES, out)


def describe_ladder():
    def it_reads_the_grammars_directory_and_writes_the_ladder(ladder_cases_function, write_cases_function, tmp_path):
        grammars = tmp_path / "grammars"
        grammars.mkdir()
        out = tmp_path / "ladder.jsonl"
        result = CliRunner().invoke(cli, ["ladder", "--grammars", str(grammars), "--out", str(out)])
        assert result.exit_code == 0, result.output
        assert ladder_cases_function.call_args.args[0] == grammars
        assert write_cases_function.call_args.args == (CASES, out)
