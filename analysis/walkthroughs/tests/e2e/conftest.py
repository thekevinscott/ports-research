import os
import subprocess
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def out():
    return Path(os.environ["WALKTHROUGHS_OUT"])


@pytest.fixture(scope="session")
def alignment():
    """The embedding server's url from `just test-e2e <out> <url>`, or the word-overlap fallback when none is given."""
    url = os.environ.get("WALKTHROUGHS_EMBEDDINGS_URL")
    return ["--embeddings-url", url] if url else ["--no-embeddings"]


@pytest.fixture(scope="session")
def run_cli():
    def run(*args):
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        return subprocess.run(["uv", "run", "walkthroughs", *[str(a) for a in args]], cwd=PACKAGE_ROOT, capture_output=True, text=True, env=env)

    return run
