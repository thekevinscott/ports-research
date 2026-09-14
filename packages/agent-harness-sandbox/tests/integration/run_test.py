from pathlib import Path

import pytest

from agent_harness_sandbox import (
    AgentHarnessSandboxError,
    ClaudeAgent,
    PiAgent,
    run_agent_harness_sandbox,
)

BUILDS = [
    "agent-harness-sandbox-base:latest",
    "agent-harness-sandbox-claude:latest",
    "agent-harness-sandbox-proxy:latest",
]


@pytest.fixture
def transcripts(tmp_path: Path) -> Path:
    directory = tmp_path / "transcript"
    directory.mkdir()
    return directory


@pytest.fixture
def proxy_log(tmp_path: Path) -> Path:
    return tmp_path / "proxy.log"


@pytest.fixture
def options(transcripts, proxy_log):
    def build(**overrides):
        return {
            "agent": ClaudeAgent(),
            "inputs": {},
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

    def it_binds_the_caller_directories_themselves(
        tmp_path, docker, claude_home, docker_calls, options
    ):
        """A copy would hide an edit the caller made mid-run and lose one made in the container."""
        in_dir = tmp_path / "in"
        in_dir.mkdir()
        (in_dir / "d.txt").write_text("x")
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        run_agent_harness_sandbox(
            "p", **options(inputs={in_dir: "/work/in"}, outputs={out_dir: "/work/out"})
        )
        [call] = docker_calls
        mounted = {target: (src, mode) for src, target, mode in call["volumes"]}
        assert mounted["/work/in"] == (str(in_dir.resolve()), "ro")
        assert mounted["/work/out"] == (str(out_dir.resolve()), "rw")

    def it_refuses_an_input_that_is_not_there(tmp_path, docker, claude_home, options):
        with pytest.raises(AgentHarnessSandboxError, match="does not exist"):
            run_agent_harness_sandbox("p", **options(inputs={tmp_path / "gone": "/work/in"}))

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
    def it_runs_pis_image_with_pis_credentials(docker, pi_home, docker_calls, options, builds):
        run_agent_harness_sandbox(
            "1+1", **options(agent=PiAgent(provider="openrouter"), effort="minimal", model="m")
        )
        [call] = docker_calls
        assert call["tag"] == "agent-harness-sandbox-pi:latest"
        assert call["cmd"][:2] == ["pi", "-p"]
        assert call["files"]["/home/node/.pi/agent"] == ["auth.json", "models.json"]
        assert builds[1] == "agent-harness-sandbox-pi:latest"

    def it_binds_the_transcripts_where_pi_writes_them(
        docker, pi_home, docker_calls, options, transcripts
    ):
        run_agent_harness_sandbox(
            "1+1", **options(agent=PiAgent(provider="openrouter"), effort="minimal", model="m")
        )
        [call] = docker_calls
        by_target = {target: src for src, target, _ in call["volumes"]}
        assert by_target["/home/node/.pi/agent/sessions"] == str(transcripts.resolve())

    def it_fails_without_pis_credentials(docker, pi_home, options):
        (pi_home / "auth.json").unlink()
        with pytest.raises(AgentHarnessSandboxError, match="does not exist"):
            run_agent_harness_sandbox(
                "1+1", **options(agent=PiAgent(provider="openrouter"), effort="minimal", model="m")
            )


def describe_image_freshness():
    def it_rebuilds_the_sandbox_and_the_proxy_on_every_run(docker, claude_home, options, builds):
        """A static tag makes the build the only step that can notice an edited context.

        Skip it and docker serves last week's Dockerfile under today's name, while
        the run record beside it names the commit that was checked out this morning.
        """
        run_agent_harness_sandbox("1+1", **options())
        run_agent_harness_sandbox("1+1", **options())
        assert builds == BUILDS * 2

    def it_runs_the_image_it_built(docker, claude_home, docker_calls, options, builds):
        run_agent_harness_sandbox("1+1", **options())
        [call] = docker_calls
        assert call["tag"] in builds
