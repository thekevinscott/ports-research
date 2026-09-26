"""Shared fixtures for the container-level suites.

Import-time cheap: nothing here touches a container until a fixture is used.
"""

from pathlib import Path

import pytest

collect_ignore = ["fixtures"]

TWO_NUMBER_ADDER = Path(__file__).parent / "fixtures" / "two_number_adder"


@pytest.fixture(scope="session")
def two_number_adder() -> Path:
    """The fixture library: both reference packages and both mounted suites."""
    return TWO_NUMBER_ADDER
