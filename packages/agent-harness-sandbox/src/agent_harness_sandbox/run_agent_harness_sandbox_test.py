from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agent_harness_sandbox.run_agent_harness_sandbox import run_agent_harness_sandbox

class SandboxError(Exception):
    """Stands in for the package's error type, a collaborator like any other."""


@pytest.fixture(autouse=True)
def sandbox_error():
    with patch("agent_harness_sandbox.run_agent_harness_sandbox.AgentHarnessSandboxError", SandboxError):
        yield


AGENT = {
    "image": "an-agent:latest",
    "dockerfile": Path("/sandbox/Dockerfile.an-agent"),
    "home": "/home/node/.an-agent",
    "transcripts": "/home/node/.an-agent/sessions",
    "allow": ("api.example.com",),
}


@pytest.fixture
def agent():
    stub = Mock(**AGENT)
    stub.command.return_value = ["an-agent"]
    stub.stage_auth.return_value = None
    return stub


@pytest.fixture
def transcripts(tmp_path):
    directory = tmp_path / "transcripts"
    directory.mkdir()
    return directory


@pytest.fixture
def options(agent, transcripts):
    return {
        "agent": agent,
        "inputs": {},
        "outputs": {},
        "envs": {},
        "debug": False,
        "home": "/workspace",
        "transcripts": transcripts,
        "proxy_log": "/p.log",
        "effort": "high",
        "model": "claude-opus-5",
    }


@pytest.fixture
def docker():
    with patch("agent_harness_sandbox.run_agent_harness_sandbox.docker", autospec=True) as m:
        m.run.return_value = "output"
        yield m


@pytest.fixture
def lockdown():
    with patch("agent_harness_sandbox.run_agent_harness_sandbox.lockdown", autospec=True) as m:
        jail = Mock(network="jail-net", envs={"HTTPS_PROXY": "http://proxy:8888"})
        m.return_value.__enter__.return_value = jail
        yield m


@pytest.fixture
def sandbox_dir():
    with (
        patch("agent_harness_sandbox.run_agent_harness_sandbox.SANDBOX_DIR", Path("/sandbox")),
        patch(
            "agent_harness_sandbox.run_agent_harness_sandbox.BASE_DOCKERFILE",
            Path("/sandbox/Dockerfile"),
        ),
    ):
        yield Path("/sandbox")


@pytest.fixture
def run(docker, lockdown, sandbox_dir, options):
    def call(**overrides):
        return run_agent_harness_sandbox("hi", **{**options, **overrides})

    return call


def volumes(docker) -> dict[str, tuple[str, str]]:
    return {target: (source, mode) for source, target, mode in docker.run.call_args.kwargs["volumes"]}


def describe_signature():
    def it_requires_every_option(options):
        for option in sorted(options):
            with pytest.raises(TypeError):
                run_agent_harness_sandbox("hi", **{k: v for k, v in options.items() if k != option})

    def it_takes_its_options_by_keyword_only(agent):
        with pytest.raises(TypeError):
            run_agent_harness_sandbox(
                "hi", agent, {}, {}, {}, False, "/workspace", "/t", "/p.log", "high", "m"
            )


def describe_run():
    def it_returns_the_container_output(run):
        assert run() == "output"

    def it_runs_the_agents_own_image_and_command(run, docker):
        run()
        assert docker.run.call_args.args == ("an-agent:latest", ["an-agent"])
        assert docker.run.call_args.kwargs["remove"] is True

    def it_casts_home_to_a_string_workdir(run, docker):
        run(home=Path("/elsewhere"))
        assert docker.run.call_args.kwargs["workdir"] == "/elsewhere"


def describe_command():
    def it_asks_the_agent_for_the_argv(run, agent):
        run(effort="low", model="claude-opus-5")
        agent.command.assert_called_once_with("hi", effort="low", model="claude-opus-5")


def describe_build():
    def it_builds_every_run(run, docker):
        """A static tag makes the build the only thing that can notice an edited context."""
        run()
        run()
        assert docker.build.call_count == 4

    def it_never_asks_whether_the_image_is_already_there(run, docker):
        run()
        docker.image.exists.assert_not_called()

    def it_builds_and_runs_the_same_image(run, docker):
        run()
        assert docker.build.call_args.kwargs["tags"] == docker.run.call_args.args[0]

    def it_builds_the_base_before_the_agent_layer(run, docker):
        run()
        assert [call.kwargs["tags"] for call in docker.build.call_args_list] == [
            "agent-harness-sandbox-base:latest",
            "an-agent:latest",
        ]

    def it_builds_the_shipped_context_quietly(run, docker, sandbox_dir):
        run()
        assert [call.args for call in docker.build.call_args_list] == [(sandbox_dir,), (sandbox_dir,)]
        assert [call.kwargs["file"] for call in docker.build.call_args_list] == [
            Path("/sandbox/Dockerfile"),
            Path("/sandbox/Dockerfile.an-agent"),
        ]
        assert [call.kwargs["progress"] for call in docker.build.call_args_list] == [False, False]

    def it_streams_build_output_in_debug(run, docker):
        run(debug=True)
        assert docker.build.call_args.kwargs["progress"] == "tty"


