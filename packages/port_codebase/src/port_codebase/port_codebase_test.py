from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from adocker import DockerException
from botbox import ClaudeAgent, CodexAgent

from port_codebase.port_codebase import CONTINUE_PROMPT, PROMPT_PATH, port_codebase

AGENT_DOCKERFILE = "FROM node:24-slim\nRUN npm install -g some-cli\n"
CLAUDE_DOCKERFILE = Path(__file__).parent / "Dockerfile.claude"


@pytest.fixture
def kept():
    """The names of the containers the daemon holds."""
    return set()


@pytest.fixture
def botbox(kept):
    with patch("port_codebase.port_codebase.Botbox", autospec=True) as mock:
        box = mock.return_value
        box.__aenter__.return_value = box
        box.run.return_value.exit_code = 1
        box.restart.return_value.exit_code = 1

        def run(*args, keep, **kwargs):
            kept.add(keep)
            return box.run.return_value

        box.run.side_effect = run
        yield mock


@pytest.fixture
def docker(kept):
    with (
        patch("port_codebase.port_codebase.Container", autospec=True) as container,
        patch("port_codebase.port_codebase.Volume", autospec=True) as volume,
    ):

        def inspect():
            [name] = container.call_args.args
            if name not in kept:
                raise DockerException(
                    ["container", "inspect", name], 1, f"Error: No such container: {name}\n"
                )
            return {"Config": {"Labels": {"botbox.run": "abc123"}}}

        container.return_value.inspect.side_effect = inspect
        yield container, volume


@pytest.fixture
def prompt_class():
    with patch("port_codebase.port_codebase.Prompt", autospec=True) as mock:
        mock.return_value.__str__ = Mock(return_value="the rendered prompt")
        yield mock


@pytest.fixture
def agent(tmp_path):
    agent = Mock(spec=ClaudeAgent, name="agent")
    agent.command.side_effect = lambda prompt, resume=False: f"cli {prompt}" + (" --continue" if resume else "")
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
def call(botbox, docker, agent, source, output, tmp_path):
    async def call(prompt="Port it.\n"):
        return await port_codebase(
            agent=agent,
            prompt=prompt,
            source=source,
            output=output,
            artifacts=tmp_path / "artifacts",
            memory="8g",
            container="ports-run",
        )

    return call


def describe_port_codebase():
    async def it_builds_a_claude_box_from_the_claude_dockerfile(call, botbox, agent):
        await call()

        botbox.assert_called_once_with(agent, dockerfile=CLAUDE_DOCKERFILE, memory="8g")

    async def it_builds_a_codex_box_from_the_codex_dockerfile(call, botbox, agent):
        agent.__class__ = CodexAgent

        await call()

        botbox.assert_called_once_with(agent, dockerfile=Path(__file__).parent / "Dockerfile.codex", memory="8g")

    async def it_requires_a_memory_cap(botbox, agent, source, output, tmp_path):
        with pytest.raises(TypeError, match="memory"):
            await port_codebase(
                agent=agent, prompt="Port it.", source=source, output=output, artifacts=tmp_path / "artifacts",
                container="ports-run",
            )

        botbox.assert_not_called()

    async def it_runs_the_agents_command_for_the_rendered_prompt(call, botbox, prompt_class):
        await call("Port it.\n")

        prompt_class.assert_called_once_with(
            PROMPT_PATH,
            agent_dockerfile=AGENT_DOCKERFILE.rstrip("\n"),
            dockerfile=CLAUDE_DOCKERFILE.read_text().rstrip("\n"),
            upstream="Port it.\n",
        )
        assert botbox.return_value.run.call_args.args == ("cli the rendered prompt",)

    async def it_shows_the_agent_both_dockerfiles_as_written(call, botbox):
        await call()

        [command] = botbox.return_value.run.call_args.args
        assert AGENT_DOCKERFILE.rstrip("\n") in command
        assert CLAUDE_DOCKERFILE.read_text().rstrip("\n") in command
        assert command.index("FROM node:24-slim") < command.index("FROM botbox-claude")

    async def it_rereads_the_agents_dockerfile_on_every_call(call, botbox, agent, kept):
        await call()
        kept.clear()
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

    async def it_writes_run_artifacts_outside_the_port(call, botbox, tmp_path):
        await call()

        assert botbox.return_value.run.call_args.kwargs["output"] == tmp_path / "artifacts"

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
            await port_codebase(
                agent=agent, prompt="Port it.", source=tmp_path / "gone",
                output=output, artifacts=tmp_path / "artifacts", memory="8g",
                container="ports-run",
            )

        assert not output.exists()
        botbox.assert_not_called()

    async def it_keeps_a_fresh_run_under_the_callers_name(call, botbox):
        await call()

        assert botbox.return_value.run.call_args.kwargs["keep"] == "ports-run"

    async def it_resumes_by_restarting_the_kept_container_with_continue(call, botbox, kept, source, output, tmp_path):
        kept.add("ports-run")
        output.mkdir(parents=True)
        (output / "ported.py").write_text("")

        await call()

        botbox.return_value.run.assert_not_called()
        botbox.return_value.restart.assert_called_once_with(
            "ports-run",
            f"cli {CONTINUE_PROMPT} --continue",
            mounts=((source, "/input", "ro"), (output, "/target", "rw")),
            workdir="/target",
            output=tmp_path / "artifacts",
        )

    async def it_runs_fresh_when_the_output_is_empty_and_no_container_was_kept(call, botbox, output):
        output.mkdir(parents=True)

        await call()

        botbox.return_value.restart.assert_not_called()
        assert botbox.return_value.run.call_args.kwargs["keep"] == "ports-run"

    async def it_refuses_a_non_empty_output_with_no_container_kept(call, botbox, output):
        output.mkdir(parents=True)
        (output / "ported.py").write_text("")

        with pytest.raises(FileExistsError, match="ports-run"):
            await call()

        botbox.assert_not_called()

    async def it_raises_a_daemon_failure_other_than_a_missing_container(call, botbox, docker):
        container, _ = docker
        container.return_value.inspect.side_effect = DockerException(["container", "inspect"], 1, "Cannot connect")

        with pytest.raises(DockerException, match="Cannot connect"):
            await call()

        botbox.assert_not_called()

    @pytest.mark.parametrize("resume", [False, True])
    async def it_removes_the_kept_container_and_its_volume_on_exit_0(call, botbox, docker, kept, resume):
        container, volume = docker
        if resume:
            kept.add("ports-run")
        botbox.return_value.run.return_value.exit_code = 0
        botbox.return_value.restart.return_value.exit_code = 0

        await call()

        container.assert_called_with("ports-run")
        container.return_value.remove.assert_awaited_once()
        volume.assert_called_once_with("botbox-run-abc123")
        volume.return_value.remove.assert_awaited_once()

    @pytest.mark.parametrize("resume", [False, True])
    async def it_leaves_the_kept_container_when_the_agent_fails(call, docker, kept, resume):
        container, volume = docker
        if resume:
            kept.add("ports-run")

        await call()

        container.return_value.remove.assert_not_called()
        volume.return_value.remove.assert_not_called()
