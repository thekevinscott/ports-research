from pathlib import Path
from unittest.mock import patch

import pytest

from gbnf_experiment.prepare_filesystem.prepare_reference_implementation import (
    prepare_image_tag,
    prepare_reference_implementation,
)

CONDITION = {
    "source_language": "javascript",
    "include_unit_tests": False,
    "include_source_integration_tests": False,
    "include_target_integration_tests": False,
}
RULES = "+ javascript/***\n- *\n"


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
def assemble_whitelist():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepare_reference_implementation.assemble_whitelist",
        autospec=True,
    ) as m:
        m.return_value = RULES
        yield m


@pytest.fixture
def docker():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepare_reference_implementation.docker",
        autospec=True,
    ) as m:

        def fake_copy(source, destination):
            _, path = source
            shared = Path(destination) / Path(path).name
            (shared / "javascript" / "src").mkdir(parents=True)
            (shared / "javascript" / "src" / "index.ts").write_text("export {};")

        m.copy.side_effect = fake_copy
        yield m


@pytest.fixture
def output_directory(tmp_path):
    return tmp_path / "staging"


def describe_prepare_image_tag():
    def it_names_the_language_and_every_flag(settings):
        assert prepare_image_tag(**CONDITION) == (
            "gbnf-prepare:javascript_unit-off_source-integration-off_target-integration-off"
        )

    def it_gives_every_condition_its_own_tag(settings):
        tags = {
            prepare_image_tag(
                source_language=source_language,
                include_unit_tests=unit,
                include_source_integration_tests=source_integration,
                include_target_integration_tests=target_integration,
            )
            for source_language in ("javascript", "python")
            for unit in (False, True)
            for source_integration in (False, True)
            for target_integration in (False, True)
        }
        assert len(tags) == 16


def describe_prepare_reference_implementation():
    def it_returns_the_copied_out_shared_folder(
        docker, settings, assemble_whitelist, output_directory
    ):
        shared = prepare_reference_implementation(
            output_directory=output_directory, debug=False, **CONDITION
        )
        assert shared == output_directory / "shared"
        assert (shared / "javascript" / "src" / "index.ts").read_text() == "export {};"

    def it_never_starts_the_image(docker, settings, assemble_whitelist, output_directory):
        """A container that only ever exists cannot write to what it is read from."""
        prepare_reference_implementation(
            output_directory=output_directory, debug=False, **CONDITION
        )
        docker.run.assert_not_called()
        docker.create.assert_called_once()

    def it_removes_the_container_it_read_from(
        docker, settings, assemble_whitelist, output_directory
    ):
        prepare_reference_implementation(
            output_directory=output_directory, debug=False, **CONDITION
        )
        docker.create.return_value.remove.assert_called_once()

    def it_removes_the_container_when_the_copy_fails(
        docker, settings, assemble_whitelist, output_directory
    ):
        docker.copy.side_effect = RuntimeError("no such path")

        with pytest.raises(RuntimeError, match="no such path"):
            prepare_reference_implementation(
                output_directory=output_directory, debug=False, **CONDITION
            )

        docker.create.return_value.remove.assert_called_once()

    def it_copies_the_whole_shared_folder(
        docker, settings, assemble_whitelist, output_directory
    ):
        prepare_reference_implementation(
            output_directory=output_directory, debug=False, **CONDITION
        )
        source, destination = docker.copy.call_args.args
        assert source == (docker.create.return_value, "/shared")
        assert destination == output_directory

    def describe_build():
        def it_builds_the_prepare_image(
            docker, settings, assemble_whitelist, output_directory
        ):
            prepare_reference_implementation(
                output_directory=output_directory, debug=False, **CONDITION
            )
            assert docker.build.call_args.args[0] == settings.prepare_docker_directory

        def it_tags_the_image_for_the_condition(
            docker, settings, assemble_whitelist, output_directory
        ):
            prepare_reference_implementation(
                output_directory=output_directory,
                debug=False,
                source_language="python",
                include_unit_tests=True,
                include_source_integration_tests=False,
                include_target_integration_tests=True,
            )
            assert docker.build.call_args.kwargs["tags"] == (
                "gbnf-prepare:python_unit-on_source-integration-off_target-integration-on"
            )

        def it_asks_the_composer_for_the_condition_s_rules(
            docker, settings, assemble_whitelist, output_directory
        ):
            prepare_reference_implementation(
                output_directory=output_directory,
                debug=False,
                source_language="python",
                include_unit_tests=False,
                include_source_integration_tests=True,
                include_target_integration_tests=False,
            )
            assert assemble_whitelist.call_args.args == ("python",)
            assert assemble_whitelist.call_args.kwargs == {
                "include_unit_tests": False,
                "include_source_integration_tests": True,
                "include_target_integration_tests": False,
            }

        def it_passes_the_pin_and_the_rules_as_the_only_build_args(
            docker, settings, assemble_whitelist, output_directory
        ):
            """The image sees no flag and no language, only the composed filter."""
            prepare_reference_implementation(
                output_directory=output_directory, debug=False, **CONDITION
            )
            assert docker.build.call_args.kwargs["build_args"] == {
                "GBNF_COMMIT": "abc123",
                "RULES": RULES,
            }

        def it_hides_build_output_unless_debugging(
            docker, settings, assemble_whitelist, output_directory
        ):
            prepare_reference_implementation(
                output_directory=output_directory, debug=False, **CONDITION
            )
            assert docker.build.call_args.kwargs["progress"] is False

        def it_streams_build_output_in_debug(
            docker, settings, assemble_whitelist, output_directory
        ):
            prepare_reference_implementation(
                output_directory=output_directory, debug=True, **CONDITION
            )
            assert docker.build.call_args.kwargs["progress"] == "tty"
