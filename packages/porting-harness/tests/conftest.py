"""Shared fixtures for the container-level suites.

Import-time cheap: nothing here touches a container until a fixture is used.
"""

from pathlib import Path

import pytest

collect_ignore = ["fixtures"]

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def fixtures() -> Path:
    """The docker context: the two_number_adder library and the Dockerfile that bakes it."""
    return FIXTURES
