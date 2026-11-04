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
    async def run(resume=False):
        return await port_codebase(
            agent=agent,
            prompt="Port it.",
            source=source,
            output=output,
            artifacts=output.parent / "artifacts",
            memory="4g",
            container="ports-run",
            resume=resume,
        )

    return run


def describe_port_codebase():
    async def it_builds_its_box_from_the_packaged_dockerfile(run, box, agent):
        await run()

        assert box.boxes == [{"agent": agent, "dockerfile": PACKAGE / "Dockerfile", "allow": (), "memory": "4g"}]

    async def it_mounts_the_source_read_only_and_the_output_read_write(run, box, source, output):
        await run()

        [call] = box.runs
        assert call["mounts"] == ((source, "/input", "ro"), (output, "/target", "rw"))

    async def it_starts_in_the_output(run, box):
        await run()

        [call] = box.runs
        assert call["workdir"] == "/target"

    async def it_runs_claude_on_the_system_prompt_with_the_callers_appended(run, box):
        await run()

        [call] = box.runs
        words = shlex.split(call["command"])
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

    async def it_keeps_the_box_result_and_writes_its_output_separately(run, box, output):
        box.stdout = '{"is_error": false}'
        box.exit_code = 3

        result = await run()

        assert result.exit_code == 3
        assert (output.parent / "artifacts" / "stdout.txt").read_text() == '{"is_error": false}'
        assert box.runs[0]["output"] == output.parent / "artifacts"

    async def it_creates_the_output_before_mounting_it(run, output):
        await run()

        assert output.is_dir()

    async def it_keeps_a_fresh_run_under_the_callers_name(run, box):
        await run()

        [call] = box.runs
        assert call["keep"] == "ports-run"

    async def it_resumes_the_kept_container_with_continue(run, box):
        await run(resume=True)

        [call] = box.runs
        assert call["restart"] == "ports-run"
        words = shlex.split(call["command"])
        assert words[:3] == ["claude", "-p", "Continue the port where you left off."]
        assert "--continue" in words

    @pytest.mark.parametrize("resume", [False, True])
    async def it_removes_the_kept_container_and_its_volume_on_exit_0(run, box, removed, resume):
        box.exit_code = 0

        await run(resume=resume)

        assert removed == ["container:ports-run", "volume:botbox-run-token-of-ports-run"]

    @pytest.mark.parametrize("resume", [False, True])
    async def it_leaves_the_kept_container_when_the_agent_fails(run, box, removed, resume):
        box.exit_code = 1

        await run(resume=resume)

        assert removed == []
