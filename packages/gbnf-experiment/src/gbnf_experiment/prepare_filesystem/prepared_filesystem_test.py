import json
import re
from datetime import UTC
from unittest.mock import Mock, patch

import pytest

from gbnf_experiment.prepare_filesystem import PreparedFilesystem

HEAD = "c" * 40
IMAGE_ID = "sha256:" + "b" * 64

AGENT = Mock(name="agent")
AGENT.image = "agent-harness-sandbox-claude:latest"

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
        m.prepared_directory = tmp_path / "cache" / "prepared"
        m.data_directory = tmp_path / "data"
        m.gbnf_commit = "13f1aca"
        yield m


@pytest.fixture
def prepare_reference_implementation():
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.prepare_reference_implementation",
        autospec=True,
    ) as m:
        yield m


@pytest.fixture
def assemble_reference_implementation(tmp_path):
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.assemble_reference_implementation",
        autospec=True,
    ) as m:
        m.return_value = (
            tmp_path / "reference_implementation",
            ["/package.json"],
            ["package.json"],
        )
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
    prepare_reference_implementation,
    assemble_reference_implementation,
    subprocess_module,
    docker_module,
):
    with PreparedFilesystem(
        source_language="typescript",
        include_typescript_tests=False,
        include_python_tests=False,
        debug=False,
    ) as prepared:
        yield prepared


def manifest(filesystem) -> dict:
    return json.loads((filesystem.run_directory / "manifest.json").read_text())


def describe_the_manifest_at_the_start_of_the_run():
    def it_exists_before_the_result_is_written(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        assert (filesystem.run_directory / "manifest.json").is_file()

    def it_leaves_completed_at_null(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        assert manifest(filesystem)["completed_at"] is None

    def it_shares_the_run_directory_s_timestamp(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        assert manifest(filesystem)["timestamp"] == (
            filesystem.timestamp.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        )

    def it_records_the_condition_it_was_given(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        assert manifest(filesystem)["condition"] == CONDITION


def describe_the_manifest_on_completion():
    def it_stamps_completed_at_in_the_same_iso8601_format(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        filesystem.write_result('{"is_error": false}', AGENT, **CONDITION)
        assert re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", manifest(filesystem)["completed_at"]
        )

    def it_stamps_completed_at_no_earlier_than_the_start(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        filesystem.write_result('{"is_error": false}', AGENT, **CONDITION)
        recorded = manifest(filesystem)
        assert recorded["completed_at"] >= recorded["timestamp"]

    def it_keeps_the_original_start_timestamp(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        filesystem.write_result('{"is_error": false}', AGENT, **CONDITION)
        assert manifest(filesystem)["timestamp"] == (
            filesystem.timestamp.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        )

    def it_carries_no_error_key(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        filesystem.write_result('{"is_error": false}', AGENT, **CONDITION)
        assert "error" not in manifest(filesystem)


def describe_the_manifest_on_failure():
    def it_stamps_completed_at(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        filesystem.write_result(None, AGENT, error="the container died", **CONDITION)
        assert re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", manifest(filesystem)["completed_at"]
        )

    def it_marks_the_error(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        filesystem.write_result(None, AGENT, error="the container died", **CONDITION)
        assert manifest(filesystem)["error"] == "the container died"

    def it_keeps_the_error_out_of_the_condition(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        filesystem.write_result(None, AGENT, error="the container died", **CONDITION)
        assert manifest(filesystem)["condition"] == CONDITION

    def it_writes_no_result_json_without_a_result(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        filesystem.write_result(None, AGENT, error="the container died", **CONDITION)
        assert not (filesystem.run_directory / "result.json").exists()

    def it_banks_the_result_when_there_is_one(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        filesystem.write_result('{"is_error": true}', AGENT, error="exit 1", **CONDITION)
        assert (filesystem.run_directory / "result.json").read_text() == '{"is_error": true}'
