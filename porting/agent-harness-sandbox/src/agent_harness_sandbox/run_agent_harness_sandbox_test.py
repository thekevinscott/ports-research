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
def options(agent, transcripts, tmp_path):
    caller_input = tmp_path / "input"
    caller_input.mkdir()
    return {
        "agent": agent,
        "image": "a-workspace:latest",
        "input": caller_input,
        "outputs": {},
        "envs": {},
        "setup": None,
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
        m.run.return_value = "container"
        m.execute.return_value = "output"
        yield m


@pytest.fixture
def lockdown():
    with patch("agent_harness_sandbox.run_agent_harness_sandbox.lockdown", autospec=True) as m:
        jail = Mock(network="jail-net", egress="egress-net", envs={"HTTPS_PROXY": "http://proxy:8888"})
        m.return_value.__enter__.return_value = jail
        yield m


@pytest.fixture
def run(docker, lockdown, options):
    def call(**overrides):
        return run_agent_harness_sandbox("hi", **{**options, **overrides})

    return call


def volumes(docker) -> dict[str, tuple[str, str]]:
    return {target: (source, mode) for source, target, mode in docker.run.call_args.kwargs["volumes"]}


@pytest.fixture
def mounted(docker) -> dict[str, dict[str, str]]:
    """What each volume source holds while the fake run is in flight, before the copies go."""
    seen: dict[str, dict[str, str]] = {}

    def capture(*_args, **kwargs):
        for source, target, _ in kwargs["volumes"]:
            root = Path(source)
            seen[str(target)] = {
                str(p.relative_to(root)): p.read_text() for p in sorted(root.rglob("*")) if p.is_file()
            }
        return "output"

    docker.run.side_effect = capture
    return seen


def describe_signature():
    def it_requires_every_option(options):
        for option in sorted(options):
            with pytest.raises(TypeError):
                run_agent_harness_sandbox("hi", **{k: v for k, v in options.items() if k != option})

    def it_takes_its_options_by_keyword_only(agent):
        with pytest.raises(TypeError):
            run_agent_harness_sandbox(
                "hi", agent, "a-workspace:latest", {}, {}, {}, False, "/workspace", "/t", "/p.log", "high", "m"
            )


def describe_run():
    def it_returns_the_agents_output(run):
        assert run() == "output"

    def it_starts_the_image_it_was_given_holding_open(run, docker):
        """The agent is exec'd in, so a setup step can run in the same container first."""
        run()
        assert docker.run.call_args.args == ("a-workspace:latest", ["sleep", "infinity"])
        assert docker.run.call_args.kwargs["detach"] is True

    def it_execs_the_agents_command_in_that_container(run, docker):
        run()
        assert docker.execute.call_args.args == ("container", ["an-agent"])

    def it_removes_the_container_afterwards(run, docker):
        run()
        docker.container.remove.assert_called_once_with("container", force=True)

    def it_removes_the_container_when_the_agent_fails(run, docker):
        docker.execute.side_effect = RuntimeError("exit 1")
        with pytest.raises(RuntimeError):
            run()
        docker.container.remove.assert_called_once_with("container", force=True)

    def it_builds_nothing(run, docker):
        """The caller builds, so an image derived from the agent's can go on top."""
        run()
        docker.build.assert_not_called()

    def it_casts_home_to_a_string_workdir(run, docker):
        run(home=Path("/elsewhere"))
        assert docker.run.call_args.kwargs["workdir"] == "/elsewhere"
        assert docker.execute.call_args.kwargs["workdir"] == "/elsewhere"


def describe_command():
    def it_asks_the_agent_for_the_argv(run, agent):
        run(effort="low", model="claude-opus-5")
        agent.command.assert_called_once_with("hi", effort="low", model="claude-opus-5")


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

    def it_mounts_a_writable_copy_of_the_input_folder_at_a_fixed_path(run, docker, tmp_path):
        data = tmp_path / "data"
        data.mkdir()
        (data / "a.txt").write_text("x")
        run(input=data)
        source, mode = volumes(docker)["/input"]
        assert source != str(data.resolve())
        assert mode == "rw"

    def it_copies_the_input_folders_files_into_what_it_mounts(run, docker, tmp_path, mounted):
        data = tmp_path / "data"
        (data / "nested").mkdir(parents=True)
        (data / "nested" / "a.txt").write_text("x")
        run(input=data)
        assert mounted["/input"] == {"nested/a.txt": "x"}

    def it_discards_the_input_copy_after_the_run(run, docker, tmp_path):
        data = tmp_path / "data"
        data.mkdir()
        run(input=data)
        assert not Path(volumes(docker)["/input"][0]).exists()

    def it_keeps_container_writes_out_of_the_callers_input_folder(run, docker, tmp_path):
        data = tmp_path / "data"
        data.mkdir()

        def write_into_the_mount(*_args, **kwargs):
            source = dict((target, src) for src, target, _ in kwargs["volumes"])["/input"]
            (Path(source) / "installed.txt").write_text("from the container")
            return "output"

        docker.run.side_effect = write_into_the_mount
        run(input=data)
        assert sorted(p.name for p in data.iterdir()) == []

    def it_mounts_each_output_writable(run, docker, tmp_path):
        out = tmp_path / "out"
        out.mkdir()
        run(outputs={out: "/work/out"})
        assert volumes(docker)["/work/out"] == (str(out.resolve()), "rw")

    def it_mounts_only_credentials_transcripts_and_input_when_there_are_no_outputs(run, docker):
        run()
        assert len(docker.run.call_args.kwargs["volumes"]) == 3

    def it_refuses_a_source_that_is_not_there(run, tmp_path):
        with pytest.raises(SandboxError, match="does not exist"):
            run(transcripts=tmp_path / "gone")


def describe_lockdown():
    def it_joins_the_locked_down_network(run, docker):
        run()
        assert docker.run.call_args.kwargs["networks"] == ["jail-net"]

    def it_pins_the_allowlist_the_agent_named(run, lockdown):
        run()
        assert lockdown.call_args.args[0] == ("api.example.com",)

    def it_hands_the_agent_the_proxy_env(run, docker):
        run()
        assert docker.execute.call_args.kwargs["envs"]["HTTPS_PROXY"] == "http://proxy:8888"

    def it_lets_a_caller_env_win_over_the_proxys(run, docker):
        run(envs={"HTTPS_PROXY": "http://elsewhere"})
        assert docker.execute.call_args.kwargs["envs"]["HTTPS_PROXY"] == "http://elsewhere"

    def it_hands_the_container_itself_only_the_callers_env(run, docker):
        run(envs={"A": "1"})
        assert docker.run.call_args.kwargs["envs"] == {"A": "1"}

    def it_forwards_the_proxy_log_path(run, lockdown):
        run(proxy_log="/tmp/proxy.log")
        assert lockdown.call_args.kwargs["log_path"] == "/tmp/proxy.log"

    def it_forwards_the_debug_flag(run, lockdown):
        run(debug=True)
        assert lockdown.call_args.kwargs["debug"] is True


def describe_setup():
    SETUP = ["pnpm", "install"]

    def it_runs_nothing_before_the_agent_by_default(run, docker):
        run()
        assert docker.execute.call_count == 1
        docker.network.connect.assert_not_called()

    def it_runs_the_setup_command_in_the_same_container_before_the_agent(run, docker):
        run(setup=SETUP)
        assert [c.args for c in docker.execute.call_args_list] == [
            ("container", SETUP),
            ("container", ["an-agent"]),
        ]

    def it_opens_the_egress_network_for_setup_and_closes_it_before_the_agent(run, docker):
        """The install reaches its registry directly; the agent still sees only its allowlist."""
        run(setup=SETUP)
        steps = [c for c in docker.mock_calls if c[0] in ("network.connect", "network.disconnect", "execute")]
        assert [(name, args[:2]) for name, args, _ in steps] == [
            ("network.connect", ("egress-net", "container")),
            ("execute", ("container", SETUP)),
            ("network.disconnect", ("egress-net", "container")),
            ("execute", ("container", ["an-agent"])),
        ]

    def it_withholds_the_proxy_env_from_setup(run, docker):
        run(setup=SETUP, envs={"A": "1"})
        assert docker.execute.call_args_list[0].kwargs["envs"] == {"A": "1"}

    def it_runs_setup_in_the_home_directory(run, docker):
        run(setup=SETUP, home="/workspace")
        assert docker.execute.call_args_list[0].kwargs["workdir"] == "/workspace"

    def it_removes_the_container_when_setup_fails(run, docker):
        docker.execute.side_effect = RuntimeError("exit 1")
        with pytest.raises(RuntimeError):
            run(setup=SETUP)
        docker.container.remove.assert_called_once_with("container", force=True)


def describe_hardening():
    def it_drops_every_capability(run, docker):
        run()
        assert docker.run.call_args.kwargs["cap_drop"] == ["ALL"]

    def it_forbids_privilege_escalation(run, docker):
        run()
        assert docker.run.call_args.kwargs["security_options"] == ["no-new-privileges"]
