from pathlib import Path

import pytest

from gbnf_experiment import config
from gbnf_experiment.config import compute_prepare_cache_key


RULES = "+ /python/\n"


@pytest.fixture
def docker_directory(tmp_path):
    directory = tmp_path / "gbnf-prepare"
    (directory / "patches").mkdir(parents=True)
    (directory / "Dockerfile").write_text("FROM node:22.19.0-slim")
    (directory / "prepare.sh").write_text("#!/bin/sh")
    (directory / "patches" / "0001.patch").write_text("diff")
    return directory


def describe_config():
    def it_pins_the_gbnf_commit():
        assert config.GBNF_COMMIT == "13f1aca495d11e160fffd68c4ba299a2415909d8"

    def it_has_a_blank_api_key():
        assert config.API_KEY == ""

    def it_reads_nothing_from_the_environment():
        assert not hasattr(config, "Settings")
        assert not hasattr(config, "os")

    def it_caches_the_prepared_corpus_outside_the_package_tree():
        """A rebuildable cache is not evidence; only runs belong under data/."""
        assert config.PREPARED_DIRECTORY == Path.home() / ".cache" / "ports" / "gbnf-experiment" / "prepared"
        assert config.PACKAGE_ROOT not in config.PREPARED_DIRECTORY.parents

    def it_points_at_a_real_prepare_dockerfile():
        assert (config.PREPARE_DOCKER_DIRECTORY / "Dockerfile").is_file()


def describe_compute_prepare_cache_key():
    def it_is_stable_across_recomputation(docker_directory):
        first = compute_prepare_cache_key("abc123", docker_directory, RULES)
        second = compute_prepare_cache_key("abc123", docker_directory, RULES)
        assert first == second

    def it_is_a_short_hex_digest(docker_directory):
        key = compute_prepare_cache_key("abc123", docker_directory, RULES)
        assert len(key) == 16
        assert all(character in "0123456789abcdef" for character in key)

    def it_changes_when_the_commit_changes(docker_directory):
        assert compute_prepare_cache_key(
            "abc123", docker_directory, RULES
        ) != compute_prepare_cache_key("def456", docker_directory, RULES)

    def it_changes_when_a_docker_file_changes(docker_directory):
        before = compute_prepare_cache_key("abc123", docker_directory, RULES)
        (docker_directory / "Dockerfile").write_text("FROM node:24-slim")
        assert compute_prepare_cache_key("abc123", docker_directory, RULES) != before

    def it_changes_when_a_patch_changes(docker_directory):
        before = compute_prepare_cache_key("abc123", docker_directory, RULES)
        (docker_directory / "patches" / "0001.patch").write_text("different diff")
        assert compute_prepare_cache_key("abc123", docker_directory, RULES) != before

    def it_changes_when_a_file_is_added(docker_directory):
        before = compute_prepare_cache_key("abc123", docker_directory, RULES)
        (docker_directory / "patches" / "0002.patch").write_text("another")
        assert compute_prepare_cache_key("abc123", docker_directory, RULES) != before

    def it_ignores_directory_entries(docker_directory):
        before = compute_prepare_cache_key("abc123", docker_directory, RULES)
        (docker_directory / "empty").mkdir()
        assert compute_prepare_cache_key("abc123", docker_directory, RULES) == before

    def it_changes_when_the_rules_change(docker_directory):
        """One entry per condition: the rules are the only input that varies by condition."""
        before = compute_prepare_cache_key("abc123", docker_directory, RULES)
        assert compute_prepare_cache_key("abc123", docker_directory, "+ /javascript/\n") != before
