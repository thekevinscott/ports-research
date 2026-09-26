import os
from pathlib import Path

import pytest

CACHE_HOME = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
REFERENCE_SOURCE = CACHE_HOME / "ports" / "gbnf-experiment" / "derivations" / "af673dbe41be73ce" / "source"


@pytest.fixture
def python_reference() -> Path:
    directory = REFERENCE_SOURCE / "python"
    if not directory.is_dir():
        pytest.skip(f"no python reference at {directory} — has gbnf-experiment been derived?")
    return directory


@pytest.fixture
def typescript_reference() -> Path:
    directory = REFERENCE_SOURCE / "typescript"
    if not directory.is_dir():
        pytest.skip(f"no typescript reference at {directory} — has gbnf-experiment been derived?")
    return directory
