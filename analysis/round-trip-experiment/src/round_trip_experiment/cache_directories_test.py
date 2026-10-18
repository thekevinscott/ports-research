from pathlib import Path

from gbnf_experiment.config import CACHE_HOME, PREPARED_DIRECTORY

from round_trip_experiment.cache_directories import prepared_directory, staging_directory


def describe_prepared_directory():
    def it_matches_where_gbnf_experiment_prepares_derivations():
        assert prepared_directory(CACHE_HOME) == PREPARED_DIRECTORY

    def it_lives_under_the_given_cache():
        assert prepared_directory(Path("/cache")) == Path("/cache/ports/gbnf-experiment/prepared")


def describe_staging_directory():
    def it_lives_under_the_given_cache():
        assert staging_directory(Path("/cache")) == Path("/cache/ports/round-trip-experiment/derivations")
