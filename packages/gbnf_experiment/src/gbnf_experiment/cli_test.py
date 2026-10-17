import json
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gbnf_experiment.cli import cli


API_KEY = "sk-ant-test"
SOURCE_LANGUAGE = ["--source-language", "javascript"]


def bank(manifest: dict | None = None, result: dict | None = None):
    """What run_gbnf_experiment leaves in the working folder."""

    def write(**_kwargs):
        Path("manifest.json").write_text(json.dumps({"exit_code": 0, **(manifest or {})}))
        if result is not None:
            Path("result.json").write_text(json.dumps(result))

    return write


@pytest.fixture(autouse=True)
def working_folder(tmp_path, monkeypatch):
    folder = tmp_path / "runs" / "models-effort" / "brave-otter"
    folder.mkdir(parents=True)
    monkeypatch.chdir(folder)
    return folder


@pytest.fixture
def gbnf_experiment():
    with patch("gbnf_experiment.cli.run_gbnf_experiment", autospec=True) as m:
        m.side_effect = bank(result={"is_error": False})
        yield m


@pytest.fixture(autouse=True)
def claude_agent():
    with patch("gbnf_experiment.cli.ClaudeAgent", autospec=True) as m:
        yield m


def invoke(argv: list[str]):
    return CliRunner().invoke(cli, argv)


def describe_cli():
    def it_runs_the_experiment(gbnf_experiment):
        result = invoke(SOURCE_LANGUAGE)
        assert result.exit_code == 0, result.output
        gbnf_experiment.assert_called_once()

    def it_runs_no_test_suite_unless_asked(gbnf_experiment, claude_agent, working_folder):
        invoke(SOURCE_LANGUAGE)
        gbnf_experiment.assert_called_once_with(
            agent=claude_agent.return_value,
            run_directory=working_folder,
            source_language="javascript",
            include_unit_tests=False,
            include_source_integration_tests=False,
            include_target_integration_tests=False,
            debug=False,
        )

    def it_requires_a_source_language(gbnf_experiment):
        result = invoke([])
        assert result.exit_code != 0
        assert "--source-language" in result.output
        gbnf_experiment.assert_not_called()

    def it_forwards_the_source_language(gbnf_experiment):
        invoke(["--source-language", "python"])
        assert gbnf_experiment.call_args.kwargs["source_language"] == "python"

    def it_rejects_an_unsupported_source_language(gbnf_experiment):
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
    def it_takes_each_test_inclusion_as_1(gbnf_experiment, flag):
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
    def it_takes_each_test_inclusion_as_0(gbnf_experiment, flag):
        invoke([*SOURCE_LANGUAGE, flag, "0"])
        assert gbnf_experiment.call_args.kwargs[flag.removeprefix("--").replace("-", "_")] is False

    @pytest.mark.parametrize("value", ["2", "true", "yes"])
    def it_rejects_a_test_inclusion_other_than_0_or_1(gbnf_experiment, value):
        result = invoke([*SOURCE_LANGUAGE, "--include-unit-tests", value])
        assert result.exit_code != 0
        gbnf_experiment.assert_not_called()

    @pytest.mark.parametrize("flag", ["--include-javascript-tests", "--include-python-tests"])
    def it_rejects_the_per_language_flags(gbnf_experiment, flag):
        result = invoke([*SOURCE_LANGUAGE, flag, "1"])
        assert result.exit_code != 0
        gbnf_experiment.assert_not_called()

    @pytest.mark.parametrize("option", ["--study", "--output"])
    def it_has_no_study_or_output_option(gbnf_experiment, option):
        result = invoke([*SOURCE_LANGUAGE, option, "x"])
        assert result.exit_code != 0
        gbnf_experiment.assert_not_called()

    def it_writes_into_the_working_folder(gbnf_experiment, working_folder):
        invoke(SOURCE_LANGUAGE)
        assert gbnf_experiment.call_args.kwargs["run_directory"] == working_folder

    def it_forwards_debug(gbnf_experiment):
        invoke([*SOURCE_LANGUAGE, "--debug"])
        assert gbnf_experiment.call_args.kwargs["debug"] is True

    def it_builds_a_claude_agent_on_the_default_model_and_effort(gbnf_experiment, claude_agent):
        invoke(SOURCE_LANGUAGE)
        claude_agent.assert_called_once_with(model="claude-opus-5", effort="high", api_key=None)

    def it_forwards_the_effort_to_the_agent(gbnf_experiment, claude_agent):
        invoke([*SOURCE_LANGUAGE, "--effort", "max"])
        assert claude_agent.call_args.kwargs["effort"] == "max"

    def it_leaves_an_unknown_effort_to_the_agent(gbnf_experiment, claude_agent):
        """Effort levels differ per agent, so the parser cannot know them at import time."""
        invoke([*SOURCE_LANGUAGE, "--effort", "turbo"])
        assert claude_agent.call_args.kwargs["effort"] == "turbo"

    def it_has_no_agent_option(gbnf_experiment):
        result = invoke([*SOURCE_LANGUAGE, "--agent", "claude"])
        assert result.exit_code != 0
        gbnf_experiment.assert_not_called()

    def it_names_the_pinned_model_in_the_help(gbnf_experiment):
        """--model is free text, so the help is the only place the pin is visible."""
        assert "claude-opus-5" in invoke(["--help"]).output

    def it_forwards_the_model_to_the_agent(gbnf_experiment, claude_agent):
        invoke([*SOURCE_LANGUAGE, "--model", "claude-sonnet-4-5"])
        assert claude_agent.call_args.kwargs["model"] == "claude-sonnet-4-5"

    def it_renders_sdk_errors_as_click_errors(gbnf_experiment):
        gbnf_experiment.side_effect = RuntimeError("no results report")
        result = invoke(SOURCE_LANGUAGE)
        assert result.exit_code == 1
        assert "no results report" in result.output


