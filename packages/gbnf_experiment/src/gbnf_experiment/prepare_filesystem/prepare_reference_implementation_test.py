import hashlib
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from gbnf_experiment.prepare_filesystem.prepare_reference_implementation import (
    prepare_reference_implementation,
)

FLAGS = {
    "include_unit_tests": False,
    "include_source_integration_tests": False,
    "include_target_integration_tests": False,
}
CONDITION = {"source_language": "python", **FLAGS}


def fake_rules(source, **flags) -> str:
    return f"rules for {source} {sorted(flags.items())}"


def fake_key(commit, directory, rules) -> str:
    return hashlib.sha256(rules.encode()).hexdigest()[:16]


KEY = fake_key("abc123", None, fake_rules("python", **FLAGS))


@pytest.fixture
def settings(tmp_path):
    with patch(
        "gbnf_experiment.prepare_filesystem.prepare_reference_implementation.settings",
        autospec=True,
    ) as m:
        m.prepare_docker_directory = tmp_path / "docker" / "gbnf-prepare"
        m.prepared_directory = tmp_path / "prepared"
        m.gbnf_commit = "abc123"
        yield m


@pytest.fixture
def assemble_whitelist():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepare_reference_implementation.assemble_whitelist",
        autospec=True,
    ) as m:
        m.side_effect = fake_rules
        yield m


@pytest.fixture
def compute_prepare_cache_key():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepare_reference_implementation.compute_prepare_cache_key",
        autospec=True,
    ) as m:
        m.side_effect = fake_key
        yield m


@pytest.fixture
def docker():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepare_reference_implementation.docker",
        autospec=True,
    ) as m:

        def fake_run(tag, command, user=None, volumes=None, remove=None):
            [staging_directory] = [
                source for source, target, _ in volumes if target == "/prepared-output"
            ]
            (Path(staging_directory) / "python").mkdir()
            (Path(staging_directory) / "python" / "pyproject.toml").write_text("[project]")

        m.run.side_effect = fake_run
        yield m


@pytest.fixture
def prepare(settings, assemble_whitelist, compute_prepare_cache_key, docker):
    def run(debug=False, **overrides) -> Path:
        return prepare_reference_implementation(**{**CONDITION, **overrides}, debug=debug)

    return run


def describe_prepare_reference_implementation():
    def describe_the_rules():
        def it_composes_them_from_the_condition(prepare, assemble_whitelist):
            prepare(source_language="javascript", include_unit_tests=True)
            assemble_whitelist.assert_called_once_with(
                "javascript",
                include_unit_tests=True,
                include_source_integration_tests=False,
                include_target_integration_tests=False,
            )

        def it_keys_the_cache_on_the_commit_the_docker_directory_and_the_rules(
            prepare, settings, compute_prepare_cache_key
        ):
            prepare()
            compute_prepare_cache_key.assert_called_once_with(
                "abc123", settings.prepare_docker_directory, fake_rules("python", **FLAGS)
            )

    def describe_the_cache():
        def it_returns_the_keyed_directory(prepare, settings):
            assert prepare() == settings.prepared_directory / KEY

        def it_holds_one_entry_per_condition(prepare, settings):
            prepare()
            prepare(include_target_integration_tests=True)
            assert len(list(settings.prepared_directory.iterdir())) == 2

        def it_prepares_a_condition_once(prepare, docker):
            prepare()
            prepare()
            docker.build.assert_called_once()
            docker.run.assert_called_once()

        def it_leaves_no_staging_directory_behind(prepare, settings):
            prepare()
            assert not list(settings.prepared_directory.glob("*.staging"))

        def it_discards_a_stale_staging_directory(prepare, settings):
            staging = settings.prepared_directory / f"{KEY}.staging"
            staging.mkdir(parents=True)
            (staging / "half-written.txt").write_text("interrupted")

            directory = prepare()

            assert not (directory / "half-written.txt").exists()

        def it_leaves_no_entry_when_the_extraction_fails(prepare, settings, docker):
            docker.run.side_effect = RuntimeError("container failed")
            with pytest.raises(RuntimeError, match="container failed"):
                prepare()
            assert not [
                path
                for path in settings.prepared_directory.iterdir()
                if not path.name.endswith(".staging")
            ]

    def describe_the_build():
        def it_builds_the_prepare_docker_directory(prepare, settings, docker):
            prepare()
            assert docker.build.call_args.args[0] == settings.prepare_docker_directory

        def it_passes_the_pinned_commit_and_the_rules(prepare, docker):
            prepare()
            assert docker.build.call_args.kwargs["build_args"] == {
                "GBNF_COMMIT": "abc123",
                "RULES": fake_rules("python", **FLAGS),
            }

        def it_tags_the_image_per_condition(prepare, docker):
            prepare()
            assert docker.build.call_args.kwargs["tags"] == f"gbnf-prepare:{KEY}"

        def it_hides_build_output_unless_debugging(prepare, docker):
            prepare()
            assert docker.build.call_args.kwargs["progress"] is False

        def it_streams_build_output_in_debug(prepare, docker):
            prepare(debug=True)
            assert docker.build.call_args.kwargs["progress"] == "tty"

    def describe_the_extraction():
        def it_runs_the_image_it_built(prepare, docker):
            prepare()
            assert docker.run.call_args.args[0] == docker.build.call_args.kwargs["tags"]

        def it_copies_shared_whole_into_the_output_mount(prepare, docker):
            prepare()
            assert docker.run.call_args.args[1] == ["cp", "-a", "/shared/.", "/prepared-output/"]

        def it_mounts_a_writable_staging_directory(prepare, docker, settings):
            directory = prepare()
            [(source, mode)] = [
                (source, mode)
                for source, target, mode in docker.run.call_args.kwargs["volumes"]
                if target == "/prepared-output"
            ]
            assert source == str(directory.with_name(directory.name + ".staging"))
            assert mode == "rw"

        def it_copies_as_the_current_user(prepare, docker):
            prepare()
            assert docker.run.call_args.kwargs["user"] == f"{os.getuid()}:{os.getgid()}"

        def it_removes_the_container(prepare, docker):
            prepare()
            assert docker.run.call_args.kwargs["remove"] is True

        def it_moves_the_copy_into_the_keyed_directory(prepare):
            directory = prepare()
            assert (directory / "python" / "pyproject.toml").read_text() == "[project]"
