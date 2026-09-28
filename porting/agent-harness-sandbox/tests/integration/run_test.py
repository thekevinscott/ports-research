from pathlib import Path

import pytest

from agent_harness_sandbox.agents.ClaudeAgent import ClaudeAgent
from agent_harness_sandbox.agents.PiAgent import PiAgent
from agent_harness_sandbox.build_agent_image import build_agent_image
from agent_harness_sandbox.errors import AgentHarnessSandboxError
from agent_harness_sandbox.run_agent_harness_sandbox import run_agent_harness_sandbox

CLAUDE_IMAGE = "agent-harness-sandbox-claude:latest"
PI_IMAGE = "agent-harness-sandbox-pi:latest"


@pytest.fixture
def transcripts(tmp_path: Path) -> Path:
    directory = tmp_path / "transcript"
    directory.mkdir()
    return directory


@pytest.fixture
def proxy_log(tmp_path: Path) -> Path:
    return tmp_path / "proxy.log"


@pytest.fixture
def options(transcripts, proxy_log, claude_home, tmp_path):
    input_folder = tmp_path / "input"
    input_folder.mkdir()

    def build(**overrides):
        return {
            "agent": ClaudeAgent(host_home=claude_home),
            "image": CLAUDE_IMAGE,
            "input_folder": input_folder,
            "outputs": {},
            "envs": {},
            "debug": False,
            "home": "/workspace",
            "transcripts": transcripts,
            "proxy_log": proxy_log,
            "effort": "high",
            "model": "claude-opus-5",
            **overrides,
        }

    return build


@pytest.fixture
def writes_into_the_input_mount(docker):
    """A stand-in for the agent installing dependencies and scratching under /input."""
    record = docker.side_effect

    def run(tag, cmd=None, **options):
        if not options.get("detach"):
            [source] = [s for s, target, _ in options["volumes"] if target == "/input"]
            (Path(source) / "node_modules").mkdir()
            (Path(source) / "d.txt").write_text("changed in the container")
        return record(tag, cmd, **options)

    docker.side_effect = run


def describe_run_agent_harness_sandbox():
    def it_returns_the_container_output(docker, claude_home, options):
        assert run_agent_harness_sandbox("1+1", **options()) == "container output"

    def it_mounts_a_credentials_copy_as_the_claude_config_dir(
        docker, claude_home, docker_calls, options
    ):
        run_agent_harness_sandbox("1+1", **options())
        [call] = docker_calls
        [src] = [s for s, target, _ in call["volumes"] if target == "/home/node/.claude"]
        assert src != str(claude_home)
        assert call["files"]["/home/node/.claude"] == [".credentials.json"]

    def it_discards_the_credentials_copy_after_the_run(docker, claude_home, docker_calls, options):
        run_agent_harness_sandbox("1+1", **options())
        [call] = docker_calls
        src, _, _ = call["volumes"][0]
        assert not Path(src).exists()

    def it_binds_the_output_directories_themselves(
        tmp_path, docker, claude_home, docker_calls, options
    ):
        """A copy would lose what the container wrote there."""
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        run_agent_harness_sandbox("p", **options(outputs={out_dir: "/work/out"}))
        [call] = docker_calls
        mounted = {target: (src, mode) for src, target, mode in call["volumes"]}
        assert mounted["/work/out"] == (str(out_dir.resolve()), "rw")

    def it_mounts_a_writable_copy_of_the_input_folder(
        tmp_path, docker, claude_home, docker_calls, options
    ):
        in_dir = tmp_path / "in"
        in_dir.mkdir()
        (in_dir / "d.txt").write_text("x")
        run_agent_harness_sandbox("p", **options(input_folder=in_dir))
        [call] = docker_calls
        mounted = {target: (src, mode) for src, target, mode in call["volumes"]}
        src, mode = mounted["/input"]
        assert src != str(in_dir.resolve())
        assert mode == "rw"
        assert call["files"]["/input"] == ["d.txt"]

    def it_leaves_the_callers_input_folder_untouched_by_the_container(
        tmp_path, docker, claude_home, options, writes_into_the_input_mount
    ):
        in_dir = tmp_path / "in"
        in_dir.mkdir()
        (in_dir / "d.txt").write_text("x")
        before = {p.name: p.read_text() for p in sorted(in_dir.iterdir())}
        run_agent_harness_sandbox("p", **options(input_folder=in_dir))
        assert {p.name: p.read_text() for p in sorted(in_dir.iterdir())} == before

    def it_refuses_an_input_that_is_not_there(tmp_path, docker, claude_home, options):
        with pytest.raises(AgentHarnessSandboxError, match="does not exist"):
            run_agent_harness_sandbox("p", **options(input_folder=tmp_path / "gone"))

    def it_binds_the_transcripts_directory_the_caller_named(
        docker, claude_home, docker_calls, options, transcripts
    ):
        run_agent_harness_sandbox("1+1", **options())
        [call] = docker_calls
        by_target = {target: src for src, target, _ in call["volumes"]}
        assert by_target["/home/node/.claude/projects"] == str(transcripts.resolve())

    def it_runs_on_a_locked_down_network_behind_the_proxy(
        docker, claude_home, docker_calls, options
    ):
        run_agent_harness_sandbox("1+1", **options())
        [call] = docker_calls
        [network] = call["networks"]
        assert network.startswith("agent-harness-sandbox-jail-")
        assert call["envs"]["HTTPS_PROXY"].startswith("http://agent-harness-sandbox-proxy-")

    def it_writes_the_proxy_log_to_the_host(docker, claude_home, options, proxy_log):
        run_agent_harness_sandbox("1+1", **options())
        assert proxy_log.exists()

    def it_hands_the_container_no_capabilities_and_no_way_to_gain_any(
        docker, claude_home, docker_calls, options
    ):
        run_agent_harness_sandbox("1+1", **options())
        [call] = docker_calls
        assert call["cap_drop"] == ["ALL"]
        assert call["security_options"] == ["no-new-privileges"]

    def it_fails_without_credentials(docker, claude_home, options):
        (claude_home / ".credentials.json").unlink()
        with pytest.raises(AgentHarnessSandboxError, match="does not exist"):
            run_agent_harness_sandbox("1+1", **options())

    def it_fails_when_the_transcripts_directory_is_missing(docker, claude_home, options, tmp_path):
        with pytest.raises(AgentHarnessSandboxError, match="does not exist"):
            run_agent_harness_sandbox("1+1", **options(transcripts=tmp_path / "gone"))

    def it_rejects_an_effort_the_agent_does_not_have(docker, claude_home, options):
        with pytest.raises(AgentHarnessSandboxError, match="unknown effort"):
            run_agent_harness_sandbox("1+1", **options(effort="minimal"))


