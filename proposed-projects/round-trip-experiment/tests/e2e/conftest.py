import json
import os
from pathlib import Path

import pytest

CACHE_HOME = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
REFERENCE_SOURCE = CACHE_HOME / "ports" / "gbnf-experiment" / "derivations" / "af673dbe41be73ce" / "source"
GBNF_EXPERIMENT_DATA = Path(__file__).resolve().parents[4] / "packages" / "gbnf-experiment" / "data"

# Copied from analysis/runs.py EXCLUDE_BY_LANGUAGE so this tier measures the same file set the notebook does.
EXCLUDE = [
    "node_modules",
    "__pycache__",
    ".venv",
    ".pytest_cache",
    "dist",
    "dev-deps",
    "tests",
    "test",
    "integration-tests",
    "conftest.py",
    "*_test.py",
    "test_*.py",
    "*.test.ts",
    "*.spec.ts",
]
EXCLUDE_BY_LANGUAGE = {"python": EXCLUDE, "typescript": [*EXCLUDE, "builder", "dev"]}


def reference(language: str) -> Path:
    directory = REFERENCE_SOURCE / language
    if not directory.is_dir():
        pytest.skip(f"no {language} reference at {directory} — has gbnf-experiment been derived?")
    return directory


def completed_run() -> Path:
    for manifest in sorted(GBNF_EXPERIMENT_DATA.glob("*/manifest.json")):
        result = manifest.with_name("result.json")
        if not result.is_file():
            continue
        if json.loads(manifest.read_text()).get("completed_at") and json.loads(result.read_text()).get("is_error") is False:
            return manifest.parent
    pytest.skip(f"no completed gbnf-experiment run under {GBNF_EXPERIMENT_DATA}")


@pytest.fixture(scope="session")
def python_reference() -> Path:
    return reference("python")


@pytest.fixture(scope="session")
def typescript_reference() -> Path:
    return reference("typescript")


@pytest.fixture(scope="session")
def exclude_by_language() -> dict[str, list[str]]:
    return EXCLUDE_BY_LANGUAGE


@pytest.fixture(scope="session")
def run_directory() -> Path:
    return completed_run()
