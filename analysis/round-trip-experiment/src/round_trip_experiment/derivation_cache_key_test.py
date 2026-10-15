from pathlib import Path
from unittest.mock import patch

import pytest

from round_trip_experiment.derivation_cache_key import derivation_cache_key


@pytest.fixture
def harness():
    with (
        patch("round_trip_experiment.derivation_cache_key.assemble_whitelist", autospec=True) as whitelist,
        patch("round_trip_experiment.derivation_cache_key.compute_prepare_cache_key", autospec=True) as compute,
        patch("round_trip_experiment.derivation_cache_key.settings") as settings,
    ):
        settings.gbnf_commit = "13f1aca"
        settings.prepare_docker_directory = Path("/repo/docker/gbnf-prepare")
        whitelist.return_value = "+ rules\n"
        compute.return_value = "390bf534c55d496b"
        yield dict(whitelist=whitelist, compute=compute)


def describe_derivation_cache_key():
    def it_asks_for_every_suite_of_the_source_language(harness):
        derivation_cache_key("javascript")
        assert harness["whitelist"].call_args.args == ("javascript",)
        assert harness["whitelist"].call_args.kwargs == {
            "include_unit_tests": True,
            "include_source_integration_tests": True,
            "include_target_integration_tests": True,
        }

    def it_keys_the_way_the_harness_does(harness):
        assert derivation_cache_key("javascript") == "390bf534c55d496b"
        assert harness["compute"].call_args.args == ("13f1aca", Path("/repo/docker/gbnf-prepare"), "+ rules\n")
