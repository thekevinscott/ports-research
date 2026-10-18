from pathlib import Path

from round_trip_experiment.config import PACKAGE_ROOT, REVERSE_DIRECTORY, STAGING_DIRECTORY


def describe_config():
    def it_puts_the_reverse_directory_inside_the_package():
        assert REVERSE_DIRECTORY == PACKAGE_ROOT / "reverse"

    def it_puts_the_staging_directory_under_the_home_cache():
        assert STAGING_DIRECTORY == Path.home() / ".cache" / "ports" / "round-trip-experiment" / "derivations"
