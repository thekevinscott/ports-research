import os
from pathlib import Path
from unittest.mock import patch

import pytest

from gbnf_experiment.config import (
    CACHE_HOME,
    PACKAGE_ROOT,
    Settings,
    compute_prepare_cache_key,
    prepare_cache_key,
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


@pytest.fixture
def env_prepared_directory():
    with patch.dict(
        os.environ, {"GBNF_EXPERIMENT_PREPARED_DIRECTORY": "/somewhere/cache"}
    ):
        yield


@pytest.fixture
def docker_directory(tmp_path):
    directory = tmp_path / "gbnf-prepare"
    (directory / "patches").mkdir(parents=True)
    (directory / "Dockerfile").write_text("FROM node:22.19.0-slim")
    (directory / "prepare.sh").write_text("#!/bin/sh")
    (directory / "patches" / "0001.patch").write_text("diff")
    return directory


def describe_settings():
    def it_pins_the_gbnf_commit():
        assert Settings().gbnf_commit == "13f1aca495d11e160fffd68c4ba299a2415909d8"

    def it_defaults_the_image_tag():
        assert Settings().image_tag == "gbnf-prepare:latest"

    def it_defaults_the_data_directory_inside_the_package():
        assert Settings().data_directory == PACKAGE_ROOT / "data"

    def it_reads_overrides_from_the_env_prefix(env_gbnf_commit):
        assert Settings().gbnf_commit == "deadbeef"

    def it_caches_the_prepared_corpus_outside_the_package_tree():
        """A rebuildable cache is not evidence; only runs belong under data/."""
        instance = Settings()
        assert instance.prepared_directory == (
            CACHE_HOME / "ports" / "gbnf-experiment" / "prepared"
        )
        assert PACKAGE_ROOT not in instance.prepared_directory.parents

    def it_honours_xdg_cache_home():
        assert CACHE_HOME == Path(
            os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
        )

    def describe_computed_directories():
        def it_locates_the_prepare_docker_directory():
            assert Settings().prepare_docker_directory.name == "gbnf-prepare"

        def it_lands_runs_directly_in_the_data_directory():
            """No `runs/` level: data/ is a flat list of run directories."""
            assert not hasattr(Settings(), "runs_directory")

        def it_follows_an_overridden_data_directory(env_data_directory):
            assert Settings().data_directory == Path("/elsewhere")

        def it_follows_an_overridden_prepared_directory(env_prepared_directory):
            assert Settings().prepared_directory == Path("/somewhere/cache")

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

        def it_points_at_a_real_prepare_dockerfile():
            assert (settings.prepare_docker_directory / "Dockerfile").is_file()


def describe_compute_prepare_cache_key():
    def it_is_stable_across_recomputation(docker_directory):
        first = compute_prepare_cache_key("abc123", docker_directory)
        second = compute_prepare_cache_key("abc123", docker_directory)
        assert first == second

    def it_is_a_short_hex_digest(docker_directory):
        key = compute_prepare_cache_key("abc123", docker_directory)
        assert len(key) == 16
        assert all(character in "0123456789abcdef" for character in key)

    def it_changes_when_the_commit_changes(docker_directory):
        assert compute_prepare_cache_key(
            "abc123", docker_directory
        ) != compute_prepare_cache_key("def456", docker_directory)

    def it_changes_when_a_docker_file_changes(docker_directory):
        before = compute_prepare_cache_key("abc123", docker_directory)
        (docker_directory / "Dockerfile").write_text("FROM node:24-slim")
        assert compute_prepare_cache_key("abc123", docker_directory) != before

    def it_changes_when_a_patch_changes(docker_directory):
        before = compute_prepare_cache_key("abc123", docker_directory)
        (docker_directory / "patches" / "0001.patch").write_text("different diff")
        assert compute_prepare_cache_key("abc123", docker_directory) != before

    def it_changes_when_a_file_is_added(docker_directory):
        before = compute_prepare_cache_key("abc123", docker_directory)
        (docker_directory / "patches" / "0002.patch").write_text("another")
        assert compute_prepare_cache_key("abc123", docker_directory) != before

    def it_ignores_directory_entries(docker_directory):
        before = compute_prepare_cache_key("abc123", docker_directory)
        (docker_directory / "empty").mkdir()
        assert compute_prepare_cache_key("abc123", docker_directory) == before


def describe_the_module_cache_key():
    def it_keys_the_real_prepare_inputs():
        assert prepare_cache_key == compute_prepare_cache_key(
            settings.gbnf_commit, settings.prepare_docker_directory
        )
