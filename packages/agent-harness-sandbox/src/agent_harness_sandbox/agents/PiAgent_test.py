import os
from unittest.mock import patch

import pytest

from agent_harness_sandbox.errors import AgentHarnessSandboxError
from agent_harness_sandbox.agents.PiAgent import PiAgent


def flag(command: list[str], name: str) -> str:
    return command[command.index(name) + 1]


MODEL = "anthropic/claude-opus-4"


@pytest.fixture
def agent():
    return PiAgent(provider="openrouter")


@pytest.fixture
def local_host():
    host = "model-host.example"
    with patch.dict(os.environ, {"PI_AGENT_HOST": host}):
        yield host


@pytest.fixture
def pi_home(tmp_path):
    home = tmp_path / "pi-home"
    home.mkdir()
    (home / "auth.json").write_text('{"key": "k"}')
    (home / "models.json").write_text('{"providers": []}')
    with patch("agent_harness_sandbox.agents.PiAgent.PI_HOME", home):
        yield home


@pytest.fixture
def destination(tmp_path):
    staged = tmp_path / "staged"
    staged.mkdir()
    return staged


def describe_the_container():
    def it_names_its_own_image(agent):
        assert agent.image == "agent-harness-sandbox-pi:latest"

    def it_points_at_its_own_dockerfile(agent):
        assert agent.dockerfile.name == "Dockerfile.pi"

    def it_puts_its_config_where_pi_looks_for_it(agent):
        assert agent.home == "/home/node/.pi/agent"

    def it_files_transcripts_under_the_sessions_directory(agent):
        assert agent.transcripts == "/home/node/.pi/agent/sessions"


def describe_the_provider():
    def it_is_required():
        with pytest.raises(TypeError):
            PiAgent()

    def it_allows_the_host_openrouter_answers_on():
        assert PiAgent(provider="openrouter").allow == ("openrouter.ai",)

    def it_allows_the_host_the_local_model_serves_from(local_host):
        assert PiAgent(provider="tower").allow == (local_host,)

    def it_refuses_a_local_provider_with_no_host_configured():
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AgentHarnessSandboxError, match="PI_AGENT_HOST"):
                PiAgent(provider="tower")

    def it_rejects_a_provider_it_has_no_allowlist_for():
        with pytest.raises(AgentHarnessSandboxError, match="anthropic"):
            PiAgent(provider="anthropic")

    def it_lists_the_providers_it_knows():
        with pytest.raises(AgentHarnessSandboxError, match="openrouter, tower"):
            PiAgent(provider="")


def describe_command():
    def it_runs_pi_headless(agent):
        assert agent.command("hi", effort="high", model=MODEL)[:2] == ["pi", "-p"]

    def it_puts_the_prompt_last(agent):
        assert agent.command("hi", effort="high", model=MODEL)[-1] == "hi"

    def it_asks_for_json_output(agent):
        assert flag(agent.command("hi", effort="high", model=MODEL), "--mode") == "json"

    def it_names_the_provider_it_was_built_for(agent, local_host):
        command = PiAgent(provider="tower").command("hi", effort="high", model=MODEL)
        assert flag(command, "--provider") == "tower"

    def it_asks_for_no_approval_bypass(agent):
        command = agent.command("hi", effort="high", model=MODEL)
        assert not any(argument.startswith("--dangerously") for argument in command)

    def it_takes_its_options_by_keyword_only(agent):
        with pytest.raises(TypeError):
            agent.command("hi", "high")

    def describe_effort():
        @pytest.mark.parametrize("level", ["off", "minimal", "low", "medium", "high", "xhigh"])
        def it_accepts_every_level(agent, level):
            assert flag(agent.command("hi", effort=level, model=MODEL), "--thinking") == level

        def it_rejects_the_level_only_claude_has(agent):
            with pytest.raises(AgentHarnessSandboxError, match="max"):
                agent.command("hi", effort="max", model=MODEL)

        def it_lists_the_valid_levels(agent):
            with pytest.raises(
                AgentHarnessSandboxError, match="off, minimal, low, medium, high, xhigh"
            ):
                agent.command("hi", effort="", model=MODEL)

    def describe_model():
        def it_passes_the_model(agent):
            assert flag(agent.command("hi", effort="high", model=MODEL), "--model") == MODEL

        def it_requires_a_model(agent):
            with pytest.raises(TypeError):
                agent.command("hi", effort="high")


def describe_stage_auth():
    def it_stages_the_key_and_the_provider_catalogue(agent, pi_home, destination):
        agent.stage_auth(destination)
        assert sorted(path.name for path in destination.iterdir()) == [
            "auth.json",
            "models.json",
        ]

    def it_copies_rather_than_shares_the_host_files(agent, pi_home, destination):
        agent.stage_auth(destination)
        copy = destination / "auth.json"
        assert copy.read_text() == '{"key": "k"}'
        assert copy.stat().st_ino != (pi_home / "auth.json").stat().st_ino

    def it_refuses_a_host_with_no_key(agent, pi_home, destination):
        (pi_home / "auth.json").unlink()
        with pytest.raises(AgentHarnessSandboxError, match="auth.json does not exist"):
            agent.stage_auth(destination)

    def it_refuses_a_host_with_no_provider_catalogue(agent, pi_home, destination):
        (pi_home / "models.json").unlink()
        with pytest.raises(AgentHarnessSandboxError, match="models.json does not exist"):
            agent.stage_auth(destination)
