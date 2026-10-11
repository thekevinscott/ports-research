from pathlib import Path
from unittest.mock import patch

import pytest

from agent_harness_sandbox.utils.lockdown import lockdown

ALLOW = ("api.anthropic.com",)


@pytest.fixture
def docker():
    with patch("agent_harness_sandbox.utils.lockdown.docker", autospec=True) as m:
        m.run.return_value = "proxy-container"
        m.logs.return_value = 'NOTICE Proxying refused on filtered domain "github.com"\nINFO ok'
        m.network.docker_cmd = ["docker"]
        yield m


@pytest.fixture
def docker_cli():
    with patch("agent_harness_sandbox.utils.lockdown.docker_utils", autospec=True) as m:
        yield m.run


@pytest.fixture
def proxy_dir(tmp_path):
    directory = tmp_path / "proxy_context"
    directory.mkdir()
    with patch("agent_harness_sandbox.utils.lockdown.PROXY_DIR", directory):
        yield directory


@pytest.fixture
def log(tmp_path):
    return tmp_path / "proxy.log"


@pytest.fixture
def jail(docker, docker_cli, proxy_dir, log):
    def call(**overrides):
        options = {"allow": ALLOW, "debug": False, "log_path": log}
        return lockdown(**{**options, **overrides})

    return call


def allowlist(docker) -> str:
    [(source, target, mode)] = docker.run.call_args.kwargs["volumes"]
    assert (target, mode) == ("/etc/tinyproxy/filter", "ro")
    return Path(source).read_text()


def describe_signature():
    @pytest.mark.parametrize("option", ["allow", "debug", "log_path"])
    def it_requires_every_option(option):
        options = {"allow": ALLOW, "debug": False, "log_path": "/p.log"}
        with pytest.raises(TypeError):
            lockdown(**{k: v for k, v in options.items() if k != option})


