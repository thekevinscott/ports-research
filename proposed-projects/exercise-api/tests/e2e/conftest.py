import os
from pathlib import Path

import pytest

CACHE_HOME = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
DERIVATION = CACHE_HOME / "ports" / "gbnf-experiment" / "derivations" / "af673dbe41be73ce"
PACKAGE_ROOT = Path(__file__).resolve().parents[2]
RUNS = PACKAGE_ROOT.parents[1] / "packages" / "gbnf-experiment" / "data"


def _existing(path: Path, what: str) -> Path:
    if not path.is_dir():
        pytest.skip(f"no {what} at {path} — has gbnf-experiment been derived?")
    return path


@pytest.fixture(scope="session")
def python_reference() -> Path:
    return _existing(DERIVATION / "source" / "python", "python reference")


@pytest.fixture(scope="session")
def typescript_reference() -> Path:
    return _existing(DERIVATION / "source" / "typescript", "typescript reference")


@pytest.fixture(scope="session")
def grammars_dir() -> Path:
    return _existing(DERIVATION / "tests" / "python" / "iteration" / "grammars", "fixture grammars")


@pytest.fixture(scope="session")
def python_port() -> Path:
    return _existing(RUNS / "20260909T011452Z_9f286468" / "ported_implementation", "python port sample")


@pytest.fixture(scope="session")
def typescript_port() -> Path:
    return _existing(RUNS / "20260909T001426Z_1c28aa33" / "ported_implementation", "typescript port sample")


@pytest.fixture(scope="session")
def generated_cases() -> Path:
    return PACKAGE_ROOT / "cases" / "generated-seed0-500.jsonl"


@pytest.fixture(scope="session")
def fixture_cases() -> Path:
    return PACKAGE_ROOT / "cases" / "fixtures.jsonl"


@pytest.fixture(scope="session")
def ladder_cases() -> Path:
    return PACKAGE_ROOT / "cases" / "ladder.jsonl"
