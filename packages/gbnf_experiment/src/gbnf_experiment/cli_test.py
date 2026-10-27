import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gbnf_experiment.cli import cli


API_KEY = "sk-ant-test"
SOURCE_LANGUAGE = ["--source-language", "javascript"]


def bank(*, run_directory, **_kwargs):
    """What run_gbnf_experiment leaves in the run folder."""
    (run_directory / "manifest.json").write_text(json.dumps({"exit_code": 0}))


@pytest.fixture(autouse=True)
def working_folder(tmp_path, monkeypatch):
    folder = tmp_path / "elsewhere"
    folder.mkdir()
    monkeypatch.chdir(folder)
    return folder


@pytest.fixture
def output(tmp_path):
    folder = tmp_path / "runs" / "models-effort" / "brave-otter"
    folder.mkdir(parents=True)
    return folder


@pytest.fixture
def gbnf_experiment():
    with patch("gbnf_experiment.cli.run_gbnf_experiment", autospec=True) as m:
        m.side_effect = bank
        yield m


@pytest.fixture(autouse=True)
def claude_agent():
    with patch("gbnf_experiment.cli.ClaudeAgent", autospec=True) as m:
        yield m


@pytest.fixture
def invoke(output):
    def run(argv: list[str], *, with_output=True):
        return CliRunner().invoke(cli, [*argv, "--output", str(output)] if with_output else argv)

    return run


def describe_cli():
    def it_runs_the_experiment(gbnf_experiment, invoke):
        result = invoke(SOURCE_LANGUAGE)
        assert result.exit_code == 0, result.output
        gbnf_experiment.assert_called_once()

    def it_runs_no_test_suite_unless_asked(gbnf_experiment, claude_agent, output, invoke):
        invoke(SOURCE_LANGUAGE)
        gbnf_experiment.assert_called_once_with(
            agent=claude_agent.return_value,
            run_directory=output,
            source_language="javascript",
            include_unit_tests=False,
            include_source_integration_tests=False,
            include_target_integration_tests=False,
            debug=False,
        )

    def it_requires_a_source_language(gbnf_experiment, invoke):
        result = invoke([])
        assert result.exit_code != 0
        assert "--source-language" in result.output
        gbnf_experiment.assert_not_called()

    def it_forwards_the_source_language(gbnf_experiment, invoke):
        invoke(["--source-language", "python"])
        assert gbnf_experiment.call_args.kwargs["source_language"] == "python"

    def it_rejects_an_unsupported_source_language(gbnf_experiment, invoke):
        result = invoke(["--source-language", "rust"])
        assert result.exit_code != 0
        gbnf_experiment.assert_not_called()

    @pytest.mark.parametrize(
        "flag",
        [
            "--include-unit-tests",
            "--include-source-integration-tests",
            "--include-target-integration-tests",
        ],
    )
    def it_takes_each_test_inclusion_as_1(gbnf_experiment, flag, invoke):
        invoke([*SOURCE_LANGUAGE, flag, "1"])
        kwargs = gbnf_experiment.call_args.kwargs
        name = flag.removeprefix("--").replace("-", "_")
        assert kwargs[name] is True
        assert [key for key, value in kwargs.items() if value is True] == [name]

    @pytest.mark.parametrize(
        "flag",
        [
            "--include-unit-tests",
            "--include-source-integration-tests",
            "--include-target-integration-tests",
        ],
    )
    def it_takes_each_test_inclusion_as_0(gbnf_experiment, flag, invoke):
        invoke([*SOURCE_LANGUAGE, flag, "0"])
        assert gbnf_experiment.call_args.kwargs[flag.removeprefix("--").replace("-", "_")] is False

    @pytest.mark.parametrize("value", ["2", "true", "yes"])
    def it_rejects_a_test_inclusion_other_than_0_or_1(gbnf_experiment, value, invoke):
        result = invoke([*SOURCE_LANGUAGE, "--include-unit-tests", value])
        assert result.exit_code != 0
        gbnf_experiment.assert_not_called()

    @pytest.mark.parametrize("flag", ["--include-javascript-tests", "--include-python-tests"])
    def it_rejects_the_per_language_flags(gbnf_experiment, flag, invoke):
        result = invoke([*SOURCE_LANGUAGE, flag, "1"])
        assert result.exit_code != 0
        gbnf_experiment.assert_not_called()

    def it_has_no_study_option(gbnf_experiment, invoke):
        result = invoke([*SOURCE_LANGUAGE, "--study", "x"])
        assert result.exit_code != 0
        gbnf_experiment.assert_not_called()

    def it_requires_an_output(gbnf_experiment, invoke):
        result = invoke(SOURCE_LANGUAGE, with_output=False)
        assert result.exit_code != 0
        assert "--output" in result.output
        gbnf_experiment.assert_not_called()

    def it_writes_into_the_output_not_the_working_folder(gbnf_experiment, output, working_folder, invoke):
        assert invoke(SOURCE_LANGUAGE).exit_code == 0
        assert gbnf_experiment.call_args.kwargs["run_directory"] == output
        assert (output / "manifest.json").is_file()
        assert list(working_folder.iterdir()) == []

    def it_creates_a_missing_output(gbnf_experiment, tmp_path):
        missing = tmp_path / "runs" / "tests-configuration" / "calm-heron"
        result = CliRunner().invoke(cli, [*SOURCE_LANGUAGE, "--output", str(missing)])
        assert result.exit_code == 0, result.output
        assert (missing / "manifest.json").is_file()
        assert list(missing.parent.iterdir()) == [missing]

    def it_resolves_a_relative_output_against_the_working_folder(gbnf_experiment, working_folder):
        result = CliRunner().invoke(cli, [*SOURCE_LANGUAGE, "--output", "."])
        assert result.exit_code == 0, result.output
        assert gbnf_experiment.call_args.kwargs["run_directory"] == working_folder

    def it_forwards_debug(gbnf_experiment, invoke):
        invoke([*SOURCE_LANGUAGE, "--debug"])
        assert gbnf_experiment.call_args.kwargs["debug"] is True

    def it_builds_a_claude_agent_on_the_default_model_and_effort(gbnf_experiment, claude_agent, invoke):
        invoke(SOURCE_LANGUAGE)
        claude_agent.assert_called_once_with(model="claude-opus-5", effort="high", api_key=None)

    def it_forwards_the_effort_to_the_agent(gbnf_experiment, claude_agent, invoke):
        invoke([*SOURCE_LANGUAGE, "--effort", "max"])
        assert claude_agent.call_args.kwargs["effort"] == "max"

    def it_leaves_an_unknown_effort_to_the_agent(gbnf_experiment, claude_agent, invoke):
        """Effort levels differ per agent, so the parser cannot know them at import time."""
        invoke([*SOURCE_LANGUAGE, "--effort", "turbo"])
        assert claude_agent.call_args.kwargs["effort"] == "turbo"

    def it_has_no_agent_option(gbnf_experiment, invoke):
        result = invoke([*SOURCE_LANGUAGE, "--agent", "claude"])
        assert result.exit_code != 0
        gbnf_experiment.assert_not_called()

    def it_names_the_pinned_model_in_the_help(gbnf_experiment, invoke):
        """--model is free text, so the help is the only place the pin is visible."""
        assert "claude-opus-5" in invoke(["--help"]).output

    def it_forwards_the_model_to_the_agent(gbnf_experiment, claude_agent, invoke):
        invoke([*SOURCE_LANGUAGE, "--model", "claude-sonnet-4-5"])
        assert claude_agent.call_args.kwargs["model"] == "claude-sonnet-4-5"



