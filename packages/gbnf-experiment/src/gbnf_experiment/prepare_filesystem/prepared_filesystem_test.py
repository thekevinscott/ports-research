import json
import re
from datetime import UTC
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from gbnf_experiment.prepare_filesystem import PreparedFilesystem

HEAD = "c" * 40
IMAGE_ID = "sha256:" + "b" * 64
AGENT_IMAGE = "agent-harness-sandbox-claude:latest"
WORKSPACE_IMAGE = "gbnf-workspace:0123456789abcdef"
LISTING = [
    "reference_implementation/typescript/package.json",
    "reference_implementation/typescript/src/gbnf.ts",
    "reference_implementation/typescript/src/gbnf.test.ts",
    "reference_implementation/python/pyproject.toml",
    "tests/python/validation/validate_test.py",
    "tests/typescript/validation/validate.test.ts",
]

AGENT = Mock(name="agent")

CONDITION = {
    "source_language": "typescript",
    "include_typescript_tests": False,
    "include_python_tests": False,
    "effort": "high",
    "model": "claude-opus-5",
}


@pytest.fixture
def settings(tmp_path):
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.settings", autospec=True
    ) as m:
        m.data_directory = tmp_path / "data"
        m.gbnf_commit = "13f1aca"
        yield m


@pytest.fixture
def list_prepared_files():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.list_prepared_files",
        autospec=True,
    ) as m:
        m.return_value = list(LISTING)
        yield m


@pytest.fixture
def build_agent_image():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.build_agent_image",
        autospec=True,
    ) as m:
        m.return_value = AGENT_IMAGE
        yield m


@pytest.fixture
def build_workspace_image():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.build_workspace_image",
        autospec=True,
    ) as m:
        m.return_value = WORKSPACE_IMAGE
        yield m


@pytest.fixture
def git_stdout():
    return {"rev-parse": HEAD + "\n", "status": ""}


@pytest.fixture
def subprocess_module(settings, git_stdout):
    with patch(
        "gbnf_experiment.prepare_filesystem.write_manifest.subprocess", autospec=True
    ) as m:
        m.run.side_effect = lambda argv, **kwargs: Mock(stdout=git_stdout[argv[3]])
        yield m


@pytest.fixture
def docker_module():
    with patch(
        "gbnf_experiment.prepare_filesystem.write_manifest.docker", autospec=True
    ) as m:
        m.image.inspect.return_value.id = IMAGE_ID
        yield m


@pytest.fixture
def filesystem(
    settings,
    list_prepared_files,
    build_agent_image,
    build_workspace_image,
    subprocess_module,
    docker_module,
):
    return PreparedFilesystem(
        agent=AGENT,
        source_language="typescript",
        include_typescript_tests=False,
        include_python_tests=False,
        debug=False,
    )


def manifest(filesystem) -> dict:
    return json.loads((filesystem.run_directory / "manifest.json").read_text())


def describe_the_workspace():
    def it_selects_the_source_from_the_prepare_stage_listing(filesystem):
        assert filesystem.included == [
            Path("reference_implementation/typescript/package.json"),
            Path("reference_implementation/typescript/src/gbnf.ts"),
        ]

    def it_selects_the_suites_the_condition_asks_for(
        settings, list_prepared_files, build_agent_image, build_workspace_image, docker_module
    ):
        prepared = PreparedFilesystem(
            agent=AGENT,
            source_language="typescript",
            include_typescript_tests=False,
            include_python_tests=True,
            debug=False,
        )
        assert Path("tests/python/validation/validate_test.py") in prepared.included
        assert Path("tests/typescript/validation/validate.test.ts") not in prepared.included

    def it_builds_the_agent_it_was_given(filesystem, build_agent_image):
        build_agent_image.assert_called_once_with(agent=AGENT, debug=False)

    def it_bakes_exactly_the_included_files_onto_the_agent_image(
        filesystem, build_workspace_image
    ):
        build_workspace_image.assert_called_once_with(
            agent_image=AGENT_IMAGE, files=filesystem.included, debug=False
        )

    def it_exposes_the_workspace_image(filesystem):
        assert filesystem.image == WORKSPACE_IMAGE

    def it_forwards_debug_to_every_build(
        settings, list_prepared_files, build_agent_image, build_workspace_image, docker_module
    ):
        PreparedFilesystem(
            agent=AGENT,
            source_language="typescript",
            include_typescript_tests=False,
            include_python_tests=False,
            debug=True,
        )
        assert list_prepared_files.call_args.kwargs["debug"] is True
        assert build_agent_image.call_args.kwargs["debug"] is True
        assert build_workspace_image.call_args.kwargs["debug"] is True

    def it_keeps_no_copy_of_the_reference_on_the_host(filesystem):
        assert not (filesystem.run_directory / "reference_implementation").exists()
        assert not hasattr(filesystem, "reference_implementation_directory")


