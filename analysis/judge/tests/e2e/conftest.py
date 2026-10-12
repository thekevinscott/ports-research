import json
import os
import subprocess
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def runs():
    """The run directories to judge, from `just test-e2e <out> <runs...>`."""
    return [Path(run) for run in os.environ["JUDGE_RUNS"].split()]


@pytest.fixture(scope="session")
def out():
    return Path(os.environ["JUDGE_OUT"])


@pytest.fixture(scope="session")
def run_cli():
    def run(*args):
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        return subprocess.run(["uv", "run", "judge", *[str(a) for a in args]], cwd=PACKAGE_ROOT, capture_output=True, text=True, env=env)

    return run


@pytest.fixture(scope="session")
def schema():
    return lambda rubric: json.loads((PACKAGE_ROOT / "rubrics" / f"{rubric}.schema.json").read_text())