@pytest.fixture(autouse=True)
def config(tmp_path):
    with patch("gbnf_experiment.cli.config", autospec=True) as m:
        m.REPO_ROOT = tmp_path
        yield m


def describe_auth():
    @pytest.mark.parametrize("auth_option", [[], ["--auth", "subscription"]])
    def it_runs_on_the_subscription_without_reading_env(gbnf_experiment, claude_agent, config, invoke, auth_option):
        (config.REPO_ROOT / ".env").write_text(f"ANTHROPIC_API_KEY={API_KEY}\n")
        with patch("gbnf_experiment.cli.dotenv_values", create=True) as read_env:
            result = invoke([*SOURCE_LANGUAGE, *auth_option])
        assert result.exit_code == 0, result.output
        read_env.assert_not_called()
        assert claude_agent.call_args.kwargs["api_key"] is None
        assert "*** auth: subscription ***" in result.output
        assert API_KEY not in result.output

    def it_never_passes_the_host_api_key(gbnf_experiment, claude_agent, config, monkeypatch, invoke):
        monkeypatch.setenv("ANTHROPIC_API_KEY", API_KEY)
        result = invoke(SOURCE_LANGUAGE)
        assert result.exit_code == 0, result.output
        assert claude_agent.call_args.kwargs["api_key"] is None

    def it_bills_the_key_from_the_repo_env(gbnf_experiment, claude_agent, config, invoke):
        (config.REPO_ROOT / ".env").write_text(f"ANTHROPIC_API_KEY={API_KEY}\n")
        result = invoke([*SOURCE_LANGUAGE, "--auth", "api"])
        assert result.exit_code == 0, result.output
        assert claude_agent.call_args.kwargs["api_key"] == API_KEY
        assert "*** auth: api ***" in result.output
        assert API_KEY not in result.output

    @pytest.mark.parametrize("contents", [None, "OTHER=value\n", "ANTHROPIC_API_KEY=\n", 'ANTHROPIC_API_KEY="   "\n'])
    def it_rejects_api_mode_without_a_key(gbnf_experiment, claude_agent, config, monkeypatch, invoke, contents):
        monkeypatch.setenv("ANTHROPIC_API_KEY", API_KEY)
        if contents is not None:
            (config.REPO_ROOT / ".env").write_text(contents)
        result = invoke([*SOURCE_LANGUAGE, "--auth", "api"])
        assert result.exit_code != 0
        assert "ANTHROPIC_API_KEY" in result.output
        claude_agent.assert_not_called()
        gbnf_experiment.assert_not_called()

    def it_rejects_an_unknown_auth_mode(gbnf_experiment, invoke):
        result = invoke([*SOURCE_LANGUAGE, "--auth", "other"])
        assert result.exit_code != 0
        gbnf_experiment.assert_not_called()


def describe_the_exit_code():
    def it_exits_zero_on_a_clean_run(gbnf_experiment, invoke):
        assert invoke(SOURCE_LANGUAGE).exit_code == 0

    def it_exits_one_with_the_run_s_exception_uncaught(gbnf_experiment, invoke):
        died = RuntimeError("API Error: 429 rate limited")
        gbnf_experiment.side_effect = died
        result = invoke(SOURCE_LANGUAGE)
        assert result.exit_code == 1
        assert result.exception is died
