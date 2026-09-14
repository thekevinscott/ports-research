from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures"


@pytest.fixture
def sample_transcript() -> Path:
    return FIXTURES / "sample_transcript.jsonl"