def describe_auth():
    def it_stages_the_agents_credentials_into_the_directory_it_mounts(run, docker, agent):
        run()
        [staged] = agent.stage_auth.call_args.args
        assert volumes(docker)["/home/node/.an-agent"] == (str(staged), "rw")

    def it_owns_the_staging_directory_rather_than_the_agent(run, agent):
        run()
        [staged] = agent.stage_auth.call_args.args
        assert not staged.exists()


def describe_volumes():
    def it_mounts_the_staged_credentials_at_the_agents_home(run, docker):
        run()
        assert volumes(docker)["/home/node/.an-agent"][1] == "rw"

    def it_mounts_the_home_before_the_transcripts_nested_inside_it(run, docker):
        """A bind nested in another is only reachable if its parent is mounted first."""
        run()
        assert [target for _, target, _ in docker.run.call_args.kwargs["volumes"]][:2] == [
            "/home/node/.an-agent",
            "/home/node/.an-agent/sessions",
        ]

    def it_mounts_the_transcripts_where_the_agent_writes_them(run, docker, transcripts):
        run()
        assert volumes(docker)["/home/node/.an-agent/sessions"] == (
            str(transcripts.resolve()),
            "rw",
        )

    def it_mounts_each_input_read_only(run, docker, tmp_path):
        """The caller's tree is the reference; a run that could edit it would rewrite history."""
        data = tmp_path / "data"
        data.mkdir()
        more = tmp_path / "more"
        more.mkdir()
        run(inputs={data: "/work/in", more: "/work/more"})
        assert volumes(docker)["/work/in"] == (str(data.resolve()), "ro")
        assert volumes(docker)["/work/more"] == (str(more.resolve()), "ro")

    def it_mounts_each_output_writable(run, docker, tmp_path):
        out = tmp_path / "out"
        out.mkdir()
        run(outputs={out: "/work/out"})
        assert volumes(docker)["/work/out"] == (str(out.resolve()), "rw")

    def it_mounts_nothing_else_when_the_caller_asks_for_nothing(run, docker):
        run()
        assert len(docker.run.call_args.kwargs["volumes"]) == 2

    def it_casts_a_path_target_to_a_string(run, docker, tmp_path):
        data = tmp_path / "data"
        data.mkdir()
        run(inputs={data: Path("/work/in")})
        assert "/work/in" in volumes(docker)

    def it_refuses_a_source_that_is_not_there(run, tmp_path):
        """docker answers a missing source by creating it root-owned, which nobody wants."""
        with pytest.raises(SandboxError, match="does not exist"):
            run(inputs={tmp_path / "gone": "/work/in"})


def describe_lockdown():
    def it_joins_the_locked_down_network(run, docker):
        run()
        assert docker.run.call_args.kwargs["networks"] == ["jail-net"]

    def it_pins_the_allowlist_the_agent_named(run, lockdown):
        run()
        assert lockdown.call_args.args[0] == ("api.example.com",)

    def it_hands_the_container_the_proxy_env(run, docker):
        run()
        assert docker.run.call_args.kwargs["envs"]["HTTPS_PROXY"] == "http://proxy:8888"

    def it_lets_a_caller_env_win_over_the_proxys(run, docker):
        run(envs={"HTTPS_PROXY": "http://elsewhere"})
        assert docker.run.call_args.kwargs["envs"]["HTTPS_PROXY"] == "http://elsewhere"

    def it_forwards_the_proxy_log_path(run, lockdown):
        run(proxy_log="/tmp/proxy.log")
        assert lockdown.call_args.kwargs["log_path"] == "/tmp/proxy.log"

    def it_forwards_the_debug_flag(run, lockdown):
        run(debug=True)
        assert lockdown.call_args.kwargs["debug"] is True


def describe_hardening():
    def it_drops_every_capability(run, docker):
        run()
        assert docker.run.call_args.kwargs["cap_drop"] == ["ALL"]

    def it_forbids_privilege_escalation(run, docker):
        run()
        assert docker.run.call_args.kwargs["security_options"] == ["no-new-privileges"]
