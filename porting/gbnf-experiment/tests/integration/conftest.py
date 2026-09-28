import json
from pathlib import Path
from unittest.mock import patch

import pytest

from gbnf_experiment.config import settings

GRAMMAR_FIXTURES = ("arithmetic", "json", "simple")
MANIFESTS = {"typescript": "package.json", "python": "pyproject.toml"}
SOURCE_DIRECTORIES = {"typescript": "src", "python": "gbnf"}
IMPLEMENTATIONS = {"typescript": "index.ts", "python": "index.py"}
COLOCATED_TESTS = {"typescript": "index.test.ts", "python": "index_test.py"}
DEV_HARNESS = (
    "dev/browser/debug/index.html",
    "dev/browser/debug/package.json",
    "dev/node/src/commands/parse.ts",
)
SANDBOX_IMAGE_ID = "sha256:fake-sandbox-image"
CLAUDE_CONFIG_TARGET = "/home/node/.claude"
FAKE_CREDENTIALS = '{"fake": "integration-suite"}'


def volume_source(volumes, target):
    [source] = [source for source, mount, _ in volumes if str(mount) == target]
    return Path(source)


def write_prepared_output(directory: Path) -> None:
    """What the real gbnf-prepare container emits into /prepared-output."""
    for language in ("typescript", "python"):
        source = directory / "source" / language
        source.mkdir(parents=True)
        (source / MANIFESTS[language]).write_text("{}")
        code = source / SOURCE_DIRECTORIES[language]
        code.mkdir()
        (code / IMPLEMENTATIONS[language]).write_text(f"{language} source")
        (code / COLOCATED_TESTS[language]).write_text(f"{language} tests")
        if language == "typescript":
            for name in DEV_HARNESS:
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("dev harness")

        tests = directory / "tests" / language
        (tests / "iteration").mkdir(parents=True)
        (tests / "validation").mkdir(parents=True)
        (tests / "iteration" / f"grammars_test.{language}").write_text(
            f"{language} iteration cases"
        )
        (tests / "validation" / f"validate_test.{language}").write_text(
            f"{language} validation cases"
        )

    grammars = directory / "tests" / "python" / "iteration" / "grammars"
    grammars.mkdir()
    for name in GRAMMAR_FIXTURES:
        (grammars / f"{name}.gbnf").write_text("root ::= 'x'")
        (grammars / f"{name}.json").write_text('["x"]')


@pytest.fixture
def data_directory(tmp_path):
    directory = tmp_path / "data"
    with patch.object(settings, "data_directory", directory):
        yield directory


@pytest.fixture(autouse=True)
def prepared_directory(tmp_path):
    """The prepared corpus cache, redirected out of the user's real ~/.cache.

    Autouse: the cache no longer sits under data_directory, so redirecting that
    alone would leave any test that prepares writing into the host's cache.
    """
    directory = tmp_path / "cache" / "prepared"
    with patch.object(settings, "prepared_directory", directory):
        yield directory


@pytest.fixture
def prepare_docker():
    """The gbnf-prepare container, faked at the docker boundary."""
    with patch(
        "gbnf_experiment.prepare_filesystem.prepare_reference_implementation.docker",
        autospec=True,
    ) as m:

        def fake_run(tag, user=None, volumes=None, remove=None):
            write_prepared_output(volume_source(volumes, "/prepared-output"))
            return "prepared"

        m.run.side_effect = fake_run
        yield m


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
    with patch("agent_harness_sandbox.agents.ClaudeAgent.CLAUDE_HOME", home):
        yield home


@pytest.fixture
def porting_calls() -> list:
    return []


@pytest.fixture
def port_result() -> dict:
    """What `claude -p --output-format json` prints, which is what run() banks."""
    return {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "num_turns": 12,
        "total_cost_usd": 3.21,
    }


@pytest.fixture
def lockdown_docker():
    """The network jail's docker client, faked at the docker boundary.

    lockdown holds its own docker binding and shells out to the CLI for
    `network create --internal`, so faking run_agent_harness_sandbox's binding leaves it
    building the proxy image, running a real tinyproxy container and creating
    and removing two real networks on every run. First-party lockdown still
    runs, so `jail.envs` and `jail.network` are the real thing.
    """
    with (
        patch("agent_harness_sandbox.utils.lockdown.docker", autospec=True) as m,
        patch("agent_harness_sandbox.utils.lockdown.docker_utils", autospec=True),
    ):
        m.image.exists.return_value = True
        m.network.docker_cmd = ["docker"]
        m.logs.return_value = ""
        yield m


@pytest.fixture
def agent_image_docker():
    """agent-harness-sandbox's image builds, faked at the docker boundary."""
    with patch("agent_harness_sandbox.build_agent_image.docker", autospec=True) as m:
        yield m


@pytest.fixture
def porting_docker(porting_calls, claude_home, lockdown_docker, agent_image_docker, port_result):
    """The porting sandbox, faked at the docker boundary.

    Standing in for the model: instead of running claude, it writes a
    plausible ported implementation into the bound output directory.
    """
    with patch("agent_harness_sandbox.run_agent_harness_sandbox.docker", autospec=True) as m:
        m.image.exists.return_value = True

        def fake_run(tag, cmd, envs=None, volumes=None, **_):
            output = volume_source(volumes, "/workspace/ported_implementation")
            credentials = volume_source(volumes, CLAUDE_CONFIG_TARGET)
            porting_calls.append(
                {
                    "prompt": cmd[-1],
                    "command": list(cmd),
                    "volumes": volumes,
                    "envs": envs,
                    "credentials": (credentials / ".credentials.json").read_text(),
                    "container_tree": sorted(
                        f"{target}/{path.relative_to(source)}"
                        for source, target, _ in volumes
                        if str(target).startswith("/workspace")
                        for path in Path(source).rglob("*")
                        if path.is_file()
                    ),
                }
            )
            (output / "ported.py").write_text("class GBNF: ...")
            return json.dumps(port_result)

        m.run.side_effect = fake_run
        yield m
