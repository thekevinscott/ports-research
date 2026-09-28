import os
from pathlib import Path
from unittest.mock import patch

import pytest

from gbnf_experiment.config import (
    PACKAGE_ROOT,
    REPO_ROOT,
    Settings,
    settings,
)


@pytest.fixture
def env_gbnf_commit():
    with patch.dict(os.environ, {"GBNF_EXPERIMENT_GBNF_COMMIT": "deadbeef"}):
        yield


@pytest.fixture
def env_data_directory():
    with patch.dict(os.environ, {"GBNF_EXPERIMENT_DATA_DIRECTORY": "/elsewhere"}):
        yield


def describe_settings():
    def it_pins_the_gbnf_commit():
        assert Settings().gbnf_commit == "13f1aca495d11e160fffd68c4ba299a2415909d8"

    def it_names_the_prepare_image_without_a_tag():
        """The tag carries the condition, so the settings only hold the name."""
        assert Settings().image_name == "gbnf-prepare"
        assert not hasattr(Settings(), "image_tag")

    def it_defaults_the_data_directory_to_the_repo_data_runs():
        assert Settings().data_directory == REPO_ROOT / "data" / "runs"

    def it_reads_overrides_from_the_env_prefix(env_gbnf_commit):
        assert Settings().gbnf_commit == "deadbeef"

    def describe_computed_directories():
        def it_locates_the_prepare_docker_directory():
            assert Settings().prepare_docker_directory.name == "gbnf-prepare"

        def it_lands_runs_directly_in_the_data_directory():
            """No `runs/` level: data/ is a flat list of run directories."""
            assert not hasattr(Settings(), "runs_directory")

        def it_follows_an_overridden_data_directory(env_data_directory):
            assert Settings().data_directory == Path("/elsewhere")

        def it_no_longer_shares_one_output_directory_across_runs():
            assert not hasattr(Settings(), "outputs_directory")

        def it_no_longer_stages_assembled_inputs_of_its_own():
            assert not hasattr(Settings(), "inputs_directory")

        def it_caches_nothing_of_its_own():
            """The image is the cache: docker layers, keyed by the build args."""
            assert not hasattr(Settings(), "prepared_directory")

    def describe_the_module_instance():
        def it_exposes_a_settings_instance():
            assert isinstance(settings, Settings)

        def it_points_at_a_real_prepare_dockerfile():
            assert (settings.prepare_docker_directory / "Dockerfile").is_file()

        def it_roots_the_package_at_the_directory_holding_the_pyproject():
            assert (PACKAGE_ROOT / "pyproject.toml").is_file()