def describe_lockdown():
    def it_yields_the_internal_network(jail):
        with jail() as net:
            assert net.network.startswith("agent-harness-sandbox-jail-")

    def it_points_the_proxy_env_at_the_sidecar(jail, docker):
        with jail() as net:
            name = docker.run.call_args.kwargs["name"]
            assert net.envs["HTTPS_PROXY"] == f"http://{name}:8888"
            assert net.envs["HTTP_PROXY"] == net.envs["HTTPS_PROXY"]
            assert net.envs["https_proxy"] == net.envs["HTTPS_PROXY"]

    def it_exempts_loopback_from_the_proxy(jail):
        with jail() as net:
            assert net.envs["NO_PROXY"] == "localhost,127.0.0.1"

    def it_names_resources_per_run(jail):
        with jail() as first, jail() as second:
            assert first.network != second.network

    def describe_the_network():
        def it_creates_the_sandbox_network_internal(jail, docker_cli):
            with jail() as net:
                pass
            [argv] = docker_cli.call_args.args
            assert argv == ["docker", "network", "create", "--internal", net.network]

        def it_creates_a_separate_egress_network_for_the_proxy(jail, docker):
            with jail():
                [egress] = docker.network.create.call_args.args
            assert "egress" in egress

        def it_puts_the_proxy_on_both(jail, docker):
            with jail() as net:
                assert docker.run.call_args.kwargs["networks"] == [
                    docker.network.create.call_args.args[0]
                ]
                docker.network.connect.assert_called_once_with(net.network, "proxy-container")

    def describe_the_allowlist():
        def it_anchors_each_host(jail, docker):
            with jail(allow=["api.anthropic.com", "example.test"]):
                assert allowlist(docker) == "^api\\.anthropic\\.com$\n^example\\.test$\n"

        def it_takes_the_allowlist_it_is_given(jail, docker):
            with jail(allow=ALLOW):
                assert allowlist(docker) == "^api\\.anthropic\\.com$\n"

        def it_is_readable_by_the_proxy_user(jail, docker):
            with jail():
                [(source, _, _)] = docker.run.call_args.kwargs["volumes"]
                assert Path(source).stat().st_mode & 0o044 == 0o044

    def describe_the_image():
        def it_builds_the_proxy_context_quietly(jail, docker, proxy_dir):
            with jail():
                pass
            [context] = docker.build.call_args.args
            assert (context, docker.build.call_args.kwargs["progress"]) == (proxy_dir, False)
            assert docker.build.call_args.kwargs["tags"] == "agent-harness-sandbox-proxy:latest"

        def it_runs_the_image_it_built(jail, docker):
            with jail():
                assert docker.run.call_args.args == (docker.build.call_args.kwargs["tags"],)

        def it_streams_build_output_in_debug(jail, docker):
            with jail(debug=True):
                pass
            assert docker.build.call_args.kwargs["progress"] == "tty"

        def it_rebuilds_every_run(jail, docker):
            """ConnectPort, FilterDefaultDeny and the setuid strip are baked into the image.

            Under a static tag the build is the only step that can notice an edit to
            any of them; skip it and the old rules keep serving with nothing wrong.
            """
            with jail():
                pass
            with jail():
                pass
            assert docker.build.call_count == 2

        def it_never_asks_whether_the_image_is_already_there(jail, docker):
            with jail():
                pass
            docker.image.exists.assert_not_called()

    def describe_hardening():
        def it_starts_the_proxy_with_the_capability_set_dropped(jail, docker):
            """The proxy is the only container with a route out; it runs hardened too."""
            with jail():
                assert docker.run.call_args.kwargs["cap_drop"] == ["ALL"]

        def it_starts_the_proxy_with_privilege_escalation_forbidden(jail, docker):
            with jail():
                assert docker.run.call_args.kwargs["security_options"] == ["no-new-privileges"]

    def describe_teardown():
        def it_removes_the_proxy_and_both_networks(jail, docker):
            with jail() as net:
                docker.container.remove.assert_not_called()
            docker.container.remove.assert_called_once_with("proxy-container", force=True)
            removed = [call.args[0] for call in docker.network.remove.call_args_list]
            assert removed[0] == net.network
            assert len(removed) == 2

        def it_tears_down_when_the_body_raises(jail, docker):
            with pytest.raises(RuntimeError):
                with jail():
                    raise RuntimeError("boom")
            docker.container.remove.assert_called_once()
            assert docker.network.remove.call_count == 2

        def it_removes_nothing_that_was_never_created(jail, docker):
            docker.network.create.side_effect = RuntimeError("no egress network")
            with pytest.raises(RuntimeError):
                with jail():
                    pass
            docker.container.remove.assert_not_called()
            docker.network.disconnect.assert_not_called()
            assert docker.network.remove.call_count == 1

        def it_removes_both_networks_even_when_the_proxy_removal_fails(jail, docker):
            """A flaky proxy removal must not strand the networks that shared its run.

            A hard SIGKILL orphans everything and is an accepted limitation.
            """
            docker.container.remove.side_effect = RuntimeError("proxy already gone")
            with jail():
                pass
            assert docker.network.remove.call_count == 2

        def it_removes_the_second_network_and_writes_the_log_when_the_first_removal_fails(
            jail, docker, log
        ):
            docker.network.remove.side_effect = [RuntimeError("network in use"), None]
            with jail():
                pass
            assert docker.network.remove.call_count == 2
            assert log.read_text() == docker.logs.return_value

        def it_frees_a_network_whose_proxy_outlived_its_removal(jail, docker):
            """A live endpoint pins its network, so the endpoint is detached first.

            `network rm` fails while a container is attached, and the suppression
            around it turns that into a stranded network nobody hears about.
            """
            docker.container.remove.side_effect = RuntimeError("proxy still running")
            with jail() as net:
                pass
            [egress] = docker.network.create.call_args.args
            steps = [
                (name, args[0])
                for name, args, _ in docker.mock_calls
                if name in {"network.disconnect", "network.remove"}
            ]
            assert steps == [
                ("network.disconnect", net.network),
                ("network.remove", net.network),
                ("network.disconnect", egress),
                ("network.remove", egress),
            ]
            assert docker.network.disconnect.call_args.kwargs == {"force": True}

        def it_disconnects_nothing_when_the_proxy_was_removed(jail, docker):
            """Detaching is recovery, not routine: a removed container has no endpoint."""
            with jail():
                pass
            docker.network.disconnect.assert_not_called()

        def it_keeps_the_previous_log_when_the_capture_fails(jail, docker, log):
            """An unread log is not an empty one, and the difference is the evidence.

            Writing `jail.log` unconditionally overwrote the host file with "" when
            `docker logs` raised, which reads like a run that was denied nothing.
            """
            log.write_text('NOTICE Proxying refused on filtered domain "github.com"\n')
            docker.logs.side_effect = RuntimeError("container already gone")
            with jail():
                pass
            assert log.read_text() == 'NOTICE Proxying refused on filtered domain "github.com"\n'

        def it_propagates_the_body_error_over_a_teardown_error(jail, docker):
            docker.container.remove.side_effect = RuntimeError("teardown boom")
            with pytest.raises(ValueError, match="body boom"):
                with jail():
                    raise ValueError("body boom")
            assert docker.network.remove.call_count == 2

        def it_drains_the_proxy_log_to_the_host(jail, docker, log):
            with jail():
                pass
            docker.logs.assert_called_once_with("proxy-container")
            assert log.read_text() == docker.logs.return_value