@pytest.fixture(autouse=True)
def config():
    with patch("gbnf_experiment.cli.config", autospec=True) as m:
        m.API_KEY = ""
        yield m


def describe_auth():
    def it_runs_on_the_subscription_when_the_configured_key_is_blank(gbnf_experiment, claude_agent, config):
        invoke(SOURCE_LANGUAGE)
        assert claude_agent.call_args.kwargs["api_key"] is None

    def it_never_passes_the_host_api_key(gbnf_experiment, claude_agent, config, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", API_KEY)
        result = invoke(SOURCE_LANGUAGE)
        assert result.exit_code == 0, result.output
        assert claude_agent.call_args.kwargs["api_key"] is None

    def it_bills_the_configured_key(gbnf_experiment, claude_agent, config):
        config.API_KEY = API_KEY
        invoke(SOURCE_LANGUAGE)
        assert claude_agent.call_args.kwargs["api_key"] == API_KEY

    @pytest.mark.parametrize("option", ["--auth", "--api-key"])
    def it_has_no_auth_option(gbnf_experiment, option):
        result = invoke([*SOURCE_LANGUAGE, option, "subscription"])
        assert result.exit_code != 0
        gbnf_experiment.assert_not_called()


def describe_the_exit_code():
    def it_exits_zero_on_a_clean_run(gbnf_experiment):
        assert invoke(SOURCE_LANGUAGE).exit_code == 0

    def it_exits_non_zero_when_the_agent_exits_non_zero(gbnf_experiment):
        gbnf_experiment.side_effect = bank(manifest={"exit_code": 137})
        assert invoke(SOURCE_LANGUAGE).exit_code != 0

    def it_exits_non_zero_when_the_result_is_an_error(gbnf_experiment):
        """claude can exit 0 with is_error set; that run must not count toward repeats."""
        gbnf_experiment.side_effect = bank(result={"is_error": True})
        assert invoke(SOURCE_LANGUAGE).exit_code != 0

    def it_exits_non_zero_when_the_manifest_carries_an_error(gbnf_experiment):
        gbnf_experiment.side_effect = bank(manifest={"error": "the container died"}, result={"is_error": False})
        assert invoke(SOURCE_LANGUAGE).exit_code != 0
