from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def sample_transcript() -> Path:
    return FIXTURES / "sample_transcript.jsonl"


@pytest.fixture
def sample_directory(tmp_path: Path) -> Path:
    """The sample transcript refiled under a run-style transcript/ tree."""
    root = tmp_path / "run" / "transcript" / "-workspace"
    root.mkdir(parents=True)
    (root / "session.jsonl").write_text(
        (FIXTURES / "sample_transcript.jsonl").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    return tmp_path / "run"
