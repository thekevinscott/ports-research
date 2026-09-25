import os
from pathlib import Path
from unittest.mock import patch

import pytest

from gbnf_experiment.config import PACKAGE_ROOT, Settings, settings


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

    def it_defaults_the_prepare_image_tag():
        assert Settings().prepare_image_tag == "gbnf-prepare:latest"

    def it_defaults_the_workspace_image_repository():
        assert Settings().workspace_image_repository == "gbnf-workspace"

    def it_defaults_the_data_directory_inside_the_package():
        assert Settings().data_directory == PACKAGE_ROOT / "data"

    def it_reads_overrides_from_the_env_prefix(env_gbnf_commit):
        assert Settings().gbnf_commit == "deadbeef"

    def describe_computed_directories():
        def it_locates_the_workspace_docker_directory():
            assert Settings().workspace_docker_directory.name == "gbnf-workspace"

        def it_lands_runs_directly_in_the_data_directory():
            """No `runs/` level: data/ is a flat list of run directories."""
            assert not hasattr(Settings(), "runs_directory")

        def it_follows_an_overridden_data_directory(env_data_directory):
            assert Settings().data_directory == Path("/elsewhere")

        def it_keeps_no_prepared_corpus_on_the_host():
            """The corpus lives in the prepare image; the host never unpacks it."""
            assert not hasattr(Settings(), "prepared_directory")

        def it_no_longer_shares_one_output_directory_across_runs():
            assert not hasattr(Settings(), "outputs_directory")

        def it_no_longer_stages_assembled_inputs_of_its_own():
            assert not hasattr(Settings(), "inputs_directory")

        def it_no_longer_owns_the_prompt():
            """The prompt is porting-harness's; this package only names a direction."""
            assert not hasattr(Settings(), "prompt_path")

    def describe_the_module_instance():
        def it_exposes_a_settings_instance():
            assert isinstance(settings, Settings)

        def it_points_at_a_real_workspace_dockerfile():
            assert (settings.workspace_docker_directory / "Dockerfile").is_file()
