import os
from pathlib import Path
from unittest.mock import patch

import pytest

from round_trip_experiment.config import CACHE_HOME, PACKAGE_ROOT, Settings, settings


@pytest.fixture
def env_overrides():
    with patch.dict(
        os.environ,
        {
            "ROUND_TRIP_EXPERIMENT_REVERSE_DIRECTORY": "/elsewhere/reverse",
            "ROUND_TRIP_EXPERIMENT_STAGING_DIRECTORY": "/elsewhere/staging",
        },
    ):
        yield


def describe_settings():
    def it_defaults_the_reverse_directory_inside_the_package():
        assert Settings().reverse_directory == PACKAGE_ROOT / "reverse"

    def it_defaults_the_staging_directory_under_the_cache_home():
        assert Settings().staging_directory == CACHE_HOME / "ports" / "round-trip-experiment" / "derivations"

    def it_follows_overridden_directories(env_overrides):
        assert Settings().reverse_directory == Path("/elsewhere/reverse")
        assert Settings().staging_directory == Path("/elsewhere/staging")

    def it_exposes_a_settings_instance():
        assert isinstance(settings, Settings)
