import os
from pathlib import Path

import pytest

CACHE_HOME = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
REFERENCE_SOURCE = CACHE_HOME / "ports" / "gbnf-experiment" / "derivations" / "af673dbe41be73ce" / "source"

# Copied from analysis/runs.py EXCLUDE_BY_LANGUAGE so this tier embeds the same file set the notebook does.
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
def model() -> str:
    if not os.environ.get("GENERATE_EMBEDDING_BASE_URL"):
        pytest.skip("GENERATE_EMBEDDING_BASE_URL is not set; no embeddings endpoint to drive")
    name = os.environ.get("MEASURE_EMBEDDING_MODEL")
    if not name:
        pytest.skip("MEASURE_EMBEDDING_MODEL is not set; no model name to send to the endpoint")
    return name
