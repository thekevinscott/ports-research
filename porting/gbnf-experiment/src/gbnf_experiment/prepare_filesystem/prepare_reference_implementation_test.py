from pathlib import Path
from unittest.mock import patch

import pytest

from gbnf_experiment.prepare_filesystem.prepare_reference_implementation import (
    prepare_image_tag,
    prepare_reference_implementation,
)

CONDITION = {
    "source_language": "typescript",
    "include_python_tests": False,
    "include_typescript_tests": False,
}


@pytest.fixture
def settings(tmp_path):
    with patch(
        "gbnf_experiment.prepare_filesystem.prepare_reference_implementation.settings",
        autospec=True,
    ) as m:
        m.prepare_docker_directory = tmp_path / "docker" / "gbnf-prepare"
        m.image_name = "gbnf-prepare"
        m.gbnf_commit = "abc123"
        yield m


@pytest.fixture
def docker():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepare_reference_implementation.docker",
        autospec=True,
    ) as m:

        def fake_copy(source, destination):
            _, path = source
            reference = Path(destination) / Path(path).name
            reference.mkdir(parents=True)
            (reference / "source").mkdir()
            (reference / "source" / "index.ts").write_text("export {};")

        m.copy.side_effect = fake_copy
        yield m


@pytest.fixture
def output_directory(tmp_path):
    return tmp_path / "staging"


def describe_prepare_image_tag():
    def it_names_the_source_language(settings):
        assert prepare_image_tag(**CONDITION) == (
            "gbnf-prepare:source-typescript_python-tests-off_typescript-tests-off"
        )

    def it_gives_every_condition_its_own_tag(settings):
        tags = {
            prepare_image_tag(
                source_language=source_language,
                include_python_tests=python,
                include_typescript_tests=typescript,
            )
            for source_language in ("typescript", "python")
            for python in (False, True)
            for typescript in (False, True)
        }
        assert len(tags) == 8


def describe_prepare_reference_implementation():
    def it_returns_the_copied_out_reference(docker, settings, output_directory):
        reference = prepare_reference_implementation(
            output_directory=output_directory, debug=False, **CONDITION
        )
        assert reference == output_directory / "reference"
        assert (reference / "source" / "index.ts").read_text() == "export {};"

    def it_never_starts_the_image(docker, settings, output_directory):
        """A container that only ever exists cannot write to what it is read from."""
        prepare_reference_implementation(
            output_directory=output_directory, debug=False, **CONDITION
        )
        docker.run.assert_not_called()
        docker.create.assert_called_once()

    def it_removes_the_container_it_read_from(docker, settings, output_directory):
        prepare_reference_implementation(
            output_directory=output_directory, debug=False, **CONDITION
        )
        docker.create.return_value.remove.assert_called_once()

    def it_removes_the_container_when_the_copy_fails(docker, settings, output_directory):
        docker.copy.side_effect = RuntimeError("no such path")

        with pytest.raises(RuntimeError, match="no such path"):
            prepare_reference_implementation(
                output_directory=output_directory, debug=False, **CONDITION
            )

        docker.create.return_value.remove.assert_called_once()

    def it_copies_the_whole_reference_folder(docker, settings, output_directory):
        prepare_reference_implementation(
            output_directory=output_directory, debug=False, **CONDITION
        )
        source, destination = docker.copy.call_args.args
        assert source == (docker.create.return_value, "/reference")
        assert destination == output_directory

    def describe_build():
        def it_builds_the_prepare_image(docker, settings, output_directory):
            prepare_reference_implementation(
                output_directory=output_directory, debug=False, **CONDITION
            )
            assert docker.build.call_args.args[0] == settings.prepare_docker_directory

        def it_tags_the_image_for_the_condition(docker, settings, output_directory):
            prepare_reference_implementation(
                output_directory=output_directory,
                debug=False,
                source_language="python",
                include_python_tests=True,
                include_typescript_tests=False,
            )
            assert docker.build.call_args.kwargs["tags"] == (
                "gbnf-prepare:source-python_python-tests-on_typescript-tests-off"
            )

        def it_passes_the_condition_as_build_args(docker, settings, output_directory):
            prepare_reference_implementation(
                output_directory=output_directory,
                debug=False,
                source_language="python",
                include_python_tests=False,
                include_typescript_tests=True,
            )
            assert docker.build.call_args.kwargs["build_args"] == {
                "GBNF_COMMIT": "abc123",
                "SOURCE_LANGUAGE": "python",
                "INCLUDE_PYTHON_TESTS": "false",
                "INCLUDE_TYPESCRIPT_TESTS": "true",
            }

        def it_hides_build_output_unless_debugging(docker, settings, output_directory):
            prepare_reference_implementation(
                output_directory=output_directory, debug=False, **CONDITION
            )
            assert docker.build.call_args.kwargs["progress"] is False

        def it_streams_build_output_in_debug(docker, settings, output_directory):
            prepare_reference_implementation(
                output_directory=output_directory, debug=True, **CONDITION
            )
            assert docker.build.call_args.kwargs["progress"] == "tty"
