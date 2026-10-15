from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from gbnf_experiment.cli import cli


RUN_DIRECTORY = Path("/pkg/data/20260906T142530Z_9f2b1c04")
STUDY = ["--study", "probe"]
OUTPUT = ["--output", "/data/runs"]
SOURCE_LANGUAGE = ["--source-language", "javascript", *STUDY, *OUTPUT]


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
            study="probe",
            output=Path("/data/runs"),
            source_language="javascript",
            include_unit_tests=False,
            include_source_integration_tests=False,
            include_target_integration_tests=False,
            debug=False,
        )

    def it_requires_a_source_language(gbnf_experiment):
        result = CliRunner().invoke(cli, [])
        assert result.exit_code != 0
        assert "--source-language" in result.output
        gbnf_experiment.assert_not_called()

    def it_forwards_the_source_language(gbnf_experiment):
        CliRunner().invoke(cli, ["--source-language", "python", *STUDY, *OUTPUT])
        assert gbnf_experiment.call_args.kwargs["source_language"] == "python"

    def it_rejects_an_unsupported_source_language(gbnf_experiment):
        result = CliRunner().invoke(cli, ["--source-language", "rust", *STUDY, *OUTPUT])
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
    def it_forwards_each_test_inclusion_flag(gbnf_experiment, flag):
        CliRunner().invoke(cli, [*SOURCE_LANGUAGE, flag])
        kwargs = gbnf_experiment.call_args.kwargs
        name = flag.removeprefix("--").replace("-", "_")
        assert kwargs[name] is True
        assert [key for key, value in kwargs.items() if value is True] == [name]

    @pytest.mark.parametrize("flag", ["--include-javascript-tests", "--include-python-tests"])
    def it_rejects_the_per_language_flags(gbnf_experiment, flag):
        result = CliRunner().invoke(cli, [*SOURCE_LANGUAGE, flag])
        assert result.exit_code != 0
        gbnf_experiment.assert_not_called()

    def it_requires_a_study(gbnf_experiment):
        result = CliRunner().invoke(cli, ["--source-language", "javascript", *OUTPUT])
        assert result.exit_code != 0
        assert "--study" in result.output
        gbnf_experiment.assert_not_called()

    def it_forwards_the_study(gbnf_experiment):
        CliRunner().invoke(cli, ["--source-language", "javascript", "--study", "v2-model-effort", *OUTPUT])
        assert gbnf_experiment.call_args.kwargs["study"] == "v2-model-effort"

    def it_requires_an_output_directory(gbnf_experiment):
        """No default: a default landed runs in whichever checkout ran them."""
        result = CliRunner().invoke(cli, ["--source-language", "javascript", *STUDY])
        assert result.exit_code != 0
        assert "--output" in result.output
        gbnf_experiment.assert_not_called()

    def it_forwards_the_output_directory_as_a_path(gbnf_experiment):
        CliRunner().invoke(cli, ["--source-language", "javascript", *STUDY, "--output", "/elsewhere"])
        assert gbnf_experiment.call_args.kwargs["output"] == Path("/elsewhere")

    def it_forwards_debug(gbnf_experiment):
        CliRunner().invoke(cli, [*SOURCE_LANGUAGE, "--debug"])
        assert gbnf_experiment.call_args.kwargs["debug"] is True

    def it_builds_a_claude_agent_on_the_default_model_and_effort(gbnf_experiment, claude_agent):
        CliRunner().invoke(cli, SOURCE_LANGUAGE)
        claude_agent.assert_called_once_with(model="claude-opus-5", effort="high")

    def it_forwards_the_effort_to_the_agent(gbnf_experiment, claude_agent):
        CliRunner().invoke(cli, [*SOURCE_LANGUAGE, "--effort", "max"])
        assert claude_agent.call_args.kwargs["effort"] == "max"

    def it_leaves_an_unknown_effort_to_the_agent(gbnf_experiment, claude_agent):
        """Effort levels differ per agent, so the parser cannot know them at import time."""
        CliRunner().invoke(cli, [*SOURCE_LANGUAGE, "--effort", "turbo"])
        assert claude_agent.call_args.kwargs["effort"] == "turbo"

    def it_has_no_agent_option(gbnf_experiment):
        result = CliRunner().invoke(cli, [*SOURCE_LANGUAGE, "--agent", "claude"])
        assert result.exit_code != 0
        gbnf_experiment.assert_not_called()

    def it_names_the_pinned_model_in_the_help(gbnf_experiment):
        """--model is free text, so the help is the only place the pin is visible."""
        assert "claude-opus-5" in CliRunner().invoke(cli, ["--help"]).output

    def it_forwards_the_model_to_the_agent(gbnf_experiment, claude_agent):
        CliRunner().invoke(cli, [*SOURCE_LANGUAGE, "--model", "claude-sonnet-4-5"])
        assert claude_agent.call_args.kwargs["model"] == "claude-sonnet-4-5"

    def it_renders_sdk_errors_as_click_errors(gbnf_experiment):
        gbnf_experiment.side_effect = RuntimeError("no results report")
        result = CliRunner().invoke(cli, SOURCE_LANGUAGE)
        assert result.exit_code == 1
        assert "no results report" in result.output
