from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from port_codebase.port_codebase import DOCKERFILE, PROMPT_PATH, port_codebase

AGENT_DOCKERFILE = "FROM node:24-slim\nRUN npm install -g some-cli\n"


@pytest.fixture
def botbox():
    with patch("port_codebase.port_codebase.Botbox", autospec=True) as mock:
        mock.return_value.__aenter__.return_value = mock.return_value
        yield mock


@pytest.fixture
def prompt_class():
    with patch("port_codebase.port_codebase.Prompt", autospec=True) as mock:
        mock.return_value.__str__ = Mock(return_value="the rendered prompt")
        yield mock


@pytest.fixture
def agent(tmp_path):
    agent = Mock(name="agent")
    agent.command.side_effect = lambda prompt: f"cli {prompt}"
    agent.dockerfile = tmp_path / "agent" / "Dockerfile"
    agent.dockerfile.parent.mkdir()
    agent.dockerfile.write_text(AGENT_DOCKERFILE)
    return agent


@pytest.fixture
def source(tmp_path):
    directory = tmp_path / "source"
    directory.mkdir()
    return directory


@pytest.fixture
def output(tmp_path):
    return tmp_path / "nested" / "output"


@pytest.fixture
def call(botbox, agent, source, output):
    async def call(prompt="Port it.\n"):
        return await port_codebase(agent=agent, prompt=prompt, source=source, output=output)

    return call


def describe_port_codebase():
    async def it_builds_the_box_from_the_packaged_dockerfile(call, botbox, agent):
        await call()

        botbox.assert_called_once_with(agent, dockerfile=Path(__file__).parent / "Dockerfile")

    async def it_runs_the_agents_command_for_the_rendered_prompt(call, botbox, prompt_class):
        await call("Port it.\n")

        prompt_class.assert_called_once_with(
            PROMPT_PATH,
            agent_dockerfile=AGENT_DOCKERFILE.rstrip("\n"),
            dockerfile=DOCKERFILE.read_text().rstrip("\n"),
            upstream="Port it.\n",
        )
        assert botbox.return_value.run.call_args.args == ("cli the rendered prompt",)

    async def it_shows_the_agent_both_dockerfiles_as_written(call, botbox):
        await call()

        [command] = botbox.return_value.run.call_args.args
        assert AGENT_DOCKERFILE.rstrip("\n") in command
        assert DOCKERFILE.read_text().rstrip("\n") in command
        assert command.index("FROM node:24-slim") < command.index("FROM botbox-claude")

    async def it_rereads_the_agents_dockerfile_on_every_call(call, botbox, agent):
        await call()
        agent.dockerfile.write_text("FROM node:25-slim\n")

        await call()

        [command] = botbox.return_value.run.call_args.args
        assert "FROM node:25-slim" in command
        assert "FROM node:24-slim" not in command

    async def it_mounts_the_source_read_only_and_the_output_read_write(call, botbox, source, output):
        await call()

        assert botbox.return_value.run.call_args.kwargs["mounts"] == (
            (source, "/input", "ro"),
            (output, "/target", "rw"),
        )

    async def it_starts_in_the_output(call, botbox):
        await call()

        assert botbox.return_value.run.call_args.kwargs["workdir"] == "/target"

    async def it_returns_the_run_result_unchanged(call, botbox):
        assert await call() is botbox.return_value.run.return_value

    async def it_creates_a_missing_output(call, output):
        await call()

        assert output.is_dir()

    async def it_accepts_an_existing_output(call, output):
        output.mkdir(parents=True)

        await call()

        assert output.is_dir()

    async def it_refuses_a_missing_source_before_creating_the_output(botbox, agent, tmp_path, output):
        with pytest.raises(FileNotFoundError):
            await port_codebase(agent=agent, prompt="Port it.", source=tmp_path / "gone", output=output)

        assert not output.exists()
        botbox.assert_not_called()
