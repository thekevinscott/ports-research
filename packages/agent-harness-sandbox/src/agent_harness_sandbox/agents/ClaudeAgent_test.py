from unittest.mock import patch

import pytest

from agent_harness_sandbox.agents.ClaudeAgent import ClaudeAgent
from agent_harness_sandbox.errors import AgentHarnessSandboxError


def flag(command: list[str], name: str) -> str:
    return command[command.index(name) + 1]


MODEL = "claude-opus-5"


@pytest.fixture
def agent():
    return ClaudeAgent()


@pytest.fixture
def claude_home(tmp_path):
    home = tmp_path / "claude-home"
    home.mkdir()
    (home / ".credentials.json").write_text('{"token": "t"}')
    with patch("agent_harness_sandbox.agents.ClaudeAgent.CLAUDE_HOME", home):
        yield home


@pytest.fixture
def destination(tmp_path):
    staged = tmp_path / "staged"
    staged.mkdir()
    return staged


def describe_the_container():
    def it_names_its_own_image(agent):
        assert agent.image == "agent-harness-sandbox-claude:latest"

    def it_points_at_its_own_dockerfile(agent):
        assert agent.dockerfile.name == "Dockerfile.claude"

    def it_puts_its_config_where_claude_looks_for_it(agent):
        assert agent.home == "/home/node/.claude"

    def it_files_transcripts_under_the_config_directory(agent):
        assert agent.transcripts == "/home/node/.claude/projects"

    def it_allows_only_the_anthropic_api(agent):
        assert agent.allow == ("api.anthropic.com",)


def describe_command():
    def it_runs_claude_headless(agent):
        command = agent.command("hi", effort="high", model=MODEL)
        assert command[:3] == ["claude", "-p", "--dangerously-skip-permissions"]

    def it_puts_the_prompt_last(agent):
        assert agent.command("hi", effort="high", model=MODEL)[-1] == "hi"

    def it_passes_the_effort(agent):
        assert flag(agent.command("hi", effort="max", model=MODEL), "--effort") == "max"

    def it_takes_its_options_by_keyword_only(agent):
        with pytest.raises(TypeError):
            agent.command("hi", "max")

    def describe_effort():
        @pytest.mark.parametrize("level", ["low", "medium", "high", "xhigh", "max"])
        def it_accepts_every_level(agent, level):
            assert flag(agent.command("hi", effort=level, model=MODEL), "--effort") == level

        def it_rejects_an_unknown_level(agent):
            with pytest.raises(AgentHarnessSandboxError, match="hihg"):
                agent.command("hi", effort="hihg", model=MODEL)

        def it_lists_the_valid_levels(agent):
            with pytest.raises(AgentHarnessSandboxError, match="low, medium, high, xhigh, max"):
                agent.command("hi", effort="", model=MODEL)

        def it_rejects_a_differently_cased_level(agent):
            with pytest.raises(AgentHarnessSandboxError):
                agent.command("hi", effort="High", model=MODEL)

    def describe_model():
        def it_passes_the_model(agent):
            command = agent.command("hi", effort="high", model=MODEL)
            assert flag(command, "--model") == "claude-opus-5"

        def it_keeps_the_prompt_last_behind_the_model(agent):
            command = agent.command("hi", effort="high", model=MODEL)
            assert command[-1] == "hi"

        def it_requires_a_model(agent):
            with pytest.raises(TypeError):
                agent.command("hi", effort="high")

    def it_sets_no_turn_cap(agent):
        assert "--max-turns" not in agent.command("hi", effort="high", model=MODEL)

    def describe_web_tools():
        def it_denies_web_search_and_web_fetch(agent):
            command = agent.command("hi", effort="high", model=MODEL)
            assert "--disallowed-tools=WebSearch,WebFetch" in command

        def it_denies_them_as_one_argv_token(agent):
            command = agent.command("hi", effort="high", model=MODEL)
            assert not any(arg in ("WebSearch", "WebFetch") for arg in command)

    def it_asks_for_json_output(agent):
        assert flag(agent.command("hi", effort="high", model=MODEL), "--output-format") == "json"


def describe_stage_auth():
    def it_leaves_only_the_credentials_in_the_destination(agent, claude_home, destination):
        agent.stage_auth(destination)
        assert [path.name for path in destination.iterdir()] == [".credentials.json"]

    def it_copies_rather_than_shares_the_host_file(agent, claude_home, destination):
        agent.stage_auth(destination)
        copy = destination / ".credentials.json"
        assert copy.read_text() == '{"token": "t"}'
        assert copy.stat().st_ino != (claude_home / ".credentials.json").stat().st_ino

    def it_leaves_the_host_file_untouched_when_the_container_rewrites_it(
        agent, claude_home, destination
    ):
        agent.stage_auth(destination)
        (destination / ".credentials.json").write_text('{"token": "refreshed"}')
        assert (claude_home / ".credentials.json").read_text() == '{"token": "t"}'

    def it_creates_no_directory_of_its_own(agent, claude_home, destination, tmp_path):
        agent.stage_auth(destination)
        assert sorted(path.name for path in tmp_path.iterdir()) == ["claude-home", "staged"]

    def it_refuses_a_host_with_no_credentials(agent, claude_home, destination):
        (claude_home / ".credentials.json").unlink()
        with pytest.raises(AgentHarnessSandboxError, match="does not exist"):
            agent.stage_auth(destination)
