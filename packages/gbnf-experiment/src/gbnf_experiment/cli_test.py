from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gbnf_experiment.cli import cli


RUN_DIRECTORY = Path("/pkg/data/20260906T142530Z_9f2b1c04")
SOURCE_LANGUAGE = ["--source-language", "typescript"]


@pytest.fixture
def gbnf_experiment():
    with patch("gbnf_experiment.cli.run_gbnf_experiment", autospec=True) as m:
        m.return_value = RUN_DIRECTORY
        yield m


@pytest.fixture(autouse=True)
def claude_agent():
    with patch("gbnf_experiment.cli.ClaudeAgent", autospec=True) as m:
        yield m


def describe_cli():
    def it_echoes_the_run_directory(gbnf_experiment):
        result = CliRunner().invoke(cli, SOURCE_LANGUAGE)
        assert result.exit_code == 0
        assert f"Run directory: {RUN_DIRECTORY}" in result.output

    def it_points_at_the_run_before_reporting_on_it(gbnf_experiment):
        lines = CliRunner().invoke(cli, SOURCE_LANGUAGE).output.splitlines()
        assert lines[0].startswith("Run directory: ")

    def it_runs_the_experiment(gbnf_experiment):
        CliRunner().invoke(cli, SOURCE_LANGUAGE)
        gbnf_experiment.assert_called_once()

    def it_runs_no_test_suite_unless_asked(gbnf_experiment, claude_agent):
        CliRunner().invoke(cli, SOURCE_LANGUAGE)
        gbnf_experiment.assert_called_once_with(
            agent=claude_agent.return_value,
            source_language="typescript",
            include_typescript_tests=False,
            include_python_tests=False,
            debug=False,
            effort="high",
            model="claude-opus-5",
        )

    def it_requires_a_source_language(gbnf_experiment):
        result = CliRunner().invoke(cli, [])
        assert result.exit_code != 0
        assert "--source-language" in result.output
        gbnf_experiment.assert_not_called()

    def it_forwards_the_source_language(gbnf_experiment):
        CliRunner().invoke(cli, ["--source-language", "python"])
        assert gbnf_experiment.call_args.kwargs["source_language"] == "python"

    def it_rejects_an_unsupported_source_language(gbnf_experiment):
        result = CliRunner().invoke(cli, ["--source-language", "rust"])
        assert result.exit_code != 0
        gbnf_experiment.assert_not_called()

    def it_forwards_the_test_inclusion_flags(gbnf_experiment):
        CliRunner().invoke(
            cli, [*SOURCE_LANGUAGE, "--include-typescript-tests", "--include-python-tests"]
        )
        assert gbnf_experiment.call_args.kwargs["include_typescript_tests"] is True
        assert gbnf_experiment.call_args.kwargs["include_python_tests"] is True

    def it_forwards_debug(gbnf_experiment):
        CliRunner().invoke(cli, [*SOURCE_LANGUAGE, "--debug"])
        assert gbnf_experiment.call_args.kwargs["debug"] is True

    def it_defaults_the_effort_to_high(gbnf_experiment):
        CliRunner().invoke(cli, SOURCE_LANGUAGE)
        assert gbnf_experiment.call_args.kwargs["effort"] == "high"

    def it_forwards_the_effort(gbnf_experiment):
        CliRunner().invoke(cli, [*SOURCE_LANGUAGE, "--effort", "max"])
        assert gbnf_experiment.call_args.kwargs["effort"] == "max"

    def it_leaves_an_unknown_effort_to_the_agent(gbnf_experiment):
        """Effort levels differ per agent, so the parser cannot know them at import time."""
        CliRunner().invoke(cli, [*SOURCE_LANGUAGE, "--effort", "turbo"])
        assert gbnf_experiment.call_args.kwargs["effort"] == "turbo"

    def it_defaults_to_claude(gbnf_experiment, claude_agent):
        CliRunner().invoke(cli, SOURCE_LANGUAGE)
        claude_agent.assert_called_once_with()

    def it_rejects_an_agent_it_does_not_ship(gbnf_experiment):
        result = CliRunner().invoke(cli, [*SOURCE_LANGUAGE, "--agent", "codex"])
        assert result.exit_code != 0
        gbnf_experiment.assert_not_called()

    def it_pins_the_model_by_default(gbnf_experiment):
        CliRunner().invoke(cli, SOURCE_LANGUAGE)
        assert gbnf_experiment.call_args.kwargs["model"] == "claude-opus-5"

    def it_names_the_pinned_model_in_the_help(gbnf_experiment):
        """--model is free text, so the help is the only place the pin is visible."""
        assert "claude-opus-5" in CliRunner().invoke(cli, ["--help"]).output

    def it_forwards_the_model(gbnf_experiment):
        CliRunner().invoke(cli, [*SOURCE_LANGUAGE, "--model", "claude-sonnet-4-5"])
        assert gbnf_experiment.call_args.kwargs["model"] == "claude-sonnet-4-5"

    def it_renders_sdk_errors_as_click_errors(gbnf_experiment):
        gbnf_experiment.side_effect = RuntimeError("no results report")
        result = CliRunner().invoke(cli, SOURCE_LANGUAGE)
        assert result.exit_code == 1
        assert "no results report" in result.output
