import json
import subprocess
from pathlib import Path

import pytest

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def run_cli():
    def run(*args):
        return subprocess.run(
            ["uv", "run", "measure-behavior", *[str(arg) for arg in args]],
            cwd=PACKAGE_ROOT,
            capture_output=True,
            text=True,
        )

    return run


@pytest.fixture
def make_corpus(tmp_path):
    def make(inputs):
        root = tmp_path / "corpus"
        (root / "grammars").mkdir(parents=True)
        (root / "inputs").mkdir()
        (root / "grammars" / "g0000.gbnf").write_text('root ::= "a"\n')
        (root / "inputs" / "g0000.json").write_text(json.dumps(inputs))
        return root

    return make


@pytest.fixture
def committed_corpus():
    return PACKAGE_ROOT / "corpus"


@pytest.fixture
def implementations():
    return {"python": FIXTURES / "python", "typescript": FIXTURES / "typescript"}