def describe_the_manifest_at_the_start_of_the_run():
    def it_exists_before_the_result_is_written(filesystem):
        filesystem.write_manifest(**CONDITION)
        assert (filesystem.run_directory / "manifest.json").is_file()

    def it_leaves_completed_at_null(filesystem):
        filesystem.write_manifest(**CONDITION)
        assert manifest(filesystem)["completed_at"] is None

    def it_shares_the_run_directory_s_timestamp(filesystem):
        filesystem.write_manifest(**CONDITION)
        assert manifest(filesystem)["timestamp"] == (
            filesystem.timestamp.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        )

    def it_records_the_condition_it_was_given(filesystem):
        filesystem.write_manifest(**CONDITION)
        assert manifest(filesystem)["condition"] == CONDITION

    def it_names_the_workspace_image_the_port_ran_in(filesystem, docker_module):
        filesystem.write_manifest(**CONDITION)
        docker_module.image.inspect.assert_called_with(WORKSPACE_IMAGE)
        assert manifest(filesystem)["sandbox"] == {"image_id": IMAGE_ID}

    def it_lists_what_the_workspace_holds(filesystem):
        filesystem.write_manifest(**CONDITION)
        assert manifest(filesystem)["reference_implementation"]["included"] == [
            "reference_implementation/typescript/package.json",
            "reference_implementation/typescript/src/gbnf.ts",
        ]


def describe_the_manifest_on_completion():
    def it_stamps_completed_at_in_the_same_iso8601_format(filesystem):
        filesystem.write_manifest(**CONDITION)
        filesystem.write_result('{"is_error": false}', **CONDITION)
        assert re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", manifest(filesystem)["completed_at"]
        )

    def it_stamps_completed_at_no_earlier_than_the_start(filesystem):
        filesystem.write_manifest(**CONDITION)
        filesystem.write_result('{"is_error": false}', **CONDITION)
        recorded = manifest(filesystem)
        assert recorded["completed_at"] >= recorded["timestamp"]

    def it_keeps_the_original_start_timestamp(filesystem):
        filesystem.write_manifest(**CONDITION)
        filesystem.write_result('{"is_error": false}', **CONDITION)
        assert manifest(filesystem)["timestamp"] == (
            filesystem.timestamp.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        )

    def it_carries_no_error_key(filesystem):
        filesystem.write_manifest(**CONDITION)
        filesystem.write_result('{"is_error": false}', **CONDITION)
        assert "error" not in manifest(filesystem)


def describe_the_manifest_on_failure():
    def it_stamps_completed_at(filesystem):
        filesystem.write_manifest(**CONDITION)
        filesystem.write_result(None, error="the container died", **CONDITION)
        assert re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", manifest(filesystem)["completed_at"]
        )

    def it_marks_the_error(filesystem):
        filesystem.write_manifest(**CONDITION)
        filesystem.write_result(None, error="the container died", **CONDITION)
        assert manifest(filesystem)["error"] == "the container died"

    def it_keeps_the_error_out_of_the_condition(filesystem):
        filesystem.write_manifest(**CONDITION)
        filesystem.write_result(None, error="the container died", **CONDITION)
        assert manifest(filesystem)["condition"] == CONDITION

    def it_writes_no_result_json_without_a_result(filesystem):
        filesystem.write_manifest(**CONDITION)
        filesystem.write_result(None, error="the container died", **CONDITION)
        assert not (filesystem.run_directory / "result.json").exists()

    def it_banks_the_result_when_there_is_one(filesystem):
        filesystem.write_manifest(**CONDITION)
        filesystem.write_result('{"is_error": true}', error="exit 1", **CONDITION)
        assert (filesystem.run_directory / "result.json").read_text() == '{"is_error": true}'
