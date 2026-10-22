import json
from pathlib import Path
import shlex
from unittest.mock import patch

import pytest
from botbox import RunResult

from gbnf_experiment import config

# What the fake prepare container leaves in /shared: upstream layout, both
# languages present the way a target-integration condition leaves them.
SHARED = (
    "javascript/integration-tests/generated/iteration/iteration.test.ts",
    "javascript/package.json",
    "python/gbnf/__init__.py",
    "python/pyproject.toml",
)
SANDBOX_IMAGE_ID = "sha256:fake-sandbox-image"
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
    with patch.object(config, "PREPARED_DIRECTORY", directory):
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
    """The agent's exit code, as the box reports it."""
    return [0]


@pytest.fixture
def agent_stderr() -> list:
    """What the agent writes to stderr."""
    return [""]


@pytest.fixture
def box_error() -> list:
    """What entering the box raises, if anything."""
    return []


@pytest.fixture(autouse=True)
def botbox(porting_calls, port_result, exit_code, agent_stderr, box_error):
    """Botbox, faked where port_codebase imports it.

    Standing in for the model, the run writes a plausible port into /target and
    returns a transcript and a proxy log.
    """

    class FakeBotbox:
        def __init__(self, agent, *, dockerfile=None, allow=()):
            self.agent = agent

        async def __aenter__(self):
            if box_error:
                raise box_error[0]
            return self

        async def __aexit__(self, *exc_info):
            return None

        async def run(self, command, *, mounts=(), workdir=None):
            porting_calls.append(
                {
                    "prompt": shlex.split(command)[2],
                    "command": shlex.split(command),
                    "volumes": mounts,
                    "container_tree": sorted(
                        f"{target}/{path.relative_to(source)}"
                        for source, target, _ in mounts
                        if str(target) in ("/input", "/target")
                        for path in Path(source).rglob("*")
                        if path.is_file()
                    ),
                }
            )
            (volume_source(mounts, "/target") / "ported.py").write_text("class GBNF: ...")
            return RunResult(
                stdout=json.dumps(port_result),
                stderr=agent_stderr[0],
                exit_code=exit_code[0],
                transcript={TRANSCRIPT_PATH: TRANSCRIPT},
                proxy=PROXY_LOG,
                image="botbox-claude:latest",
            )

    with patch("port_codebase.port_codebase.Botbox", FakeBotbox):
        yield


@pytest.fixture
def docker_daemon(builds, prepare_calls):
    """The daemon, faked where python_on_whales defines it, for the prepare image.

    The prepare container copies a fixed /shared into /prepared-output.
    """
    with (
        patch("python_on_whales.docker.build", autospec=True) as build,
        patch("python_on_whales.docker.run", autospec=True) as run,
    ):

        def fake_build(context, **options):
            builds.append({"context": Path(context), **options})

        def fake_run(image, command=(), volumes=(), **options):
            prepare_calls.append({"image": image, "command": command, "volumes": volumes, **options})
            output = volume_source(volumes, "/prepared-output")
            for name in SHARED:
                (output / name).parent.mkdir(parents=True, exist_ok=True)
                (output / name).write_text(name)
            return ""

        build.side_effect = fake_build
        run.side_effect = fake_run
        yield run
