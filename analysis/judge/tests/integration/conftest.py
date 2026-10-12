import json
import os
import subprocess
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
FAKE_CLAUDE = Path(__file__).resolve().parent / "fake_claude.py"
FLAGS = ("include_unit_tests", "include_source_integration_tests", "include_target_integration_tests")
PORTS = {
    "javascript": {"src/index.ts": "export const GBNF = (g: string) => g;\n", "src/index.test.ts": "test('x', () => {});\n"},
    "python": {"gbnf/__init__.py": "def GBNF(g):\n    return g\n", "gbnf/gbnf_test.py": "def test_x():\n    pass\n"},
}


@pytest.fixture
def calls(tmp_path):
    """Every call the fake claude received: argv, cwd, whether it saw an API key, and its prompt."""
    log = tmp_path / "calls.jsonl"

    def read():
        return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []

    read.log = log
    return read


@pytest.fixture
def run_cli(tmp_path, calls):
    bin_directory = tmp_path / "bin"
    bin_directory.mkdir()
    (bin_directory / "claude").symlink_to(FAKE_CLAUDE)

    def run(*args, fail=False):
        env = {
            **os.environ,
            "PATH": f"{bin_directory}{os.pathsep}{os.environ['PATH']}",
            "ANTHROPIC_API_KEY": "sk-must-not-reach-claude",
            "FAKE_CLAUDE_LOG": str(calls.log),
            "FAKE_CLAUDE_FAIL": "1" if fail else "",
        }
        return subprocess.run(["uv", "run", "judge", *[str(a) for a in args]], cwd=PACKAGE_ROOT, capture_output=True, text=True, env=env)

    return run


@pytest.fixture
def make_run(tmp_path):
    def make(name, source, flags=(False, True, True), exit_code=0, steps=()):
        target = {"python": "javascript", "javascript": "python"}[source]
        run = tmp_path / "runs" / name
        for relative, text in PORTS[target].items():
            (run / "ported_implementation" / relative).parent.mkdir(parents=True, exist_ok=True)
            (run / "ported_implementation" / relative).write_text(text)
        transcripts = run / "transcript" / ".claude" / "projects" / "-target"
        transcripts.mkdir(parents=True)
        (transcripts / "session.jsonl").write_text("".join(json.dumps(step) + "\n" for step in steps))
        condition = {"name": f"source-{source}", "source_language": source, "target_language": target, **dict(zip(FLAGS, flags))}
        (run / "manifest.json").write_text(json.dumps({"exit_code": exit_code, "condition": condition}))
        return run

    return make


@pytest.fixture
def rubric():
    return lambda name: (PACKAGE_ROOT / "rubrics" / f"{name}.md").read_text()


@pytest.fixture
def read_out():
    def read(out):
        judgments = [json.loads(line) for line in (out / "judgments.jsonl").read_text().splitlines()]
        return judgments, json.loads((out / "manifest.json").read_text())

    return read
