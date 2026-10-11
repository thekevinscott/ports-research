import json
import re
from datetime import UTC
from unittest.mock import Mock, patch

import pytest

from botbox import RunResult

from gbnf_experiment.prepare_filesystem import PreparedFilesystem

HEAD = "c" * 40
IMAGE_ID = "sha256:" + "b" * 64

AGENT = Mock(name="agent")
AGENT.image = "botbox-claude:latest"

TESTS = {
    "include_unit_tests": False,
    "include_source_integration_tests": False,
    "include_target_integration_tests": True,
}
CONDITION = {
    "source_language": "javascript",
    **TESTS,
    "effort": "high",
    "model": "claude-opus-5",
}
SHARED = (
    "javascript/package.json",
    "javascript/src/gbnf.ts",
    "python/tests/generated/iteration/iteration_test.py",
)


def run_result(stdout='{"is_error": false}', stderr="", exit_code=0) -> RunResult:
    return RunResult(stdout=stdout, stderr=stderr, exit_code=exit_code, transcript={}, proxy="")


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
def prepare_reference_implementation(tmp_path):
    """Returns the extracted /shared: a cache entry in upstream layout."""
    with patch(
        "gbnf_experiment.prepare_filesystem.prepared_filesystem.prepare_reference_implementation",
        autospec=True,
    ) as m:
        shared = tmp_path / "cache" / "prepared" / "key"
        for name in SHARED:
            (shared / name).parent.mkdir(parents=True, exist_ok=True)
            (shared / name).write_text(name)
        m.return_value = shared
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
    subprocess_module,
    docker_module,
):
    return PreparedFilesystem(source_language="javascript", **TESTS, debug=False)


def manifest(filesystem) -> dict:
    return json.loads((filesystem.run_directory / "manifest.json").read_text())


def describe_the_reference_implementation():
    def it_prepares_the_condition(filesystem, prepare_reference_implementation):
        prepare_reference_implementation.assert_called_once_with(
            source_language="javascript", **TESTS, debug=False
        )

    def it_is_the_extracted_shared_tree_unchanged(filesystem, prepare_reference_implementation):
        assert filesystem.reference_implementation_directory is (
            prepare_reference_implementation.return_value
        )

    def it_lists_every_file_in_it_relative_to_its_root(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        assert manifest(filesystem)["reference_implementation"]["included"] == list(SHARED)


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
        filesystem.write_result(run_result(), AGENT, **CONDITION)
        assert re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", manifest(filesystem)["completed_at"]
        )

    def it_stamps_completed_at_no_earlier_than_the_start(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        filesystem.write_result(run_result(), AGENT, **CONDITION)
        recorded = manifest(filesystem)
        assert recorded["completed_at"] >= recorded["timestamp"]

    def it_keeps_the_original_start_timestamp(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        filesystem.write_result(run_result(), AGENT, **CONDITION)
        assert manifest(filesystem)["timestamp"] == (
            filesystem.timestamp.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        )

    def it_carries_no_error_key(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        filesystem.write_result(run_result(), AGENT, **CONDITION)
        assert "error" not in manifest(filesystem)

    def it_records_the_agent_s_exit_code(filesystem):
        filesystem.write_manifest(AGENT, **CONDITION)
        filesystem.write_result(run_result(exit_code=3), AGENT, **CONDITION)
        assert manifest(filesystem)["exit_code"] == 3

    def it_banks_the_agent_s_stdout_as_result_json(filesystem):
        filesystem.write_result(run_result(stdout='{"num_turns": 4}'), AGENT, **CONDITION)
        assert (filesystem.run_directory / "result.json").read_text() == '{"num_turns": 4}'

    def it_banks_the_agent_s_stderr_beside_the_result(filesystem):
        filesystem.write_result(run_result(stderr="warning: x\n"), AGENT, **CONDITION)
        assert (filesystem.run_directory / "stderr.txt").read_text() == "warning: x\n"

    def it_banks_an_empty_stderr_as_an_empty_file(filesystem):
        filesystem.write_result(run_result(stderr=""), AGENT, **CONDITION)
        assert (filesystem.run_directory / "stderr.txt").read_text() == ""


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

    def it_writes_no_stderr_without_a_result(filesystem):
        filesystem.write_result(None, AGENT, error="the container died", **CONDITION)
        assert not (filesystem.run_directory / "stderr.txt").exists()

    def it_records_no_exit_code_without_a_result(filesystem):
        filesystem.write_result(None, AGENT, error="the container died", **CONDITION)
        assert "exit_code" not in manifest(filesystem)
