import shlex
from pathlib import Path

import pytest
from botbox import ClaudeAgent

from port_codebase import port_codebase

PACKAGE = Path(__file__).parents[2] / "src" / "port_codebase"


@pytest.fixture
def agent(tmp_path: Path) -> ClaudeAgent:
    home = tmp_path / "claude-home"
    home.mkdir()
    (home / ".credentials.json").write_text("{}")
    return ClaudeAgent(model="claude-opus-5", effort="high", host_home=home)


@pytest.fixture
def source(tmp_path: Path) -> Path:
    directory = tmp_path / "source"
    directory.mkdir()
    return directory


@pytest.fixture
def output(tmp_path: Path) -> Path:
    return tmp_path / "output"


@pytest.fixture
def run(agent, source, output):
    def run():
        return port_codebase(agent=agent, prompt="Port it.", source=source, output=output)

    return run


def describe_port_codebase():
    def it_builds_its_image_from_the_packaged_dockerfile(run, daemon):
        run()

        [layer] = [b for b in daemon.builds if b["file"] == PACKAGE / "Dockerfile"]
        assert layer["context"] == PACKAGE
        assert daemon.agent["image"] == layer["tags"]

    def it_mounts_the_source_read_only_and_the_output_read_write(run, daemon, source, output):
        run()

        volumes = daemon.agent["volumes"]
        assert (str(source.resolve()), "/input", "ro") in volumes
        assert (str(output.resolve()), "/target", "rw") in volumes

    def it_starts_in_the_output(run, daemon):
        run()

        assert daemon.agent["workdir"] == "/target"

    def it_runs_claude_on_the_system_prompt_with_the_callers_appended(run, daemon):
        run()

        [shell, flag, command] = daemon.agent["command"]
        assert (shell, flag) == ("sh", "-c")
        words = shlex.split(command)
        assert words[:2] == ["claude", "-p"]
        assert words[2].startswith("You are porting software from one language to another.")
        assert words[2].endswith("\n\nPort it.\n")
        assert words[3:] == [
            "--output-format",
            "json",
            "--dangerously-skip-permissions",
            "--strict-mcp-config",
            "--model",
            "claude-opus-5",
            "--effort",
            "high",
        ]

    def it_returns_what_the_container_printed(run, daemon):
        daemon.stdout = b'{"is_error": false}'
        daemon.exit_code = 3

        result = run()

        assert (result.stdout, result.exit_code) == ('{"is_error": false}', 3)

    def it_creates_the_output_before_mounting_it(run, output):
        run()

        assert output.is_dir()

    def it_removes_its_container_once_the_run_returns(run, daemon):
        run()

        assert daemon.removed == [str(daemon.agent["handle"])]
