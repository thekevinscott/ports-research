from pathlib import Path
from unittest.mock import patch

import pytest

from agent_harness_sandbox.config import PROXY_IMAGE


@pytest.fixture
def claude_home(tmp_path: Path) -> Path:
    home = tmp_path / "claude-home"
    home.mkdir()
    (home / ".credentials.json").write_text("{}")
    return home


@pytest.fixture
def pi_home(tmp_path: Path) -> Path:
    home = tmp_path / "pi-home"
    home.mkdir()
    (home / "auth.json").write_text("{}")
    (home / "models.json").write_text("{}")
    return home


@pytest.fixture
def docker_calls() -> list:
    return []


@pytest.fixture
def execs() -> list:
    return []


@pytest.fixture
def builds() -> list[str]:
    return []


@pytest.fixture
def docker(docker_calls, execs, builds):
    """Hold the daemon back and let everything above it run.

    The runner and the lockdown share one `python_on_whales.docker`, so the
    doubles go on that object rather than on each module that imported it —
    which is also the shape a real run has.
    """
    with (
        patch("python_on_whales.docker.build", autospec=True) as build,
        patch("python_on_whales.docker.run", autospec=True) as run,
        patch("python_on_whales.docker.execute", autospec=True) as execute,
        patch("python_on_whales.docker.logs", autospec=True) as logs,
        patch("python_on_whales.docker.network", autospec=True) as network,
        patch("python_on_whales.docker.container", autospec=True),
        patch("python_on_whales.utils.run", autospec=True),
    ):
        network.docker_cmd = ["docker"]
        logs.return_value = ""

        def record_build(_context, tags, **_options):
            builds.append(tags)

        build.side_effect = record_build

        def record_run(tag, cmd=None, **options):
            # The proxy sidecar is the lockdown's own plumbing, not the run under test.
            if tag == PROXY_IMAGE:
                return "proxy-container"
            volumes = options["volumes"]
            docker_calls.append(
                {
                    "tag": tag,
                    "cmd": cmd,
                    "volumes": volumes,
                    "networks": options.get("networks"),
                    "cap_drop": options.get("cap_drop"),
                    "security_options": options.get("security_options"),
                    "files": {
                        target: sorted(p.name for p in Path(src).iterdir())
                        for src, target, _ in volumes
                    },
                }
            )
            return "sandbox-container"

        def record_exec(container, cmd, **options):
            execs.append(
                {
                    "container": container,
                    "cmd": cmd,
                    "envs": options.get("envs"),
                    "workdir": options.get("workdir"),
                    "networks": sorted(
                        {c.args[0] for c in network.connect.call_args_list if c.args[1] == container}
                        - {c.args[0] for c in network.disconnect.call_args_list if c.args[1] == container}
                    ),
                }
            )
            return "container output"

        run.side_effect = record_run
        execute.side_effect = record_exec
        yield run
