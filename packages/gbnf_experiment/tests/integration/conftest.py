import json
from pathlib import Path
import shlex
from unittest.mock import MagicMock, patch

import pytest

from gbnf_experiment.config import settings

# What the fake prepare container leaves in /shared: upstream layout, both
# languages present the way a target-integration condition leaves them.
SHARED = (
    "javascript/integration-tests/generated/iteration/iteration.test.ts",
    "javascript/package.json",
    "python/gbnf/__init__.py",
    "python/pyproject.toml",
)
SANDBOX_IMAGE_ID = "sha256:fake-sandbox-image"
AGENT_HOME = "/home/node"
PROXY_IMAGE = "botbox-proxy:latest"
PREPARE_IMAGE = "gbnf-prepare:"
TRANSCRIPT_PATH = ".claude/projects/-target/session.jsonl"
TRANSCRIPT = '{"type": "user"}\n'
PROXY_LOG = "CONNECT api.anthropic.com:443\n"
FAKE_CREDENTIALS = '{"fake": "integration-suite"}'


def volume_source(volumes, target):
    [source] = [source for source, mount, _ in volumes if str(mount) == target]
    return Path(source)


@pytest.fixture
def data_directory(tmp_path):
    return tmp_path / "data"


@pytest.fixture(autouse=True)
def prepared_directory(tmp_path):
    """The prepared corpus cache, redirected out of the user's real ~/.cache.

    Autouse: the cache sits outside the output directory, so pointing output at
    tmp_path alone would leave any test that prepares writing into the host's cache.
    """
    directory = tmp_path / "cache" / "prepared"
    with patch.object(settings, "prepared_directory", directory):
        yield directory


@pytest.fixture(autouse=True)
def sandbox_image_id():
    """The manifest's image-id lookup, faked at the docker boundary.

    Autouse because every test that runs the experiment reaches the daemon
    whether or not it cares about the id. This layer mocks every external,
    docker included — a real daemon call here is out of policy regardless of
    what it costs. It cost ~30s across the suite.
    """
    with patch("gbnf_experiment.prepare_filesystem.write_manifest.docker", autospec=True) as m:
        m.image.inspect.return_value.id = SANDBOX_IMAGE_ID
        yield SANDBOX_IMAGE_ID


@pytest.fixture
def claude_home(tmp_path):
    """A throwaway ~/.claude, so nothing in this tier can reach the real token."""
    home = tmp_path / "claude-home"
    home.mkdir()
    (home / ".credentials.json").write_text(FAKE_CREDENTIALS)
    return home


@pytest.fixture
def porting_calls() -> list:
    return []


@pytest.fixture
def prepare_calls() -> list:
    return []


@pytest.fixture
def builds() -> list:
    return []


@pytest.fixture
def port_result() -> dict:
    """What `claude -p --output-format json` prints, which is what run() banks."""
    return {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "num_turns": 12,
    }


@pytest.fixture
def exit_code() -> list:
    """The agent container's exit code, as botbox's docker.wait returns it."""
    return [0]


@pytest.fixture
def agent_stderr() -> list:
    """What the agent container writes to stderr."""
    return [b""]


@pytest.fixture
def docker_daemon(builds, prepare_calls, porting_calls, port_result, exit_code, agent_stderr):
    """The daemon, faked where python_on_whales defines it, for both images.

    The prepare container copies a fixed /shared into /prepared-output. Standing
    in for the model, the agent container writes a plausible port into /target,
    a transcript into its home, and one line into the proxy's log.
    """
    with (
        patch("python_on_whales.docker.build", autospec=True) as build,
        patch("python_on_whales.docker.run", autospec=True) as run,
        patch("python_on_whales.docker.logs", autospec=True) as logs,
        patch("python_on_whales.docker.wait", autospec=True) as wait,
        patch("python_on_whales.docker.network", autospec=True) as network,
        patch("python_on_whales.docker.container", autospec=True),
        patch("python_on_whales.utils.run", autospec=True),
    ):
        network.docker_cmd = ["docker"]
        proxy_logs = []

        def fake_build(context, **options):
            builds.append({"context": Path(context), **options})

        def fake_run(image, command=(), volumes=(), **options):
            if image.startswith(PREPARE_IMAGE):
                prepare_calls.append({"image": image, "command": command, "volumes": volumes, **options})
                output = volume_source(volumes, "/prepared-output")
                for name in SHARED:
                    (output / name).parent.mkdir(parents=True, exist_ok=True)
                    (output / name).write_text(name)
                return ""
            if image == PROXY_IMAGE:
                proxy_logs.append(volume_source(volumes, "/var/log/tinyproxy") / "tinyproxy.log")
                return MagicMock(name=image)
            output = volume_source(volumes, "/target")
            porting_calls.append(
                {
                    "prompt": shlex.split(command[-1])[2],
                    "command": shlex.split(command[-1]),
                    "volumes": volumes,
                    "credentials": (
                        volume_source(volumes, AGENT_HOME) / ".claude" / ".credentials.json"
                    ).read_text(),
                    "container_tree": sorted(
                        f"{target}/{path.relative_to(source)}"
                        for source, target, _ in volumes
                        if str(target) in ("/input", "/target")
                        for path in Path(source).rglob("*")
                        if path.is_file()
                    ),
                }
            )
            (output / "ported.py").write_text("class GBNF: ...")
            transcript = volume_source(volumes, AGENT_HOME) / TRANSCRIPT_PATH
            transcript.parent.mkdir(parents=True)
            transcript.write_text(TRANSCRIPT)
            proxy_logs[-1].write_text(PROXY_LOG)
            return MagicMock(name=image)

        build.side_effect = fake_build
        run.side_effect = fake_run
        logs.side_effect = lambda *_args, **_options: iter(
            [("stdout", json.dumps(port_result).encode()), ("stderr", agent_stderr[0])]
        )
        wait.side_effect = lambda *_args: exit_code[0]
        yield run
