from pathlib import Path
from unittest.mock import patch

import pytest


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
def builds() -> list[str]:
    return []


@pytest.fixture
def docker(docker_calls, builds):
    """Hold the daemon back and let everything above it run.

    The runner and the lockdown share one `python_on_whales.docker`, so the
    doubles go on that object rather than on each module that imported it —
    which is also the shape a real run has.
    """
    with (
        patch("python_on_whales.docker.build", autospec=True) as build,
        patch("python_on_whales.docker.run", autospec=True) as run,
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
            if options.get("detach"):
                return "proxy-container"
            volumes = options["volumes"]
            docker_calls.append(
                {
                    "tag": tag,
                    "cmd": cmd,
                    "envs": options.get("envs"),
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
            return "container output"

        run.side_effect = record_run
        yield run
