from pathlib import Path
from unittest.mock import patch

import pytest

from gbnf_experiment.prepare_filesystem.prepare_reference_implementation import (
    prepare_reference_implementation,
)


@pytest.fixture
def settings(tmp_path):
    with patch(
        "gbnf_experiment.prepare_filesystem.prepare_reference_implementation.settings",
        autospec=True,
    ) as m:
        m.derivation_docker_directory = tmp_path / "docker" / "derivation"
        m.image_tag = "image:tag"
        m.gbnf_commit = "abc123"
        yield m


@pytest.fixture
def docker():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepare_reference_implementation.docker",
        autospec=True,
    ) as m:

        def fake_run(tag, user=None, volumes=None, remove=None):
            [staging_directory] = [
                source for source, target, _ in volumes if target == "/derivation-output"
            ]
            (Path(staging_directory) / "derived.txt").write_text("output")
            return "container output"

        m.run.side_effect = fake_run
        yield m


@pytest.fixture
def output_directory(tmp_path):
    return tmp_path / "derivations" / "key"


def describe_prepare_reference_implementation():
    def it_returns_the_output_directory(docker, settings, output_directory):
        assert prepare_reference_implementation(output_directory=output_directory, debug=False) == output_directory

    def it_renames_the_staging_directory_into_place(docker, settings, output_directory):
        prepare_reference_implementation(output_directory=output_directory, debug=False)
        assert (output_directory / "derived.txt").read_text() == "output"

    def it_leaves_no_staging_directory_behind(docker, settings, output_directory):
        prepare_reference_implementation(output_directory=output_directory, debug=False)
        assert not output_directory.with_name(output_directory.name + ".staging").exists()

    def it_removes_the_container_when_the_derivation_finishes(
        docker, settings, output_directory
    ):
        prepare_reference_implementation(output_directory=output_directory, debug=False)
        assert docker.run.call_args.kwargs["remove"] is True

    def it_generates_into_a_staging_directory(docker, settings, output_directory):
        prepare_reference_implementation(output_directory=output_directory, debug=False)
        [staged] = [
            source
            for source, target, _ in docker.run.call_args.kwargs["volumes"]
            if target == "/derivation-output"
        ]
        assert staged.endswith(".staging")

    def it_mounts_the_staging_directory_writable(docker, settings, output_directory):
        prepare_reference_implementation(output_directory=output_directory, debug=False)
        [mode] = [
            mode
            for _, target, mode in docker.run.call_args.kwargs["volumes"]
            if target == "/derivation-output"
        ]
        assert mode == "rw"

    def it_discards_a_stale_staging_directory(docker, settings, output_directory):
        staging_directory = output_directory.with_name(output_directory.name + ".staging")
        staging_directory.mkdir(parents=True)
        (staging_directory / "half-written.txt").write_text("interrupted")

        prepare_reference_implementation(output_directory=output_directory, debug=False)

        assert not (output_directory / "half-written.txt").exists()

    def it_leaves_no_output_directory_when_the_container_fails(
        docker, settings, output_directory
    ):
        docker.run.side_effect = RuntimeError("container failed")

        with pytest.raises(RuntimeError, match="container failed"):
            prepare_reference_implementation(output_directory=output_directory, debug=False)

        assert not output_directory.exists()

    def describe_build():
        def it_builds_the_derivation_image(docker, settings, output_directory):
            prepare_reference_implementation(output_directory=output_directory, debug=False)
            assert docker.build.call_args.args[0] == settings.derivation_docker_directory
            assert docker.build.call_args.kwargs["tags"] == "image:tag"

        def it_passes_the_pinned_commit_as_a_build_arg(docker, settings, output_directory):
            prepare_reference_implementation(output_directory=output_directory, debug=False)
            assert docker.build.call_args.kwargs["build_args"] == {"GBNF_COMMIT": "abc123"}

        def it_hides_build_output_unless_debugging(docker, settings, output_directory):
            prepare_reference_implementation(output_directory=output_directory, debug=False)
            assert docker.build.call_args.kwargs["progress"] is False

        def it_streams_build_output_in_debug(docker, settings, output_directory):
            prepare_reference_implementation(output_directory=output_directory, debug=True)
            assert docker.build.call_args.kwargs["progress"] == "tty"
