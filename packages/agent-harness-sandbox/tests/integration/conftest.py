from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def claude_home(tmp_path: Path) -> Path:
    home = tmp_path / "claude-home"
    home.mkdir()
    (home / ".credentials.json").write_text("{}")
    with patch("agent_harness_sandbox.agents.ClaudeAgent.CLAUDE_HOME", home):
        yield home


@pytest.fixture
def pi_home(tmp_path: Path) -> Path:
    home = tmp_path / "pi-home"
    home.mkdir()
    (home / "auth.json").write_text("{}")
    (home / "models.json").write_text("{}")
    with patch("agent_harness_sandbox.agents.PiAgent.PI_HOME", home):
        yield home


@pytest.fixture
def docker_calls() -> list:
    return []


@pytest.fixture
def builds() -> list[str]:
    return []


@pytest.fixture
def docker(docker_calls, builds):
    with (
        patch("agent_harness_sandbox.run_agent_harness_sandbox.docker", autospec=True) as m,
        patch("agent_harness_sandbox.utils.lockdown.docker", autospec=True) as proxy,
        patch("agent_harness_sandbox.utils.lockdown.docker_cli", autospec=True),
    ):
        proxy.run.return_value = "proxy-container"
        proxy.logs.return_value = ""
        proxy.network.docker_cmd = ["docker"]

        def record_build(_context, tags, **_options):
            builds.append(tags)

        m.build.side_effect = record_build
        proxy.build.side_effect = record_build

        def fake_run(
            tag,
            cmd,
            envs=None,
            volumes=None,
            remove=None,
            workdir=None,
            networks=None,
            cap_drop=None,
            security_options=None,
        ):
            docker_calls.append(
                {
                    "tag": tag,
                    "cmd": cmd,
                    "envs": envs,
                    "volumes": volumes,
                    "networks": networks,
                    "cap_drop": cap_drop,
                    "security_options": security_options,
                    "files": {
                        target: sorted(p.name for p in Path(src).iterdir())
                        for src, target, _ in volumes
                    },
                }
            )
            return "container output"

        m.run.side_effect = fake_run
        yield m