def describe_a_second_agent():
    def it_runs_pis_image_with_pis_credentials(docker, pi_home, docker_calls, options):
        run_agent_harness_sandbox(
            "1+1",
            **options(
                agent=PiAgent(provider="openrouter", host_home=pi_home),
                image=PI_IMAGE,
                effort="minimal",
                model="m",
            ),
        )
        [call] = docker_calls
        assert call["tag"] == PI_IMAGE
        assert call["cmd"][:2] == ["pi", "-p"]
        assert call["files"]["/home/node/.pi/agent"] == ["auth.json", "models.json"]

    def it_binds_the_transcripts_where_pi_writes_them(
        docker, pi_home, docker_calls, options, transcripts
    ):
        run_agent_harness_sandbox(
            "1+1", **options(agent=PiAgent(provider="openrouter", host_home=pi_home), effort="minimal", model="m")
        )
        [call] = docker_calls
        by_target = {target: src for src, target, _ in call["volumes"]}
        assert by_target["/home/node/.pi/agent/sessions"] == str(transcripts.resolve())

    def it_fails_without_pis_credentials(docker, pi_home, options):
        (pi_home / "auth.json").unlink()
        with pytest.raises(AgentHarnessSandboxError, match="does not exist"):
            run_agent_harness_sandbox(
                "1+1", **options(agent=PiAgent(provider="openrouter", host_home=pi_home), effort="minimal", model="m")
            )


def describe_image_freshness():
    def it_rebuilds_the_sandbox_on_every_build(docker, claude_home, builds):
        """A static tag makes the build the only step that can notice an edited context.

        Skip it and docker serves last week's Dockerfile under today's name, while
        the run record beside it names the commit that was checked out this morning.
        """
        agent = ClaudeAgent(host_home=claude_home)
        assert build_agent_image(agent=agent, debug=False) == CLAUDE_IMAGE
        build_agent_image(agent=agent, debug=False)
        assert builds == ["agent-harness-sandbox-base:latest", CLAUDE_IMAGE] * 2

    def it_builds_pis_layer_on_the_same_base(docker, pi_home, builds):
        build_agent_image(agent=PiAgent(provider="openrouter", host_home=pi_home), debug=False)
        assert builds == ["agent-harness-sandbox-base:latest", PI_IMAGE]

    def it_rebuilds_the_proxy_on_every_run(docker, claude_home, options, builds):
        run_agent_harness_sandbox("1+1", **options())
        run_agent_harness_sandbox("1+1", **options())
        assert builds == ["agent-harness-sandbox-proxy:latest"] * 2

    def it_runs_the_image_the_caller_named(docker, claude_home, docker_calls, options):
        """A caller's own layer on the agent image is what runs, not the agent image."""
        run_agent_harness_sandbox("1+1", **options(image="a-caller-layer:abc"))
        [call] = docker_calls
        assert call["tag"] == "a-caller-layer:abc"
